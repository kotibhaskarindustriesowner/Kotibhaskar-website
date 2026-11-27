"""One-off: seed data/sitemap-lastmod.json from git history.

    python tools/seed_sitemap_lastmod.py

For every URL in sitemap.xml it walks back through the committed versions of the page and records the
date of the commit in which the page's content (ignoring ?v= asset stamps) last changed. After this,
tools/build_site.py keeps the file up to date: a page's date only moves when its own content changes.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as h  # noqa: E402


def git(*args):
    return subprocess.run(['git', *args], cwd=h.REPO, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def version(sha, rel):
    """A committed version of a page (cat-file: 'git show' fails on long Windows paths)."""
    out = git('cat-file', '-p', f'{sha}:{rel}')
    assert out, f'could not read {rel} at {sha}'
    return out


urls = [u.replace(h.SITE, '') for u in re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(h.REPO, 'sitemap.xml'), encoding='utf-8').read())]
store = {}
for u in urls:
    rel = os.path.relpath(h.page_file(u), h.REPO).replace('\\', '/')
    log = [l.split(' ', 1) for l in git('log', '--format=%H %cs', '--', rel).splitlines() if l.strip()]
    if not log:
        continue
    head = h.page_fingerprint(version(log[0][0], rel))
    date = log[0][1]
    for sha, d in log[1:]:
        if h.page_fingerprint(version(sha, rel)) != head:
            break
        date = d                              # same content in this older commit: it changed no later than this
    store[u] = {'hash': head, 'date': date}
with open(h.LASTMOD_FILE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(store, f, indent=1, sort_keys=True)
    f.write('\n')
from collections import Counter
print(len(store), 'pages seeded;', Counter(v['date'] for v in store.values()).most_common())
