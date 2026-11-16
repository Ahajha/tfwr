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


if __name__ == "__main__":
    basic_mushroom()
