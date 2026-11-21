from utils import move_to, opposite, visit_square


def measure_mushroom() -> int | None:
    return measure()  # type: ignore


def assert_(condition):
    if not condition:
        pass


def setup_mushroom(size) -> list[list[tuple[int | None, int]]]:
    jump(Unlocks.Mushrooms)

    # Grid of (measure, height)
    info: list[list[tuple[int | None, int]]] = []
    for _ in range(size):
        row: list[tuple[int | None, int]] = []
        for _ in range(size):
            row.append((0, 0))
        info.append(row)

    def measure_mushroom_action():
        while get_ground_type() != Grounds.Mushroom:
            dig()
        info[get_pos_x()][get_pos_y()] = (measure_mushroom(), get_pos_z())

    visit_square(size, measure_mushroom_action)

    move_to(size // 2, size // 2)
    dig()
    info[size // 2][size // 2] = (measure_mushroom(), get_pos_z())
    return info


def semirandom_mushroom(info, size, target):
    # This starts a mushroom layer off with some randomness, since it's pretty
    # easy to get stuck in the initial few 'shrooms without some randomness.

    to_visit = set([(size // 2, size // 2)])
    new_to_visit: set[tuple[int, int]] = set()

    def try_dir(dst_x, dst_y, dst_z, mtype_dst, src_x, src_y, dir) -> int:
        # src: where does the top mushroom come from
        # dst: where is the mushroom going

        # Return value:
        # 0 = Can't push due to z-height difference
        # 1 = Mismatched types
        # 2 = Success
        mtype_src, src_z = info[src_x][src_y]
        if src_z <= dst_z:
            return 0

        if mtype_src != mtype_dst:
            return 1

        move_to(src_x, src_y)
        assert_(push(dir))
        info[src_x][src_y] = (measure_mushroom(), get_pos_z())
        assert_(move(dir))
        if get_ground_type() != Grounds.Mushroom:
            place(Grounds.Dirt)
            info[dst_x][dst_y] = (None, get_pos_z())
        else:
            info[dst_x][dst_y] = (measure_mushroom(), get_pos_z())
        new_to_visit.add((src_x, src_y))
        new_to_visit.add((dst_x, dst_y))
        return 2

    n_mined = 0
    while n_mined < target:
        for x, y in to_visit:
            mtype, z = info[x][y]
            if mtype == None:
                continue
            candidate_random_dirs = []
            if x < size - 1:
                result = try_dir(x, y, z, mtype, x + 1, y, West)
                if result == 2:
                    n_mined += 1
                    continue
                elif result == 1:
                    candidate_random_dirs.append(East)
            if x > 0:
                result = try_dir(x, y, z, mtype, x - 1, y, East)
                if result == 2:
                    n_mined += 1
                    continue
                elif result == 1:
                    candidate_random_dirs.append(West)
            if y < size - 1:
                result = try_dir(x, y, z, mtype, x, y + 1, South)
                if result == 2:
                    n_mined += 1
                    continue
                elif result == 1:
                    candidate_random_dirs.append(North)
            if y > 0:
                result = try_dir(x, y, z, mtype, x, y - 1, North)
                if result == 2:
                    n_mined += 1
                    continue
                elif result == 1:
                    candidate_random_dirs.append(South)

            # If none of those worked, do a random push
            if not candidate_random_dirs:
                continue
            rand_dir = candidate_random_dirs[  # type: ignore
                (random() * len(candidate_random_dirs)) // 1
            ]
            if rand_dir == East:
                move_to(x + 1, y)
                assert_(push(West))
                info[x + 1][y] = (measure_mushroom(), get_pos_z())
                assert_(move(West))
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x + 1, y))
                new_to_visit.add((x, y))
            if rand_dir == West:
                move_to(x - 1, y)
                assert_(push(East))
                info[x - 1][y] = (measure_mushroom(), get_pos_z())
                assert_(move(East))
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x - 1, y))
                new_to_visit.add((x, y))
            if rand_dir == North:
                move_to(x, y + 1)
                assert_(push(South))
                info[x][y + 1] = (measure_mushroom(), get_pos_z())
                assert_(move(South))
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x, y + 1))
                new_to_visit.add((x, y))
            if rand_dir == South:
                move_to(x, y - 1)
                assert_(push(North))
                info[x][y - 1] = (measure_mushroom(), get_pos_z())
                assert_(move(North))
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x, y - 1))
                new_to_visit.add((x, y))

        to_visit = new_to_visit
        new_to_visit = set()


def can_push_east(x, y, size, info, is_src_origin) -> bool:
    if x == size - 1:
        return False
    src_z = info[x][y][1]
    dst_z = info[x + 1][y][1]
    if is_src_origin:
        return src_z > dst_z
    else:
        return src_z >= dst_z


def can_push_west(x, y, info, is_src_origin) -> bool:
    if x == 0:
        return False
    src_z = info[x][y][1]
    dst_z = info[x - 1][y][1]
    if is_src_origin:
        return src_z > dst_z
    else:
        return src_z >= dst_z


def can_push_north(x, y, size, info, is_src_origin) -> bool:
    if y == size - 1:
        return False
    src_z = info[x][y][1]
    dst_z = info[x][y + 1][1]
    if is_src_origin:
        return src_z > dst_z
    else:
        return src_z >= dst_z


def can_push_south(x, y, info, is_src_origin) -> bool:
    if y == 0:
        return False
    src_z = info[x][y][1]
    dst_z = info[x][y - 1][1]
    if is_src_origin:
        return src_z > dst_z
    else:
        return src_z >= dst_z


# Maintain a list of mushrooms on the bottom level
#    - Then we can do proper A* to them
# If there isn't a mushroom of a certain kind at that level, make one by digging and pushing

DIRS = [North, East, South, West]

DIR_TO_OFFSETS = {
    North: (0, 1),
    East: (1, 0),
    South: (0, -1),
    West: (-1, 0),
}


def is_in_range(dir: Direction, x, y, size) -> bool:
    if dir == North:
        return y + 1 < size
    if dir == East:
        return x + 1 < size
    if dir == South:
        return y > 0
    return x > 0


def lower_mushroom(
    size: int,
    mushroom_type: int,
    info: list[list[tuple[int | None, int]]],
    min_layer: int,
):
    # Looks for a mushroom of a certain kind that can be lowered
    # onto the ground level.
    for x in range(size):
        for y in range(size):
            if info[x][y][0] != mushroom_type:
                continue
            if info[x][y][1] == min_layer:
                continue
            for dir in DIRS:
                if not is_in_range(dir, x, y, size):
                    continue
                x_offset, y_offset = DIR_TO_OFFSETS[dir]
                x_mod = x + x_offset
                y_mod = y + y_offset
                mtype, z_mod = info[x_mod][y_mod]
                if mtype != None:
                    continue
                opp = opposite(dir)
                move_to(x_mod, y_mod)
                assert_(measure() == None)
                dig()
                assert_(measure() == None)
                move(opp)
                assert_(push(dir))
                assert_(info[x_mod][y_mod][1] == min_layer)
                info[x_mod][y_mod] = (  # type: ignore
                    measure(dir),
                    get_pos_z(dir),
                )
                move(dir)
                info[x][y] = (  # type: ignore
                    measure(opp),
                    get_pos_z(opp),
                )
                return


def a_star_mushroom():
    size = get_world_size()
    info = setup_mushroom(size)
    semirandom_mushroom(info, size, 5)

    while True:
        quick_print("starting the loop")
        min_layer = None
        has_mtypes = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False}
        for i in range(size):
            for j in range(size):
                if info[i][j][0] == None:
                    min_layer = info[i][j][1]
        if min_layer:
            for i in range(size):
                for j in range(size):
                    if info[i][j][0] != None and info[i][j][1] == min_layer:
                        has_mtypes[info[i][j][0]] = True

        if min_layer != None:
            for mushroom_type in range(0, 6):
                if not has_mtypes[mushroom_type]:
                    lower_mushroom(size, mushroom_type, info, min_layer)

        for i in range(size):
            for j in range(size):
                to_visit = [(i, j)]
                from_origin: dict[tuple[int, int], Direction | None] = {(i, j): None}
                target = info[i][j][0]
                if target == None:
                    continue
                destination: tuple[int, int] | None = None
                new_to_visit: list[tuple[int, int]] = []
                while destination == None and to_visit:
                    for x, y in to_visit:
                        is_src_origin = (x, y) == (i, j)
                        if (
                            can_push_east(x, y, size, info, is_src_origin)
                            and (x + 1, y) not in from_origin
                        ):
                            from_origin[(x + 1, y)] = East
                            new_to_visit.append((x + 1, y))

                            if info[x + 1][y][0] == target:
                                # Done!
                                destination = (x + 1, y)
                                break

                        if (
                            can_push_west(x, y, info, is_src_origin)
                            and (x - 1, y) not in from_origin
                        ):
                            from_origin[(x - 1, y)] = West
                            new_to_visit.append((x - 1, y))

                            if info[x - 1][y][0] == target:
                                # Done!
                                destination = (x - 1, y)
                                break

                        if (
                            can_push_north(x, y, size, info, is_src_origin)
                            and (x, y + 1) not in from_origin
                        ):
                            from_origin[(x, y + 1)] = North
                            new_to_visit.append((x, y + 1))

                            if info[x][y + 1][0] == target:
                                # Done!
                                destination = (x, y + 1)
                                break

                        if (
                            can_push_south(x, y, info, is_src_origin)
                            and (x, y - 1) not in from_origin
                        ):
                            from_origin[(x, y - 1)] = South
                            new_to_visit.append((x, y - 1))

                            if info[x][y - 1][0] == target:
                                # Done!
                                destination = (x, y - 1)
                                break

                    to_visit = new_to_visit
                    new_to_visit = []
                if destination == None:
                    continue

                move_to(i, j)

                steps: list[Direction] = []
                current = destination
                while current != (i, j):
                    dir = from_origin[current]
                    assert_(dir != None)
                    steps.append(dir)  # type: ignore
                    if dir == North:
                        current = (current[0], current[1] - 1)
                    elif dir == South:
                        current = (current[0], current[1] + 1)
                    elif dir == East:
                        current = (current[0] - 1, current[1])
                    else:
                        current = (current[0] + 1, current[1])

                # Only the first and last spots need to update their info
                assert_(push(steps[-1]))
                quick_print(info[get_pos_x()][get_pos_y()])
                info[get_pos_x()][get_pos_y()] = (measure_mushroom(), get_pos_z())
                assert_(move(steps[-1]))

                for idx in range(len(steps) - 1):
                    dir = steps[len(steps) - idx - 2]
                    if idx != len(steps) - 2:
                        assert_(measure(dir) != target)
                    assert_(push(dir))
                    assert_(info[get_pos_x()][get_pos_y()][1] == get_pos_z())
                    assert_(move(dir))

                if get_ground_type() != Grounds.Mushroom:
                    quick_print(get_pos_z())
                    place(Grounds.Dirt)
                    info[get_pos_x()][get_pos_y()] = (None, get_pos_z())

                else:
                    info[get_pos_x()][get_pos_y()] = (measure_mushroom(), get_pos_z())


if __name__ == "__main__":
    clear()
    set_world_size(16)
    a_star_mushroom()
