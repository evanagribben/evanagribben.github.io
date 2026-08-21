"""
The Newsstand: shared design system and page templates.

Every page this generates is SELF-CONTAINED (CSS inlined in a <style> block),
so any page renders correctly opened straight off disk, emailed, or served.

Design: a restrained newspaper. Centred nameplate, real rules, generous rows,
colour used only as a hairline accent so the writing carries the page.
"""

# ---------------------------------------------------------------- publications

PUBS = {
    "bay-weekender": {
        "title": "The Bay Weekender",
        "short": "Bay Weekender",
        "tagline": "San Francisco & the Bay Area",
        "blurb": "Events across San Francisco and the wider Bay Area: music, arts "
                 "and nightlife; food, drink and festivals; outdoors, sports and "
                 "active.",
        "spine": "#b8860b",
        "text": "#8a6410",
        "cadence": "Every other Monday",
    },
    "soccer-digest": {
        "title": "The Weekly Soccer Digest",
        "short": "Soccer Digest",
        "tagline": "World football, everything but Arsenal",
        "blurb": "The Premier League, La Liga, Bundesliga, Serie A, Ligue 1 and "
                 "MLS. Transfers, tactics, and the stories breaking before they "
                 "are fully public.",
        "spine": "#0f7a4e",
        "text": "#0f7a4e",
        "cadence": "Wednesdays",
    },
    "arsenal-digest": {
        "title": "The Weekly Arsenal Digest",
        "short": "Arsenal Digest",
        "tagline": "One club, covered properly",
        "blurb": "Everything Arsenal: the first team, transfers, tactics, Hale "
                 "End, Arsenal Women and Gunners on international duty.",
        "spine": "#EF0107",
        "text": "#b00105",
        "cadence": "Tuesdays",
    },
}

PUB_ORDER = ["bay-weekender", "soccer-digest", "arsenal-digest"]

# ------------------------------------------------------------------ design css

BASE_CSS = """
/* ------------------------------------------------------------------ palette
   Every colour is a token so the whole site can flip to a dark theme. Light is
   defined on :root; dark overrides the same names, once for a reader whose
   system asks for dark and again for an explicit choice, so the toggle wins
   either way. */
:root{
  --bg:#f3efe6; --panel:#fbf8f1; --hover:#eee9dd;
  --ink:#1a1713; --ink-strong:#12100d;
  --body:#4d4638; --body-soft:#5b5344;
  --muted:#8f8571; --muted-2:#7d7466; --muted-3:#9a8f7c;
  --rule:#cec5b2; --rule-soft:#ddd4c1; --rule-hard:#b9ae99;
  --field:#fff; --btn-ink:#f3efe6; --btn-hover:#3a332a;
  --pub-bay-weekender:#8a6410;
  --pub-soccer-digest:#0f7a4e;
  --pub-arsenal-digest:#b00105;
  --spine-bay-weekender:#b8860b;
  --spine-soccer-digest:#0f7a4e;
  --spine-arsenal-digest:#EF0107;
}
@media(prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#14120f; --panel:#1c1915; --hover:#221e19;
    --ink:#ece7dd; --ink-strong:#f5f1e8;
    --body:#c6bdae; --body-soft:#b3aa9c;
    --muted:#8d8578; --muted-2:#968d7f; --muted-3:#867e72;
    --rule:#37312a; --rule-soft:#2c2721; --rule-hard:#4a4339;
    --field:#211d18; --btn-ink:#14120f; --btn-hover:#d8d2c6;
    --pub-bay-weekender:#dba53f;
    --pub-soccer-digest:#4fbf8b;
    --pub-arsenal-digest:#ff7175;
    --spine-bay-weekender:#dba53f;
    --spine-soccer-digest:#4fbf8b;
    --spine-arsenal-digest:#ff4d52;
  }
}
:root[data-theme="dark"]{
  --bg:#14120f; --panel:#1c1915; --hover:#221e19;
  --ink:#ece7dd; --ink-strong:#f5f1e8;
  --body:#c6bdae; --body-soft:#b3aa9c;
  --muted:#8d8578; --muted-2:#968d7f; --muted-3:#867e72;
  --rule:#37312a; --rule-soft:#2c2721; --rule-hard:#4a4339;
  --field:#211d18; --btn-ink:#14120f; --btn-hover:#d8d2c6;
  --pub-bay-weekender:#dba53f;
  --pub-soccer-digest:#4fbf8b;
  --pub-arsenal-digest:#ff7175;
  --spine-bay-weekender:#dba53f;
  --spine-soccer-digest:#4fbf8b;
  --spine-arsenal-digest:#ff4d52;
}

/* Sizes are in rem and spacing in em, so a reader who raises their
   browser or phone default text size gets the whole page scaled
   proportionally instead of a broken layout. */
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:Georgia,'Times New Roman',serif;line-height:1.68;
  -webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:900px;margin:0 auto;padding:0 30px}
/* Edition pages run wider on desktop so the newsletter itself can breathe. */
.wrap.wide{max-width:1180px}
.sans{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}

/* theme toggle */
.themebar{display:flex;justify-content:flex-end;padding:14px 0 0;min-height:1px}
.themetoggle{display:inline-flex;align-items:center;gap:.5rem;background:none;
  border:1px solid var(--rule);color:var(--muted);cursor:pointer;
  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:.625rem;
  letter-spacing:.2em;text-transform:uppercase;padding:.5rem .7rem;
  min-height:36px;transition:color .12s,border-color .12s}
.themetoggle:hover{color:var(--ink);border-color:var(--ink)}
.themetoggle:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.themetoggle svg{width:14px;height:14px;fill:none;stroke:currentColor;
  stroke-width:1.6;stroke-linecap:round}
.themetoggle .lbl-dark,:root[data-theme="dark"] .themetoggle .lbl-light{display:none}
:root[data-theme="dark"] .themetoggle .lbl-dark{display:inline}
.themetoggle .i-moon{display:none}
:root[data-theme="dark"] .themetoggle .i-moon{display:block}
:root[data-theme="dark"] .themetoggle .i-sun{display:none}
@media(prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .themetoggle .lbl-light{display:none}
  :root:not([data-theme="light"]) .themetoggle .lbl-dark{display:inline}
  :root:not([data-theme="light"]) .themetoggle .i-sun{display:none}
  :root:not([data-theme="light"]) .themetoggle .i-moon{display:block}
}

/* masthead */
.mast{text-align:center;padding:58px 0 0}
.mast .kick{font-size:0.625rem;letter-spacing:0.5em;text-transform:uppercase;
  color:var(--muted-3);margin-bottom:20px}
.mast h1{font-size:4.125rem;margin:0;letter-spacing:-0.023em;line-height:1;
  color:var(--ink-strong);font-weight:400}
.mast h1 a{text-decoration:none}
.mast .rule{border-top:1px solid var(--ink);border-bottom:3px solid var(--ink);
  height:5px;margin:26px 0 0}
.mast .dateline{display:flex;justify-content:space-between;flex-wrap:wrap;
  gap:12px;font-size:0.6562rem;letter-spacing:0.229em;text-transform:uppercase;
  color:var(--muted-2);padding:11px 2px;border-bottom:1px solid var(--rule)}

/* nav */
.nav{display:flex;justify-content:center;gap:44px;flex-wrap:wrap;padding:16px 0;
  border-bottom:1px solid var(--rule)}
.nav a{font-size:0.7188rem;letter-spacing:0.191em;text-transform:uppercase;
  font-weight:700;padding-bottom:4px;border-bottom:2px solid transparent}
.nav a:hover,.nav a:focus-visible{border-bottom-color:currentColor}

/* section heads: a centred label sitting on a rule */
.sec{margin:58px 0 4px;text-align:center}
.sec h2{font-size:0.6875rem;letter-spacing:0.409em;text-transform:uppercase;
  color:var(--ink);margin:0;font-weight:700;display:inline-block;
  background:var(--bg);padding:0 18px;position:relative;top:9px}
.secline{border-top:1px solid var(--rule-hard);margin-bottom:30px}

/* edition rows */
.ed{display:grid;grid-template-columns:9.4rem 1fr;gap:28px;padding:26px 0;
  border-bottom:1px solid var(--rule-soft);align-items:start;transition:background .13s}
.ed:hover{background:var(--hover)}
.ed:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.ed .side{text-align:right}
.ed .pubname{font-size:0.625rem;letter-spacing:0.22em;text-transform:uppercase;
  font-weight:700;line-height:1.5}
.ed .when{font-size:0.6562rem;letter-spacing:0.152em;text-transform:uppercase;
  color:var(--muted);margin-top:7px}
.ed h3{font-size:1.625rem;margin:0 0 8px;line-height:1.22;letter-spacing:-0.012em}
.ed p{margin:0;font-size:1.0312rem;color:var(--body);max-width:60ch}
.ed .go{margin-top:12px;font-size:0.6562rem;letter-spacing:0.21em;
  text-transform:uppercase;color:var(--muted)}

/* publication columns */
.pubs{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));
  gap:34px;margin-top:8px}
.pub{padding-top:16px}
.pub h3{font-size:1.3125rem;margin:0 0 5px;line-height:1.2}
.pub .cad{font-size:0.625rem;letter-spacing:0.22em;text-transform:uppercase;
  color:var(--muted);margin-bottom:12px}
.pub p{font-size:0.9062rem;color:var(--body);margin:0 0 14px}
.pub .go{font-size:0.6562rem;letter-spacing:0.21em;text-transform:uppercase;
  font-weight:700}

/* publication page intro */
.pubintro{text-align:center;max-width:60ch;margin:0 auto}
.pubintro p{font-size:1.0625rem;color:var(--body)}

/* compact archive list */
.arch{list-style:none;margin:0;padding:0}
.arch li{border-bottom:1px solid var(--rule-soft)}
.arch a{display:flex;gap:18px;align-items:baseline;padding:14px 4px;
  transition:background .12s}
.arch a:hover{background:var(--hover)}
.arch .dot{width:8px;height:8px;border-radius:50%;flex:0 0 8px;
  transform:translateY(-1px)}
.arch .d{font-size:0.6562rem;letter-spacing:0.152em;text-transform:uppercase;
  color:var(--muted);flex:0 0 118px}
.arch .t{flex:1;font-size:1.0312rem}
.arch .p{font-size:0.625rem;letter-spacing:0.2em;text-transform:uppercase;
  font-weight:700}

/* subscribe */
.sub{margin:66px 0 0;border:1px solid var(--ink);padding:44px 42px;
  text-align:center;background:var(--panel)}
.sub h2{font-size:2rem;margin:0 0 8px;letter-spacing:-0.016em}
.sub .lede{margin:0 auto 28px;color:var(--body-soft);font-size:1rem;max-width:48ch}
.subrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(13.75rem,1fr));
  gap:26px;text-align:left;margin-top:6px}
.subcard{border-top:3px solid var(--rule-hard);padding-top:14px}
.subcard h3{font-size:1rem;margin:0 0 4px;line-height:1.25}
.subcard .cad{font-size:0.625rem;letter-spacing:0.2em;text-transform:uppercase;
  color:var(--muted);margin-bottom:12px}
.subcard form{display:flex;gap:8px;flex-wrap:wrap}
.subcard input[type=email]{color:var(--ink);flex:1 1 9.4rem;padding:11px 12px;font-size:0.9062rem;
  border:1px solid var(--rule-hard);background:var(--field);min-height:44px}
.subcard input[type=email]:focus-visible{outline:2px solid var(--ink);
  outline-offset:1px}
.subcard button{padding:11px 18px;background:var(--ink);color:var(--btn-ink);border:0;
  font-size:0.7188rem;font-weight:700;letter-spacing:0.139em;text-transform:uppercase;
  cursor:pointer;min-height:44px}
.subcard button:hover{background:var(--btn-hover)}
.subnote{margin:26px 0 0;font-size:0.8125rem;color:var(--muted)}
.subnote a{text-decoration:underline}

footer{padding:34px 0 66px;font-size:0.7188rem;color:var(--muted);display:flex;
  justify-content:space-between;gap:14px;flex-wrap:wrap;
  border-top:3px double var(--ink);margin-top:46px}
footer a{text-decoration:underline}

/* edition page chrome */
.ed-head{padding:30px 0 24px;border-bottom:1px solid var(--rule);text-align:center}
.ed-head .back{font-size:0.6562rem;letter-spacing:0.21em;text-transform:uppercase;
  color:var(--muted)}
.ed-head .pubname{font-size:0.6875rem;letter-spacing:0.273em;text-transform:uppercase;
  font-weight:700;margin:18px 0 10px}
.ed-head h1{font-size:2.625rem;margin:0 0 12px;line-height:1.12;letter-spacing:-0.024em;
  font-weight:400}
.ed-head .dek{font-size:1.0938rem;color:var(--body);max-width:58ch;margin:0 auto 14px}
.ed-head .meta{font-size:0.6562rem;letter-spacing:0.19em;text-transform:uppercase;
  color:var(--muted)}
/* Contents shortcuts above the edition. Built by the site from the edition's
   own sections, for editions that do not already carry their own. */
.ed-toc{margin:26px 0 0;border-top:3px solid var(--rule);padding:.75rem 0 .9rem}
.ed-toc[hidden]{display:none}
.ed-toc .toc-h{font-size:.625rem;letter-spacing:.22em;text-transform:uppercase;
  font-weight:700;margin-bottom:.55rem}
.ed-toc ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;
  gap:.15rem 1.1rem}
.ed-toc li{display:flex;align-items:center;gap:1.1rem}
.ed-toc li+li::before{content:"·";color:var(--rule-hard)}
.ed-toc a{font-size:.8125rem;line-height:1.7;color:var(--body-soft);
  border-bottom:1px solid transparent}
.ed-toc a:hover{color:var(--ink);border-bottom-color:var(--ink)}
.ed-body{background:#fff;border:1px solid var(--rule);margin:26px 0;overflow:hidden}
.ed-body iframe{width:100%;border:0;display:block;min-height:2400px}
.ed-nav{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
  font-size:0.6562rem;letter-spacing:0.19em;text-transform:uppercase;padding:6px 0 0}
.ed-nav a{color:var(--body-soft)}

@media(max-width:640px){
  .mast h1{font-size:2.5rem}
  .ed{grid-template-columns:1fr;gap:8px}
  .ed .side{text-align:left}
  .ed h3{font-size:1.375rem}
  .sub{padding:32px 22px}
  .sub h2{font-size:1.5625rem}
  .ed-head h1{font-size:1.8125rem}
  .arch a{flex-wrap:wrap;gap:6px}
  .arch .d{flex:0 0 100%}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


THEME_HEAD = """<script>
/* Set the theme before the first paint so the page never flashes the wrong
   one. Wrapped in try/catch: a browser with site data blocked throws on
   localStorage, and a themeless page is far better than a blank one. */
(function(){try{var t=localStorage.getItem('newsstand-theme');
if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();
</script>"""

THEME_JS = """<script>
/* The toggle. The stored choice wins over the system setting; with nothing
   stored the page follows the system, so a first-time visitor gets whichever
   they already prefer everywhere else. */
(function(){
  var root=document.documentElement, btn=document.getElementById('themetoggle');
  if(!btn)return;
  function current(){
    var set=root.getAttribute('data-theme');
    if(set)return set;
    return window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  }
  function sync(){ btn.setAttribute('aria-pressed', current()==='dark'?'true':'false'); }
  btn.addEventListener('click',function(){
    var next=current()==='dark'?'light':'dark';
    root.setAttribute('data-theme',next);
    try{localStorage.setItem('newsstand-theme',next);}catch(e){}
    sync();
  });
  sync();
  /* Follow the system while the reader has not chosen for themselves. */
  try{
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){
      var stored=null; try{stored=localStorage.getItem('newsstand-theme');}catch(e){}
      if(!stored)sync();
    });
  }catch(e){}
})();
</script>"""

def shell(title, body, desc="", canonical="", wide=False):
    meta_desc = f'<meta name="description" content="{esc(desc)}">' if desc else ""
    canon = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    wrapcls = "wrap wide" if wide else "wrap"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
{THEME_HEAD}
{meta_desc}
{canon}
<link rel="alternate" type="application/rss+xml" title="The Newsstand" href="/feed.xml">
<style>{BASE_CSS}</style>
</head>
<body>
<div class="{wrapcls}">
{body}
</div>
{THEME_JS}
</body>
</html>
"""


def masthead(dateline=None):
    cells = "".join(f"<span>{esc(c)}</span>" for c in (dateline or []))
    nav = "".join(
        f'<a href="/{s}/" style="color:var(--pub-{s})">'
        f'{esc(PUBS[s]["title"])}</a>' for s in PUB_ORDER)
    return f"""<div class="themebar">
  <button class="themetoggle" id="themetoggle" type="button" aria-pressed="false"
          aria-label="Switch between light and dark theme">
    <svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>
    <svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 13.2A9 9 0 1 1 10.8 3a7 7 0 0 0 10.2 10.2z"/></svg>
    <span class="lbl-light">Dark</span><span class="lbl-dark">Light</span>
  </button>
</div>
<header class="mast sans">
  <div class="kick">Independent &middot; Weekly &middot; San Francisco</div>
  <h1 style="font-family:Georgia,serif"><a href="/">The Newsstand</a></h1>
  <div class="rule"></div>
  <div class="dateline">{cells}</div>
</header>
<nav class="nav sans">{nav}</nav>"""


def section(title):
    return (f'<div class="sec sans"><h2>{esc(title)}</h2></div>'
            f'<div class="secline"></div>')


def footer():
    return """<footer class="sans">
  <div>The Newsstand &middot; Written and researched weekly.</div>
  <div><a href="/feed.xml">RSS</a> &middot; <a href="/archive.html">Full archive</a></div>
</footer>"""


# ---------------------------------------------------------------- subscribe
# One signup box per publication, because each publication keeps its own list.
# Replace the FORM_EMBEDS values with the real beehiiv embed for each
# publication. Until a value is filled in, that box falls back to a mailto so
# it still does something rather than looking broken.

SUBSCRIBE_EMAIL = "evangribben@gmail.com"

# slug -> beehiiv embed HTML. Empty string means "not set up yet".
FORM_EMBEDS = {
    # beehiiv subscribe forms, one per publication. Each publication keeps its
    # own subscriber list, so these must not be swapped.
    "bay-weekender":  '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="2302d445-e133-4158-b4ef-c443d72ff16d"></script>',
    "soccer-digest":  '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="cb8efe77-7469-4940-97a7-af3a61b2d755"></script>',
    "arsenal-digest": '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="7f19d80f-156f-4d19-957a-4aabdc8bf624"></script>',
}


def _fallback_form(slug):
    p = PUBS[slug]
    subject = f"Subscribe to {p['title']}".replace(" ", "%20")
    return (f'<form action="mailto:{SUBSCRIBE_EMAIL}" method="get" '
            f'enctype="text/plain">'
            f'<input type="hidden" name="subject" value="Subscribe to {esc(p["title"])}">'
            f'<label class="sans" style="position:absolute;left:-9999px" '
            f'for="e-{slug}">Your email address</label>'
            f'<input class="sans" id="e-{slug}" type="email" name="body" '
            f'placeholder="you@example.com" required>'
            f'<button class="sans" type="submit">Subscribe</button>'
            f'</form>')


def subscribe_block(only=None):
    """only: a publication slug to show just that one box, or None for all."""
    slugs = [only] if only else PUB_ORDER
    cards = []
    for s in slugs:
        p = PUBS[s]
        form = FORM_EMBEDS.get(s) or _fallback_form(s)
        cards.append(f"""<div class="subcard" style="border-top-color:var(--spine-{s})">
  <h3 style="color:var(--pub-{s})">{esc(p['title'])}</h3>
  <div class="cad sans">{esc(p['cadence'])}</div>
  <!-- SUBSCRIBE-EMBED-START {s} -->
  {form}
  <!-- SUBSCRIBE-EMBED-END {s} -->
</div>""")
    lede = ("Every edition is published here first, then sent the same day. "
            "Free, and one click to stop. Pick the ones you want.") if not only \
        else ("Published here first, then sent the same day. Free, and one "
              "click to stop.")
    return f"""<section class="sub">
  <h2>Get these in your inbox</h2>
  <p class="lede">{lede}</p>
  <div class="subrow">{''.join(cards)}</div>
</section>"""
