from pico2d import load_image

import game_framework

# bird_animation.png 실측 프레임 테이블 (tools/analyze_bird_sheet.py 출력)
# 시트를 균등 그리드(183.6 x 168.67)로 자르면 날개가 칸 경계에 걸리므로,
# 프레임마다 실제 그림이 차지하는 사각형을 픽셀 단위로 측정해서 사용한다.
#   - 열 간격은 183.6 이 아니라 182px (눈 위치로 측정)
#   - 프레임마다 날개 모양이 달라 클립 크기도 서로 다름
# (left, bottom, width, height, ox, oy)
#   left, bottom, width, height : pico2d 좌표계(이미지 왼쪽 아래가 원점) clip 사각형
#   ox, oy : 앵커(새의 눈)에서 clip 사각형 중심까지의 오프셋(px)
#
# clip_draw 는 사각형의 '중심'을 (x, y)에 그리는데, 사각형 크기와 몸통 위치가
# 프레임마다 다르므로 그대로 그리면 몸통이 프레임마다 위아래로 최대 46px,
# 좌우로 17px 튄다. 그래서 몸통에서 움직이지 않는 점인 '눈'을 앵커로 정하고
# (x + ox, y + oy) 에 그려서 어떤 프레임이든 눈이 항상 (x, y)에 오도록 한다.
# -> 날개만 움직이고 몸통은 고정된 정확한 날갯짓
FRAMES = (
    ( 34, 362, 146, 143, -16,  21),  # 0  날개 위로 (상승 끝)
    (216, 363, 146, 141, -17,  20),  # 1
    (398, 364, 146, 130, -17,  14),  # 2
    (555, 367, 171, 122, -29,  10),  # 3  날개 앞으로 내려치기 시작
    (728, 370, 182,  88, -33,  -7),  # 4  날개 수평
    ( 34, 171, 146, 118, -16, -22),  # 5  날개 아래로 (하강 끝)
    (216, 166, 146, 124, -17, -25),  # 6
    (398, 170, 146, 120, -17, -22),  # 7
    (580, 180, 146, 109, -17, -18),  # 8
    (762, 177, 146, 110, -17, -18),  # 9
    ( 34,   6, 146, 108, -17, -17),  # 10
    (216,   6, 146, 106, -17, -15),  # 11
    (376,  23, 168,  88, -28,  -6),  # 12 날개 다시 들어올림
    (546,  22, 180, 114, -33,   6),  # 13
)
FRAMES_PER_ACTION = len(FRAMES)

# 1초에 재생할 프레임 수 (frame_time 기반 -> 컴퓨터 성능과 무관한 재생 속도)
FRAMES_PER_SECOND = 14.0


class Bird:
    image = None

    def __init__(self, x=800, y=400):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        self.frame = 0.0

    def update(self):
        self.frame = (self.frame + FRAMES_PER_SECOND * game_framework.frame_time) % FRAMES_PER_ACTION

    def draw(self):
        left, bottom, w, h, ox, oy = FRAMES[int(self.frame)]
        Bird.image.clip_draw(left, bottom, w, h, self.x + ox, self.y + oy)
