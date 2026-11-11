from math import cos, pi

from pico2d import load_image, get_canvas_width

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


# ---------------------------------------------------------------------------
# 실제 단위 기반 크기 / 날갯짓 속도  (boy.py 와 같은 축척: 10px = 30cm)
# ---------------------------------------------------------------------------
PIXEL_PER_METER = (10.0 / 0.3)

# 새의 몸길이(부리~꼬리) 1.5m 로 설정. 시트에서 몸길이는 146px(날개를 접은
# 프레임의 폭)이므로 화면 크기 50px 이 되도록 축소 비율을 계산한다.
BIRD_SIZE_M = 1.5
BIRD_BODY_PX_IN_SHEET = 146
BIRD_SCALE = BIRD_SIZE_M * PIXEL_PER_METER / BIRD_BODY_PX_IN_SHEET

# 14프레임 = 날갯짓 1회(위로 든 날개 -> 내려치기 -> 다시 들어올리기).
# 이 크기의 새는 초당 약 2~3회 날갯짓하므로 2회/초로 설정.
# 1초에 재생할 프레임 수 = 초당 날갯짓 수 x 날갯짓 1회당 프레임 수
FLAPS_PER_SECOND = 2.0
FRAMES_PER_SECOND = FLAPS_PER_SECOND * FRAMES_PER_ACTION   # 28 fps

# 비행 속도: 20 km/h -> m/s -> px/s  (boy.py 의 RUN_SPEED 계산과 같은 방식)
FLY_SPEED_KMPH = 20.0
FLY_SPEED_MPM = (FLY_SPEED_KMPH * 1000.0 / 60.0)
FLY_SPEED_MPS = (FLY_SPEED_MPM / 60.0)
FLY_SPEED_PPS = (FLY_SPEED_MPS * PIXEL_PER_METER)          # 약 185 px/s

# 앵커(눈)에서 부리 끝까지의 거리. 시트에서 0번 프레임 기준
# 사각형 오른쪽 끝(중심 + 73) - 눈(중심 + 16) = 57px.
# 부리 끝이 화면 가장자리에 닿는 순간 방향을 바꾸기 위해 사용한다.
BEAK_LENGTH_PX = 57 * BIRD_SCALE

# 날갯짓 동기화 상하 움직임(bob)
# 날개를 내려칠 때(프레임 3~7) 양력이 생겨 몸이 올라가고, 날개를 들어올릴 때
# (프레임 10~13, 0) 몸이 내려간다. 시트 자체의 몸통 위치 차이는 앵커 보정으로
# 없앴으므로, 물리적으로 맞는 움직임을 프레임 값에 동기화해서 다시 넣는다.
#   bob = -BOB_AMPLITUDE * cos(2π (frame - LOWEST_FRAME) / 14)
#   -> frame = 0.5(날개 최고점, 내려치기 직전)에서 가장 낮고
#      frame = 7.5(내려치기 끝)에서 가장 높다.
# frame 이 실수이므로 프레임 경계에서도 끊기지 않고 부드럽게 움직인다.
BOB_AMPLITUDE_PX = 0.12 * PIXEL_PER_METER    # 12cm -> 4px
BOB_LOWEST_FRAME = 0.5


class Bird:
    image = None

    def __init__(self, x=800, y=400, dir=1, start_frame=0.0, flap_rate=1.0):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        self.dir = dir                      # 1: 오른쪽, -1: 왼쪽
        self.frame = start_frame            # 날갯짓 시작 위상 (0 ~ 14)
        self.frames_per_second = FRAMES_PER_SECOND * flap_rate   # 개체별 날갯짓 빈도

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + self.frames_per_second * dt) % FRAMES_PER_ACTION
        self.x += self.dir * FLY_SPEED_PPS * dt

        # 좌우 반복 비행: 부리 끝이 화면 끝에 닿으면 방향 전환.
        # 한 프레임에 경계를 넘어간 만큼은 반대쪽으로 되돌려(반사) 위치 오차를 없앤다.
        left_limit = BEAK_LENGTH_PX
        right_limit = get_canvas_width() - BEAK_LENGTH_PX
        if self.x > right_limit:
            self.x = 2 * right_limit - self.x
            self.dir = -1
        elif self.x < left_limit:
            self.x = 2 * left_limit - self.x
            self.dir = 1

    def draw(self):
        left, bottom, w, h, ox, oy = FRAMES[int(self.frame)]
        # 원본 그림은 오른쪽을 보고 있다. 왼쪽으로 날 때는 좌우 반전('h')하고,
        # 그림이 뒤집히면 눈에서 사각형 중심까지의 가로 오프셋도 뒤집혀야 하므로
        # ox 에 dir 을 곱한다. (크기를 줄인 만큼 오프셋도 BIRD_SCALE 배)
        flip = '' if self.dir == 1 else 'h'
        bob = -BOB_AMPLITUDE_PX * cos(2 * pi * (self.frame - BOB_LOWEST_FRAME) / FRAMES_PER_ACTION)
        Bird.image.clip_composite_draw(
            left, bottom, w, h, 0, flip,
            self.x + self.dir * ox * BIRD_SCALE, self.y + bob + oy * BIRD_SCALE,
            w * BIRD_SCALE, h * BIRD_SCALE)
