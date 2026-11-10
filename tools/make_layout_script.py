# 조판 데이터(JSON)를 담은 인디자인 조판 스크립트(UXP .idjs / ExtendScript .jsx 겸용)를 만든다.
# 사용: python3 -I make_layout_script.py <조판 폴더>
# 스크립트 본문은 ES3 문법만 쓴다(ExtendScript에서도 돌아야 하므로 let·const·화살표 함수 금지).
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
JS = r'''// 《10대를 위한 부동산 교양 수업》 본문 조판 스크립트 (자동 생성: tools/make_layout_script.py — 이 파일을 직접 고치지 말 것)
// UXP(.idjs)와 ExtendScript(.jsx) 모두에서 돈다.
// 준비: 인디자인에서 《국부론 수업》 새 조판 파일(국부론수업_본문_새조판.indd)을 열어 두고 앞에 둔다. 원본은 읽기만 한다.
// 동작: 새 문서를 만들고 국부론의 스타일·견본·부모 페이지를 가져온 뒤, 원고 1~7장과 뒷부속을 흘려 넣는다.
// 결과: 끝나면 요약 창을 띄우고, 전체 기록을 1쪽 왼쪽 대지에 '조판 기록' 글상자로 남긴다.
var ID = (typeof require !== "undefined") ? require("indesign") : null;   // UXP면 indesign 모듈, ExtendScript면 null
var APP = ID ? ID.app : app;
function E(name) { return ID ? ID[name] : eval(name); }   // 열거형 이름 → 값 (UXP/ExtendScript 공통)
var DATA = __DATA__;
var MM = 72 / 25.4;
var FRAME_H = 214 - 19.5 - 31;      // 판면 높이(mm)
var FIG_MAX_H = FRAME_H - 15;       // 도판 자리 상자 최대 높이(mm): 판면 높이 − (자리 문단 한 줄 + 앞뒤 간격)
var log = [];          // 확인 필요
var report = [];       // 장별 시작 쪽 등
var started = false;

// ── 공통 도우미 ──────────────────────────────────────────
function say(msg) {
    // UXP 스크립트에는 alert가 없을 수 있다 → 인디자인 대화상자로 대신 띄운다
    if (typeof alert === "function") { try { alert(msg); return; } catch (e) {} }
    try { if (typeof console !== "undefined") console.log(msg); } catch (e) {}
    try {
        var d = APP.dialogs.add({ name: "조판 결과" });
        var col = d.dialogColumns.add();
        var lines = String(msg).split("\n");
        for (var i = 0; i < lines.length && i < 30; i++) col.staticTexts.add({ staticLabel: lines[i] || " " });
        d.show(); d.destroy();
    } catch (e) {}
}
function filePath(f) {
    // ExtendScript는 File 객체, UXP는 경로 문자열을 돌려준다
    if (f === null || f === undefined) return "";
    if (typeof f === "string") return f;
    return f.fsName || f.nativePath || String(f);
}
function withSource(srcFile, label, fn) {
    // 원본 파일을 받는 메서드: 받은 값 그대로 시도 → 실패하면 경로 문자열로 다시 시도
    try { fn(srcFile); return; } catch (e1) {
        var p = filePath(srcFile);
        if (p && p !== srcFile) { try { fn(p); return; } catch (e2) { log.push(label + ": " + e2); return; } }
        log.push(label + ": " + e1);
    }
}
function findStyle(doc, coll, name) { var s = doc[coll].itemByName(name); return s.isValid ? s : null; }
function setp(obj, k, v) {
    var who = "";
    try { who = obj.name; } catch (e) {}
    try { obj[k] = v; } catch (e) { log.push(who + "." + k + ": " + e); return; }
    // UXP에서는 잘못된 속성 이름이 오류 없이 무시될 수 있다 → 숫자·참거짓은 다시 읽어 확인
    if (typeof v === "number" || typeof v === "boolean") {
        var r; try { r = obj[k]; } catch (e) { r = undefined; }
        if (typeof v === "number" ? !(typeof r === "number" && Math.abs(r - v) < 0.01) : r !== v)
            log.push(who + "." + k + " 적용 안 됨(값 " + r + ")");
    }
}
function fontName(family, styles) {
    // 설치된 글꼴에서 '가족\t스타일' 이름을 찾는다. 스타일 이름 후보를 차례로 시도
    for (var i = 0; i < styles.length; i++) {
        var n = family + "\t" + styles[i];
        try { if (APP.fonts.itemByName(n).isValid) return n; } catch (e) {}
    }
    log.push("글꼴 없음: " + family + " " + styles.join("/") + " — 국부론 패키지의 Document fonts가 새 문서에는 적용되지 않았을 수 있음");
    return null;
}
function swatchOrMake(doc, names, cmyk) {
    for (var i = 0; i < names.length; i++) { var s = doc.swatches.itemByName(names[i]); if (s.isValid) return s; }
    try {
        var c = doc.colors.add({ name: names[0], model: E("ColorModel").PROCESS, space: E("ColorSpace").CMYK, colorValue: cmyk });
        log.push("견본 새로 만듦: " + names[0] + " (국부론에서 같은 이름을 못 찾음)");
        return c;
    } catch (e) { log.push("견본 만들기 실패: " + names[0] + ": " + e); return doc.swatches.itemByName("Black"); }
}
function isRightPage(page) {
    // 마주 보는 페이지, 1쪽 시작: documentOffset 짝수 = 오른쪽(홀수 쪽). 열거형 비교를 피한다(UXP 차이)
    return page.documentOffset % 2 === 0;
}

// ── 본 작업 ──────────────────────────────────────────────
function main() {
    started = true;
    if (APP.documents.length === 0) { say("《국부론 수업》 파일을 먼저 여세요."); return; }
    var src = APP.activeDocument;
    if (!src.saved) { say("열린 문서를 먼저 저장하세요(스타일을 파일에서 가져옵니다)."); return; }
    var srcFile = src.fullName;
    var srcMasterName = mainMasterName(src);
    var MU = E("MeasurementUnits");
    APP.scriptPreferences.measurementUnit = MU.POINTS;

    // 1) 새 문서: 판형 150×214, 여백 위19.5 아래31 안쪽27 바깥22, 1단, 도련 3 (국부론 IDML 값)
    var doc = APP.documents.add();
    var dp = doc.documentPreferences;
    dp.facingPages = true; dp.pageWidth = 150 * MM; dp.pageHeight = 214 * MM;
    dp.documentBleedTopOffset = 3 * MM; dp.documentBleedBottomOffset = 3 * MM;
    dp.documentBleedInsideOrLeftOffset = 3 * MM; dp.documentBleedOutsideOrRightOffset = 3 * MM;
    setMargins(doc.marginPreferences);
    var ms0 = doc.masterSpreads.item(0);
    for (var mi = 0; mi < ms0.pages.length; mi++) setMargins(ms0.pages.item(mi).marginPreferences);

    // 2) 국부론에서 스타일·견본·부모 페이지 가져오기
    var CR = E("GlobalClashResolutionStrategy").LOAD_ALL_WITH_OVERWRITE, IF = E("ImportFormat");
    withSource(srcFile, "견본", function (f) { doc.loadSwatches(f); });
    withSource(srcFile, "문자·문단 스타일", function (f) { doc.importStyles(IF.TEXT_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "개체 스타일", function (f) { doc.importStyles(IF.OBJECT_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "표 스타일", function (f) { doc.importStyles(IF.TABLE_AND_CELL_STYLES_FORMAT, f, CR); });
    withSource(srcFile, "부모 페이지", function (f) { doc.loadMasters(f, CR); });
    var master = pickMaster(doc, srcMasterName);

    // 3) 이 책용 스타일(제안) 만들기 — 국부론 스타일을 바탕으로
    makeStyles(doc);

    // 4) 장마다 흘리기
    var LO = E("LocationOptions");
    var first = true;
    for (var c = 0; c < DATA.book.length; c++) {
        var ch = DATA.book[c];
        var page;
        if (first) { page = doc.pages.item(0); first = false; } else { page = doc.pages.add(LO.AT_END); }
        var line = (ch.num ? ch.num + "장" : ch.key) + ": ";
        if (ch.num) {
            // 도비라 펼침면(짝수 쪽 + 홀수 쪽): 지금 쪽이 홀수(오른쪽)면 그 쪽을 빈 쪽으로 두고 다음 쪽부터
            if (isRightPage(page)) { page.appliedMaster = master; page = doc.pages.add(LO.AT_END); }
            page.appliedMaster = master;
            var right = doc.pages.add(LO.AT_END); right.appliedMaster = master;
            dobira(doc, right, ch);
            line += "도비라 " + page.name + "~" + right.name + "쪽, ";
            page = doc.pages.add(LO.AT_END);
        }
        page.appliedMaster = master;
        line += "본문 " + page.name + "쪽부터";
        var res = flow(doc, page, ch, master);
        line += " " + res.last + "쪽까지" + (res.overset ? " ※넘침 남음" : "");
        report.push(line);
    }
    APP.scriptPreferences.measurementUnit = MU.AUTO_VALUE;
    var summary = "조판 완료: 총 " + doc.pages.length + "쪽\n" + report.join("\n") +
        (log.length ? ("\n\n확인 필요 " + log.length + "건 (전체는 1쪽 왼쪽 대지의 '조판 기록')\n" + log.slice(0, 12).join("\n")) : "\n\n확인 필요 없음");
    writeLog(doc, summary + (log.length > 12 ? "\n" + log.slice(12).join("\n") : ""));
    say(summary);
}

function setMargins(mp) {
    // 마주 보는 페이지에서 left = 안쪽, right = 바깥
    mp.top = 19.5 * MM; mp.bottom = 31 * MM; mp.left = 27 * MM; mp.right = 22 * MM; mp.columnCount = 1;
}

function mainMasterName(src) {
    // 국부론 페이지에 가장 많이 적용된 부모 페이지 이름 = 본문용
    var count = {}, best = "", n = 0;
    try {
        var pages = src.pages;
        for (var i = 0; i < pages.length; i++) {
            var m = pages.item(i).appliedMaster;
            if (!m || !m.isValid) continue;
            var k = m.name; count[k] = (count[k] || 0) + 1;
            if (count[k] > n) { n = count[k]; best = k; }
        }
    } catch (e) { log.push("국부론 부모 페이지 집계: " + e); }
    return best;
}
function pickMaster(doc, name) {
    if (name) { var m = doc.masterSpreads.itemByName(name); if (m.isValid) { report.push("부모 페이지: " + name + " (국부론 본문에 가장 많이 쓰인 것)"); return m; } }
    var last = doc.masterSpreads.item(doc.masterSpreads.length - 1);
    log.push("본문 부모 페이지를 이름으로 못 찾아 마지막 부모 페이지(" + last.name + ")를 썼음");
    return last;
}

function frameBounds(page) {
    var b = page.bounds, top = 19.5 * MM, bot = 31 * MM, ins = 27 * MM, out = 22 * MM;
    var isRight = isRightPage(page);
    return [b[0] + top, b[1] + (isRight ? ins : out), b[2] - bot, b[3] - (isRight ? out : ins)];
}

function dobira(doc, page, ch) {
    var b = page.bounds, bl = 3 * MM;
    var r = page.rectangles.add({ geometricBounds: [b[0] - bl, b[1], b[2] + bl, b[3] + bl] });
    var k80 = doc.swatches.itemByName("C=0 M=0 Y=0 K=80");
    setp(r, "fillColor", k80.isValid ? k80 : doc.swatches.itemByName("Black"));
    var t = page.textFrames.add({ geometricBounds: [b[0] + 95 * MM, b[1] + 38.3 * MM, b[0] + 160 * MM, b[1] + 115 * MM] });
    t.contents = ch.num + "\r" + ch.title + "\r\r[도비라 자리 — 공통 일러스트: 시안/illust/도비라_공통_v1.png]";
    var ps = findStyle(doc, "paragraphStyles", "도비라 제목");
    if (ps) { var tp = t.parentStory.paragraphs; for (var i = 0; i < tp.length; i++) tp.item(i).appliedParagraphStyle = ps; }
}

function flow(doc, page, ch, master) {
    var LO = E("LocationOptions");
    var tf = page.textFrames.add({ geometricBounds: frameBounds(page) });
    var texts = [];
    for (var i = 0; i < ch.p.length; i++) texts.push(ch.p[i][1]);
    tf.contents = texts.join("\r");
    var story = tf.parentStory, paras = story.paragraphs;
    if (paras.length !== ch.p.length) log.push(ch.key + ": 문단 수 불일치(데이터 " + ch.p.length + ", 인디자인 " + paras.length + ")");
    var cache = {};
    for (var j = 0; j < ch.p.length && j < paras.length; j++) {
        var nm = ch.p[j][0];
        if (!(nm in cache)) { cache[nm] = findStyle(doc, "paragraphStyles", nm); if (!cache[nm]) log.push("스타일 없음: " + nm); }
        if (cache[nm]) paras.item(j).applyParagraphStyle(cache[nm], true);
    }
    // 도판 자리: 시안 크기의 회색 상자를 '줄 위' 고정 개체로 넣는다.
    // (인라인으로 넣으면 고정 행간 26pt 때문에 상자가 윗줄 글자를 덮는다)
    var AP = E("AnchorPosition"), HA = E("HorizontalAlignment");
    var gray = doc.swatches.itemByName("C=0 M=0 Y=0 K=20");
    if (!gray.isValid) gray = doc.swatches.itemByName("Paper");
    for (var k = ch.p.length - 1; k >= 0; k--) {
        var fid = ch.p[k][2];
        if (!fid || k >= paras.length) continue;
        var ids = (fid === "2-1") ? ["2-1R", "2-1"] : [fid];   // 뒤에서부터 넣으므로 결과 순서는 2-1, 2-1R
        for (var q = 0; q < ids.length; q++) {
            var sz = DATA.fig[ids[q]] || [101, 60], h = sz[1];
            if (h > FIG_MAX_H) { log.push("도" + ids[q] + ": 높이 " + h + "mm가 판면에 안 들어가 자리 상자를 " + FIG_MAX_H + "mm로 줄임(실제 도판은 한 면 전체로 따로 앉힐 것)"); h = FIG_MAX_H; }
            try {
                if (q > 0) paras.item(k).insertionPoints.item(0).contents = "\r";   // 2-1 펼침면: 상자마다 문단을 나눈다
                var box = paras.item(k).insertionPoints.item(0).textFrames.add();
                box.geometricBounds = [0, 0, h * MM, sz[0] * MM];
                var ao = box.anchoredObjectSettings;
                setp(ao, "anchoredPosition", AP.ABOVE_LINE);
                setp(ao, "horizontalAlignment", HA.CENTER_ALIGN);
                box.contents = "[도" + ids[q].replace("R", " 오른쪽") + "] " + sz[0] + "×" + sz[1] + "mm — 시안 PDF를 놓을 자리";
                box.fillColor = gray;
            } catch (e) { log.push("도판 자리 " + ids[q] + ": " + e); }
        }
    }
    // 넘친 글을 새 쪽으로 이어 흘리기. 새 틀에 글이 한 자도 안 들어가면(안 들어가는 개체) 멈춘다
    var last = tf, guard = 0, overset = false;
    while (last.overflows) {
        if (guard++ >= 400) { overset = true; log.push(ch.key + ": 400쪽을 넘겨 흘리기를 멈춤"); break; }
        var np = doc.pages.add(LO.AT_END);
        np.appliedMaster = master;
        var nf = np.textFrames.add({ geometricBounds: frameBounds(np) });
        last.nextTextFrame = nf;
        try { nf.recompose(); } catch (e) {}
        if (nf.characters.length === 0) {
            overset = true;
            log.push(ch.key + ": " + np.name + "쪽 틀에 글이 들어가지 않아 멈춤(판면보다 큰 개체 확인)");
            nf.remove(); np.remove(); break;
        }
        last = nf;
    }
    return { last: last.parentPage ? last.parentPage.name : page.name, overset: overset };
}

function makeStyles(doc) {
    var P = doc.paragraphStyles;
    function mk(name, base, props) {
        var s = P.itemByName(name);
        if (!s.isValid) s = P.add({ name: name });
        var b = P.itemByName(base);
        if (b.isValid) setp(s, "basedOn", b); else log.push("바탕 스타일 없음: " + base + " (" + name + ")");
        for (var i = 0; i < props.length; i++) {
            if (props[i][1] === null) continue;   // 글꼴을 못 찾은 경우
            setp(s, props[i][0], props[i][1]);
        }
        return s;
    }
    var SP = E("StartParagraph"), J = E("Justification");
    var yellow = swatchOrMake(doc, ["C=0 M=6 Y=68 K=0"], [0, 6, 68, 0]);
    var teal = swatchOrMake(doc, ["도해_청록 c80m30y40"], [80, 30, 40, 0]);
    var gothicBd = fontName("Sandoll 고딕Neo1", ["07 Bd", "Bd"]);
    var gothicLt = fontName("Sandoll 고딕Neo1", ["03 Lt", "Lt"]);
    var gyeokdong = fontName("Sandoll 격동굴림2", ["06 Hv", "Hv"]);
    // [확정 2026-11-10] 절 제목: 국부론 '대제목'과 같은 서체·크기·색, 새 쪽 시작만 끔
    mk("절 제목", "대제목", [["startParagraph", SP.ANYWHERE], ["spaceBefore", 39], ["spaceAfter", 6.5], ["keepWithNext", 3]]);
    // [레퍼런스] 소제목 = 국부론 '큰 제목'
    mk("소제목", "큰 제목", [["spaceBefore", 13]]);
    // [제안] 셋째 단계 제목
    mk("소소제목", "본문", [["appliedFont", gothicBd], ["pointSize", 10.5], ["firstLineIndent", 0], ["spaceBefore", 6.5], ["keepWithNext", 2]]);
    mk("질문 제목", "소소제목", [["fillColor", teal]]);
    mk("목록", "본문", [["leftIndent", 4 * MM], ["firstLineIndent", -4 * MM]]);
    mk("번호 목록", "본문", [["leftIndent", 5 * MM], ["firstLineIndent", -5 * MM]]);
    // [제안] '잠깐!' 상자: 국부론 상자와 같은 연노랑(0/6/68/0)을 문단 음영으로.
    // 음영 폭은 단(판면 101mm)에 맞추고 좌우 오프셋 0, 글은 들여쓰기 3mm로 안쪽 여백을 만든다(음영이 판면 밖으로 나가지 않게)
    var shade = [["paragraphShadingOn", true], ["paragraphShadingColor", yellow], ["paragraphShadingTopOffset", 4 * MM],
                 ["paragraphShadingBottomOffset", 3 * MM], ["paragraphShadingLeftOffset", 0], ["paragraphShadingRightOffset", 0]];
    mk("잠깐 라벨", "만화 대사", [["justification", J.LEFT_ALIGN], ["pointSize", 13], ["firstLineIndent", 0], ["leftIndent", 3 * MM], ["rightIndent", 3 * MM], ["spaceBefore", 26], ["keepWithNext", 2]].concat(shade));
    mk("잠깐 본문", "본문", [["firstLineIndent", 0], ["leftIndent", 3 * MM], ["rightIndent", 3 * MM], ["spaceAfter", 26]].concat(shade));
    mk("도판 자리", "본문", [["firstLineIndent", 0], ["justification", J.CENTER_ALIGN], ["spaceBefore", 6.5], ["spaceAfter", 13]]);
    mk("참고 자료", "본문", [["appliedFont", gothicLt], ["pointSize", 8], ["leading", 12], ["firstLineIndent", -6 * MM], ["leftIndent", 6 * MM]]);
    mk("참고 자료 제목", "소소제목", [["spaceBefore", 13]]);
    var white = doc.swatches.itemByName("Paper");
    mk("도비라 제목", "대제목", [["appliedFont", gyeokdong], ["pointSize", 18], ["fillColor", white], ["justification", J.CENTER_ALIGN], ["startParagraph", SP.ANYWHERE]]);
}

function writeLog(doc, text) {
    try {
        var p = doc.pages.item(0), b = p.bounds;
        var t = p.textFrames.add({ geometricBounds: [b[0], b[1] - 130 * MM, b[2], b[1] - 10 * MM] });
        t.contents = text;
        t.name = "조판 기록";
        try { t.nonprinting = true; } catch (e) {}
    } catch (e) { log.push("조판 기록 글상자: " + e); }
}

// 실행: 되돌리기 한 번으로 전체를 취소할 수 있게 doScript로 감싼다. 안 되면 그냥 실행
(function () {
    try {
        var lang = ID ? E("ScriptLanguage").UXPSCRIPT : E("ScriptLanguage").JAVASCRIPT;
        APP.doScript(main, lang, [], E("UndoModes").ENTIRE_SCRIPT, "부동산교양수업 조판");
        if (!started) main();   // doScript가 함수를 실행하지 않은 경우
    } catch (e) {
        if (!started) main(); else say("실행 중 오류: " + e + "\n" + log.join("\n"));
    }
})();
'''
JS = JS.replace("__DATA__", data)
for ext in ("idjs", "jsx"):
    with open(os.path.join(D, f"조판_부동산교양수업.{ext}"), "w", encoding="utf-8-sig" if ext == "jsx" else "utf-8") as f:
        f.write(JS)
print("ok", len(JS))
