from utils import move_to


def measure_bamboo() -> int:
    return measure()  # type: ignore


def bamboo(x, y):
    move_to(x, y)
    size = get_world_size()

    init = True
    while True:
        left_heights = []
        right_heights = []

        for i in range(size):
            if init:
                dig()
            plant(Entities.Bamboo)
            left_heights.append(measure_bamboo())
            if i == size - 1:
                move(East)
            move(North)
        if init:
            for _ in range(size):
                dig()
                move(North)
        move(East)
        for i in range(size):
            if init:
                dig()
            plant(Entities.Bamboo)
            right_heights.append(measure_bamboo())
            if i == size - 1:
                move(West)
            move(North)

        for _ in range(2):
            for i in range(size):
                hover(left_heights[i])
                move(West)
                left_heights[i] = measure_bamboo()
                move(East)

                hover(right_heights[i])
                move(East)
                right_heights[i] = measure_bamboo()
                move(West)

                move(North)

        hover(0)
        do_a_flip()
        do_a_flip()
        do_a_flip()
        move(East)
        for _ in range(size):
            move(North)
        move(West)
        move(West)
        for _ in range(size):
            move(North)

        init = False


if __name__ == "__main__":
    clear()
    bamboo(0, 0)
