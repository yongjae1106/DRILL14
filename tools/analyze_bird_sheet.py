"""bird_animation.png 스프라이트 시트 분석 도구 (개발용, 게임 실행에는 불필요).

실행: python tools/analyze_bird_sheet.py   (Pillow 필요)

시트를 단순히 '가로 5칸 x 세로 3칸'으로 나누면 칸 크기가 918/5 = 183.6,
506/3 = 168.67 로 정수가 아니고, 실제로 그림이 놓인 간격과도 다르다.
그래서 픽셀을 직접 조사해서 다음을 측정한다.

1. 열 간격: 각 프레임에서 눈(파란 홍채) 픽셀의 무게중심 x 좌표를 구해
   실제 프레임 간격(pitch)을 알아낸다.
2. 행 경계: 투명하지 않은 픽셀이 있는 가로줄 구간으로 행을 나눈다.
3. 프레임별 클립 사각형: 각 칸 안에서 알파 > 0 인 픽셀의 bounding box.
4. 앵커(눈) 기준 오프셋: 클립 사각형 중심이 눈에서 얼마나 떨어져 있는지.
   이 값을 draw 시에 보정하면 몸통이 프레임마다 흔들리지 않는다.

출력은 pico2d 좌표계(원점 = 이미지 왼쪽 아래)로 변환된
(left, bottom, width, height, offset_x, offset_y) 튜플이며,
bird.py 의 FRAMES 테이블에 그대로 복사해서 쓴다.
"""
import os
import sys

from PIL import Image

COLS, ROWS, FRAME_COUNT = 5, 3, 14


def is_iris(r, g, b, a):
    return a > 200 and b > 150 and r < 80 and g < 160 and b - r > 100


def runs(flags):
    result, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            result.append((start, i))
            start = None
    if start is not None:
        result.append((start, len(flags)))
    return result


def main(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    px = im.load()
    alpha = im.split()[3]
    print(f'sheet size = {w} x {h}, naive cell = {w / COLS:.2f} x {h / ROWS:.2f}')

    # 2. 행 경계: 내용이 있는 가로줄 구간 사이의 빈 공간 한가운데에서 자른다.
    row_has = [any(alpha.getpixel((x, y)) for x in range(w)) for y in range(h)]
    row_runs = runs(row_has)
    print('row content runs (top-down):', row_runs)

    # 1. 열 간격: 첫 행의 눈 위치로 pitch 측정
    def iris_center(x0, y0, x1, y1):
        xs, ys = [], []
        for y in range(y0, y1):
            for x in range(x0, x1):
                if is_iris(*px[x, y]):
                    xs.append(x)
                    ys.append(y)
        return sum(xs) / len(xs), sum(ys) / len(ys)

    naive_w = w / COLS
    eye0 = [iris_center(int(c * naive_w), 0, int((c + 1) * naive_w), h // ROWS)[0]
            for c in range(COLS)]
    pitch = round((eye0[-1] - eye0[0]) / (COLS - 1))
    print('row0 iris x:', [round(e, 1) for e in eye0], '-> pitch =', pitch)

    # 행 밴드: 측정된 내용 구간 사이 '빈 공간의 한가운데'에서 자른다.
    # (균등 그리드 경계 337 로 자르면 행1 날개 끝 337~339 가 행2 프레임에 섞인다)
    bands = []
    for k, (start, end) in enumerate(row_runs):
        top = 0 if k == 0 else (row_runs[k - 1][1] + start) // 2
        bottom = h if k == len(row_runs) - 1 else (end + row_runs[k + 1][0]) // 2
        bands.append((top, bottom))
    print('row bands:', bands)

    print('\nFRAMES = (')
    for i in range(FRAME_COUNT):
        r, c = divmod(i, COLS)
        cx0, cx1 = c * pitch, min(w, (c + 1) * pitch)
        cy0, cy1 = bands[r]
        bx0, by0, bx1, by1 = alpha.crop((cx0, cy0, cx1, cy1)).getbbox()
        left, top = cx0 + bx0, cy0 + by0
        fw, fh = bx1 - bx0, by1 - by0
        ex, ey = iris_center(cx0, cy0, cx1, cy1)
        # pico2d 좌표: y 축이 위로 증가
        bottom = h - (top + fh)
        center_x, center_y = left + fw / 2, top + fh / 2
        ox = round(center_x - ex)
        oy = round(-(center_y - ey))
        print(f'    ({left:3d}, {bottom:3d}, {fw:3d}, {fh:3d}, {ox:3d}, {oy:3d}),  # {i:2d}')
    print(')')


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'bird_animation.png'))
