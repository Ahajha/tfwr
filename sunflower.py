from utils import move_to, visit_square


def measure_sunflower() -> int:
    return measure()  # type: ignore


def dumb_sunflower():
    init = True

    while True:
        size_to_locations: dict[int, list[tuple[int, int]]] = {}
        for size in range(7, 16):
            size_to_locations[size] = []

        def plant_sunflower():
            if init:
                till()
            while get_water() < 0.5:
                use_item(Items.Water)
            plant(Entities.Sunflower)
            size_to_locations[measure_sunflower()].append((get_pos_x(), get_pos_y()))

        visit_square(8, plant_sunflower)

        quick_print(size_to_locations)

        for size in range(15, 6, -1):
            for loc in size_to_locations[size]:
                move_to(loc[0], loc[1])
                while not can_harvest():
                    pass
                harvest()

        move_to(0, 0)

        init = False


if __name__ == "__main__":
    clear()
    dumb_sunflower()
