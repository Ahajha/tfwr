from __builtins__ import (
    East,
    Entities,
    North,
    South,
    West,
    can_harvest,
    do_a_flip,
    get_entity_type,
    get_pos_x,
    get_pos_y,
    harvest,
    measure,
    move,
    plant,
    swap,
    till,
)
from utils import move_to


# For laundering the return type, since it depends on the entity. Purely to make type checking happy.
def measure_cactus(dir) -> int | None:
    return measure(dir)  # type: ignore


def measure_cactus_current() -> int:
    return measure()  # type: ignore


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
        layout = []
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append(-1)
            layout.append(row)
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
