"""IDML 타이포그래피 추출기 (읽기 전용). usage: python3 -I extract.py <unzipped_idml_dir> <out.json>"""
import sys, os, re, json, glob
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

D, OUT = sys.argv[1], sys.argv[2]
PT2MM = 25.4 / 72

def mm(v):
    try: return round(float(v) * PT2MM, 2)
    except: return v

def parse(p):
    return ET.parse(os.path.join(D, p)).getroot()

# ---------- fonts: family + style -> PostScript ----------
fonts = {}
for fam in parse('Resources/Fonts.xml').iter('FontFamily'):
    for f in fam.iter('Font'):
        fonts[(fam.get('Name'), f.get('FontStyleName'))] = f.get('PostScriptName')

def ps(fam, sty):
    if not fam: return None
    return fonts.get((fam, sty)) or f'{fam} / {sty} (PS명 미확인)'

# ---------- styles ----------
ATTRS = ['FontStyle', 'PointSize', 'Tracking', 'HorizontalScale', 'VerticalScale', 'KerningMethod',
         'Justification', 'FirstLineIndent', 'LeftIndent', 'RightIndent', 'SpaceBefore', 'SpaceAfter',
         'AlignToBaseline', 'Hyphenation', 'Composer', 'KeepWithNext', 'KeepLinesTogether',
         'KeepAllLinesTogether', 'KeepFirstLines', 'KeepLastLines', 'StartParagraph', 'FillColor',
         'FillTint', 'BaselineShift', 'Capitalization', 'Underline', 'SpanColumnType',
         'KinsokuSet', 'KinsokuType', 'MojikumiTable', 'LeadingModel', 'CharacterAlignment',
         'RuleAbove', 'RuleBelow', 'RuleAboveColor', 'RuleBelowColor', 'ParagraphShadingOn',
         'ParagraphBorderOn', 'DropCapLines', 'DropCapCharacters', 'StrokeColor', 'Skew',
         'DesiredWordSpacing', 'MinimumWordSpacing', 'MaximumWordSpacing',
         'DesiredLetterSpacing', 'MinimumLetterSpacing', 'MaximumLetterSpacing', 'SingleWordJustification',
         'AutoLeading', 'GridAlignment', 'GridAlignFirstLineOnly', 'BulletsAndNumberingListType', 'Position']
PROPS = ['Leading', 'AppliedFont', 'BasedOn', 'BalanceRaggedLines']

def node_vals(el):
    v = {a: el.get(a) for a in ATTRS if el.get(a) is not None}
    pr = el.find('Properties')
    if pr is not None:
        for p in PROPS:
            x = pr.find(p)
            if x is not None and x.text is not None:
                v[p] = x.text
    return v

S = parse('Resources/Styles.xml')
styles = {'para': {}, 'char': {}}
for tag, key in [('ParagraphStyle', 'para'), ('CharacterStyle', 'char')]:
    for el in S.iter(tag):
        v = node_vals(el)
        v['_self'] = el.get('Self'); v['_name'] = el.get('Name'); v['_next'] = el.get('NextStyle')
        styles[key][el.get('Self')] = v

def resolve(key, sid, seen=None):
    seen = seen or set()
    st = styles[key].get(sid)
    if not st or sid in seen: return {}
    seen.add(sid)
    base = st.get('BasedOn')
    out = {}
    if base:
        bid = base if base.startswith(('ParagraphStyle/', 'CharacterStyle/')) else \
              ('ParagraphStyle/' if key == 'para' else 'CharacterStyle/') + base
        out = resolve(key, bid, seen)
    out.update({k: v for k, v in st.items() if not k.startswith('_')})
    return out

def other_styles(tag):
    res = []
    for el in S.iter(tag):
        d = dict(el.attrib); res.append({k: d[k] for k in d if k in (
            'Name', 'AppliedParagraphStyle', 'TopInset', 'BottomInset', 'LeftInset', 'RightInset',
            'FillColor', 'StrokeColor', 'StrokeWeight', 'CornerOption', 'CornerRadius')})
    return res

# ---------- stories: actual usage ----------
master_story_ids = set()
for mf in glob.glob(os.path.join(D, 'MasterSpreads/*.xml')):
    for tf in ET.parse(mf).getroot().iter('TextFrame'):
        master_story_ids.add(tf.get('ParentStory'))

usage = defaultdict(lambda: {'chars': 0, 'paras': 0, 'eff': defaultdict(Counter), 'char_styles': Counter(), 'local_override_chars': 0, 'samples': []})
cstyle_usage = defaultdict(lambda: {'chars': 0, 'eff': defaultdict(Counter), 'samples': []})
footnote_chars = Counter()

EFF_KEYS = ['Font', 'PointSize', 'Leading', 'Tracking', 'HorizontalScale', 'Justification',
            'FirstLineIndent', 'LeftIndent', 'SpaceBefore', 'SpaceAfter', 'FillColor', 'AlignToBaseline', 'Hyphenation']

def text_of(el):
    t = []
    for c in el.iter():
        if c.tag == 'Content' and c.text: t.append(c.text)
        elif c.tag == 'Br': t.append('\n')
    return ''.join(t)

for sf in sorted(glob.glob(os.path.join(D, 'Stories/*.xml'))):
    root = ET.parse(sf).getroot()
    story = root.find('Story')
    sid = story.get('Self')
    is_master = sid in master_story_ids
    for psr in story.iter('ParagraphStyleRange'):
        pstyle = psr.get('AppliedParagraphStyle')
        base = resolve('para', pstyle)
        plocal = node_vals(psr)
        key = ('[마스터] ' if is_master else '') + (styles['para'].get(pstyle, {}).get('_name') or pstyle)
        u = usage[key]
        ptext = ''
        for csr in psr.findall('CharacterStyleRange'):
            cstyle = csr.get('AppliedCharacterStyle')
            cres = resolve('char', cstyle) if cstyle else {}
            clocal = node_vals(csr)
            eff = dict(base); eff.update(plocal)
            for k, v in cres.items():
                if k != 'BasedOn': eff[k] = v
            eff.update(clocal)
            txt = ''.join(c.text or '' for c in csr.findall('Content'))
            n = len(txt.strip())
            ptext += txt + ('\n' if csr.find('Br') is not None else '')
            if n == 0: continue
            u['chars'] += n
            eff['Font'] = ps(eff.get('AppliedFont'), eff.get('FontStyle'))
            for k in EFF_KEYS:
                val = eff.get(k)
                if k == 'Leading' and val is None: val = 'Auto'
                u['eff'][k][str(val)] += n
            cname = styles['char'].get(cstyle, {}).get('_name', cstyle) if cstyle else None
            if cname and 'No character style' not in cname:
                u['char_styles'][cname] += n
                cu = cstyle_usage[cname]; cu['chars'] += n
                for k in ['Font', 'PointSize', 'Tracking', 'HorizontalScale', 'FillColor', 'BaselineShift', 'Underline']:
                    cu['eff'][k][str(eff.get(k))] += n
                if len(cu['samples']) < 3: cu['samples'].append(txt.strip()[:40])
            loc = {k for k in clocal if k not in ('BasedOn',)} | {k for k in plocal}
            if loc & {'PointSize', 'Leading', 'AppliedFont', 'FontStyle', 'Tracking', 'HorizontalScale'}:
                u['local_override_chars'] += n
        u['paras'] += max(1, ptext.count('\n'))
        s = ptext.strip().replace('\n', ' / ')
        if s and len(u['samples']) < 4 and s[:50] not in u['samples']:
            u['samples'].append(s[:50])
    # footnotes
    for fn in story.iter('Footnote'):
        for psr in fn.iter('ParagraphStyleRange'):
            footnote_chars[styles['para'].get(psr.get('AppliedParagraphStyle'), {}).get('_name')] += len(text_of(psr))

# ---------- masters & spreads ----------
def bounds_of_tf(tf):
    # PathPointArray anchors -> bbox, then transform
    pts = [tuple(map(float, a.get('Anchor').split())) for a in tf.iter('PathPointType')]
    if not pts: return None
    t = list(map(float, tf.get('ItemTransform').split()))
    xs = [t[0]*x + t[2]*y + t[4] for x, y in pts]; ys = [t[1]*x + t[3]*y + t[5] for x, y in pts]
    return (min(xs), min(ys), max(xs), max(ys))

def story_summary(story_id):
    p = os.path.join(D, f'Stories/Story_{story_id}.xml')
    if not os.path.exists(p): return None
    st = ET.parse(p).getroot().find('Story')
    raw = open(p, encoding='utf8').read()
    out = []
    for psr in st.iter('ParagraphStyleRange'):
        pn = styles['para'].get(psr.get('AppliedParagraphStyle'), {}).get('_name')
        base = resolve('para', psr.get('AppliedParagraphStyle')); base.update(node_vals(psr))
        for csr in psr.findall('CharacterStyleRange'):
            e = dict(base); cs = csr.get('AppliedCharacterStyle')
            if cs: e.update({k: v for k, v in resolve('char', cs).items() if k != 'BasedOn'})
            e.update(node_vals(csr))
            t = ''.join(c.text or '' for c in csr.findall('Content'))
            out.append({'pstyle': pn, 'text': t[:60], 'font': ps(e.get('AppliedFont'), e.get('FontStyle')),
                        'size': e.get('PointSize'), 'tracking': e.get('Tracking'), 'just': e.get('Justification'),
                        'fill': e.get('FillColor'), 'hscale': e.get('HorizontalScale')})
    return {'runs': out, 'has_pagenum': '<?ACE 18?>' in raw, 'has_section_marker': '<?ACE 19?>' in raw,
            'textvars': re.findall(r'<TextVariableInstance[^>]*ResultText="([^"]*)"[^>]*AssociatedTextVariable="([^"]*)"', raw)}

masters = []
for mf in sorted(glob.glob(os.path.join(D, 'MasterSpreads/*.xml'))):
    ms = ET.parse(mf).getroot().find('MasterSpread')
    m = {'name': ms.get('Name'), 'basedOn': ms.get('AppliedMaster'), 'pages': [], 'frames': []}
    for pg in ms.findall('Page'):
        mp = pg.find('MarginPreference')
        gb = list(map(float, pg.get('GeometricBounds').split()))
        it = list(map(float, pg.get('ItemTransform').split()))
        m['pages'].append({'name': pg.get('Name'), 'w_mm': mm(gb[3]-gb[1]), 'h_mm': mm(gb[2]-gb[0]),
                           'x_off': gb[1] + it[4], 'y_off': gb[0] + it[5],
                           'margin_mm': {k: mm(mp.get(k)) for k in ('Top', 'Bottom', 'Left', 'Right')} if mp is not None else None,
                           'columns': mp.get('ColumnCount') if mp is not None else None,
                           'gutter_mm': mm(mp.get('ColumnGutter')) if mp is not None else None})
    for tf in ms.iter('TextFrame'):
        b = bounds_of_tf(tf)
        m['frames'].append({'bbox_pt': b, 'story': story_summary(tf.get('ParentStory')),
                            'objstyle': tf.get('AppliedObjectStyle')})
    masters.append(m)

# body pages: master usage, main text frame size
master_use = Counter(); frame_sizes = Counter(); text_frame_cols = Counter()
self2master = {}
for mf in glob.glob(os.path.join(D, 'MasterSpreads/*.xml')):
    ms = ET.parse(mf).getroot().find('MasterSpread'); self2master[ms.get('Self')] = ms.get('Name')
for sf in glob.glob(os.path.join(D, 'Spreads/*.xml')):
    sp = ET.parse(sf).getroot().find('Spread')
    for pg in sp.findall('Page'):
        master_use[self2master.get(pg.get('AppliedMaster'), pg.get('AppliedMaster'))] += 1
    for tf in sp.iter('TextFrame'):
        b = bounds_of_tf(tf)
        if b:
            w, h = round(mm(b[2]-b[0]), 1), round(mm(b[3]-b[1]), 1)
            frame_sizes[f'{w}x{h}'] += 1
        tfp = tf.find('TextFramePreference')
        if tfp is not None: text_frame_cols[(tfp.get('TextColumnCount'), tfp.get('UseFixedColumnWidth'))] += 1

P = parse('Resources/Preferences.xml')
def first(tag):
    e = P.find('.//' + tag); return dict(e.attrib) if e is not None else None
prefs = {k: first(k) for k in ['DocumentPreference', 'GridPreference', 'MarginPreference', 'FootnoteOption',
                                'TextPreference', 'TextDefault', 'TextFramePreference', 'BaselineFrameGridOption']}
dm = parse('designmap.xml')
sections = [dict(s.attrib) for s in dm.iter('Section')]
textvars = []
for tv in dm.iter('TextVariable'):
    d = dict(tv.attrib)
    for c in tv:
        d['_pref'] = dict(c.attrib)
    textvars.append(d)

# ---------- swatches ----------
G = parse('Resources/Graphic.xml')
colors = [{k: c.get(k) for k in ('Name', 'Model', 'Space', 'ColorValue', 'AlternateSpace', 'AlternateColorValue')} for c in G.iter('Color')]
tints = [{k: c.get(k) for k in ('Self', 'Name', 'BaseColor', 'TintValue')} for c in G.iter('Tint')]
inks = [{k: c.get(k) for k in ('Name', 'IsProcessInk', 'InkType')} for c in G.iter('Ink')]

def counter_top(c, n=4, total=None):
    total = total or sum(c.values()) or 1
    return [(k, round(v*100/total, 1)) for k, v in c.most_common(n)]

usage_out = {}
for k, u in sorted(usage.items(), key=lambda x: -x[1]['chars']):
    usage_out[k] = {'chars': u['chars'], 'paras': u['paras'], 'local_override_pct': round(100*u['local_override_chars']/max(1, u['chars']), 1),
                    'eff': {kk: counter_top(vv) for kk, vv in u['eff'].items()},
                    'char_styles': dict(u['char_styles'].most_common(6)), 'samples': u['samples']}

json.dump({
    'para_styles_resolved': {v['_name']: dict(resolve('para', k), _next=styles['para'].get(v['_next'], {}).get('_name'),
                                             _font_ps=ps(resolve('para', k).get('AppliedFont'), resolve('para', k).get('FontStyle')))
                             for k, v in styles['para'].items()},
    'char_styles_resolved': {v['_name']: dict(resolve('char', k), _font_ps=ps(resolve('char', k).get('AppliedFont'), resolve('char', k).get('FontStyle')))
                             for k, v in styles['char'].items()},
    'object_styles': other_styles('ObjectStyle'), 'table_styles': other_styles('TableStyle'), 'cell_styles': other_styles('CellStyle'),
    'usage': usage_out,
    'char_usage': {k: {'chars': v['chars'], 'eff': {kk: counter_top(vv) for kk, vv in v['eff'].items()}, 'samples': v['samples']} for k, v in cstyle_usage.items()},
    'footnotes': dict(footnote_chars),
    'masters': masters, 'master_use': dict(master_use), 'frame_sizes_top': frame_sizes.most_common(12),
    'text_frame_cols': {str(k): v for k, v in text_frame_cols.items()},
    'prefs': prefs, 'sections': sections, 'textvars': textvars,
    'colors': colors, 'tints': tints, 'inks': inks,
}, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=1, default=str)
print('ok', OUT)
