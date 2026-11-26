"""
Generate static product pages from the data files. GitHub Pages serves the
generated HTML directly — no server, database or build step on GitHub.

    python tools/build_site.py

Reads   data/products/wheels/*.json
Writes  wheels-castors/index.html                         (Wheels & Castors hub)
        wheels-castors/<category>/index.html              (category page)
        wheels-castors/<category>/<product-slug>/index.html  (one page per product)
        sitemap.xml                                       (homepage + all product pages)

Product pages are fully regenerated each run, so never edit them by hand —
edit the data file (or the Word documents + re-import) and rebuild.
"""
import datetime
import hashlib
import glob
import html
import json
import os
import re
import shutil
import sys
import urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kotibhaskarindustries.com'
CATALOGUE = '/Kotibhaskar%201%20Castor%20Catalogue.pdf'
WHATSAPP = '919822413252'
TODAY = datetime.date.today().isoformat()
OUT_ROOT = os.path.join(REPO, 'wheels-castors')
def asset_version(rel):
    """Short content hash for cache-busting: a changed file gets a new URL, so browsers
    never pair new pages with an old cached stylesheet or script."""
    with open(os.path.join(REPO, rel), 'rb') as f:
        data = f.read().replace(bytes([13, 10]), bytes([10]))   # same hash regardless of CRLF/LF line endings
    return hashlib.sha256(data).hexdigest()[:10]


CSS_URL = '/assets/css/site.css?v=' + asset_version('assets/css/site.css')
JS_URL = '/assets/js/site.js?v=' + asset_version('assets/js/site.js')
NAV_CATS = []   # all built categories, used for footer links (filled in main)

e = lambda s: html.escape(str(s), quote=True)


# ---- Product demonstration videos (data/videos.json): one entry per YouTube video, listing its product pages
def load_videos():
    with open(os.path.join(REPO, 'data', 'videos.json'), encoding='utf-8') as f:
        data = json.load(f)
    by_page = {}
    for v in data['videos']:
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', v['id']):
            raise SystemExit(f"videos.json: '{v['id']}' is not a YouTube video id (11 characters after youtu.be/)")
        for pg in v['pages']:
            by_page.setdefault(pg, []).append(v)
    return by_page


VIDEOS = load_videos()
VIDEO_PAGES_USED = set()


def video_html(url):
    """Compact 'Watch Product Demonstration' strip for a product page; '' when the page has no video.
    The link opens YouTube without JavaScript; site.js turns it into an in-page popup player."""
    vs = VIDEOS.get(url)
    if not vs:
        return ''
    VIDEO_PAGES_USED.add(url)

    def link(v, cls, inner):
        return (f'<a class="{cls}" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener" '
                f'data-yt="{v["id"]}" data-yt-title="{e(v["title"])}">{inner}</a>')
    v = vs[0]
    main = link(v, 'vid-main',
                f'<span class="vid-thumb"><img src="https://i.ytimg.com/vi/{v["id"]}/mqdefault.jpg" alt="" width="320" height="180" '
                f'loading="lazy" decoding="async"><span class="vid-play" aria-hidden="true"></span>'
                f'<span class="vid-dur">{e(v.get("duration", ""))}</span></span>'
                f'<span class="vid-text"><b>{e(v["title"])}</b><small>&#9654; Play video</small></span>')
    more = ''
    if len(vs) > 1:
        more = (f'<details class="vid-more"><summary>More videos ({len(vs) - 1})</summary><ul>' + ''.join(
            f'<li>{link(o, "vid-link", "&#9654; " + e(o["title"]) + (" <span>" + e(o["duration"]) + "</span>" if o.get("duration") else ""))}</li>'
            for o in vs[1:]) + '</ul></details>')
    return (f'<section class="vid-box" aria-label="Product demonstration video">'
            f'<h2 class="vid-label">Watch Product Demonstration</h2>{main}{more}</section>')


def check_videos_used():
    missing = sorted(set(VIDEOS) - VIDEO_PAGES_USED)
    if missing:
        raise SystemExit('videos.json lists pages that were not built (check the URL): ' + ', '.join(missing))


def n(v):
    """Format a number without a trailing .0"""
    return str(int(v)) if float(v).is_integer() else str(v)


def x(s):
    return s.replace(' x ', ' &times; ')


def enquire_url(name, size=None, category=None, page_url=None):
    """Link to the homepage enquiry form, pre-filled with the product details.
    The form reads: enquire (product name), size, cat (category), page (product URL)."""
    q = {'enquire': name}
    if size:
        q['size'] = size
    if category:
        q['cat'] = category
    if page_url:
        q['page'] = SITE + page_url
    return '/?' + urllib.parse.urlencode(q) + '#contact'


def wa_url(text):
    return f'https://wa.me/{WHATSAPP}?text=' + urllib.parse.quote(text)


# ----------------------------------------------------------------------------
# Company details for the printed datasheet letterhead. Every value here is
# taken from the existing website (index.html contact section / JSON-LD).
# Edit in ONE place; all product datasheets pick it up on the next build.
COMPANY = {
    'name': 'Kotibhaskar Material Handling Equipments',
    'tagline': 'Manufacturer of Material Handling Equipments, Industrial Trolleys, and Industrial Wheels & Castors',
    'address': 'Plot No. K-3/2/1, Additional MIDC, Satara - 415004, Maharashtra, India',
    'address_line1': 'Plot No. K-3/2/1, Additional MIDC,',
    'address_line2': 'Satara - 415004, Maharashtra, India',
    'phones': ['+91 98224 13252', '+91 83800 95804', '+91 83800 95805'],
    'emails': ['amodsales@gmail.com', 'amodsatara@gmail.com'],
    'website': 'kotibhaskarindustries.com',
    'logo': '/assets/brand/kotibhaskar-logo.png',   # official black KOTIBHASKAR wordmark (392x120)
}

# Spec rows that are highlighted on the web page and the printed datasheet.
# ('Load Capacity' is the label used by the pallet truck wheel & roller documents.)
KEY_ROWS = ('Size', 'Load Capacity per Caster', 'Load Capacity')


def size_label(p):
    """Standard size format used everywhere: 100 × 32 mm (4 Inch Wheel)"""
    return f"{n(p['diameter_mm'])} × {n(p['width_mm'])} mm ({n(p['inch'])} Inch Wheel)"


def display_spec(label, value):
    """Format a Word spec value for display without changing any number.
    'Size' rows such as '100 x 32 (4 Inch Wheel)' become '100 × 32 mm (4 Inch Wheel)'."""
    if label == 'Size':
        m = re.match(r'^([\d.]+) x ([\d.]+)(?: mm)? \((.+)\)$', value)
        if m:
            return f'{m.group(1)} × {m.group(2)} mm ({m.group(3)})'
        # pallet truck rollers: '80 x 100 x 20 mm' (diameter x width x bore) -> '80 × 100 × 20 mm'
        if re.match(r'^[\d.]+( x [\d.]+)+ mm$', value):
            return value.replace(' x ', ' × ')
    return value


def spec_rows_html(specs):
    return ''.join(
        f'<tr{" class=\"key\"" if label in KEY_ROWS else ""}><th scope="row">{e(label)}</th><td>{e(display_spec(label, value))}</td></tr>'
        for label, value in specs)


def print_sheet(*, category, group_name, title, size, load, photo, drawing, specs, url, load_label='Load Capacity per Caster'):
    """Branded A4 product datasheet. Hidden on screen; it is the only thing
    printed when the visitor uses Print / Save as PDF (see site.css)."""
    c = COMPANY
    return f'''<div class="print-sheet" aria-hidden="true">
  <div class="ps-head">
    <img class="ps-logo" src="{c['logo']}" alt="KOTIBHASKAR">
    <div class="ps-company">
      <div class="ps-name">{e(c['name'])}</div>
      <div class="ps-tag">{e(c['tagline'])}</div>
      <div class="ps-contact">{e(c['address'])}<br>
        Tel: {' &middot; '.join(e(t) for t in c['phones'])}<br>
        Email: {' &middot; '.join(e(m) for m in c['emails'])} &nbsp;|&nbsp; Web: {e(c['website'])}</div>
    </div>
  </div>
  <div class="ps-band"><span>Product Specification Sheet</span><span>Wheels &amp; Castors &middot; {e(category)}</span></div>
  <div class="ps-title">
    <div>
      <div class="ps-cat">{e(category)} &middot; {e(group_name)}</div>
      <div class="ps-h">{e(title)}</div>
      <div class="ps-size">{e(size)}</div>
    </div>
    <div class="ps-load"><span>{e(load_label)}</span><b>{e(load)}</b></div>
  </div>
  <div class="ps-imgs">
    <figure><div class="ps-img"><img src="{photo}" alt=""></div><figcaption>Product Photograph</figcaption></figure>
    <figure><div class="ps-img"><img src="{drawing}" alt=""></div><figcaption>Technical Drawing</figcaption></figure>
  </div>
  <div class="ps-sec">Technical Specifications</div>
  <table class="ps-specs"><tbody>{spec_rows_html(specs)}</tbody></table>
  <div class="ps-note">Specifications subject to change without notice. Contact us for a quotation.</div>
  <div class="ps-foot">
    <div><b>{e(c['name'])}</b><br>{e(c['website'])}</div>
    <div>{e(c['phones'][0])} &nbsp;|&nbsp; {e(c['emails'][0])}</div>
    <div class="ps-url">{'/<wbr>'.join(f'<span>{e(seg)}</span>' for seg in (c['website'] + url).split('/'))}</div>
  </div>
</div>'''


DL_ICON = ('<svg width="14" height="16" viewBox="0 0 14 16" fill="none" aria-hidden="true"><path d="M7 1v9M7 10l-3-3M7 10l3-3M1 13h12" '
           'stroke="#E07B2A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M1 13v2h12v-2" stroke="#E07B2A" '
           'stroke-width="1.8" stroke-linecap="round"/></svg>')
WA_ICON = ('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>')


EQ_CSS_URL = '/assets/css/equipment.css?v=' + asset_version('assets/css/equipment.css')


# Datasheet header strip: the navy fill is drawn as an inline SVG (foreground content), not only as a
# CSS background, so it still prints when the browser's "Background graphics" option is off and the
# white header text always stays readable.
BAND_BG = ('<svg class="ps-band-bg" aria-hidden="true" focusable="false" viewBox="0 0 10 10" preserveAspectRatio="none">'
           '<rect width="10" height="10" fill="#1A2332"/></svg>')


def page(*, title, description, canonical, body, og_image=None, jsonld=None, wa_text=None, sheet='', extra_css=None):
    og_image = og_image or f'{SITE}/assets/brand/og-image.png'
    if sheet:
        sheet = sheet.replace('<div class="ps-band">', '<div class="ps-band">' + BAND_BG)
    wa_text = wa_text or 'Hello, I visited kotibhaskarindustries.com and would like to enquire about your products.'
    ld = ''
    if jsonld:
        ld = '<script type="application/ld+json">\n' + json.dumps(jsonld, ensure_ascii=False, indent=1).replace('</', '<\\/') + '\n</script>\n'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{e(SITE + canonical)}">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Kotibhaskar Industries">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(SITE + canonical)}">
<meta property="og:image" content="{e(og_image)}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{e(og_image)}">
{ld}<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{CSS_URL}">
{f'<link rel="stylesheet" href="{extra_css}">{chr(10)}' if extra_css else ''}</head>
<body{' class="has-sheet"' if sheet else ''}>
<!-- Generated by tools/build_site.py from data/products — do not edit by hand -->
<nav id="main-nav">
  <a href="/" class="brand" aria-label="Kotibhaskar Industries home">
    <img src="{COMPANY['logo']}" alt="KOTIBHASKAR" width="392" height="120">
  </a>
  <ul class="nav-links">
    <li><a href="/#hero">Home</a></li>
    <li><a href="/#products" class="current">Products</a></li>
    <li><a href="/#customers">Customers</a></li>
    <li><a href="/#network">Pan-India Reach</a></li>
    <li><a href="/#location">Our Location</a></li>
    <li><a href="/#about">About</a></li>
    <li><a href="/#contact" class="nav-cta">Contact Us</a></li>
  </ul>
  <button class="hamburger" type="button" aria-label="Open menu" aria-controls="mobileMenu" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <a href="/#hero">Home</a>
  <a href="/#products">Products</a>
  <a href="/wheels-castors/">Wheels &amp; Castors</a>
  <a href="/#customers">Customers</a>
  <a href="/#network">Pan-India Reach</a>
  <a href="/#location">Our Location</a>
  <a href="/#about">About Us</a>
  <a href="/#contact">Contact &amp; Quote</a>
  <a href="/Kotibhaskar%201%20Catalogue.pdf" target="_blank" rel="noopener" class="accent">&#8595; MHE Catalogue</a>
  <a href="{CATALOGUE}" target="_blank" rel="noopener" class="accent">&#8595; Wheels &amp; Castors Catalogue</a>
</div>
<main>
{body}
</main>
<footer>
  <div class="footer-top">
    <div class="footer-brand">
      <a href="/" class="brand footer-logo"><img src="{COMPANY['logo']}" alt="KOTIBHASKAR" width="392" height="120"></a>
      <p>{e(COMPANY['tagline'])}. Serving Indian industry since 2000.</p>
    </div>
    <div class="footer-col">
      <h4>Products</h4>
      <a href="/material-handling-equipment/">MHE Equipment</a>
      <a href="/material-handling-trolleys/">Trolleys</a>
      <a href="/wheels-castors/">Wheels &amp; Castors</a>
      {''.join(f'<a href="{c["url"]}">{e(c["name"])}</a>' for c in NAV_CATS)}
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <a href="/#about">About Us</a>
      <a href="/#customers">Customers</a>
      <a href="/#network">Pan-India Reach</a>
      <a href="/#location">Our Location</a>
      <a href="https://www.linkedin.com/company/kotibhaskar-industries/" target="_blank" rel="noopener">LinkedIn</a>
    </div>
    <div class="footer-col">
      <h4>Contact</h4>
      <a href="tel:+919822413252">+91 98224 13252</a>
      <a href="mailto:amodsales@gmail.com">amodsales@gmail.com</a>
      <a>{e(COMPANY['address_line1'])}<br>{e(COMPANY['address_line2'])}</a>
    </div>
    <div class="footer-col">
      <h4>Resources</h4>
      <a href="/Kotibhaskar%201%20Catalogue.pdf" target="_blank" rel="noopener">&#8595; MHE Catalogue</a>
      <a href="{CATALOGUE}" target="_blank" rel="noopener">&#8595; Wheels &amp; Castors Catalogue</a>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="footer-copy">&copy; 2025 Kotibhaskar Industries. All rights reserved.</div>
    <div class="footer-copy">kotibhaskarindustries.com</div>
  </div>
</footer>
<a id="wa-btn" href="{e(wa_url(wa_text))}" target="_blank" rel="noopener" aria-label="WhatsApp Enquiry">{WA_ICON}<span class="wa-label">WhatsApp Enquiry</span></a>
{sheet}
<script src="{JS_URL}" defer></script>
</body>
</html>
'''


def crumbs(items):
    """items: list of (label, href or None). Returns HTML + JSON-LD BreadcrumbList."""
    parts, ld = [], []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span class="sep">/</span>')
        if href:
            parts.append(f'<a href="{e(href)}">{label}</a>')
        else:
            parts.append(f'<span aria-current="page">{label}</span>')
        ld.append({'@type': 'ListItem', 'position': i + 1, 'name': html.unescape(label),
                   **({'item': SITE + href} if href else {})})
    return ('<nav class="crumbs" aria-label="Breadcrumb">' + ''.join(parts) + '</nav>',
            {'@type': 'BreadcrumbList', 'itemListElement': ld})


def short_name(p, group):
    return f"{group['short']} {n(p['diameter_mm'])} × {n(p['width_mm'])} mm"


# ----------------------------------------------------------------------------
def build_category(cat):
    groups = cat['groups']
    gmap = {g['id']: g for g in groups}
    prods = cat['products']
    url = cat['url']
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), None)])
    loads = [p['load_per_caster_kg'] for p in prods]

    filter_btns = [f'<button type="button" class="filter-btn active" data-filter="all" aria-pressed="true">All <span>{len(prods)}</span></button>']
    blocks, rows = [], []
    gi = 0
    for g in groups:
        gp = [p for p in prods if p['group'] == g['id']]
        if not gp:
            continue
        gi += 1
        filter_btns.append(f'<button type="button" class="filter-btn" data-filter="{g["id"]}" aria-pressed="false">{e(g["name"])} <span>{len(gp)}</span></button>')
        cards = []
        for j, p in enumerate(gp):
            cards.append(f'''<a class="p-card" href="{url}{p['slug']}/">
  <div class="p-card-img"><img src="{p['images']['thumb']}" alt="{e(p['name'])}" loading="lazy" width="420" height="594"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{e(cat['name'])} &middot; {e(g['name'])}</div>
    <div class="p-card-inch">{n(p['inch'])} Inch Wheel</div>
    <div class="p-card-name">{e(short_name(p, g))}</div>
    <div class="p-card-load">Load per caster: <b>{n(p['load_per_caster_kg'])} kg</b></div>
    <div class="p-card-cta">View details &rarr;</div>
  </div>
</a>''')
            rows.append(f'<tr class="grp-{(gi - 1) % 3 + 1}{" grp-start" if j == 0 else ""}"><td>{e(g["short"])}</td><td><a href="{url}{p["slug"]}/">{n(p["diameter_mm"])} &times; {n(p["width_mm"])} mm '
                        f'<span class="inch-cell">({n(p["inch"])} Inch Wheel)</span></a></td><td>{n(p["load_per_caster_kg"])} kg</td></tr>')
        gl = [p['load_per_caster_kg'] for p in gp]
        blocks.append(f'''<section class="group-block" id="{g['id']}" aria-labelledby="h-{g['id']}">
  <div class="group-head"><h2 id="h-{g['id']}">{e(cat['name'])} &mdash; <b>{e(g['name'])}</b></h2><p>{len(gp)} sizes &middot; {n(min(gl))}&ndash;{n(max(gl))} kg per caster</p></div>
  <div class="card-grid">
{chr(10).join(cards)}
  </div>
</section>''')

    feats = ''.join(f'<li>{e(f)}</li>' for f in cat.get('features', []))
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">Wheels &amp; Castors</div>
  <h1 class="page-title">{e(cat['name'].split()[0])} <span class="hl">{e(' '.join(cat['name'].split()[1:]))}</span></h1>
  <p class="page-sub">{e(cat['intro'])}</p>
  <div class="head-actions">
    <a class="btn-primary" href="{e(enquire_url(cat['name'] + ' (all sizes)', None, 'Wheels & Castors > ' + cat['name'], url))}">Enquire Now</a>
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue</a>
  </div>
  <div class="key-facts">
    <div class="fact"><div class="fact-num">{len(prods)}</div><div class="fact-label">Sizes</div></div>
    <div class="fact"><div class="fact-num">{len([g for g in groups if any(p['group'] == g['id'] for p in prods)])}</div><div class="fact-label">Duty ranges</div></div>
    <div class="fact"><div class="fact-num">{n(min(p['diameter_mm'] for p in prods))}&ndash;{n(max(p['diameter_mm'] for p in prods))}<small>mm</small></div><div class="fact-label">Wheel diameter</div></div>
    <div class="fact"><div class="fact-num">{n(min(loads))}&ndash;{n(max(loads))}<small>kg</small></div><div class="fact-label">Load per caster</div></div>
  </div>
</header>

<div class="wrap">
  <div class="filter-bar" role="group" aria-label="Filter by duty">
    {''.join(filter_btns)}
  </div>
{chr(10).join(blocks)}
</div>

<div class="wrap alt">
  <h2 class="h2">Why {e(cat['name'].split()[0])}?</h2>
  <ul class="feat-list">{feats}</ul>
</div>

<div class="wrap sum-table">
  <h2 class="h2">Size &amp; Load Table <small>{len(prods)} sizes</small></h2>
  <div class="tbl-wrap">
    <table class="data-table">
      <thead><tr><th scope="col">Duty</th><th scope="col">Size</th><th scope="col">Load Capacity per Caster</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</div>

<section class="cta-band">
  <div><h2>Need help choosing the right wheel?</h2><p>Tell us your load, floor and application &mdash; our team will recommend the right size.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(enquire_url(cat['name'], None, 'Wheels & Castors > ' + cat['name'], url))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''

    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'CollectionPage', 'name': cat['full_name'], 'url': SITE + url, 'description': cat['intro'],
         'isPartOf': {'@id': f'{SITE}/#website'},
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}{url}{p['slug']}/", 'name': p['name']} for i, p in enumerate(prods)]}},
    ]}
    title = f"{cat['full_name']} – {len(prods)} Sizes, {n(min(loads))}–{n(max(loads))} kg | Kotibhaskar Industries"
    desc = (f"{cat['full_name']} manufactured by Kotibhaskar Industries, Satara. {len(prods)} sizes in "
            + ', '.join(g['name'] for g in groups) + f" ranges, {n(min(loads))} to {n(max(loads))} kg load capacity per caster. "
            "Wheel only, fixed, swivel and swivel with brake.")
    return page(title=title, description=desc, canonical=url, body=body, jsonld=jsonld,
                og_image=SITE + prods[0]['images']['photo'] if prods else None,
                wa_text=f"Hello, I'm interested in your {cat['name']} (kotibhaskarindustries.com{url}).")


# ----------------------------------------------------------------------------
def build_product(cat, p, idx):
    groups = {g['id']: g for g in cat['groups']}
    g = groups[p['group']]
    url = f"{cat['url']}{p['slug']}/"
    same = [q for q in cat['products'] if q['group'] == p['group']]
    prods = cat['products']
    prev_p = prods[idx - 1] if idx > 0 else None
    next_p = prods[idx + 1] if idx + 1 < len(prods) else None
    dims = f"{n(p['diameter_mm'])} × {n(p['width_mm'])} mm"
    size = size_label(p)
    base_name = f"{cat['name'].rstrip('s')} {g['short']}"
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), cat['url']),
                                   (e(g['name']), f"{cat['url']}#{g['id']}"), (e(size), None)])

    spec_rows = spec_rows_html(p['specs'])
    sibs = ''.join(
        f'<a class="sib{" current" if q["slug"] == p["slug"] else ""}" href="{cat["url"]}{q["slug"]}/"'
        f'{" aria-current=\"page\"" if q["slug"] == p["slug"] else ""}>{n(q["diameter_mm"])} &times; {n(q["width_mm"])} mm'
        f'<small>{n(q["inch"])} Inch Wheel &middot; {n(q["load_per_caster_kg"])} kg</small></a>' for q in same)
    pn = ''
    if prev_p:
        pn += f'<a class="btn-outline" href="{cat["url"]}{prev_p["slug"]}/">&larr; {e(short_name(prev_p, groups[prev_p["group"]]))}</a>'
    else:
        pn += '<span></span>'
    if next_p:
        pn += f'<a class="btn-outline" href="{cat["url"]}{next_p["slug"]}/">{e(short_name(next_p, groups[next_p["group"]]))} &rarr;</a>'

    enquiry_name = p['name']
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="duty-badge">{e(cat['name'])} &middot; <b>{e(g['name'])}</b></div>
  <h1 class="page-title">{e(base_name)} <span class="size-line">{n(p['diameter_mm'])} &times; {n(p['width_mm'])} mm <span class="size-inch">({n(p['inch'])} Inch Wheel)</span></span></h1>
  <p class="page-sub">{e(cat['material'])} wheel &mdash; available as wheel only, fixed caster, swivel caster and swivel caster with brake.</p>
  <div class="key-facts">
    <div class="fact fact-inch"><div class="fact-num">{n(p['inch'])}<small>inch</small></div><div class="fact-label">Wheel size</div></div>
    <div class="fact"><div class="fact-num">{n(p['diameter_mm'])}<small>mm</small></div><div class="fact-label">Wheel diameter</div></div>
    <div class="fact"><div class="fact-num">{n(p['width_mm'])}<small>mm</small></div><div class="fact-label">Wheel width</div></div>
    <div class="fact"><div class="fact-num">{n(p['load_per_caster_kg'])}<small>kg</small></div><div class="fact-label">Load capacity per caster</div></div>
  </div>
</header>

<div class="wrap">
  <div class="prod-layout">
    <div>
      <div class="gallery">
        <figure>
          <a href="{p['images']['photo']}" data-lightbox><img src="{p['images']['photo']}" alt="{e(p['name'])} — product photograph" width="900" height="1273"></a>
          <figcaption>Product photo <span>Click to enlarge</span></figcaption>
        </figure>
        <figure>
          <a href="{p['images']['drawing']}" data-lightbox><img src="{p['images']['drawing']}" alt="{e(p['name'])} — technical dimensional drawing" width="1100" height="1556"></a>
          <figcaption>Technical drawing <span>Click to enlarge</span></figcaption>
        </figure>
      </div>
    </div>
    <div>
      <h2 class="sec-label">Technical Specifications</h2>
      <div class="tbl-wrap">
        <table class="data-table spec-table"><tbody>{spec_rows}</tbody></table>
      </div>
      <div class="action-box">
        <a class="btn-primary" href="{e(enquire_url(enquiry_name, size, f"Wheels & Castors > {cat['name']} > {g['name']}", url))}">&#9993; Enquire Now</a>
        <a class="btn-wa" href="{e(wa_url(f'Hello, I would like a quotation for: {enquiry_name} ({SITE}{url})'))}" target="_blank" rel="noopener">{WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
        <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue (PDF)</a>
        <button type="button" class="btn-outline" data-print>&#128438; Print / Save as PDF</button>
        <p class="action-note">No prices are listed online &mdash; send an enquiry for a quotation.</p>
      </div>
    </div>
  </div>
</div>

<div class="wrap alt siblings-wrap">
  <h2 class="h2">Other {e(cat['name'])} &mdash; {e(g['name'])} sizes</h2>
  <div class="siblings">{sibs}</div>
  <div class="prev-next">{pn}</div>
  <p style="margin-top:22px;"><a class="btn-outline" href="{cat['url']}">View all {len(prods)} {e(cat['name'])}</a></p>
</div>'''

    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'Product', 'name': p['name'], 'url': SITE + url, 'sku': f"KI-{cat['id'].upper()}-{p['slug'].upper()}",
         'image': [SITE + p['images']['photo'], SITE + p['images']['drawing']],
         'description': f"{p['name']}: {cat['material']} wheel, {size}, load capacity {n(p['load_per_caster_kg'])} kg per caster.",
         'brand': {'@type': 'Brand', 'name': 'Kotibhaskar'},
         'manufacturer': {'@id': f'{SITE}/#organization'},
         'category': f"Wheels & Castors > {cat['name']} > {g['name']}",
         'material': cat['material'],
         'additionalProperty': [{'@type': 'PropertyValue', 'name': k, 'value': display_spec(k, v)} for k, v in p['specs']]},
    ]}
    title = f"{base_name} {size} – {n(p['load_per_caster_kg'])} kg per Caster | Kotibhaskar"
    desc = (f"{p['name']} — {cat['material']} wheel, diameter {n(p['diameter_mm'])} mm, width {n(p['width_mm'])} mm, "
            f"load capacity {n(p['load_per_caster_kg'])} kg per caster. Available as wheel only, fixed, swivel and swivel with brake. "
            "Made in India by Kotibhaskar Industries, Satara.")
    sheet = print_sheet(category=cat['name'], group_name=g['name'], title=base_name, size=size,
                        load=f"{n(p['load_per_caster_kg'])} kg", photo=p['images']['photo'],
                        drawing=p['images']['drawing'], specs=p['specs'], url=url)
    return page(title=title, description=desc, canonical=url, body=body, jsonld=jsonld,
                og_image=SITE + p['images']['photo'],
                wa_text=f'Hello, I would like a quotation for: {enquiry_name} ({SITE}{url})', sheet=sheet)


# ----------------------------------------------------------------------------
def build_hub(cats, pt=None, ms=None):
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', None)])
    cards = []
    for c in cats:
        p0 = c['products'][0]
        loads = [p['load_per_caster_kg'] for p in c['products']]
        cards.append(f'''<a class="p-card" href="{c['url']}">
  <div class="p-card-img"><img src="{p0['images']['thumb']}" alt="{e(c['full_name'])}" loading="lazy" width="420" height="594"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{len(c['products'])} sizes</div>
    <div class="p-card-name">{e(c['name'])}</div>
    <div class="p-card-meta">{' &middot; '.join(e(g['name']) for g in c['groups'])}</div>
    <div class="p-card-load">Load per caster: <b>{n(min(loads))}&ndash;{n(max(loads))} kg</b></div>
    <div class="p-card-cta">View range &rarr;</div>
  </div>
</a>''')
    if pt and pt.get('products'):
        loads = [p['load_kg'] for p in pt['products']]
        cards.append(f'''<a class="p-card" href="{pt['url']}">
  <div class="p-card-img"><img src="/assets/products/pallet-truck/category-thumb.jpg" alt="{e(pt['name'])}" loading="lazy" width="600" height="450"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{len(pt['products'])} products</div>
    <div class="p-card-name">{e(pt['name'])}</div>
    <div class="p-card-meta">{' &middot; '.join(e(s['name']) for s in pt['subcats'])}</div>
    <div class="p-card-load">Load capacity: <b>{n(min(loads))}&ndash;{n(max(loads))} kg</b></div>
    <div class="p-card-cta">View range &rarr;</div>
  </div>
</a>''')
    if ms:
        loads = [r['load_kg'] for r in ms['rows']]
        cards.append(f'''<a class="p-card hub-cover" href="{ms['url']}">
  <div class="p-card-img"><img src="/assets/products/ms-track/cover-thumb.jpg" alt="{e(ms['name'])}" loading="lazy" width="480" height="679"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{len(ms['profiles'])} profiles</div>
    <div class="p-card-name">{e(ms['name'])}</div>
    <div class="p-card-meta">{' &middot; '.join(e(p['name']) for p in ms['profiles'])}</div>
    <div class="p-card-load">Load per wheel: <b>{n(min(loads))}&ndash;{n(max(loads))} kg</b></div>
    <div class="p-card-cta">View range &rarr;</div>
  </div>
</a>''')
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">What We Make</div>
  <h1 class="page-title">Wheels <span class="hl">&amp; Castors</span></h1>
  <p class="page-sub">Industrial wheels and castors manufactured at our Satara MIDC plant. Browse each range for sizes, technical drawings and specifications.</p>
  <div class="head-actions">
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue</a>
    <a class="btn-outline" href="/#products">All product categories</a>
  </div>
</header>
<div class="wrap">
  <div class="card-grid hub-grid">
{chr(10).join(cards)}
  </div>
  <div class="custom-note hub-note"><strong>More ranges coming online</strong>Further wheel and castor ranges will be added here soon. Meanwhile, see our <a href="{CATALOGUE}" target="_blank" rel="noopener" style="color:#C85A00;">Wheels &amp; Castors catalogue</a> or <a href="/#contact" style="color:#C85A00;">send us an enquiry</a>.</div>
</div>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld]}
    return page(title='Industrial Wheels & Castors Manufacturer | Kotibhaskar Industries, Satara',
                description='Industrial wheels and castors by Kotibhaskar Industries, Satara: ' + ', '.join(c['name'] for c in cats)
                + ' in medium duty, heavy duty and heavy duty twin ranges'
                + (f", plus {pt['name'].lower()}" if pt and pt.get('products') else '')
                + ', with technical drawings and specifications.',
                canonical='/wheels-castors/', body=body, jsonld=jsonld)


# ============================================================================
# PALLET TRUCK WHEELS & ROLLERS (data/products/pallet-truck/pallet-truck.json)
# 4th wheels & castors category with three material sub-categories.
# Sizes are diameter x width x bore; no caster / inch conventions are applied.
# ============================================================================
PT_ROOT = os.path.join(OUT_ROOT, 'pallet-truck')


def pt_size(p):
    return f"{p['diameter_mm']} × {p['width_mm']} × {p['bore_mm']} mm"


def pt_range(vals, unit):
    lo, hi = min(vals), max(vals)
    return f'{n(lo)} {unit}' if lo == hi else f'{n(lo)}–{n(hi)} {unit}'


def pt_card(cat, sc, p):
    return f'''<a class="p-card" href="{cat['url']}{sc['id']}/{p['slug']}/">
  <div class="p-card-img"><img src="{p['images']['thumb']}" alt="{e(p['name'])}" loading="lazy" width="420" height="594"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{e(sc['short'])} &middot; Pallet Truck {e(p['kind'])}</div>
    <div class="p-card-inch">{n(p['diameter_mm'])} &times; {n(p['width_mm'])} mm</div>
    <div class="p-card-name">Bore {n(p['bore_mm'])} mm &middot; Ball bearing</div>
    <div class="p-card-load">Load capacity: <b>{n(p['load_kg'])} kg</b></div>
    <div class="p-card-cta">View details &rarr;</div>
  </div>
</a>'''


def pt_table(cat, prods, subcats, show_material=True):
    sname = {s['id']: s for s in subcats}
    head = ('<th scope="col">Material</th>' if show_material else '') + '<th scope="col">Type</th><th scope="col">Size (Dia &times; Width &times; Bore)</th><th scope="col">Load Capacity</th>'
    order = [s['id'] for s in subcats]
    rows, prev = '', None
    for p in prods:
        cls = [f'grp-{order.index(p["subcat"]) % 3 + 1}'] if show_material else []
        if show_material and p['subcat'] != prev:
            cls.append('grp-start')
        if p['kind'] == 'Wheel':
            cls.append('row-wheel')
        prev = p['subcat']
        kind = '<span class="kind-tag">Wheel</span>' if p['kind'] == 'Wheel' else e(p['kind'])
        rows += (f'<tr class="{" ".join(cls)}">' + (f'<td>{e(sname[p["subcat"]]["short"])}</td>' if show_material else '')
                 + f'<td>{kind}</td><td><a href="{cat["url"]}{p["subcat"]}/{p["slug"]}/">{e(pt_size(p))}</a></td><td>{n(p["load_kg"])} kg</td></tr>')
    return f'<div class="tbl-wrap"><table class="data-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def build_pt_category(cat):
    prods, subcats, url = cat['products'], cat['subcats'], cat['url']
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), None)])
    choices = []
    for sc in subcats:
        sp = [p for p in prods if p['subcat'] == sc['id']]
        kinds = sorted({p['kind'] for p in sp}, key=lambda k: k != 'Roller')
        choices.append(f'''<a class="pt-choice" href="{url}{sc['id']}/">
  <div class="pt-choice-img"><img src="/assets/products/pallet-truck/{sc['id']}/material-wheel-roller.jpg" alt="{e(sc['short'])} pallet truck wheel and roller" loading="lazy" width="720" height="478"></div>
  <div class="pt-choice-body">
    <div class="pt-choice-name">{e(sc['short'])}</div>
    <div class="pt-choice-full">{e(sc['full'])}</div>
    <ul class="pt-choice-facts">
      <li><b>{len(sp)}</b> products &middot; {' &amp; '.join(e(k + 's') for k in kinds)}</li>
      <li>Load capacity <b>{pt_range([p['load_kg'] for p in sp], 'kg')}</b></li>
    </ul>
    <div class="pt-choice-cta">View {e(sc['short'])} range &rarr;</div>
  </div>
</a>''')
    loads = [p['load_kg'] for p in prods]
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">Wheels &amp; Castors</div>
  <h1 class="page-title">Pallet Truck <span class="hl">Wheels &amp; Rollers</span></h1>
  <p class="page-sub">{e(cat['intro'])}</p>
  <div class="head-actions">
    <a class="btn-primary" href="{e(enquire_url(cat['name'], None, 'Wheels & Castors > ' + cat['name'], url))}">Enquire Now</a>
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue</a>
  </div>
  <div class="key-facts">
    <div class="fact"><div class="fact-num">{len(prods)}</div><div class="fact-label">Products</div></div>
    <div class="fact"><div class="fact-num">{len(subcats)}</div><div class="fact-label">Materials</div></div>
    <div class="fact"><div class="fact-num">{n(prods[0]['bore_mm']) if len({p['bore_mm'] for p in prods}) == 1 else '—'}<small>mm</small></div><div class="fact-label">Bore</div></div>
    <div class="fact"><div class="fact-num">{n(min(loads))}&ndash;{n(max(loads))}<small>kg</small></div><div class="fact-label">Load capacity</div></div>
  </div>
</header>

<div class="wrap">
  <h2 class="h2">Choose a Material</h2>
  <div class="pt-choices">
{chr(10).join(choices)}
  </div>
</div>

<div class="wrap alt sum-table">
  <h2 class="h2">All Sizes &amp; Load Capacities <small>{len(prods)} products</small></h2>
  {pt_table(cat, prods, subcats)}
</div>

<section class="cta-band">
  <div><h2>Need a replacement wheel or roller?</h2><p>Tell us your pallet truck model and the size you need &mdash; our team will confirm the right part.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(enquire_url(cat['name'], None, 'Wheels & Castors > ' + cat['name'], url))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'CollectionPage', 'name': cat['name'], 'url': SITE + url, 'description': cat['intro'],
         'isPartOf': {'@id': f'{SITE}/#website'},
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}{url}{p['subcat']}/{p['slug']}/", 'name': p['name']} for i, p in enumerate(prods)]}},
    ]}
    return page(title=f"Pallet Truck Wheels & Rollers – UHMW, PU-CI & Cast Iron, {n(min(loads))}–{n(max(loads))} kg | Kotibhaskar",
                description=f"{cat['intro']} {len(prods)} products with technical drawings and specifications. Made in India by Kotibhaskar Industries, Satara.",
                canonical=url, body=body, jsonld=jsonld, og_image=SITE + '/assets/products/pallet-truck/category.jpg',
                wa_text=f"Hello, I'm interested in your pallet truck wheels & rollers (kotibhaskarindustries.com{url}).")


def build_pt_subcat(cat, sc):
    prods = [p for p in cat['products'] if p['subcat'] == sc['id']]
    url = f"{cat['url']}{sc['id']}/"
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), cat['url']), (e(sc['short']), None)])
    switch = ''.join(f'<a class="filter-btn{" active" if s["id"] == sc["id"] else ""}" href="{cat["url"]}{s["id"]}/"'
                     f'{" aria-current=\"page\"" if s["id"] == sc["id"] else ""}>{e(s["short"])} <span>{sum(p["subcat"] == s["id"] for p in cat["products"])}</span></a>'
                     for s in cat['subcats'])
    blocks = []
    for kind in ('Roller', 'Wheel'):
        kp = [p for p in prods if p['kind'] == kind]
        if not kp:
            continue
        blocks.append(f'''<section class="group-block" aria-labelledby="h-{kind.lower()}">
  <div class="group-head"><h2 id="h-{kind.lower()}">{e(sc['short'])} Pallet Truck <b>{e(kind)}s</b></h2><p>{len(kp)} {'size' if len(kp) == 1 else 'sizes'} &middot; {pt_range([p['load_kg'] for p in kp], 'kg')}</p></div>
  <div class="card-grid">
{chr(10).join(pt_card(cat, sc, p) for p in kp)}
  </div>
</section>''')
    loads = [p['load_kg'] for p in prods]
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="duty-badge">{e(cat['name'])} &middot; <b>{e(sc['short'])}</b></div>
  <h1 class="page-title">{e(sc['short'])} Pallet Truck <span class="hl">Wheels &amp; Rollers</span></h1>
  <p class="page-sub">{e(sc['full'])} rollers and wheels for hand pallet trucks &mdash; ball bearing, {n(prods[0]['bore_mm'])} mm bore.</p>
  <div class="key-facts">
    <div class="fact"><div class="fact-num">{len(prods)}</div><div class="fact-label">Products</div></div>
    <div class="fact"><div class="fact-num">{pt_range([p['diameter_mm'] for p in prods], '').strip()}<small>mm</small></div><div class="fact-label">Diameter</div></div>
    <div class="fact"><div class="fact-num">{pt_range([p['width_mm'] for p in prods], '').strip()}<small>mm</small></div><div class="fact-label">Width</div></div>
    <div class="fact"><div class="fact-num">{n(min(loads))}&ndash;{n(max(loads))}<small>kg</small></div><div class="fact-label">Load capacity</div></div>
  </div>
</header>

<div class="wrap">
  <div class="filter-bar" role="navigation" aria-label="Choose material">{switch}<a class="filter-btn" href="{cat['url']}">All materials</a></div>
{chr(10).join(blocks)}
</div>

<div class="wrap alt sum-table">
  <h2 class="h2">{e(sc['short'])} Size &amp; Load Table <small>{len(prods)} products</small></h2>
  {pt_table(cat, prods, cat['subcats'], show_material=False)}
</div>

<section class="cta-band">
  <div><h2>Need a replacement wheel or roller?</h2><p>Tell us your pallet truck model and the size you need &mdash; our team will confirm the right part.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(enquire_url(f"{sc['short']} {cat['name']}", None, f"Wheels & Castors > {cat['name']} > {sc['short']}", url))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'CollectionPage', 'name': f"{sc['short']} {cat['name']}", 'url': SITE + url,
         'isPartOf': {'@id': f'{SITE}/#website'},
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}{url}{p['slug']}/", 'name': p['name']} for i, p in enumerate(prods)]}},
    ]}
    return page(title=f"{sc['short']} Pallet Truck Wheels & Rollers ({sc['full']}) – {len(prods)} Sizes | Kotibhaskar",
                description=f"{sc['short']} ({sc['full']}) pallet truck rollers and wheels by Kotibhaskar Industries, Satara: {len(prods)} sizes, "
                            f"ball bearing, {n(prods[0]['bore_mm'])} mm bore, {n(min(loads))}–{n(max(loads))} kg load capacity.",
                canonical=url, body=body, jsonld=jsonld, og_image=SITE + prods[0]['images']['photo'],
                wa_text=f"Hello, I'm interested in your {sc['short']} pallet truck wheels & rollers (kotibhaskarindustries.com{url}).")


def build_pt_product(cat, sc, p):
    url = f"{cat['url']}{sc['id']}/{p['slug']}/"
    size = pt_size(p)
    path = f"Wheels & Castors > {cat['name']} > {sc['short']}"
    title_base = f"{sc['short']} Pallet Truck {p['kind']}"
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), cat['url']),
                                   (e(sc['short']), f"{cat['url']}{sc['id']}/"), (e(f"{p['kind']} {size}"), None)])
    same = [q for q in cat['products'] if q['subcat'] == sc['id']]
    sibs = ''.join(
        f'<a class="sib{" current" if q["slug"] == p["slug"] else ""}" href="{cat["url"]}{sc["id"]}/{q["slug"]}/"'
        f'{" aria-current=\"page\"" if q["slug"] == p["slug"] else ""}>{e(q["kind"])} {n(q["diameter_mm"])} &times; {n(q["width_mm"])} mm'
        f'<small>Bore {n(q["bore_mm"])} mm &middot; {n(q["load_kg"])} kg</small></a>' for q in same)
    others = [q for q in cat['products'] if q['subcat'] != sc['id'] and q['slug'] == p['slug']]
    smap = {s['id']: s for s in cat['subcats']}
    alt = ''
    if others:
        alt = ('<p class="pt-alt"><b>Same size in other materials:</b> ' + ' &middot; '.join(
            f'<a href="{cat["url"]}{q["subcat"]}/{q["slug"]}/">{e(smap[q["subcat"]]["short"])} &ndash; {n(q["load_kg"])} kg</a>' for q in others) + '</p>')
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="duty-badge">{e(cat['name'])} &middot; <b>{e(sc['short'])}</b></div>
  <h1 class="page-title">{e(title_base)} <span class="size-line">{n(p['diameter_mm'])} &times; {n(p['width_mm'])} &times; {n(p['bore_mm'])} mm <span class="size-inch">(Dia &times; Width &times; Bore)</span></span></h1>
  <p class="page-sub">{e(sc['full'])} {e(p['kind'].lower())} for hand pallet trucks, with ball bearings.</p>
  <div class="key-facts">
    <div class="fact"><div class="fact-num">{n(p['diameter_mm'])}<small>mm</small></div><div class="fact-label">{e(p['kind'])} diameter</div></div>
    <div class="fact"><div class="fact-num">{n(p['width_mm'])}<small>mm</small></div><div class="fact-label">{e(p['kind'])} width</div></div>
    <div class="fact"><div class="fact-num">{n(p['bore_mm'])}<small>mm</small></div><div class="fact-label">Bore ID</div></div>
    <div class="fact"><div class="fact-num">{n(p['load_kg'])}<small>kg</small></div><div class="fact-label">Load capacity</div></div>
  </div>
</header>

<div class="wrap">
  <div class="prod-layout">
    <div>
      <div class="gallery">
        <figure>
          <a href="{p['images']['photo']}" data-lightbox><img src="{p['images']['photo']}" alt="{e(p['name'])} — product photograph" width="900" height="1273"></a>
          <figcaption>Product photo <span>Click to enlarge</span></figcaption>
        </figure>
        <figure>
          <a href="{p['images']['drawing']}" data-lightbox><img src="{p['images']['drawing']}" alt="{e(p['name'])} — technical dimensional drawing" width="1100" height="1556"></a>
          <figcaption>Technical drawing <span>Click to enlarge</span></figcaption>
        </figure>
      </div>
    </div>
    <div>
      <h2 class="sec-label">Technical Specifications</h2>
      <div class="tbl-wrap">
        <table class="data-table spec-table"><tbody>{spec_rows_html(p['specs'])}</tbody></table>
      </div>
      {alt}
      <div class="action-box">
        <a class="btn-primary" href="{e(enquire_url(p['name'], size, path, url))}">&#9993; Enquire Now</a>
        <a class="btn-wa" href="{e(wa_url(f'Hello, I would like a quotation for: {p["name"]} ({SITE}{url})'))}" target="_blank" rel="noopener">{WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
        <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue (PDF)</a>
        <button type="button" class="btn-outline" data-print>&#128438; Print / Save as PDF</button>
        <p class="action-note">No prices are listed online &mdash; send an enquiry for a quotation.</p>
      </div>
    </div>
  </div>
</div>

<div class="wrap alt siblings-wrap">
  <h2 class="h2">Other {e(sc['short'])} Pallet Truck Wheels &amp; Rollers</h2>
  <div class="siblings">{sibs}</div>
  <p style="margin-top:22px;"><a class="btn-outline" href="{cat['url']}">View all {len(cat['products'])} {e(cat['name'])}</a></p>
</div>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'Product', 'name': p['name'], 'url': SITE + url,
         'image': [SITE + p['images']['photo'], SITE + p['images']['drawing']],
         'description': f"{p['name']}: {sc['full']} pallet truck {p['kind'].lower()}, diameter {n(p['diameter_mm'])} mm, width {n(p['width_mm'])} mm, "
                        f"bore {n(p['bore_mm'])} mm, ball bearing, load capacity {n(p['load_kg'])} kg.",
         'brand': {'@type': 'Brand', 'name': 'Kotibhaskar'},
         'manufacturer': {'@id': f'{SITE}/#organization'},
         'category': path, 'material': dict(p['specs']).get('Wheel Material', ''),
         'additionalProperty': [{'@type': 'PropertyValue', 'name': k, 'value': display_spec(k, v)} for k, v in p['specs']]},
    ]}
    sheet = print_sheet(category=cat['name'], group_name=sc['short'], title=title_base, size=f'{size} (Dia × Width × Bore)',
                        load=f"{n(p['load_kg'])} kg", photo=p['images']['photo'], drawing=p['images']['drawing'],
                        specs=p['specs'], url=url, load_label='Load Capacity')
    return page(title=f"{title_base} {size} – {n(p['load_kg'])} kg | Kotibhaskar",
                description=f"{p['name']} — {sc['full']}, diameter {n(p['diameter_mm'])} mm, width {n(p['width_mm'])} mm, bore {n(p['bore_mm'])} mm, "
                            f"ball bearing, load capacity {n(p['load_kg'])} kg. Made in India by Kotibhaskar Industries, Satara.",
                canonical=url, body=body, jsonld=jsonld, og_image=SITE + p['images']['photo'],
                wa_text=f'Hello, I would like a quotation for: {p["name"]} ({SITE}{url})', sheet=sheet)


# ============================================================================
# MS SOLID TRACK WHEELS (data/products/ms-track/ms-track.json)
# 5th wheels & castors category: 1 category page + 4 profile pages.
# One shared size table (capacities are the same for all profiles per the catalogue).
# Mounting type and bracket information are not in the source and are not shown.
# ============================================================================
MS_ROOT = os.path.join(OUT_ROOT, 'ms-track')


def ms_list(vals, unit='mm'):
    vals = sorted(set(vals))
    return (', '.join(n(v) for v in vals[:-1]) + ' and ' + n(vals[-1]) if len(vals) > 1 else n(vals[0])) + (f' {unit}' if unit else '')


def ms_range(vals, unit):
    return f'{n(min(vals))}–{n(max(vals))} {unit}'


def ms_bearing(r):
    return f"Ball Bearing &middot; {e(r['bearing_no'])}" if r['bearing_no'] else 'Plain Bore'


def ms_table(cat, rows, prof=None, url=None):
    """Complete size table; rows tinted per wheel width. With prof, each row gets an Enquire link."""
    widths = sorted({r['width_mm'] for r in rows})
    head = ('<th scope="col">Wheel Diameter<br><small>mm</small></th><th scope="col">Wheel Width<br><small>mm</small></th>'
            '<th scope="col">Boss Width<br><small>mm</small></th><th scope="col">Bore ID<br><small>mm</small></th>'
            '<th scope="col">Bearing Type / Number</th><th scope="col">Load Capacity per Wheel<br><small>kg</small></th>'
            + ('<th scope="col"><span class="sr-only">Enquiry</span></th>' if prof else ''))
    body, prev = '', None
    for r in rows:
        cls = f'grp-{widths.index(r["width_mm"]) % 3 + 1}' + (' grp-start' if r['width_mm'] != prev else '')
        prev = r['width_mm']
        enq = ''
        if prof:
            size = f"{r['diameter_mm']} × {r['width_mm']} mm, bore {r['bore_mm']} mm, {r['bearing']}" + (f" {r['bearing_no']}" if r['bearing_no'] else '')
            link = enquire_url(f"{prof['title'][:-1]} – {size}", size, f"Wheels & Castors > {cat['name']} > {prof['name']}", url)
            enq = f'<td><a class="row-enq" href="{e(link)}">Enquire</a></td>'
        body += (f'<tr class="{cls}"><td>{n(r["diameter_mm"])}</td><td>{n(r["width_mm"])}</td><td>{n(r["boss_mm"])}</td>'
                 f'<td>{n(r["bore_mm"])}</td><td>{ms_bearing(r)}</td><td class="key">{n(r["load_kg"])}</td>{enq}</tr>')
    return f'<div class="tbl-wrap"><table class="data-table ms-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def ms_specs(cat, prof):
    rows = cat['rows']
    bnos = sorted({r['bearing_no'] for r in rows if r['bearing_no']}, key=lambda b: [r['bearing_no'] for r in rows].index(b))
    return [
        ('Wheel Material', cat['material']),
        ('Wheel Profile', prof['name']),
        ('Wheel Diameter', ms_range([r['diameter_mm'] for r in rows], 'mm') + ' (see size table)'),
        ('Wheel Width', ms_list([r['width_mm'] for r in rows])),
        ('Boss Width', ms_list([r['boss_mm'] for r in rows]) + ' (by wheel width)'),
        ('Bore ID', ms_list([r['bore_mm'] for r in rows]) + ' (see size table)'),
        ('Bearing Type', 'Plain Bore or Ball Bearing (see size table)'),
        ('Bearing Number', ', '.join(bnos) + ' (ball bearing versions)'),
        ('Load Capacity per Wheel', ms_range([r['load_kg'] for r in rows], 'kg') + ' (see size table)'),
        ('Maximum Working Temperature', cat['max_temp']),
        ('Brand', 'Kotibhaskar'),
        ('Country', 'Made in India'),
    ]


def ms_head_facts(cat):
    rows = cat['rows']
    return f'''<div class="key-facts">
    <div class="fact"><div class="fact-num">{len({(r['diameter_mm'], r['width_mm'], r['bore_mm']) for r in rows})}</div><div class="fact-label">Sizes</div></div>
    <div class="fact"><div class="fact-num">{n(min(r['diameter_mm'] for r in rows))}&ndash;{n(max(r['diameter_mm'] for r in rows))}<small>mm</small></div><div class="fact-label">Wheel diameter</div></div>
    <div class="fact"><div class="fact-num">{n(min(r['load_kg'] for r in rows))}&ndash;{n(max(r['load_kg'] for r in rows))}<small>kg</small></div><div class="fact-label">Load per wheel</div></div>
    <div class="fact"><div class="fact-num">{e(cat['max_temp'].replace(' °C', ''))}<small>°C</small></div><div class="fact-label">Max. working temp.</div></div>
  </div>'''


def build_ms_category(cat):
    url = cat['url']
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), None)])
    cards = ''.join(f'''<a class="pt-choice" href="{url}{p['id']}/">
  <div class="pt-choice-img"><img src="{p['images']['card']}" alt="{e(p['title'])}" loading="lazy" width="600" height="606"></div>
  <div class="pt-choice-body">
    <div class="pt-choice-name">{e(p['name'])}</div>
    <div class="pt-choice-full">{e(p['title'])}</div>
    <ul class="pt-choice-facts">
      <li><b>{len({(r['diameter_mm'], r['width_mm'], r['bore_mm']) for r in cat['rows']})}</b> sizes &middot; plain bore &amp; ball bearing</li>
      <li>Load per wheel <b>{ms_range([r['load_kg'] for r in cat['rows']], 'kg')}</b></li>
    </ul>
    <div class="pt-choice-cta">View {e(p['name'])} wheels &rarr;</div>
  </div>
</a>''' for p in cat['profiles'])
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">Wheels &amp; Castors</div>
  <h1 class="page-title">MS Solid <span class="hl">Track Wheels</span></h1>
  <p class="page-sub">{e(cat['intro'])}</p>
  <div class="head-actions">
    <a class="btn-primary" href="{e(enquire_url(cat['name'], None, 'Wheels & Castors > ' + cat['name'], url))}">Enquire Now</a>
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue</a>
  </div>
  {ms_head_facts(cat)}
</header>

<div class="wrap">
  <h2 class="h2">Choose a Profile</h2>
  <div class="pt-choices ms-choices">
{cards}
  </div>
</div>

<div class="wrap alt sum-table">
  <h2 class="h2">All Sizes &amp; Load Capacities <small>{len(cat['rows'])} configurations</small></h2>
  <p class="ms-note">{e(cat['shared_capacity_note'])}</p>
  {ms_table(cat, cat['rows'])}
</div>

<section class="cta-band">
  <div><h2>Need help choosing a track wheel?</h2><p>Tell us the profile, size and bearing you need &mdash; our team will confirm availability.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(enquire_url(cat['name'], None, 'Wheels & Castors > ' + cat['name'], url))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'CollectionPage', 'name': cat['name'], 'url': SITE + url, 'description': cat['intro'],
         'isPartOf': {'@id': f'{SITE}/#website'},
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(cat['profiles']), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}{url}{p['id']}/", 'name': p['title']} for i, p in enumerate(cat['profiles'])]}},
    ]}
    loads = [r['load_kg'] for r in cat['rows']]
    return page(title=f"MS Solid Track Wheels – V-Groove, Square, Round & Flange, {n(min(loads))}–{n(max(loads))} kg | Kotibhaskar",
                description=f"{cat['intro']} Load capacity {n(min(loads))}–{n(max(loads))} kg per wheel. Made in India by Kotibhaskar Industries, Satara.",
                canonical=url, body=body, jsonld=jsonld, og_image=SITE + cat['cover']['image'],
                wa_text=f"Hello, I'm interested in your MS solid track wheels (kotibhaskarindustries.com{url}).")


def ms_letterhead(cat, prof):
    c = COMPANY
    return f'''  <div class="ps-head">
    <img class="ps-logo" src="{c['logo']}" alt="KOTIBHASKAR">
    <div class="ps-company">
      <div class="ps-name">{e(c['name'])}</div>
      <div class="ps-tag">{e(c['tagline'])}</div>
      <div class="ps-contact">{e(c['address'])}<br>
        Tel: {' &middot; '.join(e(t) for t in c['phones'])}<br>
        Email: {' &middot; '.join(e(m) for m in c['emails'])} &nbsp;|&nbsp; Web: {e(c['website'])}</div>
    </div>
  </div>
  <div class="ps-band"><span>Product Specification Sheet</span><span>Wheels &amp; Castors &middot; {e(cat['name'])}</span></div>'''


def ms_foot(url, page_no):
    c = COMPANY
    return f'''  <div class="ps-foot">
    <div><b>{e(c['name'])}</b><br>{e(c['website'])}</div>
    <div>{e(c['phones'][0])} &nbsp;|&nbsp; {e(c['emails'][0])} &nbsp;|&nbsp; Page {page_no} of 2</div>
    <div class="ps-url">{'/<wbr>'.join(f'<span>{e(seg)}</span>' for seg in (c['website'] + url).split('/'))}</div>
  </div>'''


def ms_sheet(cat, prof, url):
    rows = cat['rows']
    specs = ''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k, v in ms_specs(cat, prof))
    draws = ''.join(f'<figure><div class="ps-img"><img src="{d["src"]}" alt=""></div><figcaption>W {d["width_mm"]} &middot; Boss {d["boss_mm"]} mm</figcaption></figure>'
                    for d in prof['images']['drawings'])
    load = ms_range([r['load_kg'] for r in rows], 'kg')
    trows = ''.join(f'<tr><td>{n(r["diameter_mm"])}</td><td>{n(r["width_mm"])}</td><td>{n(r["boss_mm"])}</td><td>{n(r["bore_mm"])}</td>'
                    f'<td>{ms_bearing(r)}</td><td class="key">{n(r["load_kg"])}</td></tr>' for r in rows)
    return f'''<div class="print-sheet ms-sheet" aria-hidden="true">
{ms_letterhead(cat, prof)}
  <div class="ps-title">
    <div>
      <div class="ps-cat">{e(cat['name'])} &middot; {e(prof['name'])}</div>
      <div class="ps-h">{e(prof['title'])}</div>
      <div class="pst-sub">{e(cat['material'])} &middot; plain bore and ball bearing versions &middot; maximum working temperature {e(cat['max_temp'])}</div>
    </div>
    <div class="ps-load"><span>Load Capacity per Wheel</span><b>{load}</b></div>
  </div>
  <div class="ms-ps-top">
    <div class="ms-ps-photo"><img src="{prof['images']['photo']}" alt=""></div>
    <div>
      <div class="ps-sec">Technical Specifications</div>
      <table class="ps-specs"><tbody>{specs}</tbody></table>
    </div>
  </div>
  <div class="ps-sec">Dimensional Drawings <span class="ms-ps-legend">D = wheel diameter &middot; d = bore ID &middot; values per size on page 2</span></div>
  <div class="ms-ps-draw">{draws}</div>
  <div class="ps-note">The drawings illustrate ball-bearing configurations; plain-bore versions are available where listed in the size table.</div>
{ms_foot(url, 1)}
</div>
<div class="print-sheet ms-sheet" aria-hidden="true">
{ms_letterhead(cat, prof)}
  <div class="ps-title">
    <div>
      <div class="ps-cat">{e(cat['name'])} &middot; {e(prof['name'])}</div>
      <div class="ps-h">{e(prof['title'])} &mdash; Sizes &amp; Load Capacities</div>
    </div>
  </div>
  <table class="pst-table ms-ps-table"><thead><tr><th>Wheel Diameter (mm)</th><th>Wheel Width (mm)</th><th>Boss Width (mm)</th><th>Bore ID (mm)</th><th>Bearing Type / Number</th><th>Load Capacity per Wheel (kg)</th></tr></thead><tbody>{trows}</tbody></table>
  <div class="ps-note">{e(cat['shared_capacity_note'])} Specifications subject to change without notice. Contact us for a quotation.</div>
{ms_foot(url, 2)}
</div>'''


def build_ms_product(cat, prof):
    url = f"{cat['url']}{prof['id']}/"
    rows = cat['rows']
    path = f"Wheels & Castors > {cat['name']} > {prof['name']}"
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Wheels &amp; Castors', '/wheels-castors/'), (e(cat['name']), cat['url']), (e(prof['name']), None)])
    specs_html = ''.join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in ms_specs(cat, prof))
    draws = ''.join(f'''<figure>
          <a href="{d['src']}" data-lightbox><img src="{d['src']}" alt="{e(prof['title'])} — dimensional drawing, wheel width {d['width_mm']} mm" loading="lazy" width="1100" height="1556"></a>
          <figcaption>Wheel width {d['width_mm']} mm <span>Boss width {d['boss_mm']} mm</span></figcaption>
        </figure>''' for d in prof['images']['drawings'])
    sibs = ''.join(f'<a class="sib{" current" if q["id"] == prof["id"] else ""}" href="{cat["url"]}{q["id"]}/"'
                   f'{" aria-current=\"page\"" if q["id"] == prof["id"] else ""}>{e(q["name"])}<small>MS track wheels</small></a>' for q in cat['profiles'])
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="duty-badge">{e(cat['name'])} &middot; <b>{e(prof['name'])}</b></div>
  <h1 class="page-title">{e(prof['title'])}</h1>
  <p class="page-sub">Mild steel solid track wheels with a {e(prof['name'])} profile, in plain bore and ball bearing versions.</p>
  {ms_head_facts(cat)}
</header>

<div class="wrap">
  <div class="t-layout ms-layout">
    <figure class="t-photo ms-photo">
      <a href="{prof['images']['photo']}" data-lightbox><img src="{prof['images']['photo']}" alt="{e(prof['title'])} — product photograph" width="900" height="1273"></a>
      <figcaption>Product photo <span>Click to enlarge</span></figcaption>
    </figure>
    <div>
      <h2 class="sec-label">Technical Specifications</h2>
      <div class="tbl-wrap"><table class="data-table spec-table"><tbody>{specs_html}</tbody></table></div>
      <p class="ms-note">{e(cat['shared_capacity_note'])}</p>
      <div class="action-box">
        <a class="btn-primary" href="{e(enquire_url(prof['title'], None, path, url))}">&#9993; Enquire Now</a>
        <a class="btn-wa" href="{e(wa_url(f'Hello, I would like a quotation for: {prof["title"]} ({SITE}{url})'))}" target="_blank" rel="noopener">{WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
        <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue (PDF)</a>
        <button type="button" class="btn-outline" data-print>&#128438; Print / Save as PDF</button>
        <p class="action-note">No prices are listed online &mdash; send an enquiry for a quotation.</p>
      </div>
    </div>
  </div>
</div>

<div class="wrap alt sum-table" id="sizes">
  <h2 class="h2">Sizes &amp; Load Capacities <small>{len(rows)} configurations</small></h2>
  {ms_table(cat, rows, prof, url)}
</div>

<div class="wrap">
  <h2 class="h2">Dimensional Drawings <small>by wheel width</small></h2>
  <p class="ms-note">D = wheel diameter, d = bore ID &mdash; the values for each size are listed in the table above. Click a drawing to enlarge.</p>
  <p class="ms-note ms-draw-note">The drawings illustrate ball-bearing configurations; plain-bore versions are available where listed in the size table.</p>
  <div class="ms-drawings">
        {draws}
  </div>
</div>

<div class="wrap alt siblings-wrap">
  <h2 class="h2">Other MS Track Wheel Profiles</h2>
  <div class="siblings">{sibs}</div>
  <p style="margin-top:22px;"><a class="btn-outline" href="{cat['url']}">View all MS Solid Track Wheels</a></p>
</div>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'Product', 'name': prof['title'], 'url': SITE + url,
         'image': [SITE + prof['images']['photo']] + [SITE + d['src'] for d in prof['images']['drawings']],
         'description': f"{prof['title']}: {cat['material']}, {ms_range([r['diameter_mm'] for r in rows], 'mm')} diameter, plain bore and ball bearing, "
                        f"{ms_range([r['load_kg'] for r in rows], 'kg')} per wheel, maximum working temperature {cat['max_temp']}.",
         'brand': {'@type': 'Brand', 'name': 'Kotibhaskar'}, 'manufacturer': {'@id': f'{SITE}/#organization'},
         'category': path, 'material': cat['material'],
         'additionalProperty': [{'@type': 'PropertyValue', 'name': k, 'value': v} for k, v in ms_specs(cat, prof)]},
    ]}
    return page(title=f"{prof['title']} – {ms_range([r['diameter_mm'] for r in rows], 'mm')}, {ms_range([r['load_kg'] for r in rows], 'kg')} | Kotibhaskar",
                description=f"{prof['title']} by Kotibhaskar Industries, Satara: {cat['material']}, plain bore and ball bearing, "
                            f"{len(rows)} size and bearing configurations, {ms_range([r['load_kg'] for r in rows], 'kg')} per wheel, max. {cat['max_temp']}.",
                canonical=url, body=body, jsonld=jsonld, og_image=SITE + prof['images']['photo'],
                wa_text=f'Hello, I would like a quotation for: {prof["title"]} ({SITE}{url})', sheet=ms_sheet(cat, prof, url))



# ============================================================================
# MATERIAL HANDLING TROLLEYS (data/products/trolleys/trolleys.json)
# Flexible products: each trolley has its own spec columns and size variants.
# No model codes and no prices are ever rendered (checked by check_public_output).
# ============================================================================
TROLLEY_ROOT = os.path.join(REPO, 'material-handling-trolleys')


def _num_unit(v):
    m = re.match(r'\s*([\d.]+)\s*(kg|lit|liters|litres|L)\b', v or '')
    return (float(m.group(1)), m.group(2)) if m else (None, None)


def capacity_range(p):
    vals = [_num_unit(v.get('Load Capacity', ''))[0] for v in p['variants']]
    vals = [x for x in vals if x is not None]
    if not vals:
        return ''
    lo, hi = min(vals), max(vals)
    return f'{n(lo)} kg' if lo == hi else f'{n(lo)}–{n(hi)} kg'


def split_columns(p):
    """Columns identical for every size become 'common' specs; the rest form the table."""
    cols = list(p['variants'][0].keys())
    if len(p['variants']) == 1:
        return cols, []
    keep = set(p.get('table_always', []))
    common = [c for c in cols if c not in keep and len({v.get(c) for v in p['variants']}) == 1]
    table = [c for c in cols if c not in common]
    return table, common


def variant_text(p, v):
    return ', '.join(v[k] for k in p.get('variant_key', []) if v.get(k))


def wheel_html(cat, p, cls='chip-list'):
    if not p.get('wheels'):
        return ''
    # a material links to a wheel category only when it is the same construction (PU-PP has no wheel page)
    chips = ''.join((f'<a class="chip" href="{w["url"]}">' if w.get('url') else '<span class="chip">')
                    + f'<b>{e(w["name"])}</b> {e(w["full"])}' + ('</a>' if w.get('url') else '</span>')
                    for w in (cat['wheel_materials'][k] for k in p['wheels']))
    return f'<div class="{cls}">{chips}</div>'


def build_trolley_product(cat, p, idx):
    groups = {g['id']: g for g in cat['groups']}
    g = groups[p['group']]
    url = f"{cat['url']}{p['slug']}/"
    crange = capacity_range(p)
    table_cols, common_cols = split_columns(p)
    vid = video_html(url)
    nsizes = len(p['variants'])
    crumb_html, crumb_ld = crumbs([('Home', '/'), (e(cat['name']), cat['url']), (e(g['name']), f"{cat['url']}#{g['id']}"), (e(p['name']), None)])
    path = f"{cat['name']} > {g['name']}"
    if p.get('facts'):      # products without wheels (pallets) show their own key facts instead
        extra_facts = ''.join(f'<div class="fact"><div class="fact-num{"" if re.match(r"^[0-9.–-]+$", num) else " fact-text"}">{e(num)}{f"<small>{e(unit)}</small>" if unit else ""}</div><div class="fact-label">{e(label)}</div></div>'
                              for num, unit, label in p['facts'])
    else:
        brake_word = {'optional': 'Optional', 'standard': 'Standard'}.get(p.get('brake'), '—')
        extra_facts = (f'<div class="fact"><div class="fact-num">{len(p.get("wheels", []))}</div><div class="fact-label">Wheel options</div></div>'
                       f'<div class="fact"><div class="fact-num fact-text">{brake_word}</div><div class="fact-label">Parking brake</div></div>')

    head_cells = ''.join(f'<th scope="col">{e(c)}</th>' for c in table_cols) + '<th scope="col"><span class="sr-only">Enquiry</span></th>'
    body_rows = ''
    for v in p['variants']:
        cells = ''.join(f'<td{" class=\"key\"" if c == "Load Capacity" else ""}>{e(v[c])}</td>' for c in table_cols)
        vt = variant_text(p, v)
        link = enquire_url(f"{p['name']} – {vt}" if vt else p['name'], vt or None, path, url)
        body_rows += f'<tr>{cells}<td><a class="row-enq" href="{e(link)}">Enquire</a></td></tr>'
    common = ''
    if common_cols:
        common = '<p class="common-specs"><b>Common to all sizes:</b> ' + ' &middot; '.join(
            f'{e(c)} <span>{e(p["variants"][0][c])}</span>' for c in common_cols) + '</p>'
    feats = ''.join(f'<li>{e(f)}</li>' for f in p['features'])
    notes = ''.join(f'<p class="t-note">{e(nt)}</p>' for nt in p.get('notes', []))
    brake = f'<div class="brake-note"><b>Brakes</b> {e(p["brake_text"])}</div>' if p.get('brake') else ''
    wheels = (f'<h2 class="sec-label">Wheel Options</h2>{wheel_html(cat, p)}') if p.get('wheels') else ''
    same = [q for q in cat['products'] if q['group'] == p['group'] and q['slug'] != p['slug']]
    sibs = ''
    if same:
        sibs = '<div class="wrap alt siblings-wrap"><h2 class="h2">Other ' + e(g['name']) + '</h2><div class="siblings">' + ''.join(
            f'<a class="sib" href="{cat["url"]}{q["slug"]}/">{e(q["name"])}<small>{capacity_range(q)}</small></a>' for q in same) + '</div></div>'

    body = f'''<header class="page-head t-head">
  {crumb_html}
  <div class="duty-badge">{e(cat['name'])} &middot; <b>{e(g['name'])}</b></div>
  <h1 class="page-title">{e(p['name'])}</h1>
  <p class="page-sub">{e(p['summary'])}</p>
  <div class="key-facts">
    <div class="fact"><div class="fact-num">{crange.replace(' kg', '')}<small>kg</small></div><div class="fact-label">Load capacity</div></div>
    <a class="fact fact-link" href="#sizes"><div class="fact-num">{nsizes}</div><div class="fact-label">{'Size available' if nsizes == 1 else 'Sizes available'} &darr;</div></a>
    {extra_facts}
  </div>
</header>

<div class="wrap t-main">
  <div class="t-layout">
    {'<div class="t-media">' if vid else ''}<figure class="t-photo">
      <a href="{p['images']['photo']}" data-lightbox><img src="{p['images']['photo']}" alt="{e(p['name'])} — product photograph" width="900" height="1165"></a>
      <figcaption>Product photo <span>Click to enlarge</span></figcaption>
    </figure>{vid + '</div>' if vid else ''}
    <div>
      <h2 class="sec-label">Construction &amp; Features</h2>
      <ul class="feat-list t-feats">{feats}</ul>
      {'<p class="t-multi">Available in multiple sizes and configurations. Please refer to the <a href="#sizes">specifications table below</a> for details.</p>' if nsizes > 1 else ''}
      {notes}
      {wheels}
      {brake}
      <dl class="t-origin"><div><dt>Brand</dt><dd>Kotibhaskar</dd></div><div><dt>Country of Origin</dt><dd>Made in India</dd></div></dl>
      <div class="action-box">
        <a class="btn-primary" href="{e(enquire_url(p['name'], None, path, url))}">&#9993; Enquire Now</a>
        <a class="btn-wa" href="{e(wa_url(f'Hello, I would like a quotation for: {p["name"]} ({SITE}{url})'))}" target="_blank" rel="noopener">{WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
        <a class="btn-dark" href="{cat['catalogue']}" target="_blank" rel="noopener">{DL_ICON} Trolley Catalogue (PDF)</a>
        <button type="button" class="btn-outline" data-print>&#128438; Print / Save as PDF</button>
        <p class="action-note">No prices are listed online &mdash; send an enquiry for a quotation.</p>
      </div>
    </div>
  </div>
</div>

<div class="wrap alt t-sizes" id="sizes">
  <h2 class="h2">Available Sizes &amp; Specifications <small>{nsizes} {'size' if nsizes == 1 else 'sizes'}</small></h2>
  <div class="tbl-wrap"><table class="data-table variant-table"><thead><tr>{head_cells}</tr></thead><tbody>{body_rows}</tbody></table></div>
  {common}
</div>
{sibs}'''

    jsonld = {'@context': 'https://schema.org', '@graph': [
        crumb_ld,
        {'@type': 'Product', 'name': p['name'], 'url': SITE + url, 'image': [SITE + p['images']['photo']],
         'description': p['summary'], 'brand': {'@type': 'Brand', 'name': 'Kotibhaskar'},
         'manufacturer': {'@id': f'{SITE}/#organization'}, 'category': path},
    ]}
    sheet = trolley_sheet(cat, g, p, url, table_cols, common_cols, crange)
    title = f"{p['name']} – {crange} Load Capacity, {nsizes} {'Size' if nsizes == 1 else 'Sizes'} | Kotibhaskar"
    desc = f"{p['name']} by Kotibhaskar Industries, Satara: {p['summary']} Load capacity {crange}."
    return page(title=title, description=desc, canonical=url, body=body, jsonld=jsonld,
                og_image=SITE + p['images']['photo'],
                wa_text=f'Hello, I would like a quotation for: {p["name"]} ({SITE}{url})', sheet=sheet)


def trolley_sheet(cat, g, p, url, table_cols, common_cols, crange):
    """Branded A4 datasheet for a trolley (same letterhead as the wheel datasheets)."""
    c = COMPANY
    head = ''.join(f'<th>{e(col)}</th>' for col in table_cols)
    rows = ''.join('<tr>' + ''.join(f'<td{" class=\"key\"" if col == "Load Capacity" else ""}>{e(v[col])}</td>' for col in table_cols) + '</tr>'
                   for v in p['variants'])
    common = (' &middot; '.join(f'{e(col)}: <b>{e(p["variants"][0][col])}</b>' for col in common_cols)) if common_cols else ''
    wheels = ''
    if p.get('wheels'):
        wheels = '<div class="pst-line"><b>Wheel options:</b> ' + ' &middot; '.join(
            f'{e(w["name"])} ({e(w["full"])})' for w in (cat['wheel_materials'][k] for k in p['wheels'])) + '</div>'
    brake = f'<div class="pst-line"><b>Brakes:</b> {e(p["brake_text"])}</div>' if p.get('brake') else ''
    notes = ''.join(f'<div class="pst-line">{e(nt)}</div>' for nt in p.get('notes', []))
    feats = ''.join(f'<li>{e(f)}</li>' for f in p['features'])
    return f'''<div class="print-sheet" aria-hidden="true">
  <div class="ps-head">
    <img class="ps-logo" src="{c['logo']}" alt="KOTIBHASKAR">
    <div class="ps-company">
      <div class="ps-name">{e(c['name'])}</div>
      <div class="ps-tag">{e(c['tagline'])}</div>
      <div class="ps-contact">{e(c['address'])}<br>
        Tel: {' &middot; '.join(e(t) for t in c['phones'])}<br>
        Email: {' &middot; '.join(e(m) for m in c['emails'])} &nbsp;|&nbsp; Web: {e(c['website'])}</div>
    </div>
  </div>
  <div class="ps-band"><span>Product Specification Sheet</span><span>{e(cat['name'])} &middot; {e(g['name'])}</span></div>
  <div class="ps-title">
    <div>
      <div class="ps-cat">{e(cat['name'])} &middot; {e(g['name'])}</div>
      <div class="ps-h">{e(p['name'])}</div>
      <div class="pst-sub">{e(p['summary'])}</div>
    </div>
    <div class="ps-load"><span>Load Capacity</span><b>{e(crange)}</b></div>
  </div>
  <div class="pst-top">
    <div class="pst-photo"><img src="{p['images']['photo']}" alt=""></div>
    <div class="pst-info">
      <div class="ps-sec">Construction &amp; Features</div>
      <ul class="pst-feats">{feats}</ul>
      {wheels}{brake}{notes}
      <div class="pst-line"><b>Brand:</b> Kotibhaskar &nbsp;&middot;&nbsp; <b>Country of Origin:</b> Made in India</div>
    </div>
  </div>
  <div class="ps-sec">Available Sizes &amp; Specifications</div>
  <table class="pst-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>
  {f'<div class="pst-common">Common to all sizes: {common}</div>' if common else ''}
  <div class="ps-note">Specifications subject to change without notice. Contact us for a quotation.</div>
  <div class="ps-foot">
    <div><b>{e(c['name'])}</b><br>{e(c['website'])}</div>
    <div>{e(c['phones'][0])} &nbsp;|&nbsp; {e(c['emails'][0])}</div>
    <div class="ps-url">{'/<wbr>'.join(f'<span>{e(seg)}</span>' for seg in (c['website'] + url).split('/'))}</div>
  </div>
</div>'''


def build_trolley_category(cat):
    groups = cat['groups']
    prods = cat['products']
    url = cat['url']
    crumb_html, crumb_ld = crumbs([('Home', '/'), (e(cat['name']), None)])
    filter_btns = [f'<button type="button" class="filter-btn active" data-filter="all" aria-pressed="true">All <span>{len(prods)}</span></button>']
    blocks = []
    for g in groups:
        gp = [p for p in prods if p['group'] == g['id']]
        if not gp:
            continue
        filter_btns.append(f'<button type="button" class="filter-btn" data-filter="{g["id"]}" aria-pressed="false">{e(g["name"])} <span>{len(gp)}</span></button>')
        cards = ''.join(f'''<a class="p-card" href="{url}{p['slug']}/">
  <div class="p-card-img"><img src="{p['images']['thumb']}" alt="{e(p['name'])}" loading="lazy" width="420" height="544"></div>
  <div class="p-card-body">
    <div class="p-card-duty">{e(g['name'])}</div>
    <div class="p-card-name">{e(p['name'])}</div>
    <div class="p-card-meta">{len(p['variants'])} {'size' if len(p['variants']) == 1 else 'sizes'}</div>
    <div class="p-card-load">Load capacity: <b>{capacity_range(p)}</b></div>
    <div class="p-card-cta">View details &rarr;</div>
  </div>
</a>''' for p in gp)
        blocks.append(f'''<section class="group-block" id="{g['id']}" aria-labelledby="h-{g['id']}">
  <div class="group-head"><h2 id="h-{g['id']}">{e(g['name'])}</h2><p>{len(gp)} {'product' if len(gp) == 1 else 'products'}</p></div>
  <div class="card-grid">{cards}</div>
</section>''')
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">What We Make</div>
  <h1 class="page-title">Material Handling <span class="hl">Trolleys</span></h1>
  <p class="page-sub">{e(cat['intro'])}</p>
  <div class="head-actions">
    <a class="btn-primary" href="{e(enquire_url(cat['name'], None, cat['name'], url))}">Enquire Now</a>
    <a class="btn-dark" href="{cat['catalogue']}" target="_blank" rel="noopener">{DL_ICON} Trolley Catalogue</a>
  </div>
</header>
<div class="wrap">
  <div class="filter-bar" role="group" aria-label="Filter by trolley type">{''.join(filter_btns)}</div>
{chr(10).join(blocks)}
</div>
<section class="cta-band">
  <div><h2>Need a trolley for a specific load or space?</h2><p>Tell us what you need to move &mdash; our team will recommend the right trolley and size.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(enquire_url(cat['name'], None, cat['name'], url))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld,
        {'@type': 'CollectionPage', 'name': cat['name'], 'url': SITE + url, 'description': cat['intro'],
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}{url}{p['slug']}/", 'name': p['name']} for i, p in enumerate(prods)]}}]}
    return page(title='Material Handling Trolleys – Platform, Shelf, Turntable & Utility Trolleys | Kotibhaskar Industries',
                description=f"{cat['intro']} {len(prods)} trolley products with sizes, capacities and specifications.",
                canonical=url, body=body, jsonld=jsonld,
                og_image=SITE + prods[0]['images']['photo'] if prods else None,
                wa_text='Hello, I am interested in your material handling trolleys (kotibhaskarindustries.com).')


# Public-output safety checks: no prices and no model codes on trolley pages
PRICE_RX = re.compile(r'(?i)\bprice\b|\bdiscount\b|\bgst\b|\btaxable\b|total amount|\bRs\.?\s?\d|₹|\b\d{1,3},\d{3}\.\d{2}\b')
CODE_RX = re.compile(r'\b(?:PL|WS|DR|TP|TW|SA|TPT|TWT|DWB|2SH|3SH|5SH|MU|GAS|CH|PA|CFT|CNC|WT|MAS)\.\d{2}\.[0-9A-Z]{1,2}\b|\bBIN\.\d\.[SD]\d\b')


def check_public_output(paths, forbid_puci=True):
    problems = []
    for pth in paths:
        txt = open(pth, encoding='utf-8').read()
        visible = re.sub(r'No prices are listed online', '', txt)
        # product content only (structured data + <main> + datasheet), not the shared nav/footer,
        # which correctly links to the PU-CI wheel category
        content = (txt.split('<body', 1)[0] + txt.split('<main>', 1)[-1].split('</main>', 1)[0]
                   + (txt.split('class="print-sheet"', 1)[1] if 'class="print-sheet"' in txt else ''))
        # trolleys use PU-PP wheels; PU-CI (a different construction) must never appear in trolley content
        checks = [(PRICE_RX, 'price/commercial text', visible), (CODE_RX, 'model code', visible)]
        if forbid_puci:
            checks.append((re.compile(r'PU\s*-?\s*CI|Cast Iron Core|/wheels-castors/puci'), 'PU-CI in trolley content', content))
        for rx, label, scope in checks:
            m = rx.search(scope)
            if m:
                problems.append(f'{os.path.relpath(pth, REPO)}: {label} "{m.group(0)}"')
    if problems:
        print('BUILD STOPPED - public output check failed:')
        for pr in problems:
            print('  -', pr)
        sys.exit(1)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def main():
    cats = []
    for path in sorted(glob.glob(os.path.join(REPO, 'data', 'products', 'wheels', '*.json'))):
        with open(path, encoding='utf-8') as f:
            c = json.load(f)
        if c.get('products'):
            cats.append(c)
    # order categories like the source folders ("10 UHMW", "20 PU CI", "30 ...")
    def order(c):
        m = re.match(r'(\d+)', os.path.basename(c.get('source_dir', '')))
        return (int(m.group(1)) if m else 999, c['name'])
    cats.sort(key=order)
    NAV_CATS[:] = cats
    pt = None
    ptpath = os.path.join(REPO, 'data', 'products', 'pallet-truck', 'pallet-truck.json')
    if os.path.exists(ptpath):
        with open(ptpath, encoding='utf-8') as f:
            pt = json.load(f)
        if pt.get('products'):
            NAV_CATS.append({'url': pt['url'], 'name': pt['name']})   # footer link
        else:
            pt = None
    ms = None
    mspath = os.path.join(REPO, 'data', 'products', 'ms-track', 'ms-track.json')
    if os.path.exists(mspath):
        with open(mspath, encoding='utf-8') as f:
            ms = json.load(f)
        for prof in ms['profiles']:
            prof['images']['card'] = f"/assets/products/ms-track/{prof['id']}/card.jpg"
        NAV_CATS.append({'url': ms['url'], 'name': ms['name']})   # footer link

    # wipe old generated pages so removed products disappear
    for c in cats:
        shutil.rmtree(os.path.join(OUT_ROOT, c['id']), ignore_errors=True)

    urls = ['/', '/wheels-castors/']
    write(os.path.join(OUT_ROOT, 'index.html'), build_hub(cats, pt, ms))
    count = 0
    for c in cats:
        write(os.path.join(OUT_ROOT, c['id'], 'index.html'), build_category(c))
        urls.append(c['url'])
        for i, p in enumerate(c['products']):
            write(os.path.join(OUT_ROOT, c['id'], p['slug'], 'index.html'), build_product(c, p, i))
            urls.append(f"{c['url']}{p['slug']}/")
            count += 1

    # ---- Pallet Truck Wheels & Rollers (category > material > product)
    ptcount = 0
    if pt:
        shutil.rmtree(PT_ROOT, ignore_errors=True)
        written = [os.path.join(PT_ROOT, 'index.html')]
        write(written[0], build_pt_category(pt))
        urls.append(pt['url'])
        for sc in pt['subcats']:
            pth = os.path.join(PT_ROOT, sc['id'], 'index.html')
            write(pth, build_pt_subcat(pt, sc))
            written.append(pth)
            urls.append(f"{pt['url']}{sc['id']}/")
            for p in [q for q in pt['products'] if q['subcat'] == sc['id']]:
                pth = os.path.join(PT_ROOT, sc['id'], p['slug'], 'index.html')
                write(pth, build_pt_product(pt, sc, p))
                written.append(pth)
                urls.append(f"{pt['url']}{sc['id']}/{p['slug']}/")
                ptcount += 1
        check_public_output(written, forbid_puci=False)

    # ---- MS Solid Track Wheels (category + 4 profile pages)
    mscount = 0
    if ms:
        shutil.rmtree(MS_ROOT, ignore_errors=True)
        written = [os.path.join(MS_ROOT, 'index.html')]
        write(written[0], build_ms_category(ms))
        urls.append(ms['url'])
        for prof in ms['profiles']:
            pth = os.path.join(MS_ROOT, prof['id'], 'index.html')
            write(pth, build_ms_product(ms, prof))
            written.append(pth)
            urls.append(f"{ms['url']}{prof['id']}/")
            mscount += 1
        check_public_output(written, forbid_puci=False)

    # ---- Material Handling Trolleys
    tcount = 0
    tpath = os.path.join(REPO, 'data', 'products', 'trolleys', 'trolleys.json')
    if os.path.exists(tpath):
        with open(tpath, encoding='utf-8') as f:
            tcat = json.load(f)
        shutil.rmtree(TROLLEY_ROOT, ignore_errors=True)
        written = [os.path.join(TROLLEY_ROOT, 'index.html')]
        write(written[0], build_trolley_category(tcat))
        urls.append(tcat['url'])
        for i, p in enumerate(tcat['products']):
            pth = os.path.join(TROLLEY_ROOT, p['slug'], 'index.html')
            write(pth, build_trolley_product(tcat, p, i))
            written.append(pth)
            urls.append(f"{tcat['url']}{p['slug']}/")
            tcount += 1
        check_public_output(written)

    # ---- Material Handling Equipment (hub > family > product) + homepage showcase
    import build_equipment
    eq_urls, eqcount = build_equipment.build(sys.modules[__name__])
    urls += eq_urls
    check_videos_used()

    # ---- Homepage Solution Finder data (verified capacities / heights only) + its script tag
    import build_finder
    build_finder.build(sys.modules[__name__])

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pr = '1.0' if u == '/' else ('0.8' if u.count('/') <= 3 else '0.6')
        sm.append(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>')
    sm.append('</urlset>')
    write(os.path.join(REPO, 'sitemap.xml'), '\n'.join(sm) + '\n')
    print(f'Built hub + {len(cats)} category page(s) + {count} product pages; '
          f'pallet truck: category + {len(pt["subcats"]) if pt else 0} material pages + {ptcount} product pages; '
          f'MS track wheels: category + {mscount} profile pages; '
          f'trolleys: category + {tcount} product page(s); equipment: {eqcount} product pages; sitemap has {len(urls)} URLs.')


if __name__ == '__main__':
    main()
