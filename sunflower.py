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


def multithreaded_sunflower(size=None):
    if size == None:
        size = get_world_size()
    init = True

    def plant_sunflowers(x):
        move_to(x, 0)
        for i in range(size):
            if init:
                till()
            while get_water() < 0.5:
                use_item(Items.Water)
            plant(Entities.Sunflower)
            if i < size - 1:
                move(North)

    def harvest_sunflowers_of_size(x, n):
        move_to(x, 0)
        for i in range(size):
            if measure_sunflower() == n:
                while not can_harvest():
                    pass
                harvest()
            if i < size - 1:
                move(North)

    while True:
        drones = []
        for i in range(size - 1):
            drones.append(spawn_drone(plant_sunflowers, i + 1))  # type: ignore

        plant_sunflowers(0)
        # The above leaves us one short
        move(North)

        for drone in drones:
            wait_for(drone)

        for n in range(15, 6, -1):
            drones = []
            for i in range(size - 1):
                drones.append(spawn_drone(harvest_sunflowers_of_size, i + 1, n))  # type: ignore

            harvest_sunflowers_of_size(0, n)
            # The above leaves us one short
            move(North)

        init = False


if __name__ == "__main__":
    clear()
    multithreaded_sunflower()
