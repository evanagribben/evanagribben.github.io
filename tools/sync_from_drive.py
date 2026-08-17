#!/usr/bin/env python3
"""
Pull new editions out of Google Drive and into the site.

This runs inside GitHub Actions, NOT in the newsletter task's sandbox. That is
the whole point: the tasks can always reach Drive, and GitHub can always reach
Drive, but the tasks cannot reach GitHub. So GitHub pulls instead of the task
pushing.

Needs one secret, GOOGLE_API_KEY, which is a plain Google API key with the
Drive API enabled. It only ever reads. The three Drive folders must be shared
"Anyone with the link -> Viewer", which is what lets a key-only request see
them. Nothing here can write to, rename or delete anything in Drive.

Usage:
  GOOGLE_API_KEY=... python3 tools/sync_from_drive.py [--dry-run]
"""

import html as htmllib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "manifest.json")
RAW_DIR = os.path.join(ROOT, "editions", "raw")

API = "https://www.googleapis.com/drive/v3"
KEY = os.environ.get("GOOGLE_API_KEY", "")

# Publication slug -> the Drive folder its editions are saved into.
FOLDERS = {
    "bay-weekender":  "1-8m1qdNphhUprVn7Um98j8UX9r1nmAon",
    "soccer-digest":  "1iLxnfixwH3AprW5Y9BI2aZGv6tryQtTy",
    "arsenal-digest": "1OGM0twyssyxMghwMkAymHsbp2jNG4n89",
}

GDOC = "application/vnd.google-apps.document"
FOLDER = "application/vnd.google-apps.folder"
SHEET = "application/vnd.google-apps.spreadsheet"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}
DATE_RE = re.compile(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})")

MIN_BYTES = 4000          # same stub guard publish.py uses
DRY = "--dry-run" in sys.argv


def log(msg):
    print(msg, flush=True)


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "newsstand-sync"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def list_folder(folder_id):
    """Every non-folder file directly inside a public Drive folder."""
    out, token = [], None
    while True:
        q = urllib.parse.urlencode({
            "q": f"'{folder_id}' in parents and trashed = false",
            "key": KEY,
            "fields": "nextPageToken,files(id,name,mimeType,size,modifiedTime)",
            "pageSize": "200",
            **({"pageToken": token} if token else {}),
        })
        data = json.loads(get(f"{API}/files?{q}"))
        out.extend(data.get("files", []))
        token = data.get("nextPageToken")
        if not token:
            return out


def edition_date(name):
    m = DATE_RE.search(name)
    if not m:
        return None
    try:
        return (f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
                if m.group(1) in MONTHS else None)
    except Exception:
        return None


def download(f):
    """Return the edition's HTML bytes, whatever kind of Drive file it is."""
    if f["mimeType"] == GDOC:
        # Native Docs export as HTML through the public docs endpoint.
        return get(f"https://docs.google.com/document/d/{f['id']}/export?format=html")
    return get(f"{API}/files/{f['id']}?alt=media&key={KEY}")


def extract_dek(html, fallback):
    """Prefer an explicit <meta name="dek">; otherwise take the first real
    sentence of visible text. Never invent anything."""
    m = re.search(r'<meta\s+name=["\']dek["\']\s+content=["\'](.*?)["\']',
                  html, re.I | re.S)
    if m:
        return htmllib.unescape(re.sub(r"\s+", " ", m.group(1))).strip()[:400]

    body = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", body)
    text = htmllib.unescape(text).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Skip the masthead words and find something sentence-shaped.
    for chunk in re.split(r"(?<=[.!?])\s+", text):
        c = chunk.strip()
        if 60 <= len(c) <= 300:
            return c
    return fallback


def main():
    if not KEY:
        log("ERROR: GOOGLE_API_KEY is not set. Add it as a repository secret.")
        return 1

    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    # A slug only counts as "have" if its raw file is ACTUALLY on disk. A
    # manifest entry whose file is missing renders as an empty iframe on the
    # site, so treat it as absent and re-fetch it.
    listed = {e["slug"] for e in manifest.get("editions", [])}
    have = {s for s in listed
            if os.path.isfile(os.path.join(RAW_DIR, f"{s}.html"))}
    orphans = listed - have
    log(f"manifest lists {len(listed)} edition(s); {len(have)} have files")
    if orphans:
        log("re-fetching entries whose file is missing: " + ", ".join(sorted(orphans)))
        manifest["editions"] = [e for e in manifest["editions"]
                                if e["slug"] not in orphans]

    added, skipped, failed = [], 0, []

    for pub, folder_id in FOLDERS.items():
        log(f"\n=== {pub}")
        try:
            files = list_folder(folder_id)
        except Exception as e:
            log(f"  ! cannot list folder: {e}")
            log("    Is it shared 'Anyone with the link -> Viewer'?")
            failed.append(pub)
            continue

        # newest first, so if two files share a date the latest one wins
        files.sort(key=lambda f: f.get("modifiedTime", ""), reverse=True)
        seen_dates = set()

        for f in files:
            name = f["name"]
            if f["mimeType"] in (FOLDER, SHEET):
                continue
            if "[TEST]" in name.upper() or name.lower().endswith(".pdf"):
                continue

            date = edition_date(name)
            if not date:
                log(f"  ? no date in name, skipping: {name}")
                continue
            if date in seen_dates:
                continue            # older duplicate of a date already taken
            seen_dates.add(date)

            slug = f"{pub}-{date}"
            if slug in have:
                skipped += 1
                continue

            log(f"  + {slug}  <- {name}")
            if DRY:
                added.append(slug)
                continue

            try:
                blob = download(f)
            except Exception as e:
                log(f"    ! download failed: {e}")
                failed.append(slug)
                continue

            if len(blob) < MIN_BYTES:
                log(f"    ! only {len(blob)} bytes, refusing to publish a stub")
                failed.append(slug)
                continue

            html = blob.decode("utf-8", errors="replace")
            os.makedirs(RAW_DIR, exist_ok=True)
            with open(os.path.join(RAW_DIR, f"{slug}.html"), "w",
                      encoding="utf-8") as fh:
                fh.write(html)

            title = datetime.strptime(date, "%Y-%m-%d").strftime("%B %-d, %Y")
            manifest.setdefault("editions", []).append({
                "slug": slug, "pub": pub, "date": date, "title": title,
                "dek": extract_dek(html, title),
            })
            have.add(slug)
            added.append(slug)
            log(f"    wrote {len(blob):,} bytes")

    if added and not DRY:
        manifest["editions"].sort(key=lambda e: (e["date"], e["slug"]),
                                  reverse=True)
        with open(MANIFEST, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    log(f"\nadded {len(added)}, already had {skipped}, failed {len(failed)}")
    if failed:
        log("failed: " + ", ".join(map(str, failed)))
    # A failure to fetch should be visible, but must not wipe a good site.
    return 1 if failed and not added else 0


if __name__ == "__main__":
    sys.exit(main())
