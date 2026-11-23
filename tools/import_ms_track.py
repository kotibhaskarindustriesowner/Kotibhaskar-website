"""
Import MS Solid Track Wheels from product-sources into data/products/ms-track/ms-track.json.

    python tools/import_ms_track.py

Source (read-only): product-sources/30 Wheels & Caster/50 MS Track wheels/
  Information/<catalogue page>.pdf   master specification table (34 rows)
  01 V Groove 00/ ... 04 Flange Type 00/   one photo ("... 00.png") + drawings "... 25/32/40/50/75.png"
  Cover image.png                    category cover photo

* Every row is read from the PDF text (pdftotext from Git for Windows) and checked:
  the description (D x W x bore, PLB/BB) must match the Wheel Size / Bore / Bearing columns,
  PLB rows must have no bearing number, BB rows must have one.
* Owner-approved corrections are listed in CORRECTIONS and recorded in the data file.
* The catalogue footnote stating that capacities are the same for all four profiles is required.
* The importer STOPS on any other mismatch or missing file.
"""
import json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data', 'products', 'ms-track', 'ms-track.json')
PDFTOTEXT = r'C:\Program Files\Git\mingw64\bin\pdftotext.exe'
PROFILES = [  # folder prefix, slug, display name
    ('01', 'v-groove', 'V-Groove'), ('02', 'square-groove', 'Square-Groove'),
    ('03', 'round-groove', 'Round-Groove'), ('04', 'flange-type', 'Flange-Type')]
WIDTHS = [25, 32, 40, 50, 75]
# Row 27: description "200 x 50 x 25 - PLB" but Wheel Size column printed "150 x 50".
# Owner instruction 2026-11-23: show 200 x 50, Plain Bore, 900 kg.
CORRECTIONS = {27: {'wheel_size': (200, 50),
                    'note': 'Wheel Size column printed "150 x 50"; description says 200 x 50 x 25 PLB. '
                            'Owner confirmed 200 x 50 mm, Plain Bore, 900 kg (2026-11-23).'}}
ROW = re.compile(r'^(\d{2})\s+MS\s*-\s*VG\s*-\s*WHEEL\s*-?\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*-\s*(PLB|BB)\s+'
                 r'(\d+)\s*x\s*(\d+)\s+(\d+)\s+(\d+)\s+(---|\d{4})\s+(\d+)\s*$')


def main():
    base = os.path.join(REPO, 'product-sources', '30 Wheels & Caster')
    root = next(os.path.join(base, d) for d in os.listdir(base) if d.startswith('50'))
    info = os.path.join(root, 'Information')
    pdf = next(os.path.join(info, f) for f in os.listdir(info) if f.lower().endswith('.pdf'))
    text = subprocess.run([PDFTOTEXT, '-table', '-enc', 'UTF-8', pdf, '-'], capture_output=True, text=True, encoding='utf-8').stdout
    errors, rows = [], []
    for line in text.splitlines():
        m = ROW.match(re.sub(r'\s+', ' ', line.strip()).replace('WHEEL-', 'WHEEL -'))
        if not m:
            continue
        no, dd, dw, db, kind, cd, cw, boss, bore, brg, load = m.groups()
        no = int(no)
        size = (int(cd), int(cw))
        fix = CORRECTIONS.get(no)
        if (int(dd), int(dw)) != size:
            if fix and fix['wheel_size'] == (int(dd), int(dw)):
                size = fix['wheel_size']
            else:
                errors.append(f'row {no}: description {dd} x {dw} but Wheel Size column {cd} x {cw}')
        elif fix:
            errors.append(f'row {no}: listed in CORRECTIONS but the source is already consistent')
        if int(db) != int(bore):
            errors.append(f'row {no}: description bore {db} but Bore-ID column {bore}')
        if (kind == 'PLB') != (brg == '---'):
            errors.append(f'row {no}: {kind} with bearing number "{brg}"')
        r = {'no': no, 'diameter_mm': size[0], 'width_mm': size[1], 'boss_mm': int(boss), 'bore_mm': int(bore),
             'bearing': 'Plain Bore' if kind == 'PLB' else 'Ball Bearing', 'bearing_no': None if brg == '---' else brg,
             'load_kg': int(load)}
        if fix:
            r['correction'] = fix['note']
        rows.append(r)
    if [r['no'] for r in rows] != list(range(1, 35)):
        errors.append(f'expected rows 01-34, found {[r["no"] for r in rows]}')
    if not re.search(r'Capacity\s+of\s+Wheels\s+with\s+V\s+groove,\s+Square\s+groove,\s+Round\s+groove\s+&\s+Flange\s+type\s+is\s+same', re.sub(r'\s+', ' ', text)):
        errors.append('catalogue footnote "capacity ... same for all four profiles" not found')
    if not re.search(r'Maximum\s+working\s+temperature\s*-\s*250', re.sub(r'\s+', ' ', text)):
        errors.append('maximum working temperature 250 not found in catalogue text')
    keys = [(r['diameter_mm'], r['width_mm'], r['bore_mm'], r['bearing']) for r in rows]
    for k in set(keys):
        if keys.count(k) > 1:
            errors.append(f'duplicate configuration {k}')
    widths = sorted({r['width_mm'] for r in rows})
    if widths != WIDTHS:
        errors.append(f'wheel widths {widths} differ from drawing widths {WIDTHS}')
    profiles = []
    for prefix, slug, name in PROFILES:
        folder = next(d for d in os.listdir(root) if d.startswith(prefix + ' '))
        fdir = os.path.join(root, folder)
        files = os.listdir(fdir)
        rel = lambda f: os.path.relpath(os.path.join(fdir, f), REPO).replace('\\', '/')
        photo = next((f for f in files if f.endswith(' 00.png')), None)
        drawings = {}
        for w in WIDTHS:
            f = next((x for x in files if x.endswith(f' {w}.png')), None)
            if not f:
                errors.append(f'{folder}: drawing for width {w} missing')
            drawings[str(w)] = f
        if not photo:
            errors.append(f'{folder}: photo "... 00.png" missing')
            continue
        img = f'/assets/products/ms-track/{slug}'
        boss_by_width = {r['width_mm']: r['boss_mm'] for r in rows}
        profiles.append({
            'id': slug, 'name': name, 'title': f'MS {name} Track Wheels',
            'images': {'photo': f'{img}/photo.jpg', 'thumb': f'{img}/thumb.jpg',
                       'drawings': [{'width_mm': w, 'boss_mm': boss_by_width[w], 'src': f'{img}/drawing-{w}.jpg'} for w in WIDTHS]},
            'source': {'photo': rel(photo), 'drawings': {w: rel(f) for w, f in drawings.items() if f}},
        })
    cover = os.path.join(root, 'Cover image.png')
    if not os.path.exists(cover):
        errors.append('Cover image.png missing')
    if errors:
        print('IMPORT STOPPED - please check:')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    data = {
        'id': 'ms-track', 'name': 'MS Solid Track Wheels', 'url': '/wheels-castors/ms-track/',
        'intro': 'Mild steel solid track wheels in V-groove, square-groove, round-groove and flange-type profiles, '
                 'available in plain bore and ball bearing versions. Maximum working temperature 250 °C.',
        'material': 'Mild Steel', 'max_temp': '250 °C',
        'shared_capacity_note': 'Load capacities are the same for V-groove, square-groove, round-groove and flange-type wheels.',
        'cover': {'image': '/assets/products/ms-track/cover.jpg', 'source': os.path.relpath(cover, REPO).replace('\\', '/')},
        'source_pdf': os.path.relpath(pdf, REPO).replace('\\', '/'),
        'rows': rows, 'profiles': profiles,
    }
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Imported {len(rows)} rows ({len({(r["diameter_mm"], r["width_mm"], r["bore_mm"]) for r in rows})} nominal sizes, '
          f'{sum(r["bearing"] == "Plain Bore" for r in rows)} plain bore, {sum(r["bearing"] == "Ball Bearing" for r in rows)} ball bearing), '
          f'{len(profiles)} profiles; corrections applied: {sum("correction" in r for r in rows)}')


if __name__ == '__main__':
    main()
