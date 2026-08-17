#!/usr/bin/env python3
"""
The Newsstand: site generator.

Reads manifest.json, writes index.html, per-publication pages, archive.html,
one wrapper page per edition, and feed.xml.

Every edition's ORIGINAL html is preserved byte-for-byte in editions/raw/ and
displayed inside the site chrome via a same-origin iframe. That means the
newsletter's own styling renders exactly as it does in Gmail, with no CSS
collisions against the site and full formatting fidelity.

Usage:  python3 build.py
"""

import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime

from theme import (PUBS, PUB_ORDER, shell, esc, masthead, footer, section,
                   subscribe_block)

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://evanagribben.github.io"


def load():
    with open(os.path.join(ROOT, "manifest.json")) as f:
        m = json.load(f)
    eds = m.get("editions", [])
    eds.sort(key=lambda e: (e["date"], e["slug"]), reverse=True)
    return m, eds


def pretty(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")


def short(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d, %Y")


def plural(n, word="edition"):
    return f"{n} {word}{'s' if n != 1 else ''}"


# ------------------------------------------------------------------ components

def ed_row(e, show_pub=True):
    """A generous edition row: publication and date at left, story at right."""
    p = PUBS[e["pub"]]
    side = (f'<div class="pubname" style="color:{p["text"]}">'
            f'{esc(p["title"])}</div>' if show_pub else "")
    return f"""<a class="ed" href="/editions/{e['slug']}.html">
  <div class="side sans">
    {side}
    <div class="when">{short(e['date'])}</div>
  </div>
  <div>
    <h3>{esc(e['title'])}</h3>
    <p>{esc(e.get('dek',''))}</p>
    <div class="go sans">Read the edition &rarr;</div>
  </div>
</a>"""


def arch_rows(eds, show_pub=True):
    out = []
    for e in eds:
        p = PUBS[e["pub"]]
        pub = (f'<span class="p sans" style="color:{p["text"]}">'
               f'{esc(p["short"])}</span>' if show_pub else "")
        out.append(f"""<li><a href="/editions/{e['slug']}.html">
  <span class="dot" style="background:{p['spine']}"></span>
  <span class="d sans">{short(e['date'])}</span>
  <span class="t">{esc(e['title'])}</span>
  {pub}
</a></li>""")
    return '<ul class="arch">' + "".join(out) + "</ul>"


# ----------------------------------------------------------------------- pages

def build_home(eds):
    # One row per publication: its most recent edition. eds is newest-first,
    # so the first time a publication appears is its latest.
    latest, seen = [], set()
    for e in eds:
        if e["pub"] not in seen:
            seen.add(e["pub"])
            latest.append(e)

    body = [masthead([
        "Three publications",
        plural(len(eds)) + " archived",
        "Updated " + datetime.now(timezone.utc).strftime("%B %-d, %Y"),
    ])]

    body.append(section("Latest Edition"))
    if latest:
        body.append("".join(ed_row(e) for e in latest))
    else:
        body.append('<p style="color:#8f8571;text-align:center;max-width:52ch;'
                    'margin:0 auto">This week\'s editions appear here as they '
                    'are written. The Bay Weekender publishes Monday, '
                    'The Weekly Arsenal Digest Tuesday, and '
                    'The Weekly Soccer Digest Wednesday.</p>')

    body.append(section("The Publications"))
    body.append('<div class="pubs">')
    for slug in PUB_ORDER:
        p = PUBS[slug]
        n = sum(1 for e in eds if e["pub"] == slug)
        body.append(f"""<div class="pub" style="border-top:4px solid {p['spine']}">
  <h3>{esc(p['title'])}</h3>
  <div class="cad sans">{esc(p['cadence'])} &middot; {plural(n)}</div>
  <p>{esc(p['blurb'])}</p>
  <a class="go sans" style="color:{p['text']}" href="/{slug}/">Read them all &rarr;</a>
</div>""")
    body.append("</div>")

    body.append(subscribe_block())
    body.append(footer())
    return shell("The Newsstand", "\n".join(body),
                 desc="Three independent weekly publications: Bay Area events, "
                      "world football, and Arsenal.",
                 canonical=SITE_URL + "/")


def build_pub(slug, eds):
    p = PUBS[slug]
    mine = [e for e in eds if e["pub"] == slug]
    body = [masthead([p["cadence"], plural(len(mine)), p["tagline"]])]
    body.append(section(p["title"]))
    body.append(f'<div class="pubintro"><p>{esc(p["blurb"])}</p></div>')
    if mine:
        body.append('<div style="margin-top:26px">'
                    + "".join(ed_row(e, show_pub=False) for e in mine)
                    + "</div>")
    else:
        body.append('<p style="color:#8f8571;text-align:center">No editions yet.</p>')
    body.append(subscribe_block(only=slug))
    body.append(footer())
    return shell(p["title"] + " · The Newsstand", "\n".join(body),
                 desc=p["blurb"], canonical=f"{SITE_URL}/{slug}/")


def build_archive(eds):
    body = [masthead(["Full archive", plural(len(eds)),
                      "Three publications"])]
    by_year = {}
    for e in eds:
        by_year.setdefault(e["date"][:4], []).append(e)
    for year in sorted(by_year, reverse=True):
        body.append(section(year))
        body.append(arch_rows(by_year[year]))
    if not eds:
        body.append('<p style="color:#8f8571;text-align:center">'
                    'Nothing archived yet.</p>')
    body.append(footer())
    return shell("Archive · The Newsstand", "\n".join(body),
                 canonical=SITE_URL + "/archive.html")


def build_edition(e, eds):
    p = PUBS[e["pub"]]
    same = [x for x in eds if x["pub"] == e["pub"]]
    i = same.index(e)
    newer = same[i - 1] if i > 0 else None
    older = same[i + 1] if i + 1 < len(same) else None

    nav = [
        (f'<a href="/editions/{newer["slug"]}.html">&larr; Newer</a>'
         if newer else "<span></span>"),
        f'<a href="/{e["pub"]}/">All {esc(p["short"])} editions</a>',
        (f'<a href="/editions/{older["slug"]}.html">Older &rarr;</a>'
         if older else "<span></span>"),
    ]

    body = [masthead([p["title"], pretty(e["date"]), p["cadence"]])]
    body.append(f"""<div class="ed-head">
  <a class="back sans" href="/{e['pub']}/">&larr; {esc(p['title'])}</a>
  <div class="pubname sans" style="color:{p['text']}">{esc(p['title'])}</div>
  <h1>{esc(e['title'])}</h1>
  <p class="dek">{esc(e.get('dek',''))}</p>
  <div class="meta sans">Published {pretty(e['date'])}</div>
</div>
<div class="ed-body">
  <iframe id="ed" src="/editions/raw/{e['slug']}.html"
          title="{esc(e['title'])}" loading="lazy"></iframe>
</div>
<div class="ed-nav sans">{''.join(nav)}</div>
<p class="sans" style="font-size:11px;color:#8f8571;margin-top:16px">
  <a href="/editions/raw/{e['slug']}.html" style="text-decoration:underline">
  Open this edition on its own &rarr;</a>
</p>""")
    body.append(subscribe_block(only=e["pub"]))
    body.append(footer())
    body.append("""<script>
(function(){
  var f=document.getElementById('ed');
  function fit(){
    try{
      var d=f.contentDocument;
      if(!d||!d.body)return;
      var h=Math.max(d.body.scrollHeight,d.documentElement.scrollHeight);
      if(h>200)f.style.height=(h+60)+'px';
    }catch(e){}
  }
  f.addEventListener('load',function(){fit();setTimeout(fit,300);setTimeout(fit,1200);});
  window.addEventListener('resize',fit);
})();
</script>""")
    return shell(f"{e['title']} · {p['title']}", "\n".join(body),
                 desc=e.get("dek", ""),
                 canonical=f"{SITE_URL}/editions/{e['slug']}.html")


def build_feed(eds):
    items = []
    for e in eds[:40]:
        p = PUBS[e["pub"]]
        dt = datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        link = f"{SITE_URL}/editions/{e['slug']}.html"
        items.append(f"""  <item>
    <title>{esc(p['title'])}: {esc(e['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <category>{esc(p['title'])}</category>
    <pubDate>{format_datetime(dt)}</pubDate>
    <description>{esc(e.get('dek',''))}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>The Newsstand</title>
  <link>{SITE_URL}/</link>
  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Three independent weekly publications.</description>
  <language>en-us</language>
  <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""


# ------------------------------------------------------------------------ main

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return rel


def main():
    _, eds = load()
    written = [write("index.html", build_home(eds))]
    for slug in PUB_ORDER:
        written.append(write(f"{slug}/index.html", build_pub(slug, eds)))
    written.append(write("archive.html", build_archive(eds)))
    for e in eds:
        written.append(write(f"editions/{e['slug']}.html", build_edition(e, eds)))
    written.append(write("feed.xml", build_feed(eds)))
    print(f"built {len(written)} files from {len(eds)} editions")


if __name__ == "__main__":
    main()
