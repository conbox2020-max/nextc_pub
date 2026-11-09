# 지정한 쪽이 속한 스프레드의 독립 텍스트 프레임(캡션·도해 라벨)을 문단 스타일과 함께 출력한다.
# 사용: python3 -I idml_context.py <압축 푼 IDML 폴더> 28,32,54
import sys, os
import xml.etree.ElementTree as ET
root=sys.argv[1]; want=set(sys.argv[2].split(','))
dm=ET.parse(os.path.join(root,'designmap.xml')).getroot()
sfs=[e.get('src') for e in dm.iter() if e.get('src','').startswith('Spreads/')]
def story(sid):
    p=os.path.join(root,'Stories',f'Story_{sid}.xml')
    if not os.path.exists(p): return []
    out=[]
    for psr in ET.parse(p).getroot().iter('ParagraphStyleRange'):
        st=psr.get('AppliedParagraphStyle','').replace('ParagraphStyle/','')
        txt=''.join(c.text or '' for c in psr.iter('Content')).strip()
        if txt: out.append((st,txt))
    return out
for sf in sfs:
    sp=ET.parse(os.path.join(root,sf)).getroot()
    pages=[p.get('Name') for p in sp.iter('Page')]
    if not want & set(pages): continue
    print('=== PAGES',pages)
    seen=set()
    for tf in sp.iter('TextFrame'):
        if tf.get("PreviousTextFrame","n")!="n" or tf.get("NextTextFrame","n")!="n": continue
        s=tf.get("ParentStory")
        if s in seen: continue
        seen.add(s)
        for st,t in story(s):
            print(f'  [{st}] {t[:90]}')
