// 《10대를 위한 부동산 교양 수업》 도비라·도해 스타일 생성 스크립트
// 사양: projects/부동산교양수업/도해스타일_사양서_v1.md
// 열린 문서에 견본·문단 스타일·문자 스타일·개체 스타일을 만든다.
// 같은 이름이 이미 있으면 건너뛰고 덮어쓰지 않는다. 반드시 사본 문서에서 먼저 실행한다.
#target indesign

(function () {
    if (app.documents.length === 0) { alert("문서를 먼저 여세요."); return; }
    var doc = app.activeDocument;
    var made = [], skipped = [], warn = [];

    function setProps(obj, label, pairs) {
        // 순서가 중요한 속성(서체 → 굵기)이 있어 배열로 차례대로 지정한다
        for (var i = 0; i < pairs.length; i++) {
            try { obj[pairs[i][0]] = pairs[i][1]; }
            catch (e) { warn.push(label + " / " + pairs[i][0] + ": " + e.message); }
        }
    }

    function swatch(name) {
        var s = doc.swatches.itemByName(name);
        return s.isValid ? s : null;
    }

    function color(name, cmyk) {
        var c = doc.colors.itemByName(name);
        if (c.isValid) { skipped.push("견본 " + name); return c; }
        c = doc.colors.add({ name: name, model: ColorModel.PROCESS, space: ColorSpace.CMYK, colorValue: cmyk });
        made.push("견본 " + name);
        return c;
    }

    function pstyle(name, pairs) {
        var s = doc.paragraphStyles.itemByName(name);
        if (s.isValid) { skipped.push("문단 " + name); return s; }
        s = doc.paragraphStyles.add({ name: name });
        setProps(s, "문단 " + name, pairs);
        made.push("문단 " + name);
        return s;
    }

    function cstyle(name, pairs) {
        var s = doc.characterStyles.itemByName(name);
        if (s.isValid) { skipped.push("문자 " + name); return s; }
        s = doc.characterStyles.add({ name: name });
        setProps(s, "문자 " + name, pairs);
        made.push("문자 " + name);
        return s;
    }

    function ostyle(name, fn) {
        var s = doc.objectStyles.itemByName(name);
        if (s.isValid) { skipped.push("개체 " + name); return s; }
        s = doc.objectStyles.add({ name: name });
        try { fn(s); } catch (e) { warn.push("개체 " + name + ": " + e.message); }
        made.push("개체 " + name);
        return s;
    }

    // ── 2. 색상 견본 ─────────────────────────────
    var K80 = swatch("C=0 M=0 Y=0 K=80") || color("C=0 M=0 Y=0 K=80", [0, 0, 0, 80]);
    var K40 = swatch("C=0 M=0 Y=0 K=40") || color("C=0 M=0 Y=0 K=40", [0, 0, 0, 40]);
    var K20 = swatch("C=0 M=0 Y=0 K=20") || color("C=0 M=0 Y=0 K=20", [0, 0, 0, 20]);
    var PAPER = swatch("Paper");
    var NONE = swatch("None");
    var TEAL = swatch("도해_청록 c80m30y40") || color("도해_청록 c80m30y40", [80, 30, 40, 0]);
    color("도해_빨강 c15m100y100", [15, 100, 100, 0]);
    color("가상서류_바탕 k5", [0, 0, 0, 5]);
    color("용도_주거 시안", [0, 10, 60, 0]);
    color("용도_상업 시안", [0, 45, 15, 0]);
    color("용도_공업 시안", [35, 45, 0, 0]);
    color("용도_녹지 시안", [40, 0, 55, 0]);
    var BG = swatch("가상서류_바탕 k5");

    // ── 3. 문단·문자 스타일 ──────────────────────
    var STUDY = "Sandoll 스터디윗미";
    pstyle("도해 제목", [["appliedFont", STUDY], ["fontStyle", "03 Bold"], ["pointSize", 10], ["leading", 13],
        ["justification", Justification.CENTER_ALIGN], ["fillColor", K80], ["hyphenation", false]]);
    pstyle("도해 라벨", [["appliedFont", STUDY], ["fontStyle", "03 Bold"], ["pointSize", 8.5], ["leading", 11],
        ["justification", Justification.CENTER_ALIGN], ["fillColor", K80], ["hyphenation", false]]);
    pstyle("도해 설명", [["appliedFont", STUDY], ["fontStyle", "02 Regular"], ["pointSize", 7.5], ["leading", 10],
        ["justification", Justification.CENTER_ALIGN], ["fillColor", K80], ["hyphenation", false]]);
    pstyle("도해 주석", [["appliedFont", STUDY], ["fontStyle", "01 Light"], ["pointSize", 7], ["leading", 10],
        ["justification", Justification.LEFT_ALIGN], ["fillColor", K80], ["hyphenation", false]]);
    pstyle("도비라 번호", [["appliedFont", "Sandoll 격동굴림2"], ["fontStyle", "06 Hv"], ["pointSize", 20],
        ["justification", Justification.RIGHT_ALIGN], ["fillColor", PAPER], ["hyphenation", false]]);
    pstyle("도비라 제목", [["appliedFont", "Sandoll 격동굴림2"], ["fontStyle", "06 Hv"], ["pointSize", 18],
        ["justification", Justification.RIGHT_ALIGN], ["fillColor", PAPER], ["hyphenation", false]]);

    cstyle("도해 숫자", [["appliedFont", "DIN 2014"], ["fontStyle", "Bold"]]);
    cstyle("가상 표시", [["appliedFont", STUDY], ["fontStyle", "03 Bold"], ["pointSize", 7], ["fillColor", PAPER]]);

    // ── 4. 개체 스타일 (크기는 [변형] 패널에서 직접 입력) ──
    function iconStyle(s) {
        s.enableFill = true; s.fillColor = NONE;
        s.enableStroke = true; s.strokeColor = NONE;
        s.enableFrameFittingOptions = true;
        s.frameFittingOptions.fittingOnEmptyFrame = EmptyFrameFittingOptions.PROPORTIONALLY;
    }
    ostyle("아이콘_12", iconStyle);
    ostyle("아이콘_10.5", iconStyle);
    ostyle("아이콘_9.5", iconStyle);

    ostyle("일러스트_본문", function (s) {
        iconStyle(s);
        s.enableTextWrapAndOthers = true;
        s.textWrapPreferences.textWrapMode = TextWrapModes.BOUNDING_BOX_TEXT_WRAP;
        s.textWrapPreferences.textWrapOffset = ["4mm", "0mm", "4mm", "0mm"];
    });
    ostyle("사진_사료", function (s) {
        iconStyle(s);
        s.enableTextWrapAndOthers = true;
        s.textWrapPreferences.textWrapMode = TextWrapModes.BOUNDING_BOX_TEXT_WRAP;
        s.textWrapPreferences.textWrapOffset = ["0mm", "0mm", "2mm", "0mm"];
    });
    ostyle("가상서류_틀", function (s) {
        s.enableFill = true; s.fillColor = BG;
        s.enableStroke = true; s.strokeColor = K40; s.strokeWeight = "0.3pt";
        s.enableTextFrameGeneralOptions = true;
        s.textFramePreferences.insetSpacing = ["3mm", "3mm", "3mm", "3mm"];
    });
    ostyle("도해_칸", function (s) {
        s.enableFill = true; s.fillColor = NONE;
        s.enableStroke = true; s.strokeColor = TEAL; s.strokeWeight = "0.5pt";
        s.enableStrokeAndCornerOptions = true;
        s.topLeftCornerOption = s.topRightCornerOption = s.bottomLeftCornerOption = s.bottomRightCornerOption = CornerOptions.ROUNDED_CORNER;
        s.topLeftCornerRadius = s.topRightCornerRadius = s.bottomLeftCornerRadius = s.bottomRightCornerRadius = "1.5mm";
    });

    var msg = "만든 항목 " + made.length + "개\n" + made.join(", ") +
        "\n\n건너뜀(이미 있음) " + skipped.length + "개\n" + skipped.join(", ");
    if (warn.length) msg += "\n\n확인 필요 " + warn.length + "건\n" + warn.join("\n");
    msg += "\n\n누락 글꼴은 [문자 > 글꼴 찾기]에서 확인하세요.";
    alert(msg);
})();
