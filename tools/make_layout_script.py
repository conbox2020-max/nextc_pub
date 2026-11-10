# 조판 데이터(JSON)를 담은 인디자인 조판 스크립트(UXP .idjs / ExtendScript .jsx 겸용)를 만든다.
# 사용: python3 -I make_layout_script.py <조판 폴더>
import sys, os, json, re
D = sys.argv[1]
order = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "back"]
book = []
for k in order:
    blocks = json.load(open(os.path.join(D, k + ".json"), encoding="utf-8"))
    title = next((b for b in blocks if b["s"] == "장 제목"), None)
    paras = [b for b in blocks if b["s"] != "장 제목"]
    book.append({"key": k, "num": title["n"] if title else "", "title": title["t"] if title else "",
                 "p": [[b["s"], b["t"], b.get("fig") or ""] for b in paras]})
# 도판 크기(mm, 시안 기준). 2-1은 펼침면이라 두 칸.
FIGSIZE = {"1-1": (101, 84), "1-2": (45, 40), "1-3": (101, 84), "1-4": (101, 74), "1-5": (101, 60),
           "2-1": (101, 110), "2-1R": (101, 101), "2-2": (101, 82), "2-3": (101, 64), "2-4": (101, 106), "2-5": (101, 50),
           "3-1": (101, 75), "3-2": (101, 48), "3-3": (101, 78), "3-4": (101, 80), "3-5": (101, 75), "3-6": (101, 81), "3-7": (101, 56),
           "4-1": (101, 156), "4-2": (101, 86), "4-3": (101, 79), "4-4": (101, 82),
           "5-1": (101, 77), "5-2": (101, 62), "5-3": (101, 64), "5-4": (101, 77), "5-5": (101, 98), "5-6": (101, 78), "5-7": (101, 49),
           "6-1": (101, 57), "6-2": (101, 64), "6-4": (101, 109), "6-5": (101, 61),
           "7-1": (101, 48), "7-2": (101, 86), "7-3": (101, 72), "7-4": (101, 98), "7-5": (101, 98), "7-6": (101, 56)}
data = json.dumps({"book": book, "fig": FIGSIZE}, ensure_ascii=False)
JS = r'''// 《10대를 위한 부동산 교양 수업》 본문 조판 스크립트 (자동 생성: tools/make_layout_script.py)
// UXP(.idjs)와 ExtendScript(.jsx) 모두에서 돈다.
// 준비: 인디자인에서 《국부론 수업》 새 조판 파일(국부론수업_본문_새조판.indd)을 열어 둔다. 원본은 읽기만 한다.
// 동작: 새 문서를 만들고 국부론의 스타일·견본·부모 페이지를 가져온 뒤, 원고 1~7장과 뒷부속을 흘려 넣는다.
var ID = (typeof require !== "undefined") ? require("indesign") : null;
var APP = ID ? ID.app : app;
function E(name) { return ID ? ID[name] : eval(name); }   // 열거형 이름 → 값 (UXP/ExtendScript 공통)
var DATA = __DATA__;
var MM = 72 / 25.4;
var log = [];

function findStyle(doc, coll, name) { var s = doc[coll].itemByName(name); return s.isValid ? s : null; }
function setp(obj, k, v) { try { obj[k] = v; } catch (e) { log.push(obj.name + "." + k + ": " + e); } }

function main() {
    if (APP.documents.length === 0) { alert("《국부론 수업》 파일을 먼저 여세요."); return; }
    var src = APP.activeDocument;
    if (!src.saved) { alert("열린 문서를 먼저 저장하세요(스타일을 파일에서 가져옵니다)."); return; }
    var srcFile = src.fullName;
    var MU = E("MeasurementUnits");
    APP.scriptPreferences.measurementUnit = MU.POINTS;

    // 1) 새 문서: 판형 150×214, 여백 위19.5 아래31 안쪽27 바깥22, 1단, 도련 3 (국부론 IDML 값)
    var doc = APP.documents.add();
    var dp = doc.documentPreferences;
    dp.facingPages = true; dp.pageWidth = 150 * MM; dp.pageHeight = 214 * MM;
    dp.documentBleedTopOffset = dp.documentBleedBottomOffset = dp.documentBleedInsideOrLeftOffset = dp.documentBleedOutsideOrRightOffset = 3 * MM;
    var mp = doc.masterSpreads.item(0).pages.item(0).marginPreferences;
    // 2) 국부론에서 스타일·견본·부모 페이지 가져오기
    var CR = E("GlobalClashResolutionStrategy").LOAD_ALL_WITH_OVERWRITE, IF = E("ImportFormat");
    try { doc.loadSwatches(srcFile); } catch (e) { log.push("견본: " + e); }
    try { doc.importStyles(IF.TEXT_STYLES_FORMAT, srcFile, CR); } catch (e) { log.push("문자·문단 스타일: " + e); }
    try { doc.importStyles(IF.OBJECT_STYLES_FORMAT, srcFile, CR); } catch (e) { log.push("개체 스타일: " + e); }
    try { doc.importStyles(IF.TABLE_AND_CELL_STYLES_FORMAT, srcFile, CR); } catch (e) { log.push("표 스타일: " + e); }
    try { doc.loadMasters(srcFile, CR); } catch (e) { log.push("부모 페이지: " + e); }
    var masters = doc.masterSpreads, master = masters.item(masters.length - 1);
    // 3) 이 책용 스타일(제안) 만들기 — 국부론 스타일을 바탕으로
    makeStyles(doc);
    // 4) 장마다 흘리기
    var first = true;
    for (var c = 0; c < DATA.book.length; c++) {
        var ch = DATA.book[c];
        var page;
        if (first) { page = doc.pages.item(0); first = false; } else { page = doc.pages.add(E("LocationOptions").AT_END); }
        if (ch.num) {
            // 도비라 펼침면(짝수 쪽 + 홀수 쪽): 지금 쪽이 홀수면 빈 쪽 하나를 둔다
            if ((page.documentOffset + 1) % 2 === 1) { page.appliedMaster = master; page = doc.pages.add(E("LocationOptions").AT_END); }
            page.appliedMaster = master;
            var right = doc.pages.add(E("LocationOptions").AT_END); right.appliedMaster = master;
            dobira(doc, right, ch);
            page = doc.pages.add(E("LocationOptions").AT_END);
        }
        page.appliedMaster = master;
        flow(doc, page, ch, master);
    }
    APP.scriptPreferences.measurementUnit = MU.AUTO_VALUE;
    alert("조판 완료: " + doc.pages.length + "쪽\n" + (log.length ? ("확인 필요 " + log.length + "건\n" + log.slice(0, 15).join("\n")) : ""));
}

function frameBounds(page) {
    var b = page.bounds, top = 19.5 * MM, bot = 31 * MM, ins = 27 * MM, out = 22 * MM;
    var isRight = (page.side == E("PageSideOptions").RIGHT_HAND);
    return [b[0] + top, b[1] + (isRight ? ins : out), b[2] - bot, b[3] - (isRight ? out : ins)];
}

function dobira(doc, page, ch) {
    var b = page.bounds, bl = 3 * MM;
    var r = page.rectangles.add({ geometricBounds: [b[0] - bl, b[1], b[2] + bl, b[3] + bl] });
    setp(r, "fillColor", doc.swatches.itemByName("C=0 M=0 Y=0 K=80").isValid ? doc.swatches.itemByName("C=0 M=0 Y=0 K=80") : doc.swatches.itemByName("Black"));
    var t = page.textFrames.add({ geometricBounds: [b[0] + 95 * MM, b[1] + 38.3 * MM, b[0] + 160 * MM, b[1] + 115 * MM] });
    t.contents = ch.num + "\r" + ch.title + "\r\r[도비라 자리 — 공통 일러스트: 시안/illust/도비라_공통_v1.png]";
    var ps = findStyle(doc, "paragraphStyles", "도비라 제목");
    if (ps) t.parentStory.paragraphs.everyItem().appliedParagraphStyle = ps;
}

function flow(doc, page, ch, master) {
    var tf = page.textFrames.add({ geometricBounds: frameBounds(page) });
    var texts = [];
    for (var i = 0; i < ch.p.length; i++) texts.push(ch.p[i][1]);
    tf.contents = texts.join("\r");
    var story = tf.parentStory, paras = story.paragraphs;
    for (var j = 0; j < ch.p.length && j < paras.length; j++) {
        var st = findStyle(doc, "paragraphStyles", ch.p[j][0]);
        if (st) paras.item(j).applyParagraphStyle(st, true); else log.push("스타일 없음: " + ch.p[j][0]);
    }
    // 도판 자리: 시안 크기의 회색 인라인 상자(쪽수를 실제와 가깝게)
    for (var k = ch.p.length - 1; k >= 0; k--) {
        var fid = ch.p[k][2];
        if (!fid || k >= paras.length) continue;
        var ids = (fid === "2-1") ? ["2-1R", "2-1"] : [fid];
        for (var q = 0; q < ids.length; q++) {
            var sz = DATA.fig[ids[q]] || [101, 60];
            try {
                var box = paras.item(k).insertionPoints.item(0).textFrames.add();
                box.geometricBounds = [0, 0, sz[1] * MM, sz[0] * MM];
                box.contents = "[도" + ids[q].replace("R", " 오른쪽") + "] " + sz[0] + "×" + sz[1] + "mm — 시안 PDF를 놓을 자리";
                box.fillColor = doc.swatches.itemByName("C=0 M=0 Y=0 K=20").isValid ? doc.swatches.itemByName("C=0 M=0 Y=0 K=20") : doc.swatches.itemByName("Paper");
            } catch (e) { log.push("도판 자리 " + fid + ": " + e); }
        }
    }
    // 넘친 글을 새 쪽으로 이어 흘리기
    var last = tf, guard = 0;
    while (last.overflows && guard++ < 400) {
        var np = doc.pages.add(E("LocationOptions").AT_END);
        np.appliedMaster = master;
        var nf = np.textFrames.add({ geometricBounds: frameBounds(np) });
        last.nextTextFrame = nf; last = nf;
    }
}

function makeStyles(doc) {
    var P = doc.paragraphStyles;
    function mk(name, base, props) {
        var s = P.itemByName(name);
        if (!s.isValid) s = P.add({ name: name });
        var b = P.itemByName(base); if (b.isValid) setp(s, "basedOn", b);
        for (var i = 0; i < props.length; i++) setp(s, props[i][0], props[i][1]);
        return s;
    }
    var SP = E("StartParagraph"), J = E("Justification");
    var yellow = doc.swatches.itemByName("C=0 M=6 Y=68 K=0"), teal = doc.swatches.itemByName("도해_청록 c80m30y40");
    // [제안] 절 제목: 국부론 '대제목'과 같은 서체·크기·색, 새 쪽 시작만 끔
    mk("절 제목", "대제목", [["startParagraph", SP.ANYWHERE], ["spaceBefore", 39], ["spaceAfter", 6.5], ["keepWithNext", 3]]);
    // [레퍼런스] 소제목 = 국부론 '큰 제목'
    mk("소제목", "큰 제목", [["spaceBefore", 13]]);
    // [제안] 셋째 단계 제목
    mk("소소제목", "본문", [["appliedFont", "Sandoll 고딕Neo1"], ["fontStyle", "07 Bd"], ["pointSize", 10.5], ["firstLineIndent", 0], ["spaceBefore", 6.5], ["keepWithNext", 2]]);
    mk("질문 제목", "소소제목", [["fillColor", teal]]);
    mk("목록", "본문", [["leftIndent", 4 * MM], ["firstLineIndent", -4 * MM]]);
    mk("번호 목록", "본문", [["leftIndent", 5 * MM], ["firstLineIndent", -5 * MM]]);
    // [제안] '잠깐!' 상자: 국부론 상자와 같은 연노랑(0/6/68/0)을 문단 음영으로
    var shade = [["paragraphShadingOn", true], ["paragraphShadingColor", yellow], ["paragraphShadingTopOffset", 4 * MM],
                 ["paragraphShadingBottomOffset", 3 * MM], ["paragraphShadingLeftOffset", 3 * MM], ["paragraphShadingRightOffset", 3 * MM]];
    mk("잠깐 라벨", "만화 대사", [["justification", J.LEFT_ALIGN], ["pointSize", 13], ["leftIndent", 3 * MM], ["rightIndent", 3 * MM], ["spaceBefore", 26], ["keepWithNext", 2]].concat(shade));
    mk("잠깐 본문", "본문", [["firstLineIndent", 0], ["leftIndent", 3 * MM], ["rightIndent", 3 * MM], ["spaceAfter", 26]].concat(shade));
    mk("도판 자리", "본문", [["firstLineIndent", 0], ["justification", J.CENTER_ALIGN], ["spaceBefore", 6.5], ["spaceAfter", 13]]);
    mk("참고 자료", "본문", [["appliedFont", "Sandoll 고딕Neo1"], ["fontStyle", "Lt"], ["pointSize", 8], ["leading", 12], ["firstLineIndent", -6 * MM], ["leftIndent", 6 * MM]]);
    mk("참고 자료 제목", "소소제목", [["spaceBefore", 13]]);
    var white = doc.swatches.itemByName("Paper");
    mk("도비라 제목", "대제목", [["appliedFont", "Sandoll 격동굴림2"], ["fontStyle", "06 Hv"], ["pointSize", 18], ["fillColor", white], ["justification", J.CENTER_ALIGN], ["startParagraph", SP.ANYWHERE]]);
}

main();
'''
JS = JS.replace("__DATA__", data)
for ext in ("idjs", "jsx"):
    with open(os.path.join(D, f"조판_부동산교양수업.{ext}"), "w", encoding="utf-8-sig" if ext == "jsx" else "utf-8") as f:
        f.write(JS)
print("ok", len(JS))
