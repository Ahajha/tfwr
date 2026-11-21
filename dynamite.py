from utils import move_to, visit_rectangle


def dig_to_dynamite_action():
    while get_ground_type() != Grounds.Dynamite:
        dig()


def dig_to_dynamite(x, y, size_x, size_y):
    move_to(x, y)
    visit_rectangle(size_x, size_y, dig_to_dynamite_action)


def count_adjacent(x, y, size, info) -> tuple[int, int]:
    adj_dynamite = 0
    adj_unknown = 0
    for x_offset in (-1, 0, 1):
        if x + x_offset >= size:
            continue
        if x + x_offset < 0:
            continue
        for y_offset in (-1, 0, 1):
            if y + y_offset >= size:
                continue
            if y + y_offset < 0:
                continue
            if x_offset == 0 and y_offset == 0:
                continue
            if info[x + x_offset][y + y_offset] == None:
                adj_unknown += 1
            elif info[x + x_offset][y + y_offset] == DYNAMITE:
                adj_dynamite += 1
    return adj_dynamite, adj_unknown


DYNAMITE = 9


def mark_unknown_neighbors_as_dynamite(x, y, size, info):
    for x_offset in (-1, 0, 1):
        if x + x_offset >= size:
            continue
        if x + x_offset < 0:
            continue
        for y_offset in (-1, 0, 1):
            if y + y_offset >= size:
                continue
            if y + y_offset < 0:
                continue
            if x_offset == 0 and y_offset == 0:
                continue
            if info[x + x_offset][y + y_offset] == None:
                info[x + x_offset][y + y_offset] = DYNAMITE


def dig_unknown_neighbors(x, y, size, info, new_to_resolve):
    for x_offset in (-1, 0, 1):
        if x + x_offset >= size:
            continue
        if x + x_offset < 0:
            continue
        for y_offset in (-1, 0, 1):
            if y + y_offset >= size:
                continue
            if y + y_offset < 0:
                continue
            if x_offset == 0 and y_offset == 0:
                continue
            if info[x + x_offset][y + y_offset] == None:
                move_to(x + x_offset, y + y_offset)
                dig()
                new_to_resolve.add((get_pos_x(), get_pos_y()))
                info[get_pos_x()][get_pos_y()] = measure()


def dynamite():
    size = get_world_size()
    drones = []
    for x in range(0, get_world_size(), 4):
        for y in range(0, get_world_size(), 8):
            if x == 0 and y == 0:
                continue
            drones.append(spawn_drone(dig_to_dynamite, x, y, 4, 8))
    dig_to_dynamite(0, 0, 4, 8)
    for drone in drones:
        wait_for(drone)

    move_to(size / 2, size / 2)

    dig()

    # Each item is 0-9, or None. 0-8 is empty with a hint, 9 is a marked bomb. None is unknown.
    info: list[list[int | None]] = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        info.append(row)

    info[get_pos_x()][get_pos_y()] = measure()  # type: ignore

    to_resolve = set([(get_pos_x(), get_pos_y())])

    while to_resolve:
        # Concurrent modification nonsense
        new_to_resolve = set()
        for x, y in to_resolve:
            adj_dynamite, adj_unknown = count_adjacent(x, y, size, info)
            hint = info[x][y]
            # If the # of dynamites + # of unknowns == the hint, mark all unknowns as dynamite
            if adj_dynamite + adj_unknown == hint:
                mark_unknown_neighbors_as_dynamite(x, y, size, info)

            # If hint == # of dynamites, dig the rest
            elif hint == adj_dynamite:
                dig_unknown_neighbors(x, y, size, info, new_to_resolve)

            else:
                new_to_resolve.add((x, y))

        to_resolve = new_to_resolve


if __name__ == "__main__":
    set_world_size(8)
    jump(Unlocks.Dynamite)
    dynamite()
