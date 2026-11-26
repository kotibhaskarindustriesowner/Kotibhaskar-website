"""Build data/products/equipment/equipment.json from the private equipment price lists.

    python tools/import_equipment.py

Sources: product-sources/10 Equiptments/ (git-ignored). Each product below names its
source folder(s) and the workbook pages that hold its specification tables and
descriptive text. Only specification tables and technical text are read:
price columns, price rows, optional-extra prices, discounts, commercial terms, bank
details, erection/commissioning scope and model codes are never copied.
Owner decisions applied (Nov 2026): no 500 kg stackers; one page per stacker type
with 1000 kg and 1500 kg together; cage and jib-hook stackers 2.5 m and 3.1 m only;
dock leveller 415 V as stated; obvious spelling errors corrected, values never changed.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_read import read_rows, pages, col_index  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'product-sources', '10 Equiptments')
OUT = os.path.join(REPO, 'data', 'products', 'equipment', 'equipment.json')
IMG = '/assets/products/equipment/'

# ---------------------------------------------------------------- source helpers
def folder(*prefixes):
    """Find a source folder by its numeric prefixes, e.g. folder('20', '10', '70')."""
    d = SRC
    for p in prefixes:
        hits = [x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)) and x.split(' ')[0] == p]
        assert len(hits) == 1, (d, p, hits)
        d = os.path.join(d, hits[0])
    return d


_WB = {}


def workbook(code):
    if code not in _WB:
        for r, _, files in os.walk(SRC):
            for f in files:
                if f.startswith(code + ' ') and f.endswith('.xlsx'):
                    _WB[code] = pages(read_rows(os.path.join(r, f)))
                    break
            if code in _WB:
                break
    return _WB[code]


def rel(path):
    return os.path.relpath(path, REPO).replace('\\', '/')


# Obvious spelling / wording fixes (values are never touched)
FIXES = [
    (r'\bCarring\b', 'Carrying'), (r'\bcopled\b', 'coupled'), (r'\bPrecised controlled\b', 'Precisely controlled'),
    (r'\bprecised controlled\b', 'precisely controlled'), (r'\bAsthetic\b', 'Aesthetic'), (r'\bdisengauges\b', 'disengages'),
    (r'\bSutiable\b', 'Suitable'), (r'\bChequred\b', 'Chequered'), (r'\bchequred\b', 'chequered'), (r'\bStationery Type\b', 'Stationary Type'),
    (r'\bwear houses\b', 'warehouses'), (r'\bpressuer relife\b', 'pressure relief'), (r'\bControler\b', 'Controller'),
    (r'\babsorbtion\b', 'absorption'), (r'\b[Pp]annel\b', 'panel'), (r'\brainforcement\b', 'reinforcement'),
    (r'\bweighting scale\b', 'weighing scale'), (r'movement f pallet', 'movement of pallet'), (r'\bstainer\b', 'strainer'),
    (r'\bstiffners\b', 'stiffeners'), (r'\btechniq(ue)?\b|\btechnic\b', 'technique'), (r'\bby passes\b', 'bypasses'),
    (r'\bchecked plate\b', 'chequered plate'), (r'\bany desire (heights?)\b', r'any desired \1'), (r'\.\.', '.'),
    (r'\bheave duty\b', 'heavy duty'), (r'\bdespatch\b', 'dispatch'),(r'\bSwiveling\b', 'Swivelling'), (r'\bswiveling\b', 'swivelling'),
    (r'\bLeveler\b', 'Leveller'), (r'\bleveler\b', 'leveller'), (r'\bPhalka Size\b', 'Hinged Plate Size'),
    (r'\bsolenoid valve\b', 'solenoid valve'), (r'\bBattery Supply\b', 'Battery Supply'), (r'\bsheet bended\b', 'sheet bent'),
    (r'\bbended\b', 'bent'), (r'\bcarring\b', 'carrying'), (r'\bdesire heights\b', 'desired heights'),
    (r'\bstabilizers\b', 'stabilisers'), (r'\bdeclamps\b', 'unclamps'), (r'\bwith in built\b', 'with built-in'),
    (r'\bun loading\b', 'unloading'), (r'\bPlain,\b', 'plane,'), (r'\bone Plain\b', 'one plane'),
    (r'\bsuch as in stores\b', 'such as in stores'), (r'\bheights which reduces\b', 'heights, which reduces'),
    (r'\bMaximum Cage Height H1\b', 'Maximum Drum Height H1'), (r'\bMinimum Cage Height H2\b', 'Minimum Drum Height H2'),
]
DRUM_TILTER_LABEL_FIX = True   # electric drum tilter only (owner approved): "Cage Height" -> "Drum Height"


def fix(s, drum=False):
    for a, b in FIXES:
        if 'Cage Height' in a and not drum:
            continue
        s = re.sub(a, b, s)
    s = re.sub(r'\s*Model - [A-Z0-9 ]+$', '', s)           # model codes in text
    s = s.replace(' @ ', ' approx. ').replace('@ ', 'approx. ')
    s = re.sub(r'"\s*([A-Za-z][A-Za-z ]*?)\s*"', r'\1', s)    # '" ZF " make' -> 'ZF make'
    s = re.sub(r'(\d) ?kw\b', r'\1 kW', s)
    s = re.sub(r'\bstationery\b', 'stationary', s)
    s = re.sub(r'\s*-\s*$', '', s)                           # trailing ' -' on headings
    s = re.sub(r'\s+([,.)])', r'\1', s).replace('( ', '(')
    return re.sub(r'[ \t]{2,}', ' ', s).strip()


def bad(text):
    return re.search(r'(?i)\bRs\.?\s?\d|price|discount|\bgst\b|quotation|\bin your scope\b|ESI & PF', text)


def cells_sorted(c):
    return sorted(c.items(), key=lambda kv: col_index(kv[0]))


NUM = re.compile(r'^\d{1,2}$')
CODE = re.compile(r'^[A-Z]{2,4}[ .\-]*\d')


# ---------------------------------------------------------------- table readers
def grids(page):
    """'Model' header followed by value columns (stackers, tilters, electric, dock, shelving, conveyors)."""
    rows, out, i = page['rows'], [], 0
    while i < len(rows):
        _, c = rows[i]
        lab = 'A' if c.get('A') == 'Model' else ('C' if c.get('A') == 'No' and c.get('C') == 'Model' else None)
        others = [(k, v) for k, v in cells_sorted(c) if lab and col_index(k) > col_index(lab)]
        if not lab or not others or others[0][1] in ('Description', 'Capacity', 'Table Size'):
            i += 1
            continue
        vcols = [k for k, _ in others]
        trows, prefix, j = [], None, i + 1
        while j < len(rows):
            _, d = rows[j]
            vals = [d.get(k, '') for k in vcols]
            label = d.get(lab, '')
            if lab == 'C' and NUM.match(d.get('A', '')):
                prefix = None
            if label.startswith('www.'):
                break                                   # page footer
            if any(vals):
                if not bad(label + ' ' + ' '.join(vals)):
                    trows.append([(prefix + ' – ' + label) if prefix else label] + vals)
                j += 1
                continue
            nxt = rows[j + 1][1] if j + 1 < len(rows) else {}
            if label and any(nxt.get(k) for k in vcols) and not NUM.match(nxt.get('A', '')):
                prefix = label
                j += 1
                continue
            if label and lab == 'C' and not d.get('A') and trows:
                trows[-1][0] += ' ' + label
                j += 1
                continue
            break
        out.append({'codes': [v for _, v in others], 'rows': trows})
        i = j
    return out


def kv(page):
    """Label | value list (manual pallet trucks)."""
    rows = page['rows']
    start = next(i for i, (_, c) in enumerate(rows) if c.get('A') == 'Capacity' and len(c) >= 2)
    vcol = cells_sorted(rows[start][1])[1][0]
    out = []
    for _, c in rows[start:]:
        if not c.get('A') or not c.get(vcol):
            break
        out.append([c['A'], c[vcol]])
    return out


def nkv(pgs):
    """Numbered spec list across pages: '1 | Label | value' (+ continuation lines)."""
    out, vcol, stop = [], None, False
    for page in pgs:
        for _, c in page['rows']:
            a = c.get('A', '')
            if re.match(r'^\d\d / \d\d / \d{4}$|^www\.', a):
                continue                                  # page date / footer between continued items
            if a and not NUM.match(a) and out:
                stop = True
                break
            other = [v for k, v in cells_sorted(c) if col_index(k) > col_index('C')]
            if NUM.match(a) and c.get('C'):
                if not other:
                    if out:
                        stop = True
                        break
                    continue
                out.append([c['C'], [other[0]]])
            elif not a and out:
                if c.get('C'):
                    out[-1][0] += ' ' + c['C']
                if other:
                    out[-1][1].append(other[0])
        if stop:
            break
    rows = [[lab, '\n'.join(merge_lines(vals))] for lab, vals in out]
    return [r for r in rows if not bad(' '.join(r))]


def mlist(page, cols):
    """Model rows with named columns (mobile scissor lifts, gantries, floor cranes). Model code dropped."""
    rows = page['rows']
    hi = next(i for i, (_, c) in enumerate(rows) if c.get('A') == 'Model')
    hdr = {v: k for k, v in rows[hi][1].items()}
    units = rows[hi + 1][1] if hi + 1 < len(rows) and 'A' not in rows[hi + 1][1] else {}
    keys = [hdr[cn] for cn in cols]
    head = [cn + (f' ({units[k]})' if units.get(k) else '') for cn, k in zip(cols, keys)]
    body = [[c.get(k, '') for k in keys] for _, c in rows[hi + 1:] if CODE.match(c.get('A', ''))]
    return head, body


def items(page, notes=False):
    """Descriptive text: numbered / lettered / '*' items with their continuation lines."""
    out, cur = [], None
    for _, c in page['rows']:
        cs = cells_sorted(c)
        a = c.get('A', '')
        texts = [v for k, v in cs if k != 'A']
        if a and (NUM.match(a) or a in ('*', 'A', 'B', 'C', 'D', 'E', 'F')) and len(texts) == 1:
            cur = {'head': texts[0], 'lines': [], 'mark': a}
            out.append(cur)
        elif not a and len(texts) == 1 and cur is not None:
            cur['lines'].append(texts[0])
        elif a and len(cs) == 1 and notes:
            out.append({'head': a, 'lines': [], 'note': True, 'mark': ''})
            cur = None
        else:
            cur = None
    return out


SKIP_HEAD = re.compile(r'(?i)KOTIBHASKAR " Make|available with various types of wheels|available in various|'
                       r'^optional extra|erection|commissioning|^add for accessories|non standard|load carr|'
                       r'lift height$|available in,$|^\( |^hydraulic pallet trucks? - capacity|'
                       r'^roll lifting hydraulic pallet truck - capacity|^high lift scissor pallet truck - capacity|'
                       r'^[0-9.]+ (counter balanced|hydraulic) floor crane|are available in various sizes as|'
                       r'^Manual Type$|^Semi Electric (AC|DC) \d+ Volts|load trials|without hydraulic oil|^steel content|'
                       r'^branded material|^maintenance access|other fabricators|in other lifts|\bcost of\b')
SKIP_LINE = re.compile(r'(?i)www\.|page -|^\d\d / \d\d / \d{4}|in other lifts|other commercial manufacturers|other fabricators')
GROUP_RENAME = {'Star Features': 'Design Features'}
SKIP_GROUP = re.compile(r'(?i)erection|commissioning|^optional extra|^add for accessories|non standard')


def text(code, idxs, drop_head=(), drop_line=(), notes=False, drum=False, keep=None):
    """Feature text as [{'head', 'lines'}]. Lettered / short headings without text of their own
    ('Safety Features', 'Applications', ...) become groups that collect the items under them."""
    out, group, skipping = [], None, False
    for i in idxs:
        for it in items(workbook(code)[i], notes):
            head = it['head']
            excluded = bool(SKIP_HEAD.search(head) or bad(head) or any(re.search(p, head) for p in drop_head)
                            or (keep and not re.search(keep, head)))
            lines = [ln for ln in it['lines'] if not SKIP_LINE.search(ln) and not bad(ln) and not any(re.search(p, ln) for p in drop_line)]
            is_group = (not it['lines'] and not it.get('note') and
                        (it['mark'] in ('A', 'B', 'C', 'D', 'E', 'F') or head.endswith(':') or (len(head) < 40 and not head.endswith('.'))))
            if is_group:
                # only commercial / scope sections hide the items listed under them;
                # other excluded headings (e.g. the '"KOTIBHASKAR" Make ...' page title) are just dropped
                skipping, group = bool(SKIP_GROUP.search(head)), None
                if not excluded:
                    h = fix(head, drum).rstrip(' :')
                    group = {'head': GROUP_RENAME.get(h, h), 'lines': []}
                    out.append(group)
                continue
            if it['mark'] in ('A', 'B', 'C', 'D', 'E', 'F'):
                skipping, group = False, None          # a lettered item with its own text ends the group
            if excluded or skipping:
                continue
            if it['lines'] and not lines:
                continue                                   # heading whose content was all removed
            if it.get('note') and (SKIP_LINE.search(head) or re.search(r'(?i)UHMW Wheels with sealed|^\( BB|^model$|load capacity - uniformly', head)):
                continue
            head = fix(head, drum)
            lines = merge_lines([fix(ln, drum) for ln in lines])
            if lines and re.match(r"^[a-z&(]|^i\.e\.", lines[0]) and not re.match(r'^[a-e]\)', lines[0]):
                head, lines = head + ' ' + lines[0], lines[1:]          # sentence wrapped onto the next row
            elif lines and re.search(r'(&|,|\b(and|of|with|for))$', head):
                head, lines = head + ' ' + lines[0], lines[1:]
            if it.get('note') and out and re.match(r'^[a-z&]', head):
                out[-1]['head'] += ' ' + head                            # note continued on the next row
                continue
            if group is not None and not lines:
                group['lines'].append(head)
                continue
            group = None
            if any(e['head'] == head for e in out):
                continue                                   # same item repeated on the operation-specific page
            out.append({'head': head, 'lines': lines})
    return [e for e in out if e['lines'] or not (len(e['head']) < 40 and not e['head'].endswith('.'))]


NEW_LINE = re.compile(r'^([a-e]\)|Up |Down |UP |Pushing|Drum Rotation|Pan Rotation|Boom |To & Fro|For \d|Lifting & Lowering|'
                      r'Dia \d|\d\. |Input|\*)')


def merge_lines(lines):
    """Rejoin lines that the workbook wrapped across rows; keep real list items separate."""
    out = []
    for ln in lines:
        unfinished = out and re.search(r'(,|&|\b(with|and|of|to|the|for|in|by|at|from|is|are|a))$', out[-1])
        if out and not NEW_LINE.match(ln) and (re.match(r'^[a-z&(,]', ln) or unfinished):
            out[-1] = out[-1] + ' ' + ln
        else:
            out.append(ln)
    return [o.rstrip(' ,') for o in out]


# ---------------------------------------------------------------- table builders
def value_row(rows, rx):
    for r in rows:
        if re.search(rx, r[0], re.I):
            return r[1:]
    return None


def mm_unit(label, v):
    return f'{v} mm' if re.fullmatch(r'\d{3,4}', v) and re.search(r'(?i)height|H3|H4', label) else v


def grid_table(code, sel, hdr='{cap} · {lift}', title=None, lift_rx=r'^(Maximum (Fork|Cage|Jib Hook|Drum|Pan) Height|Lift Height|Maximum Hook Height at E)',
               drum=False, keep_cols=None):
    """Merge one or more grids (e.g. 1000 kg + 1500 kg pages) into a single column-per-configuration table."""
    cols, labels, data = [], [], {}
    for page_i, grid_i in sel:
        g = grids(workbook(code)[page_i])[grid_i]
        rows = [[fix(r[0], drum)] + r[1:] for r in g['rows']]
        cap = value_row(rows, r'^(Load (Carrying )?Capacity|Capacity)') or [''] * len(g['codes'])
        lift = value_row(rows, lift_rx) or [''] * len(g['codes'])
        width = value_row(rows, r'^Width over forks') or [''] * len(g['codes'])
        tail = [c.split(' - ')[-1] for c in g['codes']]
        start = len(cols)
        for k in range(len(g['codes'])):
            if keep_cols and k not in keep_cols:
                continue
            extra = {name: (value_row(rows, rx) or [''] * len(g['codes']))[k] for name, rx in
                     (('length', r'^Length of Shelf'), ('depth', r'^Depth of Shelf'), ('sheet', r'^Sheet Thickness'))}
            cols.append(hdr.format(cap=cap[k], lift=lift[k], width=width[k], tail=tail[k], **extra).strip(' ·'))
        for r in rows:
            if r[0] not in labels:
                labels.append(r[0])
            vals = [v for k, v in enumerate(r[1:]) if not keep_cols or k in keep_cols]
            data.setdefault(r[0], {}).update({start + k: fix(mm_unit(r[0], v), drum) for k, v in enumerate(vals)})
    body = [[lab] + [data[lab].get(k, '—') for k in range(len(cols))] for lab in labels]
    return {'title': title, 'head': ['Specification'] + cols, 'rows': body}


def electric_stacker_table():
    """The workbook's adjustable-fork grids list only the row that differs (width over forks);
    show it as an extra row under the standard-fork table instead of a near-empty table."""
    t = grid_table('315', [(0, 0), (1, 0)])
    adj = []
    for pi in (0, 1):
        g = grids(workbook('315')[pi])[1]
        row = next(r for r in g['rows'] if re.search(r'(?i)width over forks', r[0]))
        adj += row[1:]
    t['rows'].append(['Width over Forks – Adjustable-Fork Version'] + adj)
    return t


def crane_table(code, page_idxs, title=None):
    """Hydraulic floor cranes: capacity, lift, wheels, safe load and boom from each capacity page."""
    cols, rows = [], {}
    order = ['Load Capacity', 'Lift Height', 'Maximum Safe Load at Maximum Height', 'Telescopic Boom', 'Wheels (UHMW, standard)']
    for pi in page_idxs:
        pg = workbook(code)[pi]
        head, body = mlist(pg, ['Capacity', 'Lift'])
        cap, lift = body[0]
        cols.append(cap)
        lines = [ln for it in items(pg) for ln in [it['head']] + it['lines']]
        alltxt = ' '.join(lines)
        safe = re.search(r'maximum safe load capacity (?:of \d+ kg floor crane )?is @ ?(\d+ kg) at maximum height', alltxt)
        boom = re.search(r'telescopic boom from (\d+ to \d+ mm) at (\d+ mm) pitch', alltxt)
        wheel = next((ln for ln in lines if re.match(r'^Dia \d+', ln)), '')
        for k, v in zip(order, [cap, lift.replace(', @ ', ' (').replace(' ft', ' ft)'), safe and f'approx. {safe.group(1)}',
                                (boom and f'{boom.group(1)}, adjustable in {boom.group(2)} steps with locking pin'), wheel.rstrip('.')]):
            rows.setdefault(k, []).append(v or '—')
    return {'title': title, 'head': ['Specification'] + cols, 'rows': [[k] + rows[k] for k in order if any(v != '—' for v in rows[k])]}


def kv_table(code, page_i, title=None):
    return {'title': title, 'head': ['Specification', 'Value'], 'rows': [[fix(a), fix(b)] for a, b in kv(workbook(code)[page_i])]}


def nkv_table(code, page_idxs, title=None):
    rows = [[fix(a), fix(b)] for a, b in nkv([workbook(code)[i] for i in page_idxs])]
    return {'title': title, 'head': ['Specification', 'Value'], 'rows': rows}


def mlist_table(code, page_i, cols, title=None, rename=None):
    head, body = mlist(workbook(code)[page_i], cols)
    if rename:
        head = [rename.get(h, h) for h in head]
    return {'title': title, 'head': head, 'rows': body}


# ---------------------------------------------------------------- catalogue structure
FAMILIES = [
    {'id': 'pallet-trucks', 'name': 'Pallet Trucks', 'layout': 'full',
     'desc': 'Hand hydraulic, roll lifting, high lift scissor, fully electric and special-purpose pallet trucks for moving loaded pallets on the shop floor and in warehouses.'},
    {'id': 'stackers', 'name': 'Stackers', 'layout': 'full',
     'desc': 'Manual, semi-electric AC, semi-electric DC and fully electric stackers in 1000 kg and 1500 kg capacities, with standard or adjustable forks, cage and jib-hook versions.'},
    {'id': 'order-pickers', 'name': 'Order Pickers', 'layout': 'half',
     'desc': 'Semi-electric AC, semi-electric DC and fully electric order pickers with an operator cage for picking from stores and warehouse racks.'},
    {'id': 'drum-lifters-tilters', 'name': 'Drum Lifters & Tilters', 'layout': 'half',
     'desc': 'Lift, move and rotate standard 220 litre metal drums through 360° — manual, semi-electric AC, semi-electric DC and fully electric.'},
    {'id': 'material-lifters-tilters', 'name': 'Material Lifters & Tilters', 'layout': 'half',
     'desc': 'Lift and tilt a 600 × 600 × 600 mm pan to pour material into hoppers and vessels — manual, semi-electric AC and semi-electric DC.'},
    {'id': 'drum-grippers', 'name': 'Drum Lifters with Auto Gripper', 'layout': 'half',
     'desc': 'Clamp and release drums automatically, without hand contact, for loading, stacking and weighing — manual, semi-electric AC and semi-electric DC.'},
    {'id': 'floor-cranes', 'name': 'Floor Cranes', 'layout': 'full',
     'desc': 'Hydraulic floor cranes and counterbalanced floor cranes with fixed or swivelling boom — manual, semi-electric AC, semi-electric DC and fully electric.'},
    {'id': 'scissor-lifts', 'name': 'Scissor Lifts', 'layout': 'full',
     'desc': 'Mobile single and double scissor lift tables, 2000 kg electro-hydraulic pit-mounted platforms and special-purpose scissor lifts.'},
    {'id': 'gantries', 'name': 'Gantries', 'layout': 'half',
     'desc': 'Mobile gantries on swivel castors in 500, 1000 and 2000 kg capacities, with manual chain pulley block or electric hoist.'},
    {'id': 'dock-levellers', 'name': 'Dock Levellers', 'layout': 'half',
     'desc': 'Electro-hydraulic dock levellers in 5000 kg and 9000 kg capacities, bridging the gap between the dispatch floor and the vehicle.'},
    {'id': 'goods-lifts', 'name': 'Goods Lifts & Lifting Cages', 'layout': 'full',
     'desc': 'Two-channel and four-channel hydraulic goods lifts and lifting cages for moving material between floors.'},
    {'id': 'industrial-shelving', 'name': 'Industrial Shelving', 'layout': 'half',
     'desc': 'Heavy duty pallet shelving and medium duty adjustable shelving for stores and industrial storage.'},
    {'id': 'conveyors', 'name': 'Conveyors', 'layout': 'half',
     'desc': 'Mobile gravity roller, rubber belt and PVC belt conveyors in straight and inclined versions.'},
]
# display order set by the owner (26 Nov 2026); the homepage grid rows are defined in tools/build_equipment.py
FAMILY_ORDER = ['pallet-trucks', 'stackers', 'floor-cranes', 'scissor-lifts', 'drum-lifters-tilters', 'drum-grippers',
                'goods-lifts', 'material-lifters-tilters', 'gantries', 'order-pickers', 'dock-levellers',
                'industrial-shelving', 'conveyors']
FAMILIES.sort(key=lambda f: FAMILY_ORDER.index(f['id']))

OPS = {'M': 'Manual', 'AC': 'Semi-Electric AC', 'DC': 'Semi-Electric DC', 'E': 'Fully Electric', 'EH': 'Electro-Hydraulic'}
P = []


def add(slug, name, family, subtype, op, folders, tables, txt, summary, **kw):
    seen, uniq = set(), []
    for t in txt:                       # text gathered from two pages: keep the first of each heading
        key = re.sub(r'\W+', '', t['head'].lower())
        if key not in seen:
            seen.add(key)
            uniq.append(t)
    txt = uniq
    P.append(dict(slug=slug, name=name, family=family, subtype=subtype, operation=OPS[op], folders=folders,
                  tables=tables, text=txt, summary=summary, **kw))


NO500 = (r'\b500 kg\b',)
UHMW_OPTS = ['uhmw', 'puci', 'ci']

# ---------------- Pallet trucks
add('hydraulic-pallet-truck-550', 'Hydraulic Pallet Truck – 550 mm', 'pallet-trucks', 'Hydraulic Pallet Trucks', 'M', [('10', '10')],
    [kv_table('010', 1)], text('010', [0]),
    'Hand hydraulic pallet truck with 550 mm width over forks and 1220 mm fork length; load capacity 2500 kg.', wheels=UHMW_OPTS)
add('hydraulic-pallet-truck-685', 'Hydraulic Pallet Truck – 685 mm', 'pallet-trucks', 'Hydraulic Pallet Trucks', 'M', [('10', '20')],
    [kv_table('010', 2)], text('010', [0]),
    'Hand hydraulic pallet truck with 685 mm width over forks and 1220 mm fork length; load capacity 2500 kg.', wheels=UHMW_OPTS)
add('roll-lifting-pallet-truck', 'Roll Lifting Hydraulic Pallet Truck', 'pallet-trucks', 'Hydraulic Pallet Trucks', 'M', [('10', '40')],
    [kv_table('015', 1)], text('015', [0]),
    'Hydraulic pallet truck with taper forks for paper rolls of 700 to 1200 mm diameter and up to 1200 mm length; load capacity 1000 kg.', wheels=UHMW_OPTS)
add('high-lift-scissor-pallet-truck', 'High Lift Scissor Pallet Truck', 'pallet-trucks', 'Hydraulic Pallet Trucks', 'M', [('10', '50')],
    [kv_table('020', 1)], text('020', [0]),
    'Hand pallet truck with scissor lift that raises the pallet to 800 mm working height; load capacity 1000 kg, 550 mm width over forks.', wheels=UHMW_OPTS)
add('electric-pallet-truck', 'Electric Pallet Truck', 'pallet-trucks', 'Electric Pallet Trucks', 'E', [('10', '60')],
    [grid_table('300', [(0, 0)], hdr='{width} width over forks')], text('300', [1]),
    'Fully electric pallet truck with AC drive and folding stand-on platform, 24 V battery operated; 2500 kg capacity with 550 mm or 685 mm width over forks.')
add('hydraulic-pallet-truck-spm', 'Hydraulic Pallet Truck – SPM', 'pallet-trucks', 'Special Purpose Pallet Trucks (SPM)', 'M', [('10', '30')],
    [kv_table('011', 1)], text('011', [0]),
    'Special-purpose hydraulic pallet truck with 2000 mm long forks and 800 mm width over forks; load capacity 2500 kg.',
    wheels=UHMW_OPTS, spm=True)

# ---------------- Stackers
ST_LIFT = ['1.6 m', '2.5 m', '3.1 m']
for op, intro in (('M', 0), ('AC', 4), ('DC', 8)):
    opn = OPS[op]
    f550 = {'M': ('10', '10'), 'AC': ('20', '30'), 'DC': ('30', '50')}[op]
    f550b = {'M': ('10', '20'), 'AC': ('20', '40'), 'DC': ('30', '60')}[op]
    add(f'{op.lower() if op != "M" else "manual"}-stacker-550'.replace('ac-', 'semi-electric-ac-').replace('dc-', 'semi-electric-dc-'),
        f'{"Manual Hydraulic" if op == "M" else opn + " Hydraulic"} Stacker – 550 mm Fixed Forks', 'stackers', f'{opn} Stackers', op,
        [('20',) + f550, ('20',) + f550b],
        [grid_table('025', [(intro + 2, 0), (intro + 3, 0)])],
        text('025', [intro], drop_line=NO500, drop_head=(r'(?i)load carr?ying capacity',)),
        f'{opn} hydraulic stacker with fixed forks, 550 mm width over forks; 1000 kg and 1500 kg capacities with 1.6, 2.5 and 3.1 m lift heights.',
        wheels=UHMW_OPTS, capacities=['1000 kg', '1500 kg'], lifts=ST_LIFT)
for op, intro in (('M', 0), ('AC', 3), ('DC', 6)):
    opn = OPS[op]
    fa = {'M': ('10', '70'), 'AC': ('20', '90'), 'DC': ('30', '110')}[op]
    fb = {'M': ('10', '80'), 'AC': ('20', '100'), 'DC': ('30', '120')}[op]
    pre = {'M': 'manual', 'AC': 'semi-electric-ac', 'DC': 'semi-electric-dc'}[op]
    add(f'{pre}-stacker-685-adjustable-forks', f'{"Manual Hydraulic" if op == "M" else opn + " Hydraulic"} Stacker – 685 mm Adjustable Forks',
        'stackers', f'{opn} Stackers', op, [('20',) + fa, ('20',) + fb],
        [grid_table('026', [(intro + 1, 0), (intro + 2, 0)])], text('026', [intro]),
        f'{opn} hydraulic stacker with adjustable forks, 350 to 685 mm width over forks; 1000 kg and 1500 kg capacities with 1.6, 2.5 and 3.1 m lift heights.',
        wheels=UHMW_OPTS, capacities=['1000 kg', '1500 kg'], lifts=ST_LIFT)
for kind, code, desc in (('cage', '027', 'a 1200 × 1000 mm wiremesh cage welded on the forks'), ('jib-hook', '028', 'a 1000 mm jib hook')):
    for op, intro in (('M', 0), ('AC', 3), ('DC', 6)):
        opn = OPS[op]
        nums = {('cage', 'M'): ('130', '140'), ('cage', 'AC'): ('150', '160'), ('cage', 'DC'): ('170', '180'),
                ('jib-hook', 'M'): ('190', '200'), ('jib-hook', 'AC'): ('210', '220'), ('jib-hook', 'DC'): ('230', '240')}[(kind, op)]
        sub = {'M': '10', 'AC': '20', 'DC': '30'}[op]
        pre = {'M': 'manual', 'AC': 'semi-electric-ac', 'DC': 'semi-electric-dc'}[op]
        label = 'Cage' if kind == 'cage' else 'Jib Hook'
        add(f'{pre}-stacker-with-{kind}', f'{"Manual Hydraulic" if op == "M" else opn + " Hydraulic"} Stacker with {label}',
            'stackers', f'{opn} Stackers', op, [('20', sub, nums[0]), ('20', sub, nums[1])],
            [grid_table(code, [(intro + 1, 0), (intro + 2, 0)])],
            text(code, [intro, intro + 1], notes=True),
            f'{opn} hydraulic stacker with {desc}; 1000 kg and 1500 kg capacities with 2.5 and 3.1 m lift heights.',
            wheels=UHMW_OPTS, capacities=['1000 kg', '1500 kg'], lifts=['2.5 m', '3.1 m'],
            )
add('electric-stacker', 'Electric Stacker', 'stackers', 'Fully Electric Stackers', 'E', [('20', '40', '250'), ('20', '40', '260')],
    [electric_stacker_table()],
    text('315', [2], drop_line=NO500),
    'Fully electric stacker with AC drive and folding stand-on platform, 24 V battery operated; 1000 kg and 1500 kg capacities, 1.6, 2.5 and 3.1 m lift heights, with standard or adjustable forks.',
    capacities=['1000 kg', '1500 kg'], lifts=ST_LIFT)

# ---------------- Order pickers
for op, pg, f in (('AC', 1, '10'), ('DC', 3, '20')):
    add(f'semi-electric-{op.lower()}-order-picker', f'{OPS[op]} Order Picker', 'order-pickers', 'Semi-Electric Order Pickers', op, [('30', f)],
        [grid_table('030', [(pg + 1, 0)], hdr='{lift} cage height')], text('030', [pg]),
        f'{OPS[op]} order picker with an 800 × 800 mm operator cage and controls in the cage; 300 kg capacity, 3100 mm and 4000 mm maximum cage heights.',
        wheels=UHMW_OPTS, lifts=['3.1 m', '4.0 m'])
add('electric-order-picker', 'Electric Order Picker', 'order-pickers', 'Fully Electric Order Pickers', 'E', [('30', '30')],
    [grid_table('325', [(0, 0)], hdr='{lift} cage height', lift_rx=r'^Maximum Cage Height')], text('325', [0, 1]),
    'Fully electric order picker with AC drive, 24 V battery and an 800 × 800 mm operator cage; 300 kg capacity, 3100 mm and 4000 mm maximum cage heights.',
    lifts=['3.1 m', '4.0 m'])

# ---------------- Drum lifters & tilters / material tilters / drum grippers
for fam, code, base, fnum, pre, nm, sm in (
        ('drum-lifters-tilters', '035', 'Drum Lifter & Tilter', '40', 'drum-lifter-tilter', 'Hydraulic Drum Lifter & Tilter',
         'for standard 220 litre metal drums (600 mm diameter × 900 mm height), with 360° drum rotation through a self-locking worm gearbox'),
        ('material-lifters-tilters', '036', 'Material Lifter & Tilter', '50', 'material-lifter-tilter', 'Hydraulic Material Lifter & Tilter',
         'with a 600 × 600 × 600 mm pan with taper outlet, rotated through 360° by a self-locking worm gearbox'),
        ('drum-grippers', '040', 'Drum Lifter with Auto Gripper', '60', 'drum-lifter-auto-gripper', 'Hydraulic Drum Lifter with Auto Gripper',
         'that clamps and releases standard 220 litre metal drums automatically, without hand contact')):
    for op, intro, f in (('M', 0, '10'), ('AC', 2, '20'), ('DC', 4, '30')):
        name = ('Manual ' + nm) if op == 'M' else f'{OPS[op]} {nm}'
        add(f'{"manual" if op == "M" else "semi-electric-" + op.lower()}-{pre}', name, fam, f'{OPS[op]}', op, [(fnum, f)],
            [grid_table(code, [(intro + 1, 0)], hdr='{lift} lift')], (text(code, [0], drop_head=(r'Operation$',)) + text(code, [intro])) if op != 'M' else text(code, [0]),
            f'{OPS[op]} {nm.lower().replace("hydraulic ", "hydraulic ")} {sm}; 300 kg capacity with 1600, 2500 and 3100 mm lift heights.',
            wheels=UHMW_OPTS, lifts=['1.6 m', '2.5 m', '3.1 m'])
add('electric-drum-lifter-tilter', 'Electric Drum Lifter & Tilter', 'drum-lifters-tilters', 'Fully Electric', 'E', [('40', '40')],
    [grid_table('335', [(0, 0)], hdr='{lift} lift', lift_rx=r'^Maximum Drum Height', drum=True)], text('335', [0, 1], drum=True),
    'Fully electric drum lifter and tilter with AC drive and 24 V battery, for standard metal drums (600 mm diameter × 900 mm height); 300 kg capacity with 1600, 2500 and 3100 mm lift heights.',
    lifts=['1.6 m', '2.5 m', '3.1 m'])

# ---------------- Floor cranes
for op, (p1, p2), f in (('M', (1, 2), ('10', '10', '20')), ('AC', (4, 5), ('20', '30', '40')), ('DC', (7, 8), ('30', '50', '60'))):
    pre = {'M': 'manual', 'AC': 'semi-electric-ac', 'DC': 'semi-electric-dc'}[op]
    intro = {'M': [0], 'AC': [3], 'DC': [6]}[op]
    add(f'{pre}-hydraulic-floor-crane', ('Manual' if op == 'M' else OPS[op]) + ' Hydraulic Floor Crane', 'floor-cranes', f'{OPS[op]} Floor Cranes', op,
        [('70', f[0], f[1]), ('70', f[0], f[2])], [crane_table('045', [p1, p2])],
        text('045', intro) + text('045', [p1], keep=(r'Operation|telescopic boom' if op == 'M' else r'telescopic boom')),
        f'{OPS[op]} hydraulic floor crane with telescopic boom adjustable from 1000 to 1500 mm; 1000 kg and 1500 kg capacities with 2500 mm lift.',
        wheels=UHMW_OPTS, capacities=['1000 kg', '1500 kg'], lifts=['2.5 m'])
CB = {('fixed', 'M'): (1, [1], ('10', '70'), ('10', '130')), ('fixed', 'AC'): (3, [2], ('20', '80'), ('20', '140')),
      ('fixed', 'DC'): (5, [4], ('30', '90'), ('30', '150')),
      ('swivelling', 'M'): (6, [6], ('10', '100'), ('10', '160')), ('swivelling', 'AC'): (8, [7], ('20', '110'), ('20', '170')),
      ('swivelling', 'DC'): (10, [9], ('30', '120'), ('30', '180'))}
CB_LINES = (r'^Dia \d', r'(?i)maximum safe load capacity')   # wheel sizes and safe loads are in the 500 / 1000 kg table
for (boom, op), (pg, intro, f5, f10) in CB.items():
    pre = {'M': 'manual', 'AC': 'semi-electric-ac', 'DC': 'semi-electric-dc'}[op]
    bt = 'Fixed Boom' if boom == 'fixed' else 'Swivelling Boom'
    t500 = crane_table('046', [pg])
    t1000 = crane_table('047', [pg])
    tbl = {'title': None, 'head': ['Specification', '500 kg', '1000 kg'],
           'rows': [[r[0], r[1], next((s[1] for s in t1000['rows'] if s[0] == r[0]), '—')] for r in t500['rows']]}
    add(f'{pre}-counterbalance-floor-crane-{boom}-boom', f'{("Manual" if op == "M" else OPS[op])} Counterbalance Floor Crane – {bt}',
        'floor-cranes', f'{OPS[op]} Floor Cranes', op, [('70',) + f5, ('70',) + f10], [tbl],
        text('046', intro, drop_line=CB_LINES) + (text('046', [pg], keep=r'telescopic boom') if pg not in intro else []),
        f'{OPS[op]} counterbalanced floor crane with {bt.lower()}; 500 kg and 1000 kg capacities with 2500 mm lift.',
        wheels=UHMW_OPTS, capacities=['500 kg', '1000 kg'], lifts=['2.5 m'])
add('electric-floor-crane', 'Electric Floor Crane', 'floor-cranes', 'Fully Electric Floor Cranes', 'E', [('70', '40', '190')],
    # owner decision (26 Nov 2026): this product is offered in 1500 kg ONLY — the workbook's 1000 kg column is not shown
    [grid_table('340', [(0, 0)], hdr='{cap}', lift_rx=r'^Maximum Hook Height at E', keep_cols=[1])],
    text('340', [0, 1], drop_line=(r'(?<![0-9])1000 kg',)),
    'Fully electric floor crane with AC drive and 24 V battery; 1500 kg capacity with 3100 mm maximum hook height.',
    capacities=['1500 kg'], lifts=['3.1 m'], media_side=True)

# ---------------- Gantries
for op, pg, f, nm in (('M', 0, '10', 'Manual Gantry'), ('EH', 1, '20', 'Electric Gantry – 440 V 3 Phase AC')):
    add('manual-gantry' if op == 'M' else 'electric-gantry', nm, 'gantries', 'Gantries', 'M' if op == 'M' else 'E', [('80', f)],
        [mlist_table('055', pg, ['Capacity', 'Lift', 'Length x Width', 'L1 x W1 x H1'],
                     rename={'Lift': 'Lift Height', 'Length x Width': 'Clear Span (Length × Width)', 'L1 x W1 x H1': 'Overall Size (L1 × W1 × H1, mm)'})],
        text('055', [pg]),
        ('Mobile gantry with manual chain pulley block and geared trolley' if op == 'M' else 'Mobile gantry with push-button electric hoist, 440 V 3 phase AC')
        + '; 500, 1000 and 2000 kg capacities with 3000 mm lift, on swivel castors with brakes.',
        capacities=['500 kg', '1000 kg', '2000 kg'], lifts=['3.0 m'])
P[-1]['operation'] = 'Electric (440 V, 3 Phase AC)'

# ---------------- Scissor lifts
SC_COLS = ['Table Size', 'Capacity', 'Min Ht', 'Max Ht', 'Lift', 'Overall Size']
SC_REN = {'Table Size (L x W mm)': 'Table Size (L × W, mm)', 'Capacity (kg)': 'Capacity (kg)', 'Min Ht (mm)': 'Min. Table Height (mm)',
          'Max Ht (mm)': 'Max. Table Height (mm)', 'Lift (mm)': 'Lift (mm)', 'Overall Size (L1 x W1 mm)': 'Overall Size (L1 × W1, mm)'}
for op, (ps, pd), intro, (fs, fd) in (('M', (1, 2), 0, ('10', '20')), ('AC', (4, 5), 3, ('30', '40')), ('DC', (7, 8), 6, ('50', '60'))):
    pre = {'M': 'manual', 'AC': 'semi-electric-ac', 'DC': 'semi-electric-dc'}[op]
    for kind, pg, f in (('single', ps, fs), ('double', pd, fd)):
        add(f'{pre}-hydraulic-scissor-lift-{kind}', f'{("Manual" if op == "M" else OPS[op])} Hydraulic Scissor Lift – {kind.title()} Scissor',
            'scissor-lifts', f'{OPS[op]} Scissor Lifts', op, [('90', f)],
            [mlist_table('060', pg, SC_COLS, rename=SC_REN)], text('060', [0, intro] if op != 'M' else [0, pg]),
            f'{OPS[op]} mobile hydraulic {kind} scissor lift table; 500 kg and 1000 kg capacities with 1000 × 500, 1250 × 600 and 1500 × 700 mm tables.',
            wheels=UHMW_OPTS, capacities=['500 kg', '1000 kg'])
for code, size, f in (('065', '2000 × 2000', '70'), ('066', '2500 × 2000', '80'), ('067', '3000 × 2000', '90')):
    s = size.replace(' × ', 'x')
    add(f'electro-hydraulic-scissor-lift-{s}', f'Electro-Hydraulic Scissor Lift – {size} mm Platform', 'scissor-lifts',
        'Electro-Hydraulic Platform Scissor Lifts', 'EH', [('90', f)], [nkv_table(code, [0, 1])], text(code, [1, 2]),
        f'Pit-mounted electro-hydraulic single scissor lift with {size} mm platform; 2000 kg capacity, 440 V 3 phase AC.',
        capacities=['2000 kg'])
add('electro-hydraulic-scissor-lift-spm', 'Electro-Hydraulic Scissor Lift – SPM', 'scissor-lifts', 'Special Purpose Scissor Lifts (SPM)', 'EH',
    [('90', '100')], [nkv_table('068', [0, 1])], text('068', [1, 2]),
    'Special-purpose electro-hydraulic single scissor lift, built to the application; reference configuration 3000 × 2000 mm platform, 2000 kg capacity.',
    capacities=['2000 kg'], spm=True)
add('electro-hydraulic-double-scissor-lift-spm', 'Electro-Hydraulic Double Scissor Lift – SPM', 'scissor-lifts', 'Special Purpose Scissor Lifts (SPM)', 'EH',
    [('90', '110')], [nkv_table('069', [0, 1])], text('069', [1, 2]),
    'Special-purpose electro-hydraulic double scissor lift, built to the application; reference configuration 3000 × 2000 mm platform, 2000 kg capacity, 2400 mm lift.',
    capacities=['2000 kg'], spm=True)

# ---------------- Dock leveller, goods lifts, shelving, conveyors
add('electro-hydraulic-dock-leveller', 'Electro-Hydraulic Dock Leveller', 'dock-levellers', 'Dock Levellers', 'EH', [('100',)],
    [grid_table('070', [(0, 0)], hdr='{cap}')], text('070', [0, 1]),
    'Electro-hydraulic dock leveller operated by a 415 V, 3 phase AC power pack; 5000 kg and 9000 kg capacities, for forklift truck loading and unloading.',
    capacities=['5000 kg', '9000 kg'])
for code, f, slug, nm, sm in (
        ('075', '10', 'two-channel-goods-lift', 'Two Channel Goods Lift', 'Hydraulic two-channel goods lift with sliding shutters; 1000 kg capacity, 1500 × 1000 mm cage, 6200 mm lift.'),
        ('080', '20', 'four-channel-goods-lift', 'Four Channel Goods Lift', 'Hydraulic four-channel goods lift with sliding shutters; 2000 kg capacity, 2000 × 2000 mm cage, 6200 mm lift.'),
        ('085', '30', 'two-channel-lifting-cage', 'Two Channel Lifting Cage', 'Hydraulic two-channel lifting cage on leaf chains; 1000 kg capacity, 1500 × 1000 mm cage, 6200 mm lift.'),
        ('090', '40', 'four-channel-lifting-cage', 'Four Channel Lifting Cage', 'Hydraulic four-channel lifting cage on leaf chains; 2000 kg capacity, 2000 × 2000 mm cage, 6200 mm lift.')):
    add(slug, nm, 'goods-lifts', 'Goods Lifts' if 'goods' in slug else 'Lifting Cages', 'EH', [('110', f)],
        [nkv_table(code, [0, 1, 2])], text(code, [1, 2, 3]), sm)
add('industrial-shelving-heavy-duty', 'Industrial Shelving – Heavy Duty', 'industrial-shelving', 'Industrial Shelving', 'M', [('120', '10')],
    [grid_table('095', [(0, 0)], hdr='{length} × {depth} shelf')], text('095', [0, 1]),
    'Heavy duty pallet shelving with 2000 kg per shelf, 3000 mm rack height and 4 shelves per rack, in two shelf sizes.')
add('industrial-shelving-medium-duty', 'Industrial Shelving – Medium Duty', 'industrial-shelving', 'Industrial Shelving', 'M', [('120', '20')],
    [grid_table('100', [(0, 0)], hdr='{depth} deep · {sheet} shelf sheet')], text('100', [0]),
    'Medium duty adjustable shelving, 2000 mm high with 6 shelves, 450 or 600 mm deep, 100 kg or 150 kg per shelf.')
for code, f, slug, nm, sm in (
        ('105', '10', 'gravity-roller-conveyor', 'Gravity Roller Conveyor', 'Mobile gravity roller conveyor, 6000 mm long with 600 mm rollers; 100 kg per metre, straight or hydraulically inclined.'),
        ('110', '20', 'rubber-belt-conveyor', 'Rubber Belt Conveyor', 'Mobile motorised rubber belt conveyor, 6000 mm long with 600 mm belt; 50 kg per metre, straight or hydraulically inclined.'),
        ('115', '30', 'pvc-belt-conveyor', 'PVC Belt Conveyor', 'Mobile motorised PVC belt conveyor, 6000 mm long with 600 mm belt; 50 kg per metre, straight or hydraulically inclined.')):
    add(slug, nm, 'conveyors', 'Conveyors', 'M' if code == '105' else 'EH', [('130', f)], [grid_table(code, [(0, 0)], hdr='{tail}')], text(code, [0]), sm)
for p in P:
    if p['slug'] in ('rubber-belt-conveyor', 'pvc-belt-conveyor'):
        p['operation'] = 'Motorised'
    if p['slug'] == 'gravity-roller-conveyor':
        p['operation'] = 'Gravity'
    if p['family'] == 'industrial-shelving':
        p['operation'] = 'Static storage'


# ---------------------------------------------------------------- images & checks
def images(p):
    d = [folder(*f) for f in p['folders']]
    def pick(path):
        files = sorted(x for x in os.listdir(path) if x.lower().endswith('.png'))
        return files
    photos, drawings = [], []
    for path in d:
        for f in pick(path):
            (drawings if f.startswith('Copy of') or is_drawing(os.path.join(path, f)) else photos).append(os.path.join(path, f))
    return photos, drawings


def is_drawing(path):
    """Drawings are line art (almost no colour); photos are coloured. Decided from the file name list
    verified by eye during the inspection (see report)."""
    return os.path.basename(path) in DRAWINGS


# photo / drawing assignment verified visually (contact sheets, Nov 2026)
DRAWINGS = {'2.png', '4.png', '7.png', '9.png', '156.png', '139.png', '141.png', '143.png', '145.png', '147.png', '149.png', '151.png',
            '11.png', '13.png', '15.png', '17.png', '19.png', '21.png', '23.png', '25.png', '29.png', '31.png', '33.png', '35.png',
            '37.png', '39.png', '41.png', '43.png', '45.png', '47.png', '49.png', '51.png', '53.png', '55.png', '158.png', '160.png',
            '57.png', '59.png', '162.png', '61.png', '63.png', '164.png', '66.png', '68.png', '70.png', '72.png', '74.png',
            '77.png', '79.png', '81.png', '83.png', '85.png', '87.png', '89.png', '91.png', '93.png', '95.png', '97.png', '99.png',
            '101.png', '103.png', '105.png', '107.png', '109.png', '111.png', '166.png', '113.png', '115.png', '117.png', '119.png',
            '121.png', '123.png', '125.png', '127.png', '129.png', '131.png', '133.png', '135.png', '137.png'}


def main():
    data = {'name': 'Material Handling Equipment', 'url': '/material-handling-equipment/', 'families': FAMILIES, 'products': []}
    slugs = set()
    for p in P:
        assert p['slug'] not in slugs, p['slug']
        slugs.add(p['slug'])
        photos, drawings = images(p)
        assert photos, ('no photo', p['slug'])
        photo = photos[min(p.pop('photo_from', 0), len(photos) - 1)] if len(photos) > 1 else photos[0]
        p['source'] = {'photo': rel(photo), 'drawing': rel(drawings[0]) if drawings else None,
                       'folders': [rel(folder(*f)) for f in p['folders']]}
        p['images'] = {'photo': f'{IMG}{p["slug"]}-photo.jpg', 'thumb': f'{IMG}{p["slug"]}-thumb.jpg'}
        if drawings:
            p['images']['drawing'] = f'{IMG}{p["slug"]}-drawing.jpg'
        p.pop('folders')
        p.setdefault('wheels', [])
        p.setdefault('spm', False)
        data['products'].append(p)
    # privacy / content checks
    blob = json.dumps(data, ensure_ascii=False)
    for rx in (r'\bRs\.?\s?\d', r'(?i)\bprice\b', r'(?i)discount', r'(?i)\bgst\b', r'(?i)bank', r'(?i)IFSC', r'(?i)quotation',
               r'\b(ST|FC|DT|MT|DG|OP|SC|EST|EOP|EDT|EFC|EPT|GAN|PT|RPT|ISH|ISM|GRC|RBC|PBC) ?[.\-]?\s?\d{2}[ .]\d{2}'):
        hits = re.findall(rx, blob)
        assert not hits, (rx, hits[:5])
    for p in data['products']:
        if p['family'] == 'stackers':
            assert not re.search(r'(?<![0-9])500 kg', json.dumps(p, ensure_ascii=False)), p['slug']
        for t in p['tables']:
            assert t['rows'], ('empty table', p['slug'])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')
    fams = {fm['id']: 0 for fm in FAMILIES}
    for p in data['products']:
        fams[p['family']] += 1
    print(f'{len(data["products"])} products in {len(FAMILIES)} families:', fams)


if __name__ == '__main__':
    main()
