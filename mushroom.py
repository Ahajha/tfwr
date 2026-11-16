from utils import move_to, opposite, visit_square


def basic_mushroom():
    set_world_size(6)
    jump(Unlocks.Mushrooms)

    def dig_to_mushroom():
        while get_ground_type() != Grounds.Mushroom:
            dig()

    visit_square(6, dig_to_mushroom)

    move_to(3, 3)

    dig()

    dug = [(3, 3)]

    def get_valid_directions():
        size = get_world_size()
        dirs = []
        if get_pos_x() <= size - 1:
            dirs.append(East)
        if get_pos_x() > 0:
            dirs.append(West)
        if get_pos_y() <= size - 1:
            dirs.append(North)
        if get_pos_y() > 0:
            dirs.append(South)
        return dirs

    def solve_mushroom() -> bool:
        mushroom_kind = measure()
        height = get_pos_z()
        for dir in get_valid_directions():
            move(dir)
            if measure() == mushroom_kind and get_pos_z() > height:
                if not push(opposite(dir)):
                    print("Failed to push")
                move(opposite(dir))
                harvest()
                return True
            else:
                move(opposite(dir))
        return False

    while True:
        new_dug = []
        for x, y in dug:
            move_to(x, y)
            if solve_mushroom():
                new_dug.append((x, y))
            else:
                dirs = get_valid_directions()
                rand_dir = dirs[(random() * len(dirs)) // 1]
                move(rand_dir)
                push(opposite(rand_dir))
                new_dug.append((get_pos_x(), get_pos_y()))
        dug = new_dug


def measure_mushroom() -> int:
    return measure()  # type: ignore


def mushroom():
    jump(Unlocks.Mushrooms)

    size = get_world_size()
    # Grid of (measure, height)
    info: list[list[tuple[int, int]]] = []
    for _ in range(size):
        row = []
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
        push(dir)
        info[src_x][src_y] = (measure_mushroom(), get_pos_z())
        move(dir)
        harvest()
        if get_ground_type() != Grounds.Mushroom:
            place(Grounds.Dirt)
            info[dst_x][dst_y] = (100, 100)
        else:
            info[dst_x][dst_y] = (measure_mushroom(), get_pos_z())
        new_to_visit.add((src_x, src_y))
        new_to_visit.add((dst_x, dst_y))
        return 2

    while to_visit:
        for x, y in to_visit:
            mtype, z = info[x][y]
            candidate_random_dirs = []
            if x < size - 1:
                result = try_dir(x, y, z, mtype, x + 1, y, West)
                if result == 2:
                    continue
                elif result == 1:
                    candidate_random_dirs.append(East)
            if x > 0:
                result = try_dir(x, y, z, mtype, x - 1, y, East)
                if result == 2:
                    continue
                elif result == 1:
                    candidate_random_dirs.append(West)
            if y < size - 1:
                result = try_dir(x, y, z, mtype, x, y + 1, South)
                if result == 2:
                    continue
                elif result == 1:
                    candidate_random_dirs.append(North)
            if y > 0:
                result = try_dir(x, y, z, mtype, x, y - 1, North)
                if result == 2:
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
                push(West)
                info[x + 1][y] = (measure_mushroom(), get_pos_z())
                move(West)
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x + 1, y))
                new_to_visit.add((x, y))
            if rand_dir == West:
                move_to(x - 1, y)
                push(East)
                info[x - 1][y] = (measure_mushroom(), get_pos_z())
                move(East)
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x - 1, y))
                new_to_visit.add((x, y))
            if rand_dir == North:
                move_to(x, y + 1)
                push(South)
                info[x][y + 1] = (measure_mushroom(), get_pos_z())
                move(South)
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x, y + 1))
                new_to_visit.add((x, y))
            if rand_dir == South:
                move_to(x, y - 1)
                push(North)
                info[x][y - 1] = (measure_mushroom(), get_pos_z())
                move(North)
                info[x][y] = (measure_mushroom(), get_pos_z())
                new_to_visit.add((x, y - 1))
                new_to_visit.add((x, y))

        to_visit = new_to_visit
        new_to_visit = set()

    while True:
        pass


if __name__ == "__main__":
    clear()
    # set_world_size(6)
    mushroom()
