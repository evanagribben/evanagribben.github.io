# The Newsstand

The archive site for three weekly publications: **The Bay Weekender**,
**The Weekly Soccer Digest**, and **The Weekly Arsenal Digest**.

Live at **https://evanagribben.github.io**

Every edition is written by a scheduled task, published here first, then
emailed. This repo is the source of truth. The email platform is a
swappable part.

---

## How it works

```
manifest.json          the index of every edition (slug, publication, date, title, dek)
editions/raw/*.html    each edition's ORIGINAL html, byte for byte, never edited
theme.py               the design system: colors, CSS, page shell
build.py               regenerates every page from the manifest
publish.py             adds one new edition and pushes  ← this is what the tasks call
```

`build.py` regenerates the whole site from `manifest.json` every time, so
there is no partial state to get wrong. Editions are displayed inside the
site chrome via a same-origin iframe, which is what preserves each
newsletter's email-safe styling exactly as it appears in Gmail.

Everything is plain HTML. There is no build step to install, no framework,
no dependencies beyond Python 3.

### Rebuild the site

```bash
python3 build.py
```

### Preview locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Use a local server rather than opening `index.html` directly. The pages use
absolute paths (`/editions/...`), which only resolve when served.

### Publish an edition

```bash
python3 publish.py \
  --pub soccer-digest \
  --date 2026-08-19 \
  --dek "One sentence teaser shown on the homepage." \
  --html /tmp/edition.html
```

Valid `--pub` values: `bay-weekender`, `soccer-digest`, `arsenal-digest`.

The slug is derived as `<pub>-<date>`, so **re-publishing the same
publication and date replaces that edition instead of duplicating it.** A
task that retries is safe to run twice.

`publish.py` refuses to publish anything under 4 KB or anything that doesn't
look like HTML. That guard exists because a previous version of the Bay
Weekender pipeline silently shipped a 440-byte stub.

---

## Adding a new publication

Add an entry to `PUBS` in `theme.py` with its title, tagline, blurb, spine
color and cadence, then run `build.py`. Nav, homepage cards, archive grouping, and
RSS all pick it up automatically.

---

## The subscribe form

`theme.py` has a `SUBSCRIBE_PLACEHOLDER` constant marked with
`SUBSCRIBE-EMBED-START` / `SUBSCRIBE-EMBED-END`. Replace its contents with
the beehiiv embed snippet and re-run `build.py`. The form then appears on
the homepage, all three publication pages, and every edition page.

---

## Custom domain

1. Add a file named `CNAME` at the repo root containing just the domain,
   e.g. `thenewsstand.co`
2. At the registrar, point the apex at GitHub Pages:
   `A` records to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
   `185.199.111.153`, plus a `CNAME` for `www` to `evanagribben.github.io`
3. Repo → Settings → Pages → Custom domain → enter it → **Enforce HTTPS**
4. Update `SITE_URL` in `build.py` and `url` in `manifest.json`, then rebuild

Certificate issuance takes a few minutes after DNS resolves.
