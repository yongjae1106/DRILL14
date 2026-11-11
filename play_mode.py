import random

from pico2d import *
import game_world
import game_framework
from boy import Boy
from grass import Grass
from bird import Bird, FRAMES_PER_ACTION

boy = None


def handle_events():


    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)


def init():
    global boy

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)

    for bird in make_flock():
        game_world.add_oject(bird)


BIRD_COUNT = 10
FLOCK_LEADER_X, FLOCK_LEADER_Y = 700, 420
FLOCK_GAP_X, FLOCK_GAP_Y = 60, 25
FLOCK_JITTER = 8            # 대형 위치를 흐트러뜨리는 범위(px)
FLAP_RATE_VARIATION = 0.15  # 날갯짓 빈도 ±15%


def make_flock():
    # 선두 새를 꼭짓점으로 하는 V자 대형.
    # i번째 새는 (i+1)//2 번째 줄에서 위/아래로 번갈아 배치되고
    # 줄이 뒤로 갈수록 선두보다 FLOCK_GAP_X 씩 뒤(진행 반대 방향)에 위치한다.
    flock = []
    for i in range(BIRD_COUNT):
        rank = (i + 1) // 2
        side = 1 if i % 2 == 1 else -1
        x = FLOCK_LEADER_X - rank * FLOCK_GAP_X + random.uniform(-FLOCK_JITTER, FLOCK_JITTER)
        y = FLOCK_LEADER_Y + side * rank * FLOCK_GAP_Y + random.uniform(-FLOCK_JITTER, FLOCK_JITTER)
        # 개체별 차이: 시작 프레임(위상)과 날갯짓 빈도를 다르게 해서
        # 10마리가 똑같이 움직이는 '복사본'처럼 보이지 않게 한다.
        # 비행 속도는 모두 같게 유지 -> 시간이 지나도 대형이 흩어지지 않음
        start_frame = random.uniform(0, FRAMES_PER_ACTION)
        flap_rate = random.uniform(1 - FLAP_RATE_VARIATION, 1 + FLAP_RATE_VARIATION)
        flock.append(Bird(x, y, 1, start_frame, flap_rate))
    return flock


def pause():
    boy.pause()


def resume():
    pass


def finish():
    global boy
    game_world.clear()
    boy = None


def update():
    game_world.update()

def render():
    clear_canvas()
    game_world.render()
    update_canvas()









