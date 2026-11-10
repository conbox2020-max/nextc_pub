# 생성 일러스트 화질 개선: 노이즈(종이 질감·압축 잡티) 제거 → 2배 초해상(EDSR) → 약한 선명화
# 사용: python3 -I enhance_illust.py <모델 EDSR_x2.pb|FSRCNN_x2.pb> <입력.png> <출력.png> [노이즈 강도 h=5]
# 모델: OpenCV dnn_superres용 EDSR/FSRCNN x2 (github Saafke/EDSR_Tensorflow, FSRCNN_Tensorflow)
import sys, cv2, numpy as np
model, src, dst = sys.argv[1:4]
h = float(sys.argv[4]) if len(sys.argv) > 4 else 5
img = cv2.imread(src, cv2.IMREAD_COLOR)
# 1) 자글자글한 미세 노이즈 제거 (윤곽선은 유지하는 비국소 평균 필터)
den = cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)
# 2) 2배 초해상 (타일로 나눠 메모리·시간 관리)
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(model); sr.setModel("fsrcnn" if "FSRCNN" in model else "edsr", 2)
T, P = 256, 16
H, W = den.shape[:2]
out = np.zeros((H * 2, W * 2, 3), np.uint8)
for y in range(0, H, T):
    for x in range(0, W, T):
        y0, x0 = max(0, y - P), max(0, x - P)
        y1, x1 = min(H, y + T + P), min(W, x + T + P)
        up = sr.upsample(den[y0:y1, x0:x1])
        oy, ox = (y - y0) * 2, (x - x0) * 2
        th, tw = min(T, H - y) * 2, min(T, W - x) * 2
        out[y * 2:y * 2 + th, x * 2:x * 2 + tw] = up[oy:oy + th, ox:ox + tw]
# 3) 약한 언샤프 마스크로 선을 또렷하게 (과하면 테두리 번짐이 생기므로 약하게)
blur = cv2.GaussianBlur(out, (0, 0), 1.2)
out = cv2.addWeighted(out, 1.35, blur, -0.35, 0)
cv2.imwrite(dst, out, [cv2.IMWRITE_PNG_COMPRESSION, 6])
print(dst, out.shape[1], "x", out.shape[0])
