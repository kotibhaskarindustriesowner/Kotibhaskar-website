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
import glob
import html
import json
import os
import re
import shutil
import urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kotibhaskarindustries.com'
CATALOGUE = '/Kotibhaskar%201%20Castor%20Catalogue.pdf'
WHATSAPP = '919822413252'
TODAY = datetime.date.today().isoformat()
OUT_ROOT = os.path.join(REPO, 'wheels-castors')
NAV_CATS = []   # all built categories, used for footer links (filled in main)

e = lambda s: html.escape(str(s), quote=True)


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
    'tagline': 'Manufacturer of Material Handling Equipment, Industrial Trolleys, and Industrial Wheels & Castors',
    'address': 'Plot No. K-3/2/1, Additional MIDC, Satara - 415004, Maharashtra, India',
    'address_line1': 'Plot No. K-3/2/1, Additional MIDC,',
    'address_line2': 'Satara - 415004, Maharashtra, India',
    'phones': ['+91 98224 13252', '+91 83800 95804', '+91 83800 95805'],
    'emails': ['amodsales@gmail.com', 'amodsatara@gmail.com'],
    'website': 'kotibhaskarindustries.com',
    'logo': '/assets/brand/kotibhaskar-logo.png',   # official black KOTIBHASKAR wordmark (392x120)
}

# Spec rows that are highlighted on the web page and the printed datasheet.
KEY_ROWS = ('Size', 'Load Capacity per Caster')


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
    return value


def spec_rows_html(specs):
    return ''.join(
        f'<tr{" class=\"key\"" if label in KEY_ROWS else ""}><th scope="row">{e(label)}</th><td>{e(display_spec(label, value))}</td></tr>'
        for label, value in specs)


def print_sheet(*, category, group_name, title, size, load, photo, drawing, specs, url):
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
    <div class="ps-load"><span>Load Capacity per Caster</span><b>{e(load)}</b></div>
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


def page(*, title, description, canonical, body, og_image=None, jsonld=None, wa_text=None, sheet=''):
    og_image = og_image or f'{SITE}/assets/brand/og-image.png'
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
<link rel="stylesheet" href="/assets/css/site.css">
</head>
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
    <li><a href="/#about">About</a></li>
    <li><a href="/#contact" class="nav-cta">Get Quote</a></li>
  </ul>
  <button class="hamburger" type="button" aria-label="Open menu" aria-controls="mobileMenu" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <a href="/#hero">Home</a>
  <a href="/#products">Products</a>
  <a href="/wheels-castors/">Wheels &amp; Castors</a>
  <a href="/#customers">Customers</a>
  <a href="/#network">Pan-India Reach</a>
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
      <a href="/#mhe">MHE Equipment</a>
      <a href="/#trolleys">Trolleys</a>
      <a href="/wheels-castors/">Wheels &amp; Castors</a>
      {''.join(f'<a href="{c["url"]}">{e(c["name"])}</a>' for c in NAV_CATS)}
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <a href="/#about">About Us</a>
      <a href="/#customers">Customers</a>
      <a href="/#network">Pan-India Reach</a>
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
<script src="/assets/js/site.js" defer></script>
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
    for g in groups:
        gp = [p for p in prods if p['group'] == g['id']]
        if not gp:
            continue
        filter_btns.append(f'<button type="button" class="filter-btn" data-filter="{g["id"]}" aria-pressed="false">{e(g["name"])} <span>{len(gp)}</span></button>')
        cards = []
        for p in gp:
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
            rows.append(f'<tr><td>{e(g["short"])}</td><td><a href="{url}{p["slug"]}/">{n(p["diameter_mm"])} &times; {n(p["width_mm"])} mm '
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

<div class="wrap">
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
def build_hub(cats):
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
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">What We Make</div>
  <h1 class="page-title">Wheels <span class="hl">&amp; Castors</span></h1>
  <p class="page-sub">Industrial wheels and castors manufactured at our Satara MIDC plant. Browse each range for sizes, technical drawings and specifications.</p>
  <div class="head-actions">
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{DL_ICON} Wheels &amp; Castors Catalogue</a>
    <a class="btn-outline" href="/#castors">All wheel &amp; castor types</a>
  </div>
</header>
<div class="wrap">
  <div class="card-grid">
{chr(10).join(cards)}
  </div>
  <div class="custom-note" style="margin-top:32px;"><strong>More ranges coming online</strong>Other wheel and castor ranges are listed on our <a href="/#castors" style="color:#C85A00;">homepage</a> and in the Wheels &amp; Castors catalogue.</div>
</div>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld]}
    return page(title='Industrial Wheels & Castors Manufacturer | Kotibhaskar Industries, Satara',
                description='Industrial wheels and castors by Kotibhaskar Industries, Satara: ' + ', '.join(c['name'] for c in cats)
                + ' in medium duty, heavy duty and heavy duty twin ranges, with technical drawings and specifications.',
                canonical='/wheels-castors/', body=body, jsonld=jsonld)


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

    # wipe old generated pages so removed products disappear
    for c in cats:
        shutil.rmtree(os.path.join(OUT_ROOT, c['id']), ignore_errors=True)

    urls = ['/', '/wheels-castors/']
    write(os.path.join(OUT_ROOT, 'index.html'), build_hub(cats))
    count = 0
    for c in cats:
        write(os.path.join(OUT_ROOT, c['id'], 'index.html'), build_category(c))
        urls.append(c['url'])
        for i, p in enumerate(c['products']):
            write(os.path.join(OUT_ROOT, c['id'], p['slug'], 'index.html'), build_product(c, p, i))
            urls.append(f"{c['url']}{p['slug']}/")
            count += 1

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pr = '1.0' if u == '/' else ('0.8' if u.count('/') <= 3 else '0.6')
        sm.append(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>')
    sm.append('</urlset>')
    write(os.path.join(REPO, 'sitemap.xml'), '\n'.join(sm) + '\n')
    print(f'Built hub + {len(cats)} category page(s) + {count} product pages; sitemap has {len(urls)} URLs.')


if __name__ == '__main__':
    main()
