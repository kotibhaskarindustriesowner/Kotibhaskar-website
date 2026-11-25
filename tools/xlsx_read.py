"""Minimal .xlsx reader (standard library only) used by the equipment importer.

Reads the first worksheet of a workbook into rows of {column_letter: text}. Only cell
text is read; embedded images are ignored. Price columns are never needed by the
importer and are dropped by the callers, so nothing here is published directly."""
import re
import zipfile
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
_T = '{%s}t' % NS['m']


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def clean(s):
    """Collapse the workbook's double spaces and non-breaking spaces."""
    return re.sub(r'\s+', ' ', (s or '').replace('\xa0', ' ')).strip()


def read_rows(path):
    """Return a list of (row_number, {col_letter: text}) for the first sheet."""
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            shared.append(''.join(t.text or '' for t in si.iter(_T)))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {x.get('Id'): x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheet = wb.find('m:sheets', NS)[0]
    target = rels[sheet.get('{%s}id' % NS['r'])].lstrip('/')
    target = target if target.startswith('xl/') else 'xl/' + target
    rows = []
    for row in ET.fromstring(z.read(target)).iter('{%s}row' % NS['m']):
        cells = {}
        for c in row.findall('m:c', NS):
            v = c.find('m:v', NS)
            t = c.get('t')
            if t == 's' and v is not None:
                val = shared[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(_T))
            elif v is not None:
                val = v.text
            else:
                continue
            val = clean(val)
            if val:
                cells[re.match(r'[A-Z]+', c.get('r')).group()] = val
        if cells:
            rows.append((int(row.get('r')), cells))
    return rows


def pages(rows):
    """Split rows into printed pages. Each page starts with a 'Price List' header row;
    its title is the next non-'Price List' cell on that row and the subtitle is the
    following row's cell in the same column."""
    out, cur = [], None
    for i, (n, cells) in enumerate(rows):
        if cells.get('A') == 'Price List':
            title = next((v for k, v in sorted(cells.items(), key=lambda kv: col_index(kv[0])) if k != 'A'), '')
            sub = ''
            if i + 1 < len(rows):
                nxt = rows[i + 1][1]
                sub = next((v for k, v in sorted(nxt.items(), key=lambda kv: col_index(kv[0])) if k != 'A'), '')
            cur = {'title': title, 'subtitle': sub, 'rows': []}
            out.append(cur)
            continue
        if cur is not None:
            if any('Commercial Terms' in v for v in cells.values()):
                cur = None          # commercial terms and bank details: never read
                continue
            cur['rows'].append((n, cells))
    return out
