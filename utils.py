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


def move_to(x, y):
    # The world is a torus, so normalize negatives to a positive number of moves
    west_len = (get_pos_x() - x) % get_world_size()
    if west_len < get_world_size() / 2:
        ew_dir = West
    else:
        ew_dir = East
    while get_pos_x() != x:
        move(ew_dir)

    north_len = (get_pos_y() - y) % get_world_size()
    if north_len < get_world_size() / 2:
        ns_dir = South
    else:
        ns_dir = North
    while get_pos_y() != y:
        move(ns_dir)


def opposite(dir):
    if dir == North:
        return South
    if dir == South:
        return North
    if dir == East:
        return West
    return East
