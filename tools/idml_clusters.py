"""서식 조합(서체/크기/행간/정렬/색) 단위로 실사용 텍스트를 묶는다. usage: clusters.py <idml_dir> [min_chars]"""
import sys, os, glob, re
import xml.etree.ElementTree as ET
from collections import defaultdict
D = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 60

fonts = {}
for fam in ET.parse(os.path.join(D, 'Resources/Fonts.xml')).getroot().iter('FontFamily'):
    for f in fam.iter('Font'): fonts[(fam.get('Name'), f.get('FontStyleName'))] = f.get('PostScriptName')
S = ET.parse(os.path.join(D, 'Resources/Styles.xml')).getroot()
KEYS = ['FontStyle', 'PointSize', 'Justification', 'FillColor', 'FillTint', 'Tracking', 'FirstLineIndent', 'LeftIndent', 'SpaceBefore', 'HorizontalScale', 'Skew']
def vals(el):
    v = {k: el.get(k) for k in KEYS if el.get(k) is not None}
    pr = el.find('Properties')
    if pr is not None:
        for p in ('Leading', 'AppliedFont', 'BasedOn'):
            x = pr.find(p)
            if x is not None and x.text: v[p] = x.text
    return v
st = {}
for el in list(S.iter('ParagraphStyle')) + list(S.iter('CharacterStyle')): st[el.get('Self')] = (el.get('Name'), vals(el))
def res(sid, pref):
    if sid not in st: return {}
    n, v = st[sid]; b = v.get('BasedOn'); out = {}
    if b and b != sid:
        out = res(b if '/' in b else pref + b, pref)
    out.update({k: x for k, x in v.items() if k != 'BasedOn'}); return out

master = set()
for mf in glob.glob(os.path.join(D, 'MasterSpreads/*.xml')):
    for tf in ET.parse(mf).getroot().iter('TextFrame'): master.add(tf.get('ParentStory'))

cl = defaultdict(lambda: [0, [], set()])
for sf in glob.glob(os.path.join(D, 'Stories/*.xml')):
    story = ET.parse(sf).getroot().find('Story')
    if story.get('Self') in master: continue
    for psr in story.iter('ParagraphStyleRange'):
        ps = psr.get('AppliedParagraphStyle'); base = res(ps, 'ParagraphStyle/'); base.update(vals(psr))
        for csr in psr.findall('CharacterStyleRange'):
            e = dict(base); cs = csr.get('AppliedCharacterStyle')
            if cs: e.update(res(cs, 'CharacterStyle/'))
            e.update(vals(csr))
            t = ''.join(c.text or '' for c in csr.findall('Content')).strip()
            if not t: continue
            f = fonts.get((e.get('AppliedFont'), e.get('FontStyle')), f"{e.get('AppliedFont')}/{e.get('FontStyle')}")
            def r(x):
                try: return str(round(float(x), 2))
                except: return str(x)
            key = (f, r(e.get('PointSize')), r(e.get('Leading', 'Auto')), e.get('Justification'), e.get('FillColor'), e.get('FillTint'),
                   r(e.get('Tracking')), r(e.get('FirstLineIndent')), r(e.get('LeftIndent')), r(e.get('HorizontalScale')), e.get('Skew'))
            c = cl[key]; c[0] += len(t); c[2].add(st.get(ps, (ps,))[0])
            if len(c[1]) < 3: c[1].append(t[:45])
tot = sum(c[0] for c in cl.values())
print('font|pt|leading|just|fill|tint|track|1stIndent|leftIndent|hscale|skew')
for k, c in sorted(cl.items(), key=lambda x: -x[1][0]):
    if c[0] < MIN: continue
    print(f'{c[0]:>7} {100*c[0]/tot:5.1f}%', ' | '.join(str(x) for x in k), '| P:', ','.join(sorted(map(str, c[2])))[:60], '| EX:', c[1])
