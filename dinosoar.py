from utils import move_to

change_hat(Hats.Cactus_Hat)
# set_world_size(16)


def measure_apple() -> tuple[int, int]:
    return measure()  # type: ignore


size = get_world_size()


def should_do_loop(apple_pos, loop_num, length, size) -> bool:
    # Enough to loop around the map once. Anything more than this and we need loops.
    loop_length = length - (size - 1) * 4
    min_loops = loop_length / ((size - 2) * 2)

    # After a certain point, it's faster to just let it run.
    if loop_num < min_loops or min_loops >= 4:
        return True

    is_in_loop = apple_pos[1] != 0 and (
        apple_pos[0] == loop_num * 2 + 1 or apple_pos[0] == (loop_num * 2) + 2
    )
    if is_in_loop:
        return True

    return False


def dinosoar():
    length = 1
    move_to(0, 0)
    change_hat(Hats.Dinosaur_Hat)
    apple_pos = (-1, -1)  # placeholder

    while length < size * size:
        if get_entity_type() == Entities.Apple:
            quick_print(length, get_pos_x(), get_pos_y())
            apple_pos = measure_apple()
            length += 1
        move(East)

        for loop_num in range((size / 2) - 1):
            do_loop = should_do_loop(apple_pos, loop_num, length, size)
            if do_loop:
                for _ in range(size - 2):
                    if get_entity_type() == Entities.Apple:
                        quick_print(length, get_pos_x(), get_pos_y())
                        apple_pos = measure_apple()
                        length += 1
                    move(North)
            if get_entity_type() == Entities.Apple:
                quick_print(length, get_pos_x(), get_pos_y())
                apple_pos = measure_apple()
                length += 1
            move(East)
            if do_loop:
                for _ in range(size - 2):
                    if get_entity_type() == Entities.Apple:
                        quick_print(length, get_pos_x(), get_pos_y())
                        apple_pos = measure_apple()
                        length += 1
                    move(South)
            if get_entity_type() == Entities.Apple:
                quick_print(length, get_pos_x(), get_pos_y())
                apple_pos = measure_apple()
                length += 1
            move(East)

        for _ in range(size - 1):
            if get_entity_type() == Entities.Apple:
                quick_print(length, get_pos_x(), get_pos_y())
                apple_pos = measure_apple()
                length += 1
            move(North)
        for _ in range(size - 1):
            if get_entity_type() == Entities.Apple:
                quick_print(length, get_pos_x(), get_pos_y())
                apple_pos = measure_apple()
                length += 1
            move(West)
        for _ in range(size - 1):
            if get_entity_type() == Entities.Apple:
                quick_print(length, get_pos_x(), get_pos_y())
                apple_pos = measure_apple()
                length += 1
            move(South)

    change_hat(Hats.Cactus_Hat)


while True:
    dinosoar()
