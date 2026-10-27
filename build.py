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

import html as htmlmod
import json
import os
import re
from datetime import date, datetime, timezone
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
                 desc=p["blurb"], canonical=f"{SITE_URL}/{slug}/",
                 og_title=p["title"], og_image=slug)


def build_archive(eds):
    body = [masthead(["Full archive", plural(len(eds)),
                      "Three publications"], current="archive")]
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
                 desc="Every edition of The Bay Weekender, The Weekly Soccer "
                      "Digest and The Weekly Arsenal Digest.",
                 canonical=SITE_URL + "/archive.html")


def build_edition(e, eds):
    p = PUBS[e["pub"]]
    same = [x for x in eds if x["pub"] == e["pub"]]
    i = same.index(e)
    newer = same[i - 1] if i > 0 else None
    older = same[i + 1] if i + 1 < len(same) else None

    nav = [
        (f'<a href="/editions/{older["slug"]}.html">&larr; Previous: {short(older["date"])}</a>'
         if older else "<span></span>"),
        f'<a href="/{e["pub"]}/">All {esc(p["short"])} editions</a>',
        (f'<a href="/editions/{newer["slug"]}.html">Next: {short(newer["date"])} &rarr;</a>'
         if newer else "<span></span>"),
    ]

    body = [masthead([p["title"], pretty(e["date"]), p["cadence"]])]
    prev_a = (f'<a class="pv" href="/editions/{older["slug"]}.html" rel="prev">'
              f'<span class="lbl">&larr; Previous edition</span>{short(older["date"])}</a>'
              if older else "")
    next_a = (f'<a class="nx" href="/editions/{newer["slug"]}.html" rel="next">'
              f'<span class="lbl">Next edition &rarr;</span>{short(newer["date"])}</a>'
              if newer else "")
    if prev_a or next_a:
        body.append(f'<nav class="ed-topnav sans" aria-label="Other editions">'
                    f'{prev_a}{next_a}</nav>')
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
    body.append(r"""<script>
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

  /* Trim the event detail rows on older Bay editions. "Getting there" and
     "Good for" were dropped from the publication, and the date and start time
     are now labelled separately. Editions written after that change already
     look like this, so the pass simply finds nothing and stops. */
  var DATE_TIME=/^\s*(.*\b\d{4})\.\s*(\S.*)$/;

  function trimDetails(d){
    var rows=d.querySelectorAll('p.em');
    for(var i=0;i<rows.length;i++){
      var p=rows[i];
      if(p.getAttribute('data-trimmed'))continue;
      p.setAttribute('data-trimmed','1');
      var parts=p.innerHTML.split('<br>'), out=[], changed=false;
      for(var j=0;j<parts.length;j++){
        var seg=parts[j], plain=seg.replace(/<[^>]+>/g,'').trim();
        if(/^(Getting there|Good for)\b/i.test(plain)){ changed=true; continue; }
        var w=seg.match(/^\s*<b>\s*When\s*<\/b>([\s\S]*)$/i);
        if(w){
          var m=w[1].replace(/<[^>]+>/g,'').match(DATE_TIME);
          if(m){
            out.push('<b>When</b> '+m[1].trim());
            out.push('<b>Time</b> '+m[2].trim());
            changed=true;
            continue;
          }
        }
        out.push(seg);
      }
      if(changed)p.innerHTML=out.join('<br>');
    }
  }

  /* In-page jumps land the target in the middle of the window instead of
     jammed against the top. The edition fills a frame as tall as its own
     content, so the browser's anchor handling scrolls the PARENT page and
     pins the target to the very top edge, half of it hidden behind the page
     furniture. Take the jump over: unfold whatever the target is collapsed
     inside, then place it in comfortable view. */
  function anchorJump(d){
    if(d.__anchors)return;
    d.__anchors=1;
    d.addEventListener('click',function(ev){
      var a=(ev.target&&ev.target.closest)?ev.target.closest('a[href^="#"]'):null;
      if(!a)return;
      var id=(a.getAttribute('href')||'').slice(1);
      if(!id)return;
      var el=null;
      try{ el=d.getElementById(id); }catch(e){}
      if(!el)return;
      ev.preventDefault();
      /* An event sits inside a collapsed disclosure. Landing on a folded row
         is not arriving anywhere, so open every one above it first. */
      var p=el;
      while(p&&p!==d.body){ if(p.tagName==='DETAILS'&&!p.open)p.open=true; p=p.parentElement; }
      var place=function(){
        fit();                                  /* the frame just got taller */
        var r=el.getBoundingClientRect(),
            top=f.getBoundingClientRect().top+window.scrollY+r.top,
            vh=window.innerHeight,
            /* An individual event is the thing you came to read, so put it in
               the middle of the window. A section heading is a starting point,
               so sit it near the top with its contents below, which is what a
               heading is for. Anything taller than the window cannot be
               centred meaningfully, so start it a quarter of the way down. */
            isEvent=/^ev-/.test(el.id)||(el.className||'').split(' ').indexOf('ev')>-1,
            pad=!isEvent?vh*0.12:(r.height<vh*0.8?(vh-r.height)/2:vh*0.25),
            reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        window.scrollTo({top:Math.max(0,top-pad),behavior:reduce?'auto':'smooth'});
      };
      if(window.requestAnimationFrame)requestAnimationFrame(place); else setTimeout(place,0);
    },true);
  }

  /* Send outbound links to a new tab. The edition sits in a frame, so a plain
     link loads the destination INSIDE that frame: the reader gets someone
     else's site wearing our page furniture, with no way back. Same-page
     anchors are left alone so the contents shortcuts still work. */
  function externalLinks(d){
    var as=d.querySelectorAll('a[href]');
    for(var i=0;i<as.length;i++){
      var h=as[i].getAttribute('href')||'';
      if(!/^(https?:)?\/\//i.test(h))continue;      /* skip #anchors and relative links */
      if(as[i].getAttribute('target')==='_blank')continue;
      as[i].setAttribute('target','_blank');
      as[i].setAttribute('rel','noopener noreferrer');
    }
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
    try{ var d=f.contentDocument;
         if(d){inject(d);externalLinks(d);trimDetails(d);anchorJump(d);} }catch(e){}
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
                 wide=True, og_title=f"{p['title']}: {pretty(e['date'])}",
                 og_image=e["pub"], og_type="article")


# ---------------------------------------------------------------------- search

def edition_text(slug):
    """The readable words of an edition, for the search index."""
    path = os.path.join(ROOT, "editions", "raw", slug + ".html")
    try:
        with open(path, encoding="utf-8") as f:
            t = f.read()
    except OSError:
        return ""
    t = re.sub(r"<(script|style|head|svg)\b[\s\S]*?</\1>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def build_search_index(eds):
    rows = [{"s": e["slug"], "p": e["pub"], "d": e["date"],
             "t": f"{PUBS[e['pub']]['title']}: {pretty(e['date'])}",
             "k": e.get("dek", ""), "x": edition_text(e["slug"])} for e in eds]
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


def build_search(eds):
    pubs = json.dumps({s: {"t": PUBS[s]["title"]} for s in PUB_ORDER})
    checks = "".join(
        f'<label><input type="checkbox" data-pub="{s}" checked> '
        f'<span style="color:var(--pub-{s})">{esc(PUBS[s]["short"])}</span></label>'
        for s in PUB_ORDER)
    body = [masthead(["Search", plural(len(eds)), "Three publications"],
                     current="search")]
    body.append(section("Search every edition"))
    body.append(f"""<form class="searchbox sans" role="search" onsubmit="return false">
  <label for="q" style="position:absolute;left:-9999px">Search all editions</label>
  <input id="q" type="search" placeholder="Try Saka, Outside Lands, Chase Center" autocomplete="off">
</form>
<div class="searchfilters sans">{checks}</div>
<p class="searchstatus sans" id="status" aria-live="polite">Type a word or name to search all {len(eds)} editions.</p>
<ul class="hits" id="hits"></ul>
<noscript><p class="nowempty">Search needs JavaScript. The <a href="/archive.html">full archive</a> lists every edition.</p></noscript>""")
    body.append(footer())
    body.append(r"""<script>
(function(){
  var PUBS=""" + pubs + r""", DATA=null, q=document.getElementById('q'),
      hits=document.getElementById('hits'), status=document.getElementById('status'),
      boxes=document.querySelectorAll('[data-pub]');
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function load(cb){
    if(DATA)return cb();
    status.textContent='Loading the archive…';
    fetch('/search-index.json').then(function(r){return r.json();}).then(function(d){
      DATA=d.map(function(e){e.n=norm(e.x);return e;}); cb();
    }).catch(function(){status.textContent='Search could not load. Try again in a moment.';});
  }
  function snippet(e,terms){
    var at=-1;
    for(var i=0;i<terms.length&&at<0;i++)at=e.n.indexOf(terms[i]);
    var s=Math.max(0,at-90), raw=e.x.slice(s,s+260);
    var out=esc((s>0?'…':'')+raw+(s+260<e.x.length?'…':''));
    terms.forEach(function(t){
      if(t.length<2)return;
      out=out.replace(new RegExp('('+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'),'<mark>$1</mark>');
    });
    return out;
  }
  function run(){
    var raw=q.value.trim();
    try{history.replaceState(null,'',raw?('?q='+encodeURIComponent(raw)):location.pathname);}catch(e){}
    if(raw.length<2){hits.innerHTML='';status.textContent='Type a word or name to search all editions.';return;}
    load(function(){
      var terms=norm(raw).split(/\s+/).filter(Boolean), on={};
      boxes.forEach(function(b){on[b.getAttribute('data-pub')]=b.checked;});
      var res=[];
      DATA.forEach(function(e){
        if(!on[e.p])return;
        var score=0;
        for(var i=0;i<terms.length;i++){
          var c=e.n.split(terms[i]).length-1;
          if(!c)return;
          score+=c;
        }
        res.push({e:e,score:score});
      });
      res.sort(function(a,b){return b.score-a.score||(a.e.d<b.e.d?1:-1);});
      status.textContent=res.length?(res.length+' edition'+(res.length===1?'':'s')+' mention “'+raw+'”'):'No editions mention “'+raw+'”.';
      hits.innerHTML=res.slice(0,40).map(function(r){
        var e=r.e;
        return '<li><a href="/editions/'+e.s+'.html"><span class="hp sans" style="color:var(--pub-'+e.p+')">'
          +esc(PUBS[e.p].t)+'</span><span class="hd sans">'+esc(e.t.split(': ')[1]||'')+' · '+r.score+' mention'+(r.score===1?'':'s')
          +'</span><p class="hs">'+snippet(e,terms)+'</p></a></li>';
      }).join('');
    });
  }
  var t=null;
  q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,180);});
  boxes.forEach(function(b){b.addEventListener('change',run);});
  var m=location.search.match(/[?&]q=([^&]+)/);
  if(m){q.value=decodeURIComponent(m[1].replace(/\+/g,' '));run();}
})();
</script>""")
    return shell("Search · The Newsstand", "\n".join(body),
                 desc="Search every edition of The Bay Weekender, The Weekly "
                      "Soccer Digest and The Weekly Arsenal Digest.",
                 canonical=SITE_URL + "/search.html")


# ------------------------------------------------------------ what's on now

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
     "nov", "dec"], 1)}
CATS = {"music": ("Music, Arts & Nightlife", "#0e7c86"),
        "food": ("Food, Drink & Festivals", "#c85a2b"),
        "outdoors": ("Outdoors, Sports & Active", "#3b7a57")}


def _clean(s):
    s = re.sub(r"<br\s*/?>", " · ", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", htmlmod.unescape(s)).strip(" ·")


def _row(chunk, label):
    """A labelled detail (When, Time, Where, Price) in either edition style."""
    m = re.search(r"<dt>\s*" + label + r"\s*</dt>\s*<dd>([\s\S]*?)</dd>", chunk, re.I)
    if m:
        return _clean(m.group(1))
    m = re.search(r"<b>\s*" + label + r"\s*</b>([\s\S]*?)(?:<br\s*/?>\s*<b>|</p>)", chunk, re.I)
    return _clean(m.group(1)) if m else ""


def _dates(text, ed_date):
    """Every calendar date mentioned in a When line, as date objects.
    Handles 'Friday October 30', 'Oct 15 & 17', 'November 7 to December 19'."""
    out, month = [], None
    for tok in re.finditer(r"([A-Za-z]{3,9})\.?|(?<!\d)(\d{1,2})(?:st|nd|rd|th)?\b(?!:|\d)", text):
        word, num = tok.group(1), tok.group(2)
        if word:
            k = word[:3].lower()
            month = MONTHS.get(k, month) if k in MONTHS else month
            continue
        if month and num:
            d = int(num)
            if not 1 <= d <= 31:
                continue
            y = ed_date.year + (1 if month < ed_date.month - 2 else 0)
            try:
                out.append(date(y, month, d))
            except ValueError:
                pass
    return out


def bay_events(e):
    path = os.path.join(ROOT, "editions", "raw", e["slug"] + ".html")
    try:
        with open(path, encoding="utf-8") as f:
            t = f.read()
    except OSError:
        return []
    ed_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
    out = []
    for m in re.finditer(r'<details\b([^>]*\bclass="ev\b[^"]*"[^>]*)>([\s\S]*?)</details>', t):
        attrs, chunk = m.group(1), m.group(2)
        idm = re.search(r'\bid="([^"]+)"', attrs)
        cat = re.search(r'data-cat="(\w+)"', attrs) or re.search(r'\b(?:ev|c)-(music|food|outdoors)\b', attrs)
        name = re.search(r'class="(?:evname|en)"[^>]*>([\s\S]*?)</span>', chunk)
        hook = re.search(r'class="(?:hook|ek)"[^>]*>([\s\S]*?)</span>', chunk)
        link = re.search(r'<p class="(?:golink|el)"[^>]*>\s*<a href="([^"]+)"', chunk)
        when = _row(chunk, "When")
        ds = re.search(r'data-start="(\d{4}-\d{2}-\d{2})"', attrs)
        de = re.search(r'data-end="(\d{4}-\d{2}-\d{2})"', attrs)
        if ds:
            start = datetime.strptime(ds.group(1), "%Y-%m-%d").date()
            end = datetime.strptime(de.group(1), "%Y-%m-%d").date() if de else start
        else:
            found = _dates(when, ed_date)
            if not found:
                continue
            start, end = min(found), max(found)
        if not name:
            continue
        out.append({
            "id": idm.group(1) if idm else "",
            "slug": e["slug"],
            "cat": cat.group(1) if cat else "",
            "name": _clean(name.group(1)),
            "hook": _clean(hook.group(1)) if hook else "",
            "when": when, "time": _row(chunk, "Time"),
            "where": _row(chunk, "Where"), "price": _row(chunk, "Price"),
            "link": htmlmod.unescape(link.group(1)) if link else "",
            "start": start.isoformat(), "end": end.isoformat(),
        })
    return out


def build_now(eds):
    # Only the newest edition. It already looks five weeks ahead, and anything
    # still upcoming from an older edition either reappears in it or was
    # dropped on purpose, so mixing editions only adds duplicates.
    bay = [e for e in eds if e["pub"] == "bay-weekender"][:1]
    seen, events = set(), []
    for e in bay:
        for ev in bay_events(e):
            key = re.sub(r"[^a-z0-9]", "", ev["name"].lower())[:40] + ev["start"]
            addr = re.sub(r"[^a-z0-9]", "", ev["where"].split("·")[-1].lower())[:24]
            key2 = ev["start"] + addr if addr else None
            if key in seen or (key2 and key2 in seen):
                continue          # the newer edition's version wins
            seen.add(key)
            if key2:
                seen.add(key2)
            events.append(ev)
    events.sort(key=lambda v: (v["start"], v["name"]))
    checks = "".join(
        f'<label><input type="checkbox" data-cat="{k}" checked> '
        f'<span class="sw" style="background:{c}"></span>{esc(lbl)}</label>'
        for k, (lbl, c) in CATS.items())
    latest = bay[0] if bay else None
    body = [masthead(["The Bay Weekender", "What's on now",
                      "Updated with every edition"], current="now")]
    body.append(section("What's on in the Bay"))
    intro = ("Everything from the latest Bay Weekender that has not happened yet, "
             "soonest first. Past events drop off on their own.")
    if latest:
        intro += (f' The latest edition, from {pretty(latest["date"])}, is '
                  f'<a href="/editions/{latest["slug"]}.html" style="text-decoration:underline">here</a>.')
    body.append(f'<p class="nowintro">{intro}</p>')
    body.append(f'<div class="nowfilters sans">{checks}</div>')
    body.append('<p class="searchstatus sans" id="nowcount" aria-live="polite"></p>')
    body.append('<div id="nowlist"></div>')
    body.append('<noscript><p class="nowempty">This page needs JavaScript to hide '
                'past events. The latest edition lists everything.</p></noscript>')
    body.append(subscribe_block(only="bay-weekender"))
    body.append(footer())
    data = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
    cats = json.dumps({k: c for k, (_, c) in CATS.items()})
    body.append(r"""<script>
(function(){
  var EV=""" + data + """, COL=""" + cats + r""";
  var list=document.getElementById('nowlist'), count=document.getElementById('nowcount'),
      boxes=document.querySelectorAll('[data-cat]');
  function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  /* Today in San Francisco, whatever time zone the reader is in. */
  function today(){
    try{return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles'}).format(new Date());}
    catch(e){return new Date().toISOString().slice(0,10);}
  }
  function nice(iso){
    var p=iso.split('-'), d=new Date(Date.UTC(+p[0],+p[1]-1,+p[2],12));
    return d.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',timeZone:'UTC'});
  }
  function draw(){
    var t=today(), on={}, groups={}, order=[], n=0;
    boxes.forEach(function(b){on[b.getAttribute('data-cat')]=b.checked;});
    EV.forEach(function(e){
      if(e.end<t)return;
      if(e.cat&&on[e.cat]===false)return;
      var key=e.start<t?t:e.start;          /* already running: file under today */
      if(!groups[key]){groups[key]=[];order.push(key);}
      groups[key].push(e); n++;
    });
    order.sort();
    count.textContent=n?(n+' upcoming event'+(n===1?'':'s')):'';
    if(!n){list.innerHTML='<p class="nowempty">Nothing upcoming from recent editions. The next Bay Weekender will fill this up.</p>';return;}
    list.innerHTML=order.map(function(k){
      return '<div class="nowday"><h3 class="sans">'+(k===t?'Today &middot; ':'')+esc(nice(k))+'</h3>'
        +groups[k].map(function(e){
          var multi=e.end!==e.start?' &middot; runs through '+esc(nice(e.end).replace(/^\w+, /,'')):'';
          var meta=[e.time,e.where,e.price].filter(Boolean).map(esc).join(' &middot; ');
          return '<div class="nowev"><span class="spine" style="background:'+(COL[e.cat]||'#999')+'"></span><div>'
            +'<h4>'+esc(e.name)+'</h4><div class="m sans">'+meta+multi+'</div>'
            +(e.hook?'<p>'+esc(e.hook)+'</p>':'')
            +'<div class="lk sans"><a href="/editions/'+e.slug+'.html'+(e.id?'#'+e.id:'')+'">In the edition</a>'
            +(e.link?'<a href="'+esc(e.link)+'" target="_blank" rel="noopener noreferrer">Tickets and details</a>':'')
            +'</div></div></div>';
        }).join('')+'</div>';
    }).join('');
  }
  boxes.forEach(function(b){b.addEventListener('change',draw);});
  draw();
})();
</script>""")
    return shell("What's on in the Bay · The Newsstand", "\n".join(body),
                 desc="Upcoming Bay Area events from The Bay Weekender, soonest "
                      "first. Past events drop off on their own.",
                 canonical=SITE_URL + "/bay-weekender/now.html",
                 og_title="What's on in the Bay", og_image="bay-weekender")


# ----------------------------------------------------------------------- about

def build_about(eds):
    body = [masthead(["About", "Three publications", plural(len(eds))],
                     current="about")]
    body.append(section("About The Newsstand"))
    parts = ['<div class="prose">',
             "<p>The Newsstand is the home of three free newsletters. Each one is "
             "published here first and emailed to subscribers the same day. Every "
             "past edition stays here, so you can catch up on anything you "
             "missed, search the whole archive, or share a single edition with "
             "a friend.</p>"]
    for s in PUB_ORDER:
        p = PUBS[s]
        n = sum(1 for e in eds if e["pub"] == s)
        parts.append(f'<h3 style="color:var(--pub-{s})">{esc(p["title"])}</h3>'
                     f'<div class="cad sans">{esc(p["cadence"])} &middot; {plural(n)} so far</div>'
                     f'<p>{esc(p["blurb"])} <a href="/{s}/" style="text-decoration:underline">'
                     f'Read past editions</a>.</p>')
    parts.append(
        "<h3>How it works</h3><p>Every story is checked against the original "
        "source before it runs, and anything unconfirmed is labelled as a rumour. "
        "Kickoff and event times are given in Pacific time. Each edition says "
        "what it covers and when it was written, so an older edition is still "
        "useful as a record of that week.</p>"
        "<h3>Subscribing</h3><p>All three are free. Pick the ones you want "
        "below, and stop any time.</p>")
    parts.append("</div>")
    body.append("".join(parts))
    body.append(subscribe_block())
    body.append(footer())
    return shell("About · The Newsstand", "\n".join(body),
                 desc="What The Newsstand is: three free newsletters about Bay "
                      "Area events, world football and Arsenal.",
                 canonical=SITE_URL + "/about.html")


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
    written.append(write("search.html", build_search(eds)))
    written.append(write("search-index.json", build_search_index(eds)))
    written.append(write("bay-weekender/now.html", build_now(eds)))
    written.append(write("about.html", build_about(eds)))
    print(f"built {len(written)} files from {len(eds)} editions")


if __name__ == "__main__":
    main()
