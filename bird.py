from pico2d import load_image

import game_framework

# bird_animation.png 실측 프레임 테이블 (tools/analyze_bird_sheet.py 출력)
# 시트를 균등 그리드(183.6 x 168.67)로 자르면 날개가 칸 경계에 걸리므로,
# 프레임마다 실제 그림이 차지하는 사각형을 픽셀 단위로 측정해서 사용한다.
#   - 열 간격은 183.6 이 아니라 182px (눈 위치로 측정)
#   - 프레임마다 날개 모양이 달라 클립 크기도 서로 다름
# (left, bottom, width, height) : pico2d 좌표계(이미지 왼쪽 아래가 원점)
FRAMES = (
    ( 34, 362, 146, 143),  # 0  날개 위로 (상승 끝)
    (216, 363, 146, 141),  # 1
    (398, 364, 146, 130),  # 2
    (555, 367, 171, 122),  # 3  날개 앞으로 내려치기 시작
    (728, 370, 182,  88),  # 4  날개 수평
    ( 34, 171, 146, 118),  # 5  날개 아래로 (하강 끝)
    (216, 166, 146, 124),  # 6
    (398, 170, 146, 120),  # 7
    (580, 180, 146, 109),  # 8
    (762, 177, 146, 110),  # 9
    ( 34,   6, 146, 108),  # 10
    (216,   6, 146, 106),  # 11
    (376,  23, 168,  88),  # 12 날개 다시 들어올림
    (546,  22, 180, 114),  # 13
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
        left, bottom, w, h = FRAMES[int(self.frame)]
        Bird.image.clip_draw(left, bottom, w, h, self.x, self.y)
