from pico2d import load_image


class Bird:
    image = None

    def __init__(self, x=800, y=400):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        self.frame = 0

    def update(self):
        pass

    def draw(self):
        # 첫 번째 프레임(시트 왼쪽 위)만 표시
        Bird.image.clip_draw(34, 362, 146, 143, self.x, self.y)
