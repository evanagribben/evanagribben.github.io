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
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:#f3efe6;color:#1a1713;
  font-family:Georgia,'Times New Roman',serif;line-height:1.68;
  -webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:900px;margin:0 auto;padding:0 30px}
.sans{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}

/* masthead */
.mast{text-align:center;padding:58px 0 0}
.mast .kick{font-size:10px;letter-spacing:5px;text-transform:uppercase;
  color:#9a8f7c;margin-bottom:20px}
.mast h1{font-size:66px;margin:0;letter-spacing:-1.5px;line-height:1;
  color:#12100d;font-weight:400}
.mast h1 a{text-decoration:none}
.mast .rule{border-top:1px solid #1a1713;border-bottom:3px solid #1a1713;
  height:5px;margin:26px 0 0}
.mast .dateline{display:flex;justify-content:space-between;flex-wrap:wrap;
  gap:12px;font-size:10.5px;letter-spacing:2.4px;text-transform:uppercase;
  color:#7d7466;padding:11px 2px;border-bottom:1px solid #cec5b2}

/* nav */
.nav{display:flex;justify-content:center;gap:44px;flex-wrap:wrap;padding:16px 0;
  border-bottom:1px solid #cec5b2}
.nav a{font-size:11.5px;letter-spacing:2.2px;text-transform:uppercase;
  font-weight:700;padding-bottom:4px;border-bottom:2px solid transparent}
.nav a:hover,.nav a:focus-visible{border-bottom-color:currentColor}

/* section heads: a centred label sitting on a rule */
.sec{margin:58px 0 4px;text-align:center}
.sec h2{font-size:11px;letter-spacing:4.5px;text-transform:uppercase;
  color:#1a1713;margin:0;font-weight:700;display:inline-block;
  background:#f3efe6;padding:0 18px;position:relative;top:9px}
.secline{border-top:1px solid #b9ae99;margin-bottom:30px}

/* edition rows */
.ed{display:grid;grid-template-columns:150px 1fr;gap:28px;padding:26px 0;
  border-bottom:1px solid #ddd4c1;align-items:start;transition:background .13s}
.ed:hover{background:#eee9dd}
.ed:focus-visible{outline:2px solid #1a1713;outline-offset:2px}
.ed .side{text-align:right}
.ed .pubname{font-size:10px;letter-spacing:2.2px;text-transform:uppercase;
  font-weight:700;line-height:1.5}
.ed .when{font-size:10.5px;letter-spacing:1.6px;text-transform:uppercase;
  color:#8f8571;margin-top:7px}
.ed h3{font-size:26px;margin:0 0 8px;line-height:1.22;letter-spacing:-.3px}
.ed p{margin:0;font-size:16.5px;color:#4d4638;max-width:60ch}
.ed .go{margin-top:12px;font-size:10.5px;letter-spacing:2.2px;
  text-transform:uppercase;color:#8f8571}

/* publication columns */
.pubs{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:34px;margin-top:8px}
.pub{padding-top:16px}
.pub h3{font-size:21px;margin:0 0 5px;line-height:1.2}
.pub .cad{font-size:10px;letter-spacing:2.2px;text-transform:uppercase;
  color:#8f8571;margin-bottom:12px}
.pub p{font-size:14.5px;color:#4d4638;margin:0 0 14px}
.pub .go{font-size:10.5px;letter-spacing:2.2px;text-transform:uppercase;
  font-weight:700}

/* publication page intro */
.pubintro{text-align:center;max-width:60ch;margin:0 auto}
.pubintro p{font-size:17px;color:#4d4638}

/* compact archive list */
.arch{list-style:none;margin:0;padding:0}
.arch li{border-bottom:1px solid #ddd4c1}
.arch a{display:flex;gap:18px;align-items:baseline;padding:14px 4px;
  transition:background .12s}
.arch a:hover{background:#eee9dd}
.arch .dot{width:8px;height:8px;border-radius:50%;flex:0 0 8px;
  transform:translateY(-1px)}
.arch .d{font-size:10.5px;letter-spacing:1.6px;text-transform:uppercase;
  color:#8f8571;flex:0 0 118px}
.arch .t{flex:1;font-size:16.5px}
.arch .p{font-size:10px;letter-spacing:2px;text-transform:uppercase;
  font-weight:700}

/* subscribe */
.sub{margin:66px 0 0;border:1px solid #1a1713;padding:44px 42px;
  text-align:center;background:#fbf8f1}
.sub h2{font-size:32px;margin:0 0 8px;letter-spacing:-.5px}
.sub .lede{margin:0 auto 28px;color:#5b5344;font-size:16px;max-width:48ch}
.subrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:26px;text-align:left;margin-top:6px}
.subcard{border-top:3px solid #ccc;padding-top:14px}
.subcard h3{font-size:16px;margin:0 0 4px;line-height:1.25}
.subcard .cad{font-size:10px;letter-spacing:2px;text-transform:uppercase;
  color:#8f8571;margin-bottom:12px}
.subcard form{display:flex;gap:8px;flex-wrap:wrap}
.subcard input[type=email]{flex:1 1 150px;padding:11px 12px;font-size:14.5px;
  border:1px solid #b9ae99;background:#fff;min-height:44px}
.subcard input[type=email]:focus-visible{outline:2px solid #1a1713;
  outline-offset:1px}
.subcard button{padding:11px 18px;background:#1a1713;color:#f3efe6;border:0;
  font-size:11.5px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;
  cursor:pointer;min-height:44px}
.subcard button:hover{background:#3a332a}
.subnote{margin:26px 0 0;font-size:13px;color:#8f8571}
.subnote a{text-decoration:underline}

footer{padding:34px 0 66px;font-size:11.5px;color:#8f8571;display:flex;
  justify-content:space-between;gap:14px;flex-wrap:wrap;
  border-top:3px double #1a1713;margin-top:46px}
footer a{text-decoration:underline}

/* edition page chrome */
.ed-head{padding:30px 0 24px;border-bottom:1px solid #cec5b2;text-align:center}
.ed-head .back{font-size:10.5px;letter-spacing:2.2px;text-transform:uppercase;
  color:#8f8571}
.ed-head .pubname{font-size:11px;letter-spacing:3px;text-transform:uppercase;
  font-weight:700;margin:18px 0 10px}
.ed-head h1{font-size:42px;margin:0 0 12px;line-height:1.12;letter-spacing:-1px;
  font-weight:400}
.ed-head .dek{font-size:17.5px;color:#4d4638;max-width:58ch;margin:0 auto 14px}
.ed-head .meta{font-size:10.5px;letter-spacing:2px;text-transform:uppercase;
  color:#8f8571}
.ed-body{background:#fff;border:1px solid #cec5b2;margin:26px 0;overflow:hidden}
.ed-body iframe{width:100%;border:0;display:block;min-height:2400px}
.ed-nav{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
  font-size:10.5px;letter-spacing:2px;text-transform:uppercase;padding:6px 0 0}
.ed-nav a{color:#5b5344}

@media(max-width:640px){
  .mast h1{font-size:40px}
  .ed{grid-template-columns:1fr;gap:8px}
  .ed .side{text-align:left}
  .ed h3{font-size:22px}
  .sub{padding:32px 22px}
  .sub h2{font-size:25px}
  .ed-head h1{font-size:29px}
  .arch a{flex-wrap:wrap;gap:6px}
  .arch .d{flex:0 0 100%}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shell(title, body, desc="", canonical=""):
    meta_desc = f'<meta name="description" content="{esc(desc)}">' if desc else ""
    canon = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
{meta_desc}
{canon}
<link rel="alternate" type="application/rss+xml" title="The Newsstand" href="/feed.xml">
<style>{BASE_CSS}</style>
</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def masthead(dateline=None):
    cells = "".join(f"<span>{esc(c)}</span>" for c in (dateline or []))
    nav = "".join(
        f'<a href="/{s}/" style="color:{PUBS[s]["text"]}">'
        f'{esc(PUBS[s]["title"])}</a>' for s in PUB_ORDER)
    return f"""<header class="mast sans">
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
        cards.append(f"""<div class="subcard" style="border-top-color:{p['spine']}">
  <h3 style="color:{p['text']}">{esc(p['title'])}</h3>
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
