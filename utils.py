from __builtins__ import (
    East,
    North,
    South,
    West,
    get_pos_x,
    get_pos_y,
    get_world_size,
    move,
)

# Save us a tick per call, we assume the world size doesn't change mid-run.
WORLD_SIZE = get_world_size()


def move_to(x, y, current_x=None, current_y=None):
    # In case we know where we are already, we can save 2 ticks.
    if current_x == None:
        current_x = get_pos_x()
    if current_y == None:
        current_y = get_pos_y()
    # The world is a torus, so normalize negatives to a positive number of moves
    west_len = (current_x - x) % WORLD_SIZE
    if west_len < WORLD_SIZE / 2:
        ew_dir = West
        ew_distance = west_len
    else:
        ew_dir = East
        ew_distance = WORLD_SIZE - west_len
    for _ in range(ew_distance):
        move(ew_dir)

    north_len = (current_y - y) % WORLD_SIZE
    if north_len < WORLD_SIZE / 2:
        ns_dir = South
        ns_distance = north_len
    else:
        ns_dir = North
        ns_distance = WORLD_SIZE - north_len
    for _ in range(ns_distance):
        move(ns_dir)


def opposite(dir):
    if dir == North:
        return South
    if dir == South:
        return North
    if dir == East:
        return West
    return East


def visit_rectangle(size_x, size_y, action):
    # Visits every spot in a rectange and applies an action.
    # Goes in this order (6x6 for example):
    #
    # v<<<<<
    # v>>>>^
    # v^<<<<
    # v>>>>^
    # v^<<<<
    # >>>>>^
    #
    # Assumes starting in the lower-left corner, and returns there.
    action()
    move(East)
    size_y_1 = size_y - 1
    size_x_2 = size_x - 2
    is_east = True
    for i in range(size_y):
        if is_east:
            dir = East
        else:
            dir = West

        for _ in range(size_x_2):
            action()
            move(dir)
        action()
        if i < size_y_1:
            move(North)
        is_east = not is_east
    move(West)
    for _ in range(size_y_1):
        action()
        move(South)


def visit_square(size, action):
    visit_rectangle(size, size, action)
