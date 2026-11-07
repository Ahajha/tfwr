from __builtins__ import (
    Direction,
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
    get_time,
    harvest,
    measure,
    move,
    plant,
    quick_print,
    spawn_drone,
    swap,
    till,
    wait_for,
)
from utils import WORLD_SIZE, move_to, opposite, visit_square


# For laundering the return type, since it depends on the entity. Purely to make type checking happy.
def measure_cactus(dir=None) -> int:
    return measure(dir)  # type: ignore


# to figure out if a spot needs sorting:
# compare N/E -> NE_MIN
# compare S/W -> SW_MAX
# assert SW_MAX < Self < NE_MIN

# Greedy algorithm, I _think_ it is optimal but not certain.
# (probably easyish to prove exhaustively)
# Algorithm is as follows:
# Sort middle/north/east
# Sort middle/south/west
# If middle/north/east is sorted, exit, else sort
# If middle/south/west is sorted, exit, else sort
# If middle/north/east is sorted, exit, else sort
# (worst case is 5 swaps)


def swap_contents(layout: list[list[int]], x1: int, y1: int, x2: int, y2: int):
    tmp = layout[x1][y1]
    layout[x1][y1] = layout[x2][y2]
    layout[x2][y2] = tmp


def sort_ne(
    layout: list[list[int]],
    x: int,
    y: int,
    size: int,
    coord: tuple[int, int],
    new_sort_spots: list[tuple[int, int]],
) -> bool:
    # Return True iff a swap occurred
    # Return True iff a swap occurred
    current_size = layout[x][y]

    if x + 1 < size:
        east_size = layout[x + 1][y]
    else:
        east_size = None

    if y + 1 < size:
        north_size = layout[x][y + 1]
    else:
        north_size = None

    swap_dir = None
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
        return False

    swap(swap_dir)
    if swap_dir == North:
        new_sort_spots.append((coord[0], coord[1] + 1))
        swap_contents(layout, x, y + 1, x, y)
    else:
        new_sort_spots.append((coord[0] + 1, coord[1]))
        swap_contents(layout, x + 1, y, x, y)

    return True


def sort_sw(
    layout: list[list[int]],
    x: int,
    y: int,
    coord: tuple[int, int],
    new_sort_spots: list[tuple[int, int]],
):
    # Return True iff a swap occurred
    current_size = layout[x][y]

    if x > 0:
        west_size = layout[x - 1][y]
    else:
        west_size = None

    if y > 0:
        south_size = layout[x][y - 1]
    else:
        south_size = None

    swap_dir = None
    if west_size != None and current_size < west_size:
        if south_size != None and west_size < south_size:
            swap_dir = South
        else:
            swap_dir = West
    elif south_size != None and current_size < south_size:
        swap_dir = South

    if swap_dir == None:
        return False

    swap(swap_dir)
    if swap_dir == South:
        new_sort_spots.append((coord[0], coord[1] - 1))
        swap_contents(layout, x, y - 1, x, y)
    else:
        new_sort_spots.append((coord[0] - 1, coord[1]))
        swap_contents(layout, x - 1, y, x, y)

    return True


def sort_cross(layout, x, y, size, coord, new_sort_spots):
    sort_ne(layout, x, y, size, coord, new_sort_spots)
    if not sort_sw(layout, x, y, coord, new_sort_spots):
        return
    if not sort_ne(layout, x, y, size, coord, new_sort_spots):
        return
    if not sort_sw(layout, x, y, coord, new_sort_spots):
        return
    sort_ne(layout, x, y, size, coord, new_sort_spots)


def cacti_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    while True:
        move_to(start_x, start_y)
        harvest()

        layout: list[list[int]] = []
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append(-1)
            layout.append(row)
        sort_spots = []

        def plant_cactus():
            if get_entity_type() != Entities.Cactus:
                if not plant(Entities.Cactus):
                    till()
                    plant(Entities.Cactus)
            sort_spots.append((get_pos_x(), get_pos_y()))

        visit_square(size, plant_cactus)

        if size == 6:

            def measure():
                x = get_pos_x() - start_x
                y = get_pos_y() - start_y

                layout[x + 1][y] = measure_cactus(East)
                layout[x][y] = measure_cactus()
                layout[x - 1][y] = measure_cactus(West)

            move(East)
            measure()
            move(East)
            move(East)
            move(East)

            for _ in range(5):
                measure()
                move(North)
            measure()
            for _ in range(3):
                move(West)
            for _ in range(4):
                measure()
                move(South)
            measure()
        else:

            def analyze():
                while not can_harvest():
                    continue

                layout[get_pos_x() - start_x][get_pos_y() - start_y] = measure_cactus()

            visit_square(size, analyze)

        while len(sort_spots) > 0:
            # Weird concurrent modification stuff, just reconstruct the list each time
            new_sort_spots = []
            visited = set()
            for spot in sort_spots:
                if spot in visited:
                    continue
                visited.add(spot)
                x = spot[0] - start_x
                y = spot[1] - start_y

                current_size = layout[x][y]
                needs_sort = (
                    (x + 1 < size and layout[x + 1][y] < current_size)
                    or (x > 0 and layout[x - 1][y] > current_size)
                    or (y + 1 < size and layout[x][y + 1] < current_size)
                    or (y > 0 and layout[x][y - 1] > current_size)
                )

                if not needs_sort:
                    continue

                move_to(spot[0], spot[1])

                sort_cross(layout, x, y, size, spot, new_sort_spots)

            sort_spots = new_sort_spots


def cocktail_shaker(dir: Direction, x, y, size):
    move_to(x, y)
    opp = opposite(dir)
    # For now, we just sort the one in front of us. We can optimize a bit later.
    # If there are N spaces, we need to do ~N passes (again, optimize later)
    for i in range(size):
        did_swap = False
        for j in range(size - i - 1):
            if i % 2 == 0:
                if measure_cactus() > measure_cactus(dir):
                    swap(dir)
                    did_swap = True
                if j != size - i - 2:
                    move(dir)
            else:
                if measure_cactus() < measure_cactus(opp):
                    swap(opp)
                    did_swap = True
                if j != size - i - 2:
                    move(opp)
        if not did_swap:
            break


def mega_plant(x, y, size, bootstrap):
    move_to(x, y)
    for _ in range(size):
        if bootstrap:
            till()
        plant(Entities.Cactus)
        move(North)

    move_to(x, y)  # noop if size == WORLD_SIZE

    cocktail_shaker(North, x, y, size)


def mega_cactus(size=WORLD_SIZE):
    # 32 x 32 cactus!

    bootstrap = True
    while True:
        start = get_time()

        drones = []
        for i in range(size - 1):
            drones.append(spawn_drone(mega_plant, i + 1, 0, size, bootstrap))  # type: ignore
        mega_plant(0, 0, size, bootstrap)

        for drone in drones:
            wait_for(drone)

        for i in range(size - 1):
            drones.append(spawn_drone(cocktail_shaker, East, 0, i + 1, size))  # type: ignore

        cocktail_shaker(East, 0, 0, size)

        for drone in drones:
            wait_for(drone)

        harvest()

        end = get_time()

        quick_print("duration: ", (end - start))

        bootstrap = False
