"""
Import Pallet Truck Wheels & Rollers from product-sources into
data/products/pallet-truck/pallet-truck.json.

    python tools/import_pallet_truck.py

Source folders (read-only):
  product-sources/30 Wheels & Caster/40 Pallet  Truck  Wheels  &  Rollers/<CI|PUCI|UHMW>/<product folder>/
each holding one .docx (2-column spec table) and two numbered .png files
(one product photograph, one technical drawing).

* Spec rows are copied VERBATIM from the Word table.
* Photo vs drawing was identified by inspecting the images (2026-11-23); the photo
  file names are listed in PHOTO below and checked against each folder.
* The importer STOPS if a file is missing, the Word table is unreadable, or the
  Size / Wheel Diameter / Wheel Width / Bore ID do not match the folder name.
* Wheel Material must match the sub-folder, except for the corrections listed in
  MATERIAL_CORRECTIONS (approved by the owner) - these are recorded in the data.
"""
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
DATA = os.path.join(REPO, 'data', 'products', 'pallet-truck', 'pallet-truck.json')

SUBCATS = [  # order shown on the website
    {'id': 'uhmw', 'folder': 'UHMW', 'short': 'UHMW', 'name': 'UHMW', 'full': 'Ultra-High-Molecular-Weight Polyethylene',
     'material': 'UHMW ( Ultra-High-Molecular-Weight Polyethylene )', 'prefix': 'UHMW'},
    {'id': 'puci', 'folder': 'PUCI', 'short': 'PU-CI', 'name': 'PU-CI', 'full': 'Polyurethane with Cast Iron Core',
     'material': 'PUCI ( Polyurethane with Cast Iron Core )', 'prefix': 'PU - CI'},
    {'id': 'ci', 'folder': 'CI', 'short': 'CI', 'name': 'CI', 'full': 'Cast Iron',
     'material': 'CI ( Cast Iron )', 'prefix': 'CI'},
]
# Product photographs (the other image in each folder is the technical drawing).
PHOTO = {'uhmw': {'Roller': '193.png', 'Wheel': '211.png'},
         'puci': {'Roller': '199.png', 'Wheel': '213.png'},
         'ci': {'Roller': '205.png', 'Wheel': '215.png'}}
# Word documents that name the wrong material; owner instruction 2026-11-23:
# "Treat as CI, keep loads" - the folder, file name and photo are cast iron.
MATERIAL_CORRECTIONS = {
    ('ci', 'Roller', '80x100x20'): 'CI ( Cast Iron )',
    ('ci', 'Roller', '80x96x20'): 'CI ( Cast Iron )',
    ('ci', 'Wheel', '180x50x20'): 'CI ( Cast Iron )',
}
FOLDER_RE = re.compile(r'^(.+?)\s+(Roller|Wheel)\s+(\d+)\s+x\s+(\d+)\s+x\s+(\d+)(?:\s+(BB|PLB))?$')


def cell_text(el):
    parts = []
    for node in el.iter():
        if node.tag == W + 't' and node.text:
            parts.append(node.text)
        elif node.tag in (W + 'tab', W + 'br', W + 'cr'):
            parts.append(' ')
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


def read_docx_table(path):
    with zipfile.ZipFile(path) as z:
        body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    tables = body.findall(W + 'tbl')
    if len(tables) != 1:
        raise ValueError(f'expected exactly 1 table, found {len(tables)}')
    rows = []
    for tr in tables[0].iter(W + 'tr'):
        cells = [cell_text(tc) for tc in tr.findall(W + 'tc')]
        if len(cells) != 2:
            raise ValueError(f'expected 2 cells per row, found {len(cells)}')
        rows.append(cells)
    return rows


def main():
    base = os.path.join(REPO, 'product-sources', '30 Wheels & Caster')
    root = next(os.path.join(base, d) for d in os.listdir(base) if d.startswith('40'))
    with open(DATA, encoding='utf-8') as f:
        cat = json.load(f)
    products, errors, corrections = [], [], []
    for sc in SUBCATS:
        sdir = os.path.join(root, sc['folder'])
        for folder in sorted(os.listdir(sdir)):
            fpath = os.path.join(sdir, folder)
            if not os.path.isdir(fpath):
                continue
            m = FOLDER_RE.match(re.sub(r'\s+', ' ', folder).strip())
            if not m:
                errors.append(f'{sc["folder"]}/{folder}: folder name not recognised')
                continue
            prefix, kind, d, w, bore, brg = m.groups()
            if prefix.replace(' ', '') != sc['prefix'].replace(' ', ''):
                errors.append(f'{sc["folder"]}/{folder}: material prefix "{prefix}" does not match sub-folder')
            files = os.listdir(fpath)
            docs = [x for x in files if x.lower().endswith('.docx') and not x.startswith('~$')]
            imgs = sorted(x for x in files if x.lower().endswith(('.png', '.jpg', '.jpeg')))
            if len(docs) != 1 or len(imgs) != 2:
                errors.append(f'{folder}: expected 1 Word file and 2 images, found {docs} / {imgs}')
                continue
            photo = PHOTO[sc['id']][kind]
            if photo not in imgs:
                errors.append(f'{folder}: product photo {photo} not found (images: {imgs})')
                continue
            drawing = next(x for x in imgs if x != photo)
            try:
                specs = read_docx_table(os.path.join(fpath, docs[0]))
            except Exception as ex:
                errors.append(f'{folder}: cannot read {docs[0]}: {ex}')
                continue
            kv = dict(specs)
            size_key = f'{d}x{w}x{bore}'
            checks = (('Size', f'{d} x {w} x {bore} mm'), ('Wheel Diameter', f'{d} mm'),
                      ('Wheel Width', f'{w} mm'), ('Bore ID', f'{bore} mm'))
            for label, expected in checks:
                if kv.get(label) != expected:
                    errors.append(f'{folder}: {label} in Word = "{kv.get(label)}", folder name gives "{expected}"')
            load = re.match(r'^(\d+(?:\.\d+)?) kg$', kv.get('Load Capacity', ''))
            if not load:
                errors.append(f'{folder}: Load Capacity missing or not in "N kg" format')
                continue
            if kv.get('Bearing Type') != 'Ball Bearing':
                errors.append(f'{folder}: Bearing Type = "{kv.get("Bearing Type")}"')
            fix = MATERIAL_CORRECTIONS.get((sc['id'], kind, size_key))
            if kv.get('Wheel Material') != sc['material']:
                if fix and fix == sc['material']:
                    corrections.append({'field': 'Wheel Material', 'word_value': kv['Wheel Material'], 'shown_as': fix,
                                        'reason': 'Owner instruction 2026-11-23: folder, file name and photo are Cast Iron; Word material line was a copy error.'})
                    specs = [[k, fix if k == 'Wheel Material' else v] for k, v in specs]
                else:
                    errors.append(f'{folder}: Wheel Material in Word = "{kv.get("Wheel Material")}", expected "{sc["material"]}"')
            elif fix:
                errors.append(f'{folder}: listed in MATERIAL_CORRECTIONS but the Word file is already correct - remove the entry')
            slug = f'{kind.lower()}-{size_key}'
            rel = lambda name: os.path.relpath(os.path.join(fpath, name), REPO).replace('\\', '/')
            img = f'/assets/products/pallet-truck/{sc["id"]}/{slug}'
            p = {
                'subcat': sc['id'], 'kind': kind, 'slug': slug,
                'name': f'{sc["short"]} Pallet Truck {kind} {d} × {w} × {bore} mm',
                'diameter_mm': int(d), 'width_mm': int(w), 'bore_mm': int(bore),
                'load_kg': float(load.group(1)), 'specs': specs,
                'images': {'photo': f'{img}-photo.jpg', 'thumb': f'{img}-thumb.jpg', 'drawing': f'{img}-drawing.jpg'},
                'source': {'docx': rel(docs[0]), 'photo': rel(photo), 'drawing': rel(drawing)},
            }
            if fix and corrections and corrections[-1]['shown_as'] == fix and kv.get('Wheel Material') != sc['material']:
                p['corrections'] = [corrections[-1]]
            products.append(p)
    slugs = [(p['subcat'], p['slug']) for p in products]
    for s in set(slugs):
        if slugs.count(s) > 1:
            errors.append(f'duplicate product URL {s}')
    if errors:
        print('IMPORT STOPPED - please check these in the source files:')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    order = {s['id']: i for i, s in enumerate(SUBCATS)}
    products.sort(key=lambda p: (order[p['subcat']], p['kind'] != 'Roller', p['diameter_mm'], p['width_mm']))
    cat['subcats'] = [{k: s[k] for k in ('id', 'name', 'short', 'full', 'material')} for s in SUBCATS]
    cat['products'] = products
    with open(DATA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)
        f.write('\n')
    counts = {s['id']: sum(p['subcat'] == s['id'] for p in products) for s in SUBCATS}
    print(f'Imported {len(products)} products {counts}; material corrections applied: {sum("corrections" in p for p in products)}')


if __name__ == '__main__':
    main()
