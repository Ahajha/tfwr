from __builtins__ import (
    East,
    Entities,
    Items,
    North,
    South,
    West,
    can_harvest,
    clear,
    do_a_flip,
    get_entity_type,
    get_pos_x,
    get_pos_y,
    get_water,
    get_world_size,
    harvest,
    max_drones,
    measure,
    move,
    plant,
    spawn_drone,
    swap,
    till,
    use_item,
)
from maze import maze, solve_maze_multithreaded
from utils import move_to


def copy_list(lst, n):
    result = []
    for _ in range(n):
        result += lst
    return result


# For laundering the return type, since it depends on the entity. Purely to make type checking happy.
def measure_cactus(dir) -> int | None:
    return measure(dir)  # type: ignore


def measure_cactus_current() -> int:
    return measure()  # type: ignore


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


def pumpkin_thread_action(analyze_mode, redo_spots):
    if analyze_mode:
        while True:
            if can_harvest():
                break
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                redo_spots.append((get_pos_x(), get_pos_y()))
                break
    else:
        if get_entity_type() != Entities.Pumpkin:
            if not plant(Entities.Pumpkin):
                till()
                plant(Entities.Pumpkin)


def pumpkin_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    while True:
        move_to(start_x, start_y)
        harvest()

        analyze_mode = False
        redo_spots = []

        for _ in range(2):
            for i in range(size):
                for _ in range(size - 2):
                    pumpkin_thread_action(analyze_mode, redo_spots)
                    if i % 2 == 0:
                        move(East)
                    else:
                        move(West)
                pumpkin_thread_action(analyze_mode, redo_spots)
                if i == 0:
                    move(East)
                    pumpkin_thread_action(analyze_mode, redo_spots)
                if i < size - 1:
                    move(North)
                else:
                    move(West)
                    while get_pos_y() != start_y:
                        pumpkin_thread_action(analyze_mode, redo_spots)
                        move(South)
            analyze_mode = True

        while len(redo_spots) > 0:
            # Weird concurrent modification stuff, just reconstruct the list each time
            new_redo_spots = []
            for spot in redo_spots:
                move_to(spot[0], spot[1])
                # Since we look at things in the same order each time, it doesn't really make sense
                # to skip over something that isn't ready.
                while not can_harvest() and get_entity_type() != Entities.Dead_Pumpkin:
                    if get_water() < 0.5:
                        use_item(Items.Water)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    new_redo_spots.append(spot)
            redo_spots = new_redo_spots


def cacti_thread_action(analyze_mode, layout, start_x, start_y, sort_spots):
    if analyze_mode:
        while not can_harvest():
            continue

        layout[get_pos_x() - start_x][get_pos_y() - start_y] = measure_cactus_current()
        sort_spots.append((get_pos_x(), get_pos_y()))
    else:
        if get_entity_type() != Entities.Cactus:
            if not plant(Entities.Cactus):
                till()
                plant(Entities.Cactus)


def cacti_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    while True:
        move_to(start_x, start_y)
        harvest()

        analyze_mode = False
        layout = [
            # HACK
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
            copy_list([-1], size),
        ]
        sort_spots = []

        for _ in range(2):
            for i in range(size):
                for _ in range(size - 2):
                    cacti_thread_action(
                        analyze_mode,
                        layout,
                        start_x,
                        start_y,
                        sort_spots,
                    )
                    if i % 2 == 0:
                        move(East)
                    else:
                        move(West)
                cacti_thread_action(
                    analyze_mode,
                    layout,
                    start_x,
                    start_y,
                    sort_spots,
                )
                if i == 0:
                    move(East)
                    cacti_thread_action(
                        analyze_mode,
                        layout,
                        start_x,
                        start_y,
                        sort_spots,
                    )
                if i < size - 1:
                    move(North)
                else:
                    move(West)
                    while get_pos_y() != start_y:
                        cacti_thread_action(
                            analyze_mode,
                            layout,
                            start_x,
                            start_y,
                            sort_spots,
                        )
                        move(South)
            analyze_mode = True

        while len(sort_spots) > 0:
            # Weird concurrent modification stuff, just reconstruct the list each time
            new_sort_spots = []
            for spot in sort_spots:
                x = spot[0] - start_x
                y = spot[1] - start_y

                swap_dir = None

                current_size = layout[x][y]
                if x + 1 < size:
                    east_size = layout[x + 1][y]
                else:
                    east_size = None
                if y + 1 < size:
                    north_size = layout[x][y + 1]
                else:
                    north_size = None
                if east_size != None and current_size > east_size:
                    if north_size != None and east_size > north_size:
                        # N E C swap N
                        swap_dir = North
                    else:
                        # E C N swap E
                        # E N C swap E
                        swap_dir = East
                elif north_size != None and current_size > north_size:
                    # N C E swap N
                    swap_dir = North
                # Else:
                # C N E noop
                # C E N noop

                if swap_dir == None:
                    continue

                move_to(spot[0], spot[1])
                swap(swap_dir)
                # TODO: 2 schools of thought: do we just do N/E, or do we also cover S/W at the same time?
                if x > 0:
                    new_sort_spots.append((spot[0] - 1, spot[1]))
                if y > 0:
                    new_sort_spots.append((spot[0], spot[1] - 1))
                if swap_dir == North:
                    new_sort_spots.append((spot[0], spot[1] + 1))
                    tmp = layout[x][y + 1]
                    layout[x][y + 1] = layout[x][y]
                    layout[x][y] = tmp
                else:
                    new_sort_spots.append((spot[0] + 1, spot[1]))
                    tmp = layout[x + 1][y]
                    layout[x + 1][y] = layout[x][y]
                    layout[x][y] = tmp
            sort_spots = new_sort_spots


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


def cacti(size):
    bootstrap = True
    while True:
        # Plant
        move_to(0, 0)
        for j in range(size):
            for i in range(size):
                if bootstrap:
                    till()
                plant(Entities.Cactus)
                if i == size - 1:
                    if j == size - 1:
                        continue
                    move(East)
                elif j % 2 == 0:
                    move(North)
                else:
                    move(South)
        bootstrap = False
        # Sort
        move_to(0, 0)
        while True:
            sorted = True
            for j in range(size):
                for i in range(size):
                    # Note: assumes anything outside of this is not measurable. Probably needs fixing.
                    current_size = measure_cactus_current()
                    north_size = measure_cactus(North)
                    east_size = measure_cactus(East)
                    if east_size != None and current_size > east_size:
                        if north_size != None and east_size > north_size:
                            # N E C swap N
                            swap(North)
                            sorted = False
                        else:
                            # E C N swap E
                            # E N C swap E
                            swap(East)
                            sorted = False
                    elif north_size != None and current_size > north_size:
                        # N C E swap N
                        swap(North)
                        sorted = False
                    # Else:
                    # C N E noop
                    # C E N noop

                    if i == size - 1:
                        if j == size - 1:
                            continue
                        move(East)
                    elif j % 2 == 0:
                        move(North)
                    else:
                        move(South)
            move_to(0, 0)
            if sorted:
                break
        harvest()


def mazes():
    maze()
    solve_maze_multithreaded()


clear()
pumpkin_dispatch()
# mazes()
# multithread_farm()
