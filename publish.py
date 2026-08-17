#!/usr/bin/env python3
"""
The Newsstand — publish one edition.

This is the script the weekly scheduled tasks call. It takes a finished
edition's HTML, files it into the archive, rebuilds the site, and pushes.

Usage:
  python3 publish.py \
      --pub soccer-digest \
      --date 2026-08-19 \
      --dek "One sentence teaser for the index page." \
      --html /tmp/edition.html \
      [--title "August 19, 2026"] \
      [--no-push]

The slug is derived automatically as <pub>-<date>. Re-publishing the same
pub+date REPLACES that edition rather than creating a duplicate, so a task
that retries is safe to run twice.

Exit codes: 0 ok, 1 bad input, 2 git/push failure (edition still written).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

from theme import PUBS

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "manifest.json")
RAW_DIR = os.path.join(ROOT, "editions", "raw")

MIN_BYTES = 4000  # an edition smaller than this is a failed render, not an edition


def run(cmd, check=True):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode != 0:
        print(f"  ! {' '.join(cmd)}\n    {p.stderr.strip()}", file=sys.stderr)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pub", required=True, choices=sorted(PUBS))
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--html", required=True, help="path to the finished edition HTML")
    ap.add_argument("--dek", default="", help="one-sentence teaser for the index")
    ap.add_argument("--title", default="", help="defaults to the formatted date")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    # ---- validate ---------------------------------------------------------
    try:
        d = datetime.strptime(a.date, "%Y-%m-%d")
    except ValueError:
        print(f"error: --date must be YYYY-MM-DD, got {a.date!r}", file=sys.stderr)
        return 1

    if not os.path.isfile(a.html):
        print(f"error: no such file: {a.html}", file=sys.stderr)
        return 1

    size = os.path.getsize(a.html)
    if size < MIN_BYTES:
        print(f"error: {a.html} is only {size} bytes — that is a failed render, "
              f"not an edition. Refusing to publish a stub.", file=sys.stderr)
        return 1

    with open(a.html, encoding="utf-8", errors="replace") as f:
        head = f.read(2000).lower()
    if "<html" not in head and "<table" not in head and "<body" not in head:
        print(f"error: {a.html} does not look like HTML. Refusing to publish.",
              file=sys.stderr)
        return 1

    slug = f"{a.pub}-{a.date}"
    title = a.title or d.strftime("%B %-d, %Y")

    # ---- file the edition -------------------------------------------------
    os.makedirs(RAW_DIR, exist_ok=True)
    dest = os.path.join(RAW_DIR, f"{slug}.html")
    shutil.copyfile(a.html, dest)
    print(f"  filed  editions/raw/{slug}.html  ({size:,} bytes)")

    # ---- upsert into the manifest ----------------------------------------
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    eds = [e for e in m.get("editions", []) if e["slug"] != slug]
    replaced = len(eds) != len(m.get("editions", []))
    eds.append({"slug": slug, "pub": a.pub, "date": a.date,
                "title": title, "dek": a.dek})
    eds.sort(key=lambda e: (e["date"], e["slug"]), reverse=True)
    m["editions"] = eds
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  {'replaced' if replaced else 'added'} manifest entry: {slug} "
          f"({len(eds)} editions total)")

    # ---- rebuild ----------------------------------------------------------
    p = run([sys.executable, "build.py"])
    if p.returncode != 0:
        return 1
    print("  " + p.stdout.strip().splitlines()[0])

    if a.no_push:
        print("  --no-push set, stopping before git")
        return 0

    # ---- commit and push --------------------------------------------------
    run(["git", "config", "user.email", "newsstand@users.noreply.github.com"], check=False)
    run(["git", "config", "user.name", "The Newsstand"], check=False)
    run(["git", "add", "-A"], check=False)

    status = run(["git", "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        print("  nothing changed, no commit needed")
        return 0

    msg = f"{PUBS[a.pub]['title']} — {title}"
    if run(["git", "commit", "-m", msg], check=False).returncode != 0:
        print("error: commit failed", file=sys.stderr)
        return 2

    push = run(["git", "push"], check=False)
    if push.returncode != 0:
        # Most likely another edition landed first. Rebase and retry once.
        print("  push rejected, rebasing and retrying...")
        run(["git", "pull", "--rebase"], check=False)
        push = run(["git", "push"], check=False)
        if push.returncode != 0:
            print("error: push failed after retry. The edition IS committed "
                  "locally; it just is not on GitHub yet.", file=sys.stderr)
            return 2

    print(f"  pushed: {msg}")
    print(f"  live shortly at https://evanagribben.github.io/editions/{slug}.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
