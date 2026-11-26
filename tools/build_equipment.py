"""Material Handling Equipment pages (hub > family > product), built from
data/products/equipment/equipment.json by tools/build_site.py.

    /material-handling-equipment/                      hub: family showcase + A-Z list of every product
    /material-handling-equipment/<family>/             family: subtype sections with product cards
    /material-handling-equipment/<family>/<product>/   product page + 2-page A4 datasheet

The same family showcase markup is written into index.html between the
EQUIPMENT-SHOWCASE markers (it replaces the old small product grid).
"""
import html
import json
import os
import re
import shutil

ROOT_URL = '/material-handling-equipment/'
CATALOGUE = '/Kotibhaskar%201%20Catalogue.pdf'
OP_ORDER = ['Manual', 'Semi-Electric AC', 'Semi-Electric DC', 'Fully Electric', 'Electro-Hydraulic']
OP_NOTE = {'Manual': 'Hand-pump hydraulic lifting', 'Semi-Electric AC': '440 V, 3 phase AC power pack',
           'Semi-Electric DC': '24 V DC battery power pack', 'Fully Electric': '24 V battery, AC drive',
           'Electro-Hydraulic': 'Push-button hydraulic power pack'}
# short, factual configuration highlights per family (all taken from the source price lists)
HIGHLIGHTS = {
    'pallet-trucks': ['Up to 2500 kg', '550 / 685 mm widths', 'Roll lifting & high lift', 'SPM built to order'],
    'stackers': ['1000 & 1500 kg', 'Lift 1.6 / 2.5 / 3.1 m', 'Adjustable forks', 'Cage & jib-hook versions'],
    'order-pickers': ['300 kg', 'Cage height 3.1 / 4.0 m'],
    'drum-lifters-tilters': ['300 kg', '360° drum rotation', 'Lift 1.6 / 2.5 / 3.1 m'],
    'material-lifters-tilters': ['300 kg', '600 × 600 × 600 mm pan', 'Lift 1.6 / 2.5 / 3.1 m'],
    'drum-grippers': ['300 kg', 'Automatic drum clamping', 'Lift 1.6 / 2.5 / 3.1 m'],
    'floor-cranes': ['500 – 1500 kg', 'Standard & counterbalanced', 'Fixed & swivelling boom'],
    'scissor-lifts': ['500 – 2000 kg', 'Single & double scissor', 'Mobile & pit-mounted', 'SPM built to order'],
    'gantries': ['500 / 1000 / 2000 kg', '3.0 m lift', 'Chain pulley block or electric hoist'],
    'dock-levellers': ['5000 & 9000 kg', '415 V, 3 phase AC'],
    'goods-lifts': ['1000 & 2000 kg', '6200 mm lift', 'Two & four channel'],
    'industrial-shelving': ['Heavy & medium duty', 'Up to 2000 kg per shelf'],
    'conveyors': ['Gravity & motorised', 'Straight or inclined', '6000 mm long'],
}
WHEEL_LINKS = {'uhmw': ('UHMW', 'Standard — white hard-polymer wheels', '/wheels-castors/uhmw/'),
               'puci': ('PU-CI', 'Option — red polyurethane on cast iron', '/wheels-castors/puci/'),
               'ci': ('CI', 'Option — cast iron wheels', '/wheels-castors/ci/')}
SPM_NOTE = ('Special-purpose equipment (SPM): built to the customer’s application. '
            'Specifications and dimensions can be tailored to your requirement — the values shown are a reference configuration.')


def e(s):
    return html.escape(str(s), quote=True)


def family_url(f):
    return f"{ROOT_URL}{f['id']}/"


def product_url(p):
    return f"{ROOT_URL}{p['family']}/{p['slug']}/"


def ops_of(prods):
    present = {p['operation'] for p in prods}
    return [o for o in OP_ORDER if o in present]


def cap_text(p):
    if p.get('capacities'):
        return ' / '.join(p['capacities'])
    for t in p['tables']:
        if t['head'] and t['head'][0] == 'Specification':
            for r in t['rows']:
                if re.search(r'(?i)capacity', r[0]):
                    vals = list(dict.fromkeys(r[1:]))
                    return ' / '.join(vals)
        else:
            for i, h in enumerate(t['head']):
                if re.search(r'(?i)capacity', h):
                    vals = list(dict.fromkeys(row[i] for row in t['rows']))
                    unit = '' if any('kg' in v for v in vals) else ' kg'
                    return ' / '.join(vals) + unit
    return ''


def lift_text(p):
    return ' / '.join(p.get('lifts', []))


def thumb(p, cls='', lazy=True):
    return (f'<img src="{p["images"]["thumb"]}" alt="{e(p["name"])}" width="420" height="594"'
            f'{" loading=\"lazy\" decoding=\"async\"" if lazy else ""}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>')


# ---------------------------------------------------------------- family showcase (homepage + hub)
def showcase_picks(fam, prods, n):
    """Pick n products with different photos, spread across the family's subtypes."""
    by_sub = {}
    for p in prods:
        by_sub.setdefault(p['subtype'], []).append(p)
    picks, seen, rnd = [], set(), 0
    while len(picks) < n and any(len(v) > rnd for v in by_sub.values()):
        for v in by_sub.values():
            if len(v) > rnd and len(picks) < n and v[rnd]['source']['photo'] not in seen:
                picks.append(v[rnd])
                seen.add(v[rnd]['source']['photo'])
        rnd += 1
    return picks


# compact family cards (owner design, 26 Nov 2026). Rows follow the owner's order:
# Pallet Trucks, Stackers, Floor Cranes, Scissor Lifts; Drum Lifters & Tilters beside Drum Lifters with
# Auto Gripper; Goods Lifts; Material Lifters & Tilters beside Gantries; then the remaining families.
SHOWCASE_ROWS = [['pallet-trucks', 'stackers', 'floor-cranes'],
                 ['scissor-lifts', 'drum-lifters-tilters', 'drum-grippers'],
                 ['goods-lifts', 'material-lifters-tilters', 'gantries'],
                 ['order-pickers', 'dock-levellers', 'industrial-shelving', 'conveyors']]
# two visibly different machines per family (one for the single-product dock leveller)
SHOWCASE = {
    'pallet-trucks': ['hydraulic-pallet-truck-550', 'electric-pallet-truck'],
    'stackers': ['manual-stacker-550', 'electric-stacker'],
    'floor-cranes': ['manual-hydraulic-floor-crane', 'semi-electric-ac-counterbalance-floor-crane-fixed-boom'],
    'scissor-lifts': ['manual-hydraulic-scissor-lift-single', 'electro-hydraulic-scissor-lift-2000x2000'],
    'drum-lifters-tilters': ['manual-drum-lifter-tilter', 'electric-drum-lifter-tilter'],
    'drum-grippers': ['manual-drum-lifter-auto-gripper', 'semi-electric-ac-drum-lifter-auto-gripper'],
    'goods-lifts': ['two-channel-goods-lift', 'four-channel-lifting-cage'],
    'material-lifters-tilters': ['manual-material-lifter-tilter', 'semi-electric-ac-material-lifter-tilter'],
    'gantries': ['manual-gantry', 'electric-gantry'],
    'order-pickers': ['semi-electric-ac-order-picker', 'electric-order-picker'],
    'dock-levellers': ['electro-hydraulic-dock-leveller'],
    'industrial-shelving': ['industrial-shelving-heavy-duty', 'industrial-shelving-medium-duty'],
    'conveyors': ['gravity-roller-conveyor', 'rubber-belt-conveyor'],
}


def family_card(fam, prods, per_row):
    chosen = SHOWCASE.get(fam['id'])
    picks = [next(p for p in prods if p['slug'] == s) for s in chosen] if chosen else showcase_picks(fam, prods, 2)
    n = len(prods)
    imgs = ''.join(thumb(p) for p in picks)
    return f'''<a class="eqc eqc-{per_row}" href="{family_url(fam)}" aria-label="{e(fam['name'])} — {n} product{'s' if n != 1 else ''}">
  <div class="eqc-photos eqc-n{len(picks)}">{imgs}</div>
  <div class="eqc-foot"><div><h3 class="eqc-name">{e(fam['name'])}</h3><span class="eqc-count">{n} product{'s' if n != 1 else ''}</span></div><span class="eqc-arrow" aria-hidden="true">&rarr;</span></div>
</a>'''


def showcase(data):
    fams = {f['id']: f for f in data['families']}
    placed = [fid for row in SHOWCASE_ROWS for fid in row]
    assert sorted(placed) == sorted(fams), 'every equipment family must appear exactly once in SHOWCASE_ROWS'
    cards = []
    for row in SHOWCASE_ROWS:
        for fid in row:
            cards.append(family_card(fams[fid], [p for p in data['products'] if p['family'] == fid], len(row)))
    return '<div class="eqc-grid">' + '\n'.join(cards) + '</div>'


# ---------------------------------------------------------------- tables & text
def table_html(t, cls='data-table eq-table', sticky=True):
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in t['head'])
    body = ''
    spec = t['head'] and t['head'][0] == 'Specification'
    for r in t['rows']:
        cells = ''
        for i, v in enumerate(r):
            v = '<br>'.join(e(x) for x in v.split('\n'))
            if i == 0 and spec:
                cells += f'<th scope="row">{v}</th>'
            else:
                cells += f'<td>{v}</td>'
        key = ' class="key"' if re.search(r'(?i)^(load )?(carrying )?capacity', r[0]) else ''
        body += f'<tr{key}>{cells}</tr>'
    title = f'<h3 class="eq-table-title">{e(t["title"])}</h3>' if t.get('title') else ''
    return f'{title}<div class="tbl-wrap"><table class="{cls}{" eq-spec" if spec else ""}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def feats_html(items, cls='feat-list eq-feats'):
    out = []
    for it in items:
        if it['lines']:
            sub = ''.join(f'<li>{e(x)}</li>' for x in it['lines'])
            out.append(f'<li><b>{e(it["head"])}</b><ul>{sub}</ul></li>')
        else:
            out.append(f'<li>{e(it["head"])}</li>')
    return f'<ul class="{cls}">' + ''.join(out) + '</ul>'


def config_count(p):
    n = 0
    for t in p['tables']:
        n += (len(t['head']) - 1) if t['head'] and t['head'][0] == 'Specification' else len(t['rows'])
    return n


# ---------------------------------------------------------------- pages
def build_hub(h, data):
    fams = data['families']
    crumb_html, crumb_ld = h.crumbs([('Home', '/'), ('Material Handling Equipment', None)])
    az = []
    for fam in fams:
        prods = [p for p in data['products'] if p['family'] == fam['id']]
        links = ''.join(f'<li><a href="{product_url(p)}">{e(p["name"])}</a></li>' for p in prods)
        az.append(f'<div class="eq-az-fam"><h3><a href="{family_url(fam)}">{e(fam["name"])}</a> <span>{len(prods)}</span></h3><ul>{links}</ul></div>')
    n = len(data['products'])
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">What We Make</div>
  <h1 class="page-title">Material Handling <span class="hl">Equipment</span></h1>
  <p class="page-sub">{n} products in {len(fams)} equipment families — manual, semi-electric AC, semi-electric DC, fully electric and electro-hydraulic, manufactured by Kotibhaskar Industries in Satara, Maharashtra.</p>
  <div class="head-actions">
    <a class="btn-primary" href="{e(h.enquire_url('Material Handling Equipment', None, 'Material Handling Equipment', ROOT_URL))}">Enquire Now</a>
    <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{h.DL_ICON} Equipment Catalogue (PDF)</a>
  </div>
</header>
<div class="wrap eq-hub">
  {showcase(data)}
</div>
<div class="wrap alt">
  <h2 class="h2">All Equipment A&ndash;Z <small>{n} products</small></h2>
  <div class="eq-az">{''.join(az)}</div>
</div>
<section class="cta-band">
  <div><h2>Not sure which equipment suits your load?</h2><p>Tell us what you need to lift or move &mdash; we will recommend the right model, capacity and lift height.</p></div>
  <div class="acts"><a class="btn-primary" href="{e(h.enquire_url('Material Handling Equipment', None, 'Material Handling Equipment', ROOT_URL))}">Send Enquiry</a><a class="btn-outline" href="tel:+919822413252">Call +91 98224 13252</a></div>
</section>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld, {
        '@type': 'CollectionPage', 'name': 'Material Handling Equipment', 'url': h.SITE + ROOT_URL,
        'mainEntity': {'@type': 'ItemList', 'numberOfItems': n, 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': h.SITE + product_url(p), 'name': p['name']} for i, p in enumerate(data['products'])]}}]}
    return h.page(extra_css=h.EQ_CSS_URL, title='Material Handling Equipment Manufacturer – Pallet Trucks, Stackers, Floor Cranes & Lifts | Kotibhaskar',
                  description=f'{n} material handling equipment products: pallet trucks, stackers, order pickers, drum tilters, floor cranes, scissor lifts, gantries, dock levellers, goods lifts, shelving and conveyors. Manual, semi-electric and electric. Made in Satara, India.',
                  canonical=ROOT_URL, body=body, jsonld=jsonld,
                  og_image=h.SITE + data['products'][0]['images']['photo'],
                  wa_text='Hello, I am interested in your material handling equipment (kotibhaskarindustries.com).')


def product_card(p, show_sub=False):
    cap, lift = cap_text(p), lift_text(p)
    return f'''<a class="p-card eq-card" href="{product_url(p)}">
  <div class="p-card-img">{thumb(p)}</div>
  <div class="p-card-body">
    <div class="p-card-duty">{e(p['operation'])}{' · SPM' if p.get('spm') else ''}</div>
    <div class="p-card-name">{e(p['name'])}</div>
    {f'<div class="p-card-load">Capacity: <b>{e(cap)}</b></div>' if cap else ''}
    {f'<div class="p-card-meta">Lift: {e(lift)}</div>' if lift else ''}
    <div class="p-card-cta">View details &rarr;</div>
  </div>
</a>'''


def sort_by_operation(prods):
    """Manual, Semi-Electric AC, Semi-Electric DC, Fully Electric (stable within each operation)."""
    rank = {o: i for i, o in enumerate(OP_ORDER)}
    return sorted(prods, key=lambda p: rank.get(p['operation'], len(OP_ORDER)))


def build_family(h, data, fam):
    prods = [p for p in data['products'] if p['family'] == fam['id']]
    # subtype order: as listed, but any fully electric subtype comes last
    prods = sorted(prods, key=lambda p: 1 if p['subtype'].startswith('Fully Electric') else 0)
    url = family_url(fam)
    crumb_html, crumb_ld = h.crumbs([('Home', '/'), ('Material Handling Equipment', ROOT_URL), (e(fam['name']), None)])
    subs = list(dict.fromkeys(p['subtype'] for p in prods))
    jump = ''
    if len(subs) > 1:
        jump = '<nav class="eq-jump" aria-label="Jump to type">' + ''.join(
            f'<a href="#{slug(s)}">{e(s)} <span>{sum(1 for p in prods if p["subtype"] == s)}</span></a>' for s in subs) + '</nav>'
    blocks = []
    for s in subs:
        sp = sort_by_operation([p for p in prods if p['subtype'] == s])
        ops = ops_of(sp)
        note = OP_NOTE.get(ops[0]) if len(ops) == 1 else ''
        blocks.append(f'''<section class="group-block eq-group" id="{slug(s)}" aria-labelledby="h-{slug(s)}" style="--n:{min(len(sp), 4)}">
  <div class="group-head"><h2 id="h-{slug(s)}">{e(s)}</h2><p>{len(sp)} product{'s' if len(sp) != 1 else ''}{f' &middot; {e(note)}' if note else ''}</p></div>
  <div class="card-grid eq-cards">{''.join(product_card(p) for p in sp)}</div>
</section>''')
    blocks = ['<div class="eq-groups">'] + blocks + ['</div>']
    chips = ''.join(f'<li class="op">{e(o)}</li>' for o in ops_of(prods)) + ''.join(f'<li>{e(x)}</li>' for x in HIGHLIGHTS.get(fam['id'], []))
    others = ''.join(f'<a class="sib" href="{family_url(f)}">{e(f["name"])}<small>{sum(1 for p in data["products"] if p["family"] == f["id"])} products</small></a>'
                     for f in data['families'] if f['id'] != fam['id'])
    body = f'''<header class="page-head">
  {crumb_html}
  <div class="section-tag">Material Handling Equipment</div>
  <h1 class="page-title">{e(fam['name'])}</h1>
  <p class="page-sub">{e(fam['desc'])}</p>
  <ul class="eqf-chips eq-head-chips">{chips}</ul>
  <div class="head-actions">
    <a class="btn-primary" href="{e(h.enquire_url(fam['name'], None, 'Material Handling Equipment', url))}">Enquire Now</a>
    <a class="btn-wa" href="{e(h.wa_url(f'Hello, I would like a quotation for {fam["name"]} ({h.SITE}{url})'))}" target="_blank" rel="noopener">{h.WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
  </div>
</header>
<div class="wrap">
  {jump}
{chr(10).join(blocks)}
</div>
<div class="wrap alt siblings-wrap"><h2 class="h2">Other Equipment Families</h2><div class="siblings">{others}</div></div>'''
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld, {
        '@type': 'CollectionPage', 'name': fam['name'], 'url': h.SITE + url, 'description': fam['desc'],
        'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods), 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': h.SITE + product_url(p), 'name': p['name']} for i, p in enumerate(prods)]}}]}
    ops = ', '.join(ops_of(prods))
    return h.page(extra_css=h.EQ_CSS_URL, title=f"{fam['name']}{' – ' + ops if ops else ''} | Kotibhaskar Industries",
                  description=f"{fam['desc']} {len(prods)} models with specifications. Manufactured in Satara, India — enquire for a quotation.",
                  canonical=url, body=body, jsonld=jsonld, og_image=h.SITE + prods[0]['images']['photo'],
                  wa_text=f'Hello, I am interested in {fam["name"]} ({h.SITE}{url}).')


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def build_product(h, data, fam, p):
    url = product_url(p)
    crumb_html, crumb_ld = h.crumbs([('Home', '/'), ('Material Handling Equipment', ROOT_URL), (e(fam['name']), family_url(fam)),
                                     (e(p['subtype']), f"{family_url(fam)}#{slug(p['subtype'])}"), (e(p['name']), None)])
    cap, lift = cap_text(p), lift_text(p)
    path = f"Material Handling Equipment > {fam['name']} > {p['subtype']}"
    nconf = config_count(p)
    facts = [f'<div class="fact"><div class="fact-num fact-text">{e(cap or "—")}</div><div class="fact-label">Load capacity</div></div>',
             f'<div class="fact"><div class="fact-num fact-text">{e(p["operation"])}</div><div class="fact-label">Operation</div></div>']
    if lift:
        facts.append(f'<div class="fact"><div class="fact-num fact-text">{e(lift)}</div><div class="fact-label">Lift height</div></div>')
    facts.append(f'<a class="fact fact-link" href="#specs"><div class="fact-num">{nconf}</div><div class="fact-label">{"Configuration" if nconf == 1 else "Configurations"} &darr;</div></a>')
    chips = [f'<li class="op">{e(p["operation"])}</li>']
    if p.get('capacities') and len(p['capacities']) > 1:
        chips.append(f'<li>Available capacities: {e(" / ".join(p["capacities"]))}</li>')
    if p.get('lifts') and len(p['lifts']) > 1:
        chips.append(f'<li>Lift heights: {e(" / ".join(p["lifts"]))}</li>')
    if p.get('spm'):
        chips.append('<li class="spm">SPM — built to order</li>')
    drawing = ''
    if p['images'].get('drawing'):
        drawing = f'''<figure class="t-photo eq-drawing">
      <a href="{p['images']['drawing']}" data-lightbox><img src="{p['images']['drawing']}" alt="{e(p['name'])} — technical drawing with dimensions" width="1100" height="1556" loading="lazy" decoding="async"></a>
      <figcaption>Technical drawing <span>Click to enlarge</span></figcaption>
    </figure>'''
    wheels = ''
    if p.get('wheels'):
        wheels = '<h2 class="sec-label">Wheel Options</h2><ul class="eq-wheels">' + ''.join(
            f'<li><a href="{WHEEL_LINKS[w][2]}"><b>{WHEEL_LINKS[w][0]}</b> {e(WHEEL_LINKS[w][1])}</a></li>' for w in p['wheels']) + '</ul>'
    spm = f'<p class="eq-spm">{e(SPM_NOTE)}</p>' if p.get('spm') else ''
    same = [q for q in data['products'] if q['family'] == p['family'] and q['slug'] != p['slug']]
    sibs = ''
    if same:
        sibs = f'<div class="wrap alt siblings-wrap"><h2 class="h2">Other {e(fam["name"])}</h2><div class="siblings">' + ''.join(
            f'<a class="sib" href="{product_url(q)}">{e(q["name"])}<small>{e(q["operation"])}</small></a>' for q in same) + '</div></div>'
    multi = nconf > 1
    body = f'''<header class="page-head t-head">
  {crumb_html}
  <div class="duty-badge">{e(fam['name'])} &middot; <b>{e(p['subtype'])}</b></div>
  <h1 class="page-title">{e(p['name'])}</h1>
  <p class="page-sub">{e(p['summary'])}</p>
  <ul class="eqf-chips eq-head-chips">{''.join(chips)}</ul>
  <div class="key-facts">{''.join(facts)}</div>
</header>

<div class="wrap t-main">
  <div class="t-layout eq-layout{' eq-side' if p.get('media_side') and p['images'].get('drawing') else ''}">
    <div class="eq-media">
      <figure class="t-photo">
        <a href="{p['images']['photo']}" data-lightbox><img src="{p['images']['photo']}" alt="{e(p['name'])} — product photograph" width="900" height="1273"></a>
        <figcaption>Product photo <span>Click to enlarge</span></figcaption>
      </figure>
      {drawing}
    </div>
    <div>
      <h2 class="sec-label">Construction &amp; Features</h2>
      {feats_html(p['text'])}
      {f'<p class="t-multi">Available in multiple configurations. Please refer to the <a href="#specs">specifications table below</a> for details.</p>' if multi else ''}
      {spm}
      {wheels}
      <dl class="t-origin"><div><dt>Brand</dt><dd>Kotibhaskar</dd></div><div><dt>Country of Origin</dt><dd>Made in India</dd></div></dl>
      <div class="action-box">
        <a class="btn-primary" href="{e(h.enquire_url(p['name'], None, path, url))}">&#9993; Enquire Now</a>
        <a class="btn-wa" href="{e(h.wa_url(f'Hello, I would like a quotation for: {p["name"]} ({h.SITE}{url})'))}" target="_blank" rel="noopener">{h.WA_ICON.replace('width="20" height="20"', 'width="18" height="18"')} WhatsApp Enquiry</a>
        <a class="btn-dark" href="{CATALOGUE}" target="_blank" rel="noopener">{h.DL_ICON} Equipment Catalogue (PDF)</a>
        <button type="button" class="btn-outline" data-print>&#128438; Print / Save as PDF</button>
        <p class="action-note">No prices are listed online &mdash; send an enquiry for a quotation.</p>
      </div>
    </div>
  </div>
</div>

<div class="wrap alt t-sizes" id="specs">
  <h2 class="h2">Technical Specifications <small>{nconf} {'configuration' if nconf == 1 else 'configurations'}</small></h2>
  {''.join(table_html(t) for t in p['tables'])}
  <p class="eq-spec-note">Specifications are subject to change without notice. Contact us to confirm the configuration for your application.</p>
</div>
{sibs}'''
    images = [h.SITE + p['images']['photo']] + ([h.SITE + p['images']['drawing']] if p['images'].get('drawing') else [])
    jsonld = {'@context': 'https://schema.org', '@graph': [crumb_ld, {
        '@type': 'Product', 'name': p['name'], 'url': h.SITE + url, 'image': images, 'description': p['summary'],
        'brand': {'@type': 'Brand', 'name': 'Kotibhaskar'}, 'manufacturer': {'@id': f'{h.SITE}/#organization'},
        'category': path, 'countryOfOrigin': 'IN'}]}
    title = f"{p['name']}{' – ' + cap if cap and cap not in p['name'] else ''} | Kotibhaskar Industries"
    desc = f"{p['summary']} {p['operation']} operation. Manufactured by Kotibhaskar Industries, Satara, India — enquire for a quotation."
    return h.page(extra_css=h.EQ_CSS_URL, title=title, description=desc, canonical=url, body=body, jsonld=jsonld,
                  og_image=h.SITE + p['images']['photo'], wa_text=f'Hello, I would like a quotation for: {p["name"]} ({h.SITE}{url})',
                  sheet=datasheet(h, fam, p, url, cap, lift))


def datasheet(h, fam, p, url, cap, lift):
    c = h.COMPANY
    letter = f'''<div class="ps-head">
    <img class="ps-logo" src="{c['logo']}" alt="KOTIBHASKAR">
    <div class="ps-company">
      <div class="ps-name">{e(c['name'])}</div>
      <div class="ps-tag">{e(c['tagline'])}</div>
      <div class="ps-contact">{e(c['address'])}<br>
        Tel: {' &middot; '.join(e(t) for t in c['phones'])}<br>
        Email: {' &middot; '.join(e(m) for m in c['emails'])} &nbsp;|&nbsp; Web: {e(c['website'])}</div>
    </div>
  </div>'''

    def foot(n):
        return f'''<div class="ps-foot">
    <div><b>{e(c['name'])}</b><br>{e(c['website'])}</div>
    <div>{e(c['phones'][0])} &nbsp;|&nbsp; {e(c['emails'][0])} &nbsp;|&nbsp; Page {n} of 2</div>
    <div class="ps-url">{'/<wbr>'.join(f'<span>{e(seg)}</span>' for seg in (c['website'] + url).split('/'))}</div>
  </div>'''
    imgs = f'<figure><div class="ps-img"><img src="{p["images"]["photo"]}" alt=""></div><figcaption>Product photo</figcaption></figure>'
    if p['images'].get('drawing'):
        imgs += f'<figure><div class="ps-img"><img src="{p["images"]["drawing"]}" alt=""></div><figcaption>Technical drawing</figcaption></figure>'
    extra = []
    if p.get('wheels'):
        extra.append('<b>Wheels:</b> ' + ' &middot; '.join(f'{WHEEL_LINKS[w][0]} ({e(WHEEL_LINKS[w][1].split(" — ")[0].lower())})' for w in p['wheels']))
    if p.get('spm'):
        extra.append(e(SPM_NOTE))
    extra.append('<b>Brand:</b> Kotibhaskar &nbsp;&middot;&nbsp; <b>Country of Origin:</b> Made in India')

    # ---- pagination: estimate row heights (mm) and split the spec tables across sheets if needed
    def row_mm(row, ncols):
        width = 140 / max(1, ncols - 1)                    # mm available per value column
        cpl = max(8, int(width * 2.3))                     # characters per line at 7.4 pt
        lines = max(sum(-(-len(part) // cpl) or 1 for part in v.split('\n')) for v in row[1:]) if len(row) > 1 else 1
        lines = max(lines, -(-len(row[0]) // 26))          # label column wraps too
        return 2.4 + 3.35 * lines
    PAGE1, PAGEN = 112, 205                                # usable table height on page 1 / later pages
    chunks, used, page_no = [[]], 0.0, 0
    for t in p['tables']:
        head_mm = 6.5 + (6 if t.get('title') else 0)
        part = dict(t, rows=[])
        for r in t['rows']:
            need = row_mm(r, len(t['head'])) + (head_mm if not part['rows'] else 0)
            budget = PAGE1 if page_no == 0 else PAGEN
            if used + need > budget and (part['rows'] or chunks[-1]):
                if part['rows']:
                    chunks[-1].append(part)
                chunks.append([])
                page_no += 1
                used = 0.0
                part = dict(t, rows=[], title=(t.get('title') or '') + ' (continued)' if t.get('title') else None)
                need = row_mm(r, len(t['head'])) + head_mm
            part['rows'].append(r)
            used += need
        if part['rows']:
            chunks[-1].append(part)
    feats_mm = sum(7 + 3.6 * sum(-(-len(x) // 55) for x in [it['head']] + it['lines']) for it in p['text']) / 2 + 8 * len(extra)
    feats_on_last = (PAGEN - used) > feats_mm + 12 and page_no > 0
    sheets = len(chunks) + (0 if feats_on_last else 1)

    def foot(n):
        return f'''<div class="ps-foot">
    <div><b>{e(c['name'])}</b><br>{e(c['website'])}</div>
    <div>{e(c['phones'][0])} &nbsp;|&nbsp; {e(c['emails'][0])} &nbsp;|&nbsp; Page {n} of {sheets}</div>
    <div class="ps-url">{'/<wbr>'.join(f'<span>{e(seg)}</span>' for seg in (c['website'] + url).split('/'))}</div>
  </div>'''
    band2 = f'<div class="ps-band"><span>Product Specification Sheet</span><span>{e(p["name"])}</span></div>'
    feats_block = (f'<div class="ps-sec">Construction &amp; Features</div>{feats_html(p["text"], cls="pst-feats eqs-feats")}'
                   + ''.join(f'<div class="pst-line">{x}</div>' for x in extra))
    note = '<div class="ps-note">Specifications subject to change without notice. Contact us for a quotation.</div>'
    out = [f'''<div class="print-sheet eq-sheet" aria-hidden="true">
  {letter}
  <div class="ps-band"><span>Product Specification Sheet</span><span>Material Handling Equipment &middot; {e(fam['name'])}</span></div>
  <div class="ps-title">
    <div>
      <div class="ps-cat">{e(fam['name'])} &middot; {e(p['subtype'])}</div>
      <div class="ps-h">{e(p['name'])}</div>
      <div class="pst-sub">{e(p['summary'])}</div>
    </div>
    <div class="ps-load"><span>Load Capacity</span><b>{e(cap or '—')}</b></div>
  </div>
  <div class="ps-imgs{' ps-imgs-1' if not p['images'].get('drawing') else ''}">{imgs}</div>
  <div class="ps-sec">Technical Specifications &middot; {e(p['operation'])}{f' &middot; Lift {e(lift)}' if lift else ''}</div>
  {''.join(table_html(t, cls='pst-table eqs-table') for t in chunks[0])}
  {note}
  {foot(1)}
</div>''']
    for i, chunk in enumerate(chunks[1:], start=2):
        last = i == len(chunks)
        out.append(f'''<div class="print-sheet eq-sheet" aria-hidden="true">
  {letter}
  {band2}
  <div class="ps-sec">Technical Specifications (continued)</div>
  {''.join(table_html(t, cls='pst-table eqs-table') for t in chunk)}
  {feats_block if last and feats_on_last else ''}
  {note}
  {foot(i)}
</div>''')
    if not feats_on_last:
        out.append(f'''<div class="print-sheet eq-sheet" aria-hidden="true">
  {letter}
  {band2}
  {feats_block}
  {note}
  {foot(sheets)}
</div>''')
    return '\n'.join(out)


# ---------------------------------------------------------------- entry point
def build(h):
    path = os.path.join(h.REPO, 'data', 'products', 'equipment', 'equipment.json')
    if not os.path.exists(path):
        return [], 0
    data = json.load(open(path, encoding='utf-8'))
    root = os.path.join(h.REPO, 'material-handling-equipment')
    shutil.rmtree(root, ignore_errors=True)
    urls, written = [ROOT_URL], []
    pth = os.path.join(root, 'index.html')
    h.write(pth, build_hub(h, data))
    written.append(pth)
    for fam in data['families']:
        pth = os.path.join(root, fam['id'], 'index.html')
        h.write(pth, build_family(h, data, fam))
        written.append(pth)
        urls.append(family_url(fam))
        for p in [q for q in data['products'] if q['family'] == fam['id']]:
            pth = os.path.join(root, fam['id'], p['slug'], 'index.html')
            h.write(pth, build_product(h, data, fam, p))
            written.append(pth)
            urls.append(product_url(p))
    h.check_public_output(written, forbid_puci=False)
    check_equipment(h, written)
    write_homepage_showcase(h, data)
    return urls, len(data['products'])


EQ_CODE_RX = re.compile(r'\b(ST|FC|DT|MT|DG|OP|SC|EST|EOP|EDT|EFC|EPT|GAN|RPT|ISH|ISM|GRC|RBC|PBC)\s?[.\-]?\s?\d{2}\s?[.\- ]\s?\d{2,3}\b|\bPT\.25\.')


def check_equipment(h, paths):
    """Extra privacy checks for equipment pages: model codes, bank details, 500 kg stackers."""
    problems = []
    for pth in paths:
        txt = open(pth, encoding='utf-8').read()
        for rx, label in ((EQ_CODE_RX, 'model code'), (re.compile(r'(?i)IFSC|account no|axis bank|quotation no'), 'bank/commercial')):
            m = rx.search(txt)
            if m:
                problems.append(f'{os.path.relpath(pth, h.REPO)}: {label} "{m.group(0)}"')
        if '/stackers/' in pth.replace('\\', '/') and re.search(r'(?<![0-9])500 kg', txt):
            problems.append(f'{os.path.relpath(pth, h.REPO)}: 500 kg on a stacker page')
    if problems:
        print('BUILD STOPPED - equipment check failed:')
        for pr in problems:
            print('  -', pr)
        raise SystemExit(1)


SHOWCASE_START = '<!-- EQUIPMENT-SHOWCASE:START (generated by tools/build_equipment.py) -->'
SHOWCASE_END = '<!-- EQUIPMENT-SHOWCASE:END -->'


def write_homepage_showcase(h, data):
    """Replace the homepage Material Handling Equipment grid with the family showcase."""
    idx = os.path.join(h.REPO, 'index.html')
    s = open(idx, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    block = (SHOWCASE_START + nl + f'<link rel="stylesheet" href="{h.EQ_CSS_URL}">' + nl + showcase(data).replace('\n', nl) + nl +
             f'<div class="eqf-all"><a href="{ROOT_URL}">View all {len(data["products"])} equipment products &rarr;</a></div>' + nl + SHOWCASE_END)
    if SHOWCASE_START in s:
        s = re.sub(re.escape(SHOWCASE_START) + r'.*?' + re.escape(SHOWCASE_END), lambda m: block, s, flags=re.S)
    else:
        m = re.search(r'(<div class="prod-grid-wrap active" id="grid-mhe">\r?\n)(\s*<div class="prod-grid">.*?</div>\r?\n)(  </div>)', s, flags=re.S)
        assert m, 'homepage MHE grid not found'
        s = s[:m.start(2)] + block + nl + s[m.start(3):]
    s = write_homepage_search(s, data, nl)
    open(idx, 'w', encoding='utf-8', newline='').write(s)


ROUTES_START = '/* EQUIPMENT-ROUTES:START (generated by tools/build_equipment.py) */'
ROUTES_END = '/* EQUIPMENT-ROUTES:END */'
# old homepage popup ids -> (first finder keyword, new target: family id or product slug)
OLD_IDS = {'hpt': ('pallet', 'pallet-trucks'), 'ept': ('electric pallet', 'electric-pallet-truck'), 'ms': ('stack', 'stackers'),
           'es': ('electric stacker', 'electric-stacker'), 'hfc': ('floor crane', 'floor-cranes'), 'efc': ('electric crane', 'electric-floor-crane'),
           'hdt': ('drum tilt', 'drum-lifters-tilters'), 'edt': ('electric drum tilt', 'electric-drum-lifter-tilter'),
           'mdg': ('drum grip', 'drum-grippers'), 'edg': (None, 'drum-grippers'), 'gantry': ('gantry', 'gantries'),
           'sl': ('scissor', 'scissor-lifts'), 'dl': ('dock leveller', 'electro-hydraulic-dock-leveller'), 'gl': ('goods lift', 'goods-lifts'),
           'grc': ('conveyor', 'gravity-roller-conveyor'), 'bc': ('belt conveyor', 'conveyors'), 'ish': ('shelf', 'industrial-shelving')}


def js(s):
    return str(s).replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')


def write_homepage_search(s, data, nl):
    """Point the old equipment popups, product finder and search at the new pages (accurate text from the data)."""
    fams = {f['id']: f for f in data['families']}
    prods = {p['slug']: p for p in data['products']}

    def target(key):
        if key in fams:
            f = fams[key]
            n = sum(1 for p in data['products'] if p['family'] == key)
            return family_url(f), f['name'], f"{f['desc']} {n} models."
        p = prods[key]
        return product_url(p), p['name'], p['summary']
    routes = {old: target(key)[0] for old, (_, key) in OLD_IDS.items()}
    routes.update({'eq_' + p['slug'].replace('-', '_'): product_url(p) for p in data['products']})
    routes.update({'eqf_' + f['id'].replace('-', '_'): family_url(f) for f in data['families']})
    sc_fix = {kw: dict(zip(('u', 'p', 'r'), target(key))) for _, (kw, key) in OLD_IDS.items() if kw}
    si = [{'n': f['name'], 'id': 'eqf_' + f['id'].replace('-', '_'), 't': f"{f['name']} {f['desc']}".lower()} for f in data['families']]
    si += [{'n': p['name'], 'id': 'eq_' + p['slug'].replace('-', '_'),
            't': f"{p['name']} {fams[p['family']]['name']} {p['subtype']} {p['operation']}".lower()} for p in data['products']]
    lines = [ROUTES_START,
             'Object.assign(PAGES,{' + ','.join(f"{k}:'{js(v)}'" for k, v in routes.items()) + '});',
             'var EQ_SC={' + ','.join(f"'{js(k)}':{{p:'{js(v['p'])}',r:'{js(v['r'])}'}}" for k, v in sc_fix.items()) + '};',
             "SC.forEach(function(s){var f=EQ_SC[s.k[0]];if(f){s.p=f.p;s.r=f.r;}});",
             'var EQ_OLD={' + ','.join(f'{k}:1' for k in OLD_IDS) + '};',
             'SI=SI.filter(function(s){return !EQ_OLD[s.id];}).concat([' + ','.join(
                 f"{{n:'{js(x['n'])}',id:'{x['id']}',t:'{js(x['t'])}'}}" for x in si) + ']);',
             ROUTES_END]
    block = nl.join(lines)
    if ROUTES_START in s:
        return re.sub(re.escape(ROUTES_START) + r'.*?' + re.escape(ROUTES_END), lambda m: block, s, flags=re.S)
    anchor = 'var HIDDEN={'
    assert s.count(anchor) == 1, 'homepage script anchor not found'
    return s.replace(anchor, block + nl + anchor, 1)
