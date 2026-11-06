// 넥스트씨_스타일덤프.jsx
// 인디자인에서 열린 문서(활성 문서)의 단락·문자 스타일과 판형·여백·마스터 정보를
// 탭 구분 텍스트(UTF-8)로 바탕화면에 저장한다.
// 읽기 전용: 문서와 환경설정을 바꾸지 않는다. 저장 명령도 실행하지 않는다.
// 실행: 창 > 유틸리티 > 스크립트 > 사용자 폴더에 넣고 더블클릭.
#target indesign

(function () {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var out = [];
    var T = "\t";

    function safe(fn) { try { var v = fn(); return (v === undefined || v === null) ? "" : v; } catch (e) { return ""; } }
    function nm(o) { return safe(function () { return o.name; }); }
    function fontName(s) {
        return safe(function () {
            var f = s.appliedFont;
            return (typeof f === "string") ? f : f.name; // 누락 서체는 문자열로 돌아옴
        });
    }
    function en(v) { return safe(function () { return String(v).replace(/^.*\./, ""); }); }

    var hu = en(doc.viewPreferences.horizontalMeasurementUnits);
    var vu = en(doc.viewPreferences.verticalMeasurementUnits);

    out.push("# 문서" + T + doc.name);
    out.push("# 단위" + T + "크기·행간·자간: pt / 들여쓰기·간격: 가로 " + hu + ", 세로 " + vu);
    var dp = doc.documentPreferences;
    out.push("판형" + T + dp.pageWidth + " x " + dp.pageHeight + T + "마주보기=" + dp.facingPages + T + "도련(위)=" + dp.documentBleedTopOffset);
    var gp = doc.gridPreferences;
    out.push("기준선격자" + T + "시작=" + gp.baselineStart + T + "간격=" + gp.baselineDivision + T + "기준=" + en(gp.baselineGridRelativeOption));
    out.push("");

    out.push("## 마스터");
    out.push(["마스터", "페이지", "위", "아래", "안/왼", "밖/오", "단", "단간격"].join(T));
    for (var m = 0; m < doc.masterSpreads.length; m++) {
        var ms = doc.masterSpreads[m];
        for (var p = 0; p < ms.pages.length; p++) {
            var mp = ms.pages[p].marginPreferences;
            out.push([ms.name, ms.pages[p].name, mp.top, mp.bottom, mp.left, mp.right, mp.columnCount, mp.columnGutter].join(T));
        }
    }
    out.push("");

    var pCols = ["스타일", "그룹", "기반", "서체", "굵기", "크기", "행간", "자간", "장평", "커닝", "정렬",
                 "첫줄", "왼쪽", "오른쪽", "앞", "뒤", "기준선격자", "하이픈", "컴포저",
                 "다음행과", "행함께", "모든행", "시작행", "끝행", "단락시작", "색", "농도", "다음스타일"];
    out.push("## 단락 스타일");
    out.push(pCols.join(T));
    var ps = doc.allParagraphStyles;
    for (var i = 0; i < ps.length; i++) {
        var s = ps[i];
        out.push([
            nm(s), nm(safe(function () { return s.parent; })), nm(safe(function () { return s.basedOn; })),
            fontName(s), safe(function () { return s.fontStyle; }), safe(function () { return s.pointSize; }),
            safe(function () { return s.leading; }), safe(function () { return s.tracking; }),
            safe(function () { return s.horizontalScale; }), safe(function () { return s.kerningMethod; }),
            en(safe(function () { return s.justification; })),
            safe(function () { return s.firstLineIndent; }), safe(function () { return s.leftIndent; }),
            safe(function () { return s.rightIndent; }), safe(function () { return s.spaceBefore; }),
            safe(function () { return s.spaceAfter; }), en(safe(function () { return s.alignToBaseline; })),
            safe(function () { return s.hyphenation; }), safe(function () { return s.composer; }),
            safe(function () { return s.keepWithNext; }), safe(function () { return s.keepLinesTogether; }),
            safe(function () { return s.keepAllLinesTogether; }), safe(function () { return s.keepFirstLines; }),
            safe(function () { return s.keepLastLines; }), en(safe(function () { return s.startParagraph; })),
            nm(safe(function () { return s.fillColor; })), safe(function () { return s.fillTint; }),
            nm(safe(function () { return s.nextStyle; }))
        ].join(T));
    }
    out.push("");

    out.push("## 문자 스타일");
    out.push(["스타일", "기반", "서체", "굵기", "크기", "행간", "자간", "장평", "기준선이동", "기울기", "색", "농도", "밑줄"].join(T));
    var cs = doc.allCharacterStyles;
    for (var j = 0; j < cs.length; j++) {
        var c = cs[j];
        // 문자 스타일에서 지정하지 않은 속성은 NothingEnum이 돌아오므로 그대로 문자열로 기록
        out.push([
            nm(c), nm(safe(function () { return c.basedOn; })), fontName(c),
            safe(function () { return c.fontStyle; }), safe(function () { return c.pointSize; }),
            safe(function () { return c.leading; }), safe(function () { return c.tracking; }),
            safe(function () { return c.horizontalScale; }), safe(function () { return c.baselineShift; }),
            safe(function () { return c.skew; }), nm(safe(function () { return c.fillColor; })),
            safe(function () { return c.fillTint; }), safe(function () { return c.underline; })
        ].join(T));
    }
    out.push("");

    out.push("## 색상 견본");
    out.push(["이름", "모델", "공간", "값"].join(T));
    for (var k = 0; k < doc.colors.length; k++) {
        var col = doc.colors[k];
        out.push([nm(col), en(safe(function () { return col.model; })), en(safe(function () { return col.space; })),
                  safe(function () { return col.colorValue.join(" "); })].join(T));
    }

    var base = doc.name.replace(/\.indd$/i, "");
    var f = new File(Folder.desktop + "/" + base + "_스타일덤프.txt");
    f.encoding = "UTF-8";
    f.lineFeed = "Unix";
    if (!f.open("w")) { alert("파일을 만들 수 없습니다: " + f.fsName); return; }
    f.write("﻿" + out.join("\n"));
    f.close();
    alert("저장했습니다.\n" + f.fsName + "\n단락 스타일 " + ps.length + "개, 문자 스타일 " + cs.length + "개");
})();
