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
    side = (f'<div class="pubname" style="color:var(--pub-' + e["pub"] + ')">'
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
        pub = ('<span class="p sans" style="color:var(--pub-' + e["pub"] + ')">'
               f'{esc(p["short"])}</span>' if show_pub else "")
        out.append(f"""<li><a href="/editions/{e['slug']}.html">
  <span class="dot" style="background:var(--spine-{e['pub']})"></span>
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
        body.append(f"""<div class="pub" style="border-top:4px solid var(--spine-{slug})">
  <h3>{esc(p['title'])}</h3>
  <div class="cad sans">{esc(p['cadence'])} &middot; {plural(n)}</div>
  <p>{esc(p['blurb'])}</p>
  <a class="go sans" style="color:var(--pub-{slug})" href="/{slug}/">Read them all &rarr;</a>
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
  <div class="pubname sans" style="color:var(--pub-{e['pub']})">{esc(p['title'])}</div>
  <h1>{esc(e['title'])}</h1>
  <p class="dek">{esc(e.get('dek',''))}</p>
  <div class="meta sans">Published {pretty(e['date'])}</div>
</div>
<nav class="ed-toc sans" id="toc" hidden aria-label="In this edition">
  <div class="toc-h" style="color:var(--pub-{e['pub']})">In this edition</div>
  <ul id="toclist"></ul>
</nav>
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
    skip = json.dumps([p["title"], p["short"], e["title"], "The Newsstand"])
    body.append("""<script>
/* The edition renders in a same-origin iframe so its own styling survives
   byte-for-byte. Newsletters are authored to an email-safe sheet width
   (roughly 620-760px). On a desktop screen that leaves the page mostly
   margin, so we widen the sheet in place: any container whose own width
   sits in the email-sheet range is stretched to fill the frame. Narrow
   elements (cards, sidebars, images) are left alone, and everything is
   restored when the viewport gets small, so phones and the emailed
   version are untouched. */
(function(){
  var f=document.getElementById('ed');
  var MIN=520, MAX=1000, FLOOR=900;

  function fit(){
    try{
      var d=f.contentDocument;
      if(!d||!d.body)return;
      /* Measure the BODY only. documentElement.scrollHeight is at least the
         frame's own height, so feeding it back in grows the frame a little
         on every call. */
      var h=Math.max(d.body.scrollHeight,
                     Math.ceil(d.body.getBoundingClientRect().height));
      if(h>200)f.style.height=(h+40)+'px';
    }catch(e){}
  }

  /* Fixed-width tables in the source overflow a phone screen. This is
     site-side only; the emailed version is untouched. */
  function inject(d){
    if(d.getElementById('ns-fit'))return;
    var s=d.createElement('style');
    s.id='ns-fit';
    s.textContent='img,video{max-width:100%;height:auto}'
      +'@media(max-width:820px){table[width]{width:100%!important}'
      +'table{max-width:100%}}';
    (d.head||d.documentElement).appendChild(s);
  }

  /* Dark theme inside the frame. The edition is authored as a light document
     we do not control, so rather than restyle it we invert it and flip the hue
     back, which preserves relative colour, then invert media and map tiles a
     second time so photographs and maps come back the right way round. */
  function themeIsDark(){
    var set=document.documentElement.getAttribute('data-theme');
    if(set)return set==='dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function paint(){
    var d;
    try{ d=f.contentDocument; }catch(e){ return; }
    if(!d||!d.documentElement)return;
    var s=d.getElementById('ns-dark');
    if(!themeIsDark()){ if(s)s.parentNode.removeChild(s); return; }
    if(s)return;
    s=d.createElement('style');
    s.id='ns-dark';
    s.textContent='html{filter:invert(1) hue-rotate(180deg);background:#111}'
      +'img,video,canvas,picture,.leaflet-container,.leaflet-tile,.leaflet-tile-pane,'
      +'[style*="background-image"]{filter:invert(1) hue-rotate(180deg)}';
    (d.head||d.documentElement).appendChild(s);
  }

  /* Text size inside the frame. The edition is authored in px for email, so
     the root-font-size trick that scales the site does nothing here. Instead
     record each element's ORIGINAL size once, before any scaling, and set
     every one from that baseline. Scaling from the current value instead
     would compound on each press and drift. */
  var BASE=null, BASEDOC=null, TEXT=1;

  function baseline(d){
    /* Key the baseline to the document it came from. A frame starts life on a
       blank document, so a capture taken before the edition loads would find
       one element and, if memoised, silently freeze the whole feature. */
    if(BASE&&BASEDOC===d&&BASE.length>3)return;
    BASE=[]; BASEDOC=d;
    var all=d.querySelectorAll('body, body *');
    for(var i=0;i<all.length;i++){
      var px=parseFloat(getComputedStyle(all[i]).fontSize);
      if(px)BASE.push({el:all[i],px:px,inline:all[i].style.fontSize});
    }
  }

  function scaleText(){
    var d;
    try{ d=f.contentDocument; }catch(e){ return; }
    if(!d||!d.body)return;
    baseline(d);
    for(var i=0;i<BASE.length;i++){
      var o=BASE[i];
      o.el.style.fontSize = TEXT===1 ? o.inline : (o.px*TEXT)+'px';
    }
    widen(); fit();
  }

  window.addEventListener('newsstand-text',function(ev){
    var s=ev&&ev.detail;
    if(typeof s==='number'&&s>0){ TEXT=s; scaleText(); }
  });

  function restore(d){
    (d.__wide||[]).forEach(function(o){
      o.el.style.maxWidth=o.mw;
      if(o.w===null)o.el.removeAttribute('width');
      else if(o.w!==undefined)o.el.setAttribute('width',o.w);
    });
    d.__wide=null;
  }

  function widen(){
    try{
      var d=f.contentDocument;
      if(!d||!d.body)return;
      var avail=f.clientWidth;
      if(avail<FLOOR){ if(d.__wide)restore(d); return; }
      if(d.__wide)restore(d);
      var target=avail-24, store=[];
      var all=d.querySelectorAll('body, body *');
      for(var i=0;i<all.length;i++){
        var el=all[i], cs=getComputedStyle(el);
        var mw=parseFloat(cs.maxWidth);
        var wa=(el.tagName==='TABLE')?parseInt(el.getAttribute('width'),10):NaN;
        var hitMw=(mw>=MIN&&mw<=MAX);
        var hitWa=(wa>=MIN&&wa<=MAX);
        if(!hitMw&&!hitWa)continue;
        var pad=0;
        if(cs.boxSizing!=='border-box'){
          pad=(parseFloat(cs.paddingLeft)||0)+(parseFloat(cs.paddingRight)||0)
             +(parseFloat(cs.borderLeftWidth)||0)+(parseFloat(cs.borderRightWidth)||0);
        }
        store.push({el:el, mw:el.style.maxWidth,
                    w: hitWa ? el.getAttribute('width') : undefined});
        el.style.maxWidth=Math.max(MIN,target-pad)+'px';
        if(hitWa)el.setAttribute('width','100%');
      }
      d.__wide=store;
    }catch(e){}
  }

  /* Section shortcuts above the edition. Editions written from August 2026
     onwards carry their own contents block, so this only fills the gap for
     ones that do not: it reads the edition's sections and links to them.
     The frame is sized to its full content and never scrolls internally, so
     a jump is a scroll of the parent page. */
  var TOC=document.getElementById('toc'),
      LIST=document.getElementById('toclist'),
      SKIP={SKIP_JSON};

  function labelOf(el){
    var t=(el.textContent||'').replace(/\s+/g,' ').trim();
    if(t.length<3||t.length>72)return null;
    if((t.match(/[A-Za-z]/g)||[]).length<3)return null;  /* skips stat headings like 40,000 */
    return t;
  }

  function isNameplate(t){
    var k=t.toLowerCase().replace(/[^a-z]/g,'');
    for(var i=0;i<SKIP.length;i++){
      var s=SKIP[i].toLowerCase().replace(/[^a-z]/g,'');
      if(s&&k===s)return true;
    }
    return false;
  }

  function findSections(d){
    var out=[], tagged=d.querySelectorAll('[data-toc]');
    if(tagged.length>=3){
      tagged.forEach(function(el){
        var l=(el.getAttribute('data-toc')||'').trim()||labelOf(el);
        if(l)out.push({el:el,label:l});
      });
      return out.slice(0,14);
    }
    var els=d.querySelectorAll('h2'), n=0;
    els.forEach(function(el){ if(labelOf(el))n++; });
    if(n<3)els=d.querySelectorAll('h1,h2,h3');
    els.forEach(function(el){
      var t=labelOf(el);
      if(t&&!isNameplate(t))out.push({el:el,label:t});
    });
    return out.slice(0,14);
  }

  function ownTocNearTop(d){
    var els=d.querySelectorAll('h1,h2,h3,h4,div,p,td,span,strong,b');
    var all=d.querySelectorAll('*'), total=all.length||1;
    for(var i=0;i<els.length;i++){
      var t=(els[i].textContent||'').replace(/\s+/g,' ').trim();
      if(t.length>24||!/^in this edition$/i.test(t))continue;
      /* Must be near the top in DOM ORDER, not just on screen. A script-built
         panel appended to the end of the body can be pinned into view while
         sitting last in the document, and that is not a contents block a
         reader can use. */
      var pos=Array.prototype.indexOf.call(all,els[i])/total;
      if(pos<0.25&&els[i].getBoundingClientRect().top<1400)return true;
    }
    return false;
  }

  function buildToc(){
    var d;
    try{ d=f.contentDocument; }catch(err){ return; }
    if(!d||!d.body||LIST.children.length)return;
    /* If the edition already prints its own shortcuts near the top, do not add
       a second set. Test for its label rather than for anchors in general:
       editions are full of in-page links, and one edition builds a contents
       list with script and dumps it off the bottom of the page where nobody
       sees it. Only a visible block near the top counts. */
    if(ownTocNearTop(d))return;
    var found=findSections(d);
    if(found.length<3)return;
    found.forEach(function(h){
      var li=document.createElement('li'), a=document.createElement('a');
      a.href='#'; a.textContent=h.label;
      a.addEventListener('click',function(ev){
        ev.preventDefault();
        var y=f.getBoundingClientRect().top+window.scrollY
              +h.el.getBoundingClientRect().top-14;
        var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        /* Animate short hops, jump long ones. A smooth scroll across ten
           thousand pixels is a wall of blur and reads as broken. */
        var far=Math.abs(y-window.scrollY)>1800;
        window.scrollTo({top:y,behavior:(reduce||far)?'auto':'smooth'});
      });
      li.appendChild(a); LIST.appendChild(li);
    });
    TOC.hidden=false;
  }

  function run(){
    try{ var d=f.contentDocument; if(d)inject(d); }catch(e){}
    widen(); fit(); buildToc(); paint();
    if(TEXT!==1)scaleText();
  }
  /* Repaint the frame whenever the reader flips the theme. */
  try{
    new MutationObserver(paint).observe(document.documentElement,
      {attributes:true,attributeFilter:['data-theme']});
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',paint);
  }catch(e){}
  f.addEventListener('load',function(){
    run();setTimeout(run,300);setTimeout(run,1200);
  });
  window.addEventListener('resize',run);
})();
</script>""".replace("{SKIP_JSON}", skip))
    return shell(f"{e['title']} · {p['title']}", "\n".join(body),
                 desc=e.get("dek", ""),
                 canonical=f"{SITE_URL}/editions/{e['slug']}.html",
                 wide=True)


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
