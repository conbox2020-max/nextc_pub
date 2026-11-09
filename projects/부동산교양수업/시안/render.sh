#!/bin/bash
# 시안 SVG를 미리보기 PNG(12px/mm)와 실제 크기 PDF로 렌더링한다.
# 사용: ./render.sh <파일.svg> <폭mm> <높이mm>
set -e
SVG="$1"; W="$2"; H="$3"; BASE="${SVG%.svg}"
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome | head -1)
TMP=$(mktemp -d)
BODY=$(sed 's/width="[0-9.]*mm" height="[0-9.]*mm"/width="100%" height="100%"/' "$SVG")
printf '<html><head><meta charset="utf-8"></head><body style="margin:0;background:#fff"><div style="width:%spx;height:%spx;margin:24px">%s</div></body></html>' \
  "$((W*12))" "$((H*12))" "$BODY" > "$TMP/png.html"
printf '<html><head><meta charset="utf-8"><style>@page{size:%smm %smm;margin:0}body{margin:0}</style></head><body><div style="width:%smm;height:%smm">%s</div></body></html>' \
  "$W" "$H" "$W" "$H" "$BODY" > "$TMP/pdf.html"
"$CH" --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=$((W*12+48)),$((H*12+140)) \
  --screenshot="$PWD/${BASE}_미리보기.png" "file://$TMP/png.html" 2>/dev/null
"$CH" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/${BASE}_실제크기.pdf" "file://$TMP/pdf.html" 2>/dev/null
rm -rf "$TMP"
