# IDML에 배치된 이미지(링크 파일명·프레임 크기 mm·개체 스타일)를 스프레드별로 출력한다.
# 사용: python3 -I idml_graphics.py <압축 푼 IDML 폴더>
import sys, os, re, glob
import xml.etree.ElementTree as ET
from urllib.parse import unquote
root = sys.argv[1]
PT2MM = 25.4/72
def mm(v): return round(float(v)*PT2MM,1)
dm = ET.parse(os.path.join(root,'designmap.xml')).getroot()
spread_files = [e.get('src') for e in dm.iter() if e.tag.endswith('Spread') and e.get('src','').startswith('Spreads/')]
# page size
pref = ET.parse(os.path.join(root,'Resources/Preferences.xml')).getroot()
dp = pref.find('.//DocumentPreference')
print('PAGE', mm(dp.get('PageWidth')), 'x', mm(dp.get('PageHeight')), 'facing', dp.get('FacingPages'))
mp = pref.find('.//MarginPreference')
if mp is not None: print('MARGIN T/B/L/R(in/out)', mm(mp.get('Top')), mm(mp.get('Bottom')), mm(mp.get('Left')), mm(mp.get('Right')), 'cols', mp.get('ColumnCount'), 'gutter', mm(mp.get('ColumnGutter')))
def bounds(el):
    # PathPointArray anchors -> bbox in item coords, then apply ItemTransform scale only (approx)
    pts=[tuple(map(float,p.get('Anchor').split())) for p in el.iter('PathPointType')]
    if not pts: return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    t=list(map(float,el.get('ItemTransform','1 0 0 1 0 0').split()))
    w=(max(xs)-min(xs))*abs(t[0]) if t[0] else (max(ys)-min(ys))*abs(t[1])
    h=(max(ys)-min(ys))*abs(t[3]) if t[3] else (max(xs)-min(xs))*abs(t[2])
    return mm(w), mm(h)
pageno=0
for sf in spread_files:
    sp = ET.parse(os.path.join(root,sf)).getroot()
    pages=[p.get('Name') for p in sp.iter('Page')]
    items=[]
    for fr in sp.iter():
        if fr.tag in ('Rectangle','Oval','Polygon'):
            link=None
            for l in fr.iter('Link'):
                link=os.path.basename(unquote(l.get('LinkResourceURI','')))
            if link:
                b=bounds(fr)
                items.append(f"{link} [{b[0]}x{b[1]}mm] os={fr.get('AppliedObjectStyle','').replace('ObjectStyle/','')}")
    if items:
        print('PAGES', ','.join(pages))
        for i in items: print('   ', i)
