"""
Import wheel/castor products from the local product-sources folders into a
category data file (data/products/wheels/<category>.json).

    python tools/import_wheels.py uhmw

What it does (read-only on the source folders):
  * finds every numbered product folder "NNN <MATERIAL> - <DUTY> - D x W (N Inch)"
  * reads the single .docx in each folder and copies its 2-column spec table
    VERBATIM (no values are changed, estimated or invented)
  * picks the product photo ("<name>.png/.jpg") and the drawing ("<name> (2).png/.jpg")
  * cross-checks the Word values against the folder name and STOPS with an error
    report if diameter, width or inch size disagree, or a file is missing

Only the "products" list of the data file is rewritten; the category details
you edit by hand (name, intro, features, groups ...) are kept.
"""
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
FOLDER_RE = re.compile(r'^(\d{3}) (.+?) - (.+?) - (\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) \((\d+(?:\.\d+)?) Inch\)$')
IMG_EXT = ('.png', '.jpg', '.jpeg')


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
            raise ValueError(f'expected 2 cells per row, found {len(cells)}: {cells}')
        rows.append(cells)
    return rows


def num(s):
    return float(s)


def fmt(n):
    return str(int(n)) if float(n).is_integer() else str(n)


def main(category):
    data_path = os.path.join(REPO, 'data', 'products', 'wheels', f'{category}.json')
    with open(data_path, encoding='utf-8') as f:
        cat = json.load(f)
    src = os.path.join(REPO, cat['source_dir'])
    groups = {g['token']: g for g in cat['groups']}

    products, errors = [], []
    for folder in sorted(os.listdir(src)):
        fpath = os.path.join(src, folder)
        if not os.path.isdir(fpath):
            continue
        m = FOLDER_RE.match(folder)
        if not m:
            if not folder.startswith('000'):
                errors.append(f'{folder}: folder name not recognised (skipped)')
            continue
        code, material, duty_raw, d, w, inch = m.groups()
        duty_token = duty_raw.replace('(', '').replace(')', '').strip()
        group = groups.get(duty_token)
        if not group:
            errors.append(f'{code}: duty "{duty_token}" not listed in groups of {category}.json')
            continue

        files = os.listdir(fpath)
        docs = [x for x in files if x.lower().endswith('.docx') and not x.startswith('~$')]
        imgs = [x for x in files if x.lower().endswith(IMG_EXT)]
        drawings = [x for x in imgs if os.path.splitext(x)[0].endswith(' (2)')]
        photos = [x for x in imgs if x not in drawings]
        for label, lst in (('Word document', docs), ('photo', photos), ('drawing', drawings)):
            if len(lst) != 1:
                errors.append(f'{code}: expected 1 {label}, found {len(lst)}: {lst}')
        if len(docs) != 1 or len(photos) != 1 or len(drawings) != 1:
            continue

        try:
            specs = read_docx_table(os.path.join(fpath, docs[0]))
        except Exception as e:  # unreadable document
            errors.append(f'{code}: cannot read {docs[0]}: {e}')
            continue
        kv = dict(specs)

        # --- consistency checks: Word document vs folder name -----------------
        # Size may be written "100 x 32 (4 Inch Wheel)" or "100 x 32 mm (4 Inch Wheel)"
        size = re.match(r'^([\d.]+) x ([\d.]+)(?: mm)? \(([\d.]+) Inch Wheel\)$', kv.get('Size', ''))
        dia = re.match(r'^([\d.]+) mm$', kv.get('Wheel Diameter', ''))
        wid = re.match(r'^([\d.]+) mm$', kv.get('Wheel Width', ''))
        load = re.match(r'^([\d.]+) kg$', kv.get('Load Capacity per Caster', ''))
        if not (size and dia and wid and load):
            errors.append(f'{code}: Size / Wheel Diameter / Wheel Width / Load Capacity per Caster missing or not in the usual format')
            continue
        for label, doc_val, folder_val in (
            ('Size diameter', size.group(1), d), ('Size width', size.group(2), w), ('Size inch', size.group(3), inch),
            ('Wheel Diameter', dia.group(1), d), ('Wheel Width', wid.group(1), w),
        ):
            if num(doc_val) != num(folder_val):
                errors.append(f'{code}: {label} in Word = {doc_val}, folder name = {folder_val}')

        slug = f"{group['id']}-{fmt(num(d))}x{fmt(num(w))}"
        rel = lambda name: os.path.relpath(os.path.join(fpath, name), REPO).replace('\\', '/')
        products.append({
            'code': code,
            'slug': slug,
            'group': group['id'],
            'name': f"{cat['name'].rstrip('s')} {group['short']} {fmt(num(d))} × {fmt(num(w))} mm ({fmt(num(inch))} Inch Wheel)",
            'diameter_mm': num(d),
            'width_mm': num(w),
            'inch': num(inch),
            'load_per_caster_kg': num(load.group(1)),
            'specs': specs,
            'images': {
                'photo': f'/assets/products/wheels/{category}/{slug}-photo.jpg',
                'thumb': f'/assets/products/wheels/{category}/{slug}-thumb.jpg',
                'drawing': f'/assets/products/wheels/{category}/{slug}-drawing.jpg',
            },
            'source': {'docx': rel(docs[0]), 'photo': rel(photos[0]), 'drawing': rel(drawings[0])},
        })

    slugs = [p['slug'] for p in products]
    for s in set(slugs):
        if slugs.count(s) > 1:
            errors.append(f'duplicate product URL "{s}"')

    if errors:
        print('IMPORT STOPPED - please fix these in the source files:')
        for e in errors:
            print('  -', e)
        sys.exit(1)

    cat['products'] = products
    with open(data_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)
        f.write('\n')
    by_group = {g['id']: sum(p['group'] == g['id'] for p in products) for g in cat['groups']}
    print(f'Imported {len(products)} products into data/products/wheels/{category}.json {by_group}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
