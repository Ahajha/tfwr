from cactus import cacti_thread
from maze import maze, solve_maze_multithreaded
from pumpkin import pumpkin_thread
from utils import move_to


def multithread_farm(id=0):
    width = 1  # get_world_size() / max_drones()
    for _ in range(width):
        move(North)
    spawn_drone(multithread_farm, id + 1)
    while True:
        for i in range(width):
            for _ in range(get_world_size()):
                if can_harvest():
                    harvest()
                elif get_water() < 0.5:
                    use_item(Items.Water)
                if (get_pos_x() + get_pos_y()) % 2 != 0:
                    plant(Entities.Tree)
                move(East)
            if i == width - 1:
                for _ in range(width - 1):
                    move(South)
            else:
                move(North)


def carrot_thread(start_x, start_y, vertical):
    move_to(start_x, start_y)
    bootstrap = True
    if vertical:
        direction = North
    else:
        direction = East
    while True:
        if bootstrap:
            till()
        else:
            if can_harvest():
                harvest()
            elif get_water() < 0.5:
                use_item(Items.Water)
        plant(Entities.Carrot)
        move(direction)
        if get_pos_x() == start_x and get_pos_y() == start_y:
            bootstrap = False


def pumpkin_dispatch():
    pumpkin_starts = [
        (16, 0),
        (8, 8),
        (24, 8),
        (0, 16),
        (16, 16),
        (8, 24),
        (24, 24),
    ]
    cacti_starts = [
        (8, 0),
        (24, 0),
        (0, 8),
        (16, 8),
        (8, 16),
        (24, 16),
        (0, 24),
        (16, 24),
    ]
    size = 6

    carrot_starts = [
        (6, 0, True),
        (7, 0, True),
        (14, 0, True),
        (15, 0, True),
        (22, 0, True),
        (23, 0, True),
        (30, 0, True),
        (31, 0, True),
        (0, 6, False),
        (0, 7, False),
        (0, 14, False),
        (0, 15, False),
        (0, 22, False),
        (0, 23, False),
        (0, 30, False),
        (0, 31, False),
    ]

    for start in pumpkin_starts:
        spawn_drone(pumpkin_thread, start[0], start[1], size)  # type: ignore
    for start in cacti_starts:
        spawn_drone(cacti_thread, start[0], start[1], size)  # type: ignore
    for start in carrot_starts:
        spawn_drone(carrot_thread, start[0], start[1], start[2])  # type: ignore
    pumpkin_thread(0, 0, size)


def get_fertilizer():
    while True:
        for j in range(get_world_size()):
            for i in range(get_world_size()):
                if i % 2 == j % 2:
                    if can_harvest():
                        harvest()
                    plant(Entities.Tree)
                    use_item(Items.Fertilizer)
                move(North)
                if i == get_world_size() - 1:
                    move(East)


def fast_hay(init=True, y=0):
    if init:
        clear()
        for i in range(max_drones() - 1):
            spawn_drone(fast_hay, False, i + 1)

    move_to(0, y)

    while True:
        move(East)
        harvest()


def mazes():
    maze()
    solve_maze_multithreaded()


clear()
pumpkin_dispatch()
# mazes()
# multithread_farm()
