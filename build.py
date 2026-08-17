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

from theme import (PUBS, PUB_ORDER, shell, esc, masthead, footer,
                  subscribe_block)

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://evanagribben.github.io"


def load():
    with open(os.path.join(ROOT, "manifest.json")) as f:
        m = json.load(f)
    eds = m.get("editions", [])
    # newest first, stable
    eds.sort(key=lambda e: (e["date"], e["slug"]), reverse=True)
    return m, eds


def pretty(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")


def short(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d, %Y")


# ------------------------------------------------------------------ components

def lead_card(e):
    p = PUBS[e["pub"]]
    return f"""<a class="lead" style="border-left-color:{p['spine']}" href="/editions/{e['slug']}.html">
  <div class="pubname sans" style="color:{p['spine']}">{esc(p['title'])}</div>
  <h2>{esc(e['title'])}</h2>
  <p class="dek">{esc(e.get('dek',''))}</p>
  <div class="meta sans">{pretty(e['date'])} &nbsp;·&nbsp; Read the edition &rarr;</div>
</a>"""


def small_card(e):
    p = PUBS[e["pub"]]
    return f"""<a class="card" style="border-left-color:{p['spine']}" href="/editions/{e['slug']}.html">
  <div class="pubname sans" style="color:{p['spine']}">{esc(p['title'])}</div>
  <h3>{esc(e['title'])}</h3>
  <p class="dek">{esc(e.get('dek',''))}</p>
  <div class="meta sans">{short(e['date'])}</div>
</a>"""


def arch_rows(eds, show_pub=True):
    out = []
    for e in eds:
        p = PUBS[e["pub"]]
        pub = (f'<span class="p sans" style="color:{p["spine"]}">{esc(p["title"])}</span>'
               if show_pub else "")
        out.append(f"""<li><a href="/editions/{e['slug']}.html">
  <span class="dot" style="background:{p['spine']}"></span>
  <span class="d sans">{short(e['date'])}</span>
  <span class="t">{esc(e['title'])}</span>
  {pub}
</a></li>""")
    return '<ul class="arch">' + "".join(out) + "</ul>"


# ----------------------------------------------------------------------- pages

def build_home(eds):
    body = [masthead()]
    body.append('<div class="wrap">')
    body.append(f'<div class="rule-row sans"><span>Three publications</span>'
                f'<span>{len(eds)} edition{"s" if len(eds)!=1 else ""} archived</span>'
                f'<span>Updated {datetime.now(timezone.utc).strftime("%B %-d, %Y")}</span></div>')

    # One card per publication: its most recent edition, newest publication
    # first. eds is already sorted newest-first, so the first time a pub is
    # seen is its latest.
    latest = []
    seen = set()
    for e in eds:
        if e["pub"] not in seen:
            seen.add(e["pub"])
            latest.append(e)

    body.append('<div class="kicker sans">Latest edition</div>')
    if latest:
        body.append('<div class="grid">'
                    + "".join(small_card(e) for e in latest) + "</div>")
    else:
        body.append('<p style="color:#6b6459">No editions published yet. '
                    'The first one lands here automatically.</p>')

    body.append('<div class="kicker sans">The publications</div>')
    body.append('<div class="grid">')
    for slug in PUB_ORDER:
        p = PUBS[slug]
        n = sum(1 for e in eds if e["pub"] == slug)
        body.append(f"""<div class="pubcard" style="border-top-color:{p['spine']}">
  <h3>{esc(p['title'])}</h3>
  <div class="cad sans">{esc(p['cadence'])} &nbsp;·&nbsp; {n} edition{"s" if n!=1 else ""}</div>
  <p>{esc(p['blurb'])}</p>
  <a class="more sans" style="color:{p['spine']}" href="/{slug}/">Read {esc(p['title'])} &rarr;</a>
</div>""")
    body.append("</div>")
    body.append("</div>")
    body.append(subscribe_block())
    body.append(footer())
    return shell("The Newsstand", "\n".join(body),
                 desc="Three independent weekly editions: Bay Area events, world "
                      "football, and Arsenal.",
                 canonical=SITE_URL + "/")


def build_pub(slug, eds):
    p = PUBS[slug]
    mine = [e for e in eds if e["pub"] == slug]
    body = [masthead(active=slug)]
    body.append('<div class="wrap">')
    body.append(f'<div class="kicker sans" style="border-bottom-color:{p["spine"]}">'
                f'{esc(p["title"])}</div>')
    body.append(f'<p style="font-size:17px;color:#4f4a42;max-width:660px">{esc(p["blurb"])}</p>')
    body.append(f'<div class="rule-row sans"><span>{esc(p["cadence"])}</span>'
                f'<span>{len(mine)} edition{"s" if len(mine)!=1 else ""}</span></div>')
    if mine:
        body.append(lead_card(mine[0]))
        if mine[1:]:
            body.append('<div class="kicker sans">Every edition</div>')
            body.append(arch_rows(mine[1:], show_pub=False))
    else:
        body.append('<p style="color:#6b6459">No editions yet.</p>')
    body.append("</div>")
    body.append(subscribe_block())
    body.append(footer())
    return shell(p["title"] + " · The Newsstand", "\n".join(body),
                 desc=p["blurb"], canonical=f"{SITE_URL}/{slug}/")


def build_archive(eds):
    body = [masthead()]
    body.append('<div class="wrap">')
    body.append('<div class="kicker sans">Full archive</div>')
    by_year = {}
    for e in eds:
        by_year.setdefault(e["date"][:4], []).append(e)
    for year in sorted(by_year, reverse=True):
        body.append(f'<div class="kicker sans">{year}</div>')
        body.append(arch_rows(by_year[year]))
    if not eds:
        body.append('<p style="color:#6b6459">Nothing archived yet.</p>')
    body.append("</div>")
    body.append(footer())
    return shell("Archive · The Newsstand", "\n".join(body),
                 canonical=SITE_URL + "/archive.html")


def build_edition(e, eds):
    p = PUBS[e["pub"]]
    same = [x for x in eds if x["pub"] == e["pub"]]
    i = same.index(e)
    newer = same[i - 1] if i > 0 else None
    older = same[i + 1] if i + 1 < len(same) else None

    nav = []
    nav.append(f'<a href="/editions/{newer["slug"]}.html">&larr; Newer</a>'
               if newer else "<span></span>")
    nav.append(f'<a href="/{e["pub"]}/">All {esc(p["title"])} editions</a>')
    nav.append(f'<a href="/editions/{older["slug"]}.html">Older &rarr;</a>'
               if older else "<span></span>")

    body = [masthead(active=e["pub"])]
    body.append('<div class="wrap">')
    body.append(f"""<div class="ed-head">
  <a class="back sans" href="/{e['pub']}/">&larr; {esc(p['title'])}</a>
  <div class="pubname sans" style="color:{p['spine']}">{esc(p['title'])}</div>
  <h1>{esc(e['title'])}</h1>
  <p style="font-size:17px;color:#4f4a42;max-width:660px;margin:4px 0 12px">{esc(e.get('dek',''))}</p>
  <div class="meta sans">Published {pretty(e['date'])}</div>
</div>""")
    body.append(f"""<div class="ed-body">
  <iframe id="ed" src="/editions/raw/{e['slug']}.html"
          title="{esc(e['title'])}" loading="lazy"></iframe>
</div>
<div class="ed-nav sans">{''.join(nav)}</div>
<p class="sans" style="font-size:12px;color:#8a8377;margin-top:18px">
  <a href="/editions/raw/{e['slug']}.html">Open this edition on its own &rarr;</a>
</p>""")
    body.append("</div>")
    body.append(subscribe_block())
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
    <title>{esc(e['title'])} · {esc(p['title'])}</title>
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
  <description>Three independent weekly editions.</description>
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
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main()
