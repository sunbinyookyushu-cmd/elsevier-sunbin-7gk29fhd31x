# -*- coding: utf-8 -*-
from docx import Document
d = Document('GACI_coauthor_report.docx')
print('=== HEADINGS ===')
for p in d.paragraphs:
    if p.style.name.startswith('Heading') and p.text.strip():
        print('  ', p.text)
print('=== TABLES:', len(d.tables), '===')
for i, t in enumerate(d.tables):
    row0 = ' | '.join(c.text.replace('\n', ' ')[:16] for c in t.rows[0].cells)
    print('  Table%d: %dx%d  row0= %s' % (i, len(t.rows), len(t.columns), row0[:95]))
allt = '\n'.join(p.text for p in d.paragraphs)
print('=== shock content check (should be False) ===')
for kw in ['shock', 'COVID', 'Russia', 'Table 3', 'disruption', 'collapse']:
    print('  %-12s in body: %s' % (repr(kw), kw.lower() in allt.lower()))
# Panel A label of Table 1
print('=== Table 1 panel rows ===')
for t in d.tables:
    for r in t.rows:
        c0 = r.cells[0].text
        if 'Panel' in c0:
            print('  ', c0[:70])
