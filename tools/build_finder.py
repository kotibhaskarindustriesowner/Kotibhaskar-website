"""Homepage Solution Finder data: one compact, public JSON file with the verified figures the
finder may compare against (assets/data/finder.json), built from the same product data as the pages.

Called from tools/build_site.py after all product pages are written. Every item carries only:
name, page URL, thumbnail, product type, operation, capacity unit and the documented
configurations as [capacity_kg, height_mm] pairs taken column-by-column from the specification
tables. Nothing is estimated: a product whose capacity or height is not documented gets no value,
and the finder then refuses to claim it meets a stated load or height.
"""
import hashlib
import json
import os
import re

KG = re.compile(r'(\d[\d,]*(?:\.\d+)?)\s*kg', re.I)
MM = re.compile(r'(\d[\d,]*(?:\.\d+)?)\s*mm', re.I)
M = re.compile(r'(\d+(?:\.\d+)?)\s*m\b')

# which specification row is the "lifting height" a customer means, per equipment family
HEIGHT_ROW = {
    'stackers': (r'^maximum (fork|cage|jib hook) height', 'lift height'),
    'pallet-trucks': (r'^maximum fork height', 'fork height'),
    'order-pickers': (r'^maximum cage height', 'cage height'),
    'drum-lifters-tilters': (r'^maximum drum height', 'drum lift height'),
    'drum-grippers': (r'^lift height', 'lift height'),
    'material-lifters-tilters': (r'^maximum pan height', 'pan lift height'),
    'scissor-lifts': (r'^maximum table height', 'max. table height'),
    'goods-lifts': (r'^lift$', 'lift'),
    'floor-cranes': (None, 'lift height'),      # product 'lifts' field (hook height)
    'gantries': (None, 'lift height'),
}
CAP_ROW = r'^(load )?(carrying )?capacity$|^load capacity$|^load carrying capacity$'
LIFTING = {'stackers', 'order-pickers', 'drum-lifters-tilters', 'drum-grippers', 'material-lifters-tilters',
           'floor-cranes', 'gantries', 'scissor-lifts', 'goods-lifts'}


def num(rx, s):
    m = rx.search(str(s))
    return float(m.group(1).replace(',', '')) if m else None


def eq_type(p):
    f, s = p['family'], p['slug']
    if f == 'stackers':
        return 'stacker-cage' if 'cage' in s else ('stacker-jib' if 'jib' in s else 'stacker')
    if f == 'scissor-lifts':
        return 'scissor-pit' if p['operation'] == 'Electro-Hydraulic' else 'scissor-mobile'
    if f == 'goods-lifts':
        return 'lifting-cage' if 'cage' in s else 'goods-lift'
    if f == 'pallet-trucks':
        return 'pallet-truck-highlift' if 'high-lift' in s else 'pallet-truck'
    return {'pallet-trucks': 'pallet-truck', 'order-pickers': 'order-picker', 'drum-lifters-tilters': 'drum-tilter',
            'drum-grippers': 'drum-gripper', 'material-lifters-tilters': 'material-tilter', 'floor-cranes': 'floor-crane',
            'gantries': 'gantry', 'dock-levellers': 'dock-leveller', 'industrial-shelving': 'shelving',
            'conveyors': 'conveyor'}[f]


def eq_configs(p):
    """[[kg, mm], ...] from the spec tables, one pair per table column; None where not documented."""
    hrx, _ = HEIGHT_ROW.get(p['family'], (None, None))
    lifts_mm = [round(float(x.split()[0]) * 1000) for x in (p.get('lifts') or [])]
    cfg = []
    for t in p['tables']:
        rows = t.get('rows') or []
        head = [str(x) for x in (t.get('head') or [])]
        ci = next((i for i, x in enumerate(head) if re.search(r'^capacity', x, re.I)), None)
        hi = next((i for i, x in enumerate(head) if re.search(r'^max\.? (table )?height', x, re.I)), None)
        if ci is not None:          # row-per-size table (mobile scissor lifts): one configuration per row
            for r in rows:
                k = num(re.compile(r'(\d[\d,]*)'), r[ci])
                hh = num(re.compile(r'(\d[\d,]*)'), r[hi]) if hi is not None else None
                if k:
                    cfg.append([k, hh])
            continue
        cap = next((r[1:] for r in rows if re.search(CAP_ROW, str(r[0]).strip(), re.I)), None)
        hgt = next((r[1:] for r in rows if hrx and re.search(hrx, str(r[0]).strip(), re.I)), None)
        if not cap:
            continue
        kgs = [num(KG, v) for v in cap]
        if hgt:
            hs = [num(MM, re.sub(r'^H\d?\s*-\s*', '', str(v))) for v in hgt]
            if len(hs) == 1:
                hs = hs * len(kgs)
            if len(kgs) == 1:
                kgs = kgs * len(hs)
            if len(hs) != len(kgs):
                hs = [None] * len(kgs)
        elif lifts_mm and p['family'] in ('floor-cranes', 'gantries') and len(lifts_mm) == 1:
            hs = lifts_mm * len(kgs)
        else:
            hs = [None] * len(kgs)
        cfg += [[k, h] for k, h in zip(kgs, hs) if k]
    if not cfg and p.get('capacities'):          # documented on the product but not in a table row
        hs = lifts_mm or [None]
        cfg = [[num(KG, c), h] for c in p['capacities'] for h in hs]
    # drop duplicates, keep order
    out = []
    for c in cfg:
        c = [int(c[0]) if c[0] else None, int(c[1]) if c[1] else None]
        if c not in out:
            out.append(c)
    return out


def build(h):
    R = h.REPO
    load = lambda *a: json.load(open(os.path.join(R, 'data', 'products', *a), encoding='utf-8'))
    items = []

    eq = load('equipment', 'equipment.json')
    for p in eq['products']:
        unit = {'industrial-shelving': 'per-shelf', 'conveyors': 'per-metre'}.get(p['family'], 'total')
        cfg = eq_configs(p)
        cap_text = None
        if unit != 'total':        # shelving "per shelf" / conveyor "per metre": kept as text only, never compared
            cfg = []
            row = next((r for t in p['tables'] for r in (t.get('rows') or []) if re.search(r'capacity', str(r[0]), re.I)), None)
            cap_text = ' / '.join(dict.fromkeys(str(v) for v in row[1:])) if row else None
        items.append({'n': p['name'], 'u': f"/material-handling-equipment/{p['family']}/{p['slug']}/",
                      'img': p['images'].get('thumb') or p['images'].get('photo'), 'c': 'equipment', 't': eq_type(p),
                      'op': p['operation'], 'unit': unit, 'cfg': cfg,
                      'hl': HEIGHT_ROW.get(p['family'], (None, None))[1], 'lift': p['family'] in LIFTING,
                      'spm': bool(p.get('spm')), **({'ct': cap_text} if cap_text else {})})

    tr =load('trolleys', 'trolleys.json')
    for p in tr['products']:
        kgs = []
        for v in p['variants']:
            k = num(KG, v.get('Load Capacity', ''))
            if k and [int(k), None] not in kgs:
                kgs.append([int(k), None])
        items.append({'n': p['name'], 'u': f"{tr['url']}{p['slug']}/", 'img': p['images'].get('thumb') or p['images'].get('photo'),
                      'c': 'trolley', 't': 'trolley-' + p['slug'], 'g': p['group'], 'op': 'Manual (push)', 'unit': 'total',
                      'cfg': kgs, 'hl': None, 'lift': False, 'spm': False})

    for mat in ('uhmw', 'puci', 'ci'):
        w = load('wheels', f'{mat}.json')
        loads = sorted(int(p['load_per_caster_kg']) for p in w['products'])
        items.append({'n': w['name'], 'u': w['url'], 'img': w['products'][0]['images'].get('thumb'), 'c': 'wheel',
                      't': 'wheel-' + mat, 'op': '', 'unit': 'per-caster', 'cfg': [[loads[0], None], [loads[-1], None]],
                      'hl': None, 'lift': False, 'spm': False, 'range': True})
        for p in w['products']:
            items.append({'n': p['name'], 'u': f"{w['url']}{p['slug']}/", 'img': p['images'].get('thumb'), 'c': 'wheel',
                          't': 'wheelsize-' + mat, 'op': '', 'unit': 'per-caster', 'cfg': [[int(p['load_per_caster_kg']), None]],
                          'hl': None, 'lift': False, 'spm': False})
    pt = load('pallet-truck', 'pallet-truck.json')
    ptl = sorted(int(p['load_kg']) for p in pt['products'])
    items.append({'n': pt['name'], 'u': pt['url'], 'img': None, 'c': 'wheel', 't': 'wheel-pallet-truck', 'op': '',
                  'unit': 'per-caster', 'cfg': [[ptl[0], None], [ptl[-1], None]], 'hl': None, 'lift': False, 'spm': False, 'range': True})
    ms = load('ms-track', 'ms-track.json')
    msl = sorted(int(r['load_kg']) for r in ms['rows'])
    items.append({'n': ms['name'], 'u': ms['url'], 'img': None, 'c': 'wheel', 't': 'wheel-ms-track', 'op': '',
                  'unit': 'per-caster', 'cfg': [[msl[0], None], [msl[-1], None]], 'hl': None, 'lift': False, 'spm': False, 'range': True})

    # every URL must be a page that exists
    for it in items:
        if not os.path.isfile(os.path.join(R, it['u'].strip('/').replace('/', os.sep), 'index.html')):
            raise SystemExit('finder: page not found for ' + it['u'])
        if it['img'] and not os.path.isfile(os.path.join(R, it['img'].lstrip('/').replace('/', os.sep))):
            it['img'] = None

    out = json.dumps({'items': items}, ensure_ascii=False, separators=(',', ':'))
    if re.search(r'₹|\bgst\b|discount|ifsc|price', out, re.I):
        raise SystemExit('finder.json would contain commercial data')
    os.makedirs(os.path.join(R, 'assets', 'data'), exist_ok=True)
    pth = os.path.join(R, 'assets', 'data', 'finder.json')
    open(pth, 'w', encoding='utf-8', newline='\n').write(out + '\n')

    # homepage script tag, with content hashes so browsers never mix an old script with new data
    data_v = hashlib.sha256(out.encode()).hexdigest()[:10]
    js_v = h.asset_version('assets/js/finder.js')
    idx = os.path.join(R, 'index.html')
    s = open(idx, encoding='utf-8', newline='').read()
    tag = (f'<script src="/assets/js/finder.js?v={js_v}" data-finder-data="/assets/data/finder.json?v={data_v}" defer></script>')
    s2 = re.sub(r'<!-- FINDER-SCRIPT:START -->.*?<!-- FINDER-SCRIPT:END -->',
                lambda m: f'<!-- FINDER-SCRIPT:START -->{tag}<!-- FINDER-SCRIPT:END -->', s, flags=re.S)
    if s2 == s and tag not in s:
        raise SystemExit('finder: FINDER-SCRIPT markers missing from index.html')
    open(idx, 'w', encoding='utf-8', newline='').write(s2)
    return items
