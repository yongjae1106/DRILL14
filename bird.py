from pico2d import load_image

import game_framework

# 스프라이트 시트: 5열 x 3행, 총 14프레임(마지막 칸은 비어 있음)
FRAME_COLS = 5
FRAME_ROWS = 3
FRAMES_PER_ACTION = 14

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
        # 균등 그리드로 칸을 나눔 (918/5 = 183.6, 506/3 = 168.67)
        cell_w = Bird.image.w // FRAME_COLS
        cell_h = Bird.image.h // FRAME_ROWS
        index = int(self.frame)
        col, row = index % FRAME_COLS, index // FRAME_COLS
        # pico2d 는 아래쪽이 y=0 이므로 위쪽 행부터 읽으려면 뒤집어야 한다
        bottom = Bird.image.h - (row + 1) * cell_h
        Bird.image.clip_draw(col * cell_w, bottom, cell_w, cell_h, self.x, self.y)
