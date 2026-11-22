# Product page tools

The website is plain static HTML served by GitHub Pages. Product pages are
**generated** from data files by these scripts, then committed. GitHub does
not run any build; there is no server or database.

```
product-sources/  (local only, git-ignored)      Word specs + full-size photos/drawings
        │  tools/import_wheels.py   reads Word tables verbatim, checks them against folder names
        ▼
data/products/wheels/<category>.json             one data file per wheel category
        │  tools/optimise_images.ps1  makes web-size JPEGs
        ▼
assets/products/wheels/<category>/               <slug>-photo.jpg, -thumb.jpg, -drawing.jpg
        │  tools/build_site.py      writes all pages + sitemap.xml
        ▼
wheels-castors/<category>/<slug>/index.html      e.g. /wheels-castors/uhmw/md-75x32/
```

## Update or rebuild a category (e.g. after correcting a Word file)

Run from the repository folder:

```powershell
python tools/import_wheels.py uhmw
powershell -ExecutionPolicy Bypass -File tools\optimise_images.ps1 uhmw
python tools/build_site.py
```

The importer **stops with a list of problems** (missing file, unreadable Word
document, diameter/width/inch not matching the folder name) instead of
publishing doubtful data.

## Add a new wheel category (e.g. PU-CI wheels)

1. Put the product folders in `product-sources/30 Wheels & Caster/<NN Name>/`,
   named like `001 PUCI - MD - 100 x 40 (4 Inch)`, each holding one `.docx`,
   one photo and one drawing named `... (2).png` or `.jpg`.
2. Copy `data/products/wheels/uhmw.json` to `data/products/wheels/puci.json`,
   edit `id`, `name`, `full_name`, `material`, `url`, `source_dir`, `intro`,
   `features` and `groups`, and set `"products": []`.
3. Run the three commands above with `puci` instead of `uhmw`.
4. To route the homepage card to the new pages, add the popup id to
   `var PAGES={...}` in `index.html`.

## Rules
- Never edit files in `wheels-castors/` by hand — they are overwritten on each build.
- Spec values come only from the Word documents; nothing is typed in by hand.
- Original files in `product-sources/` are only read, never changed.
