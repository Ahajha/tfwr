from utils import move_to, visit_square


def plant_rice():
    while get_ground_type() != Grounds.Clay:
        dig()
    plant(Entities.Rice)


def harvest_rice():
    while not can_harvest():
        pass
    harvest()
    dig()


def rice(x, y, size):
    move_to(x, y)
    visit_square(size, plant_rice)
    visit_square(size, harvest_rice)
    visit_square(size, plant_rice)
    visit_square(size, harvest_rice)


def multirice():
    SITES = [
        (0, 8, 8),
        (0, 16, 8),
        (0, 24, 8),
        (8, 0, 8),
        (8, 8, 8),
        (8, 16, 8),
        (8, 24, 8),
        (16, 0, 8),
        (16, 8, 8),
        (16, 16, 8),
        (16, 24, 8),
        (24, 0, 8),
        (24, 8, 8),
        (24, 16, 8),
        (24, 24, 8),
    ]
    while True:
        drones = []
        for x, y, size in SITES:
            drones.append(spawn_drone(rice, x, y, size))  # type: ignore
        rice(0, 0, 8)
        for drone in drones:
            wait_for(drone)
        clear()


if __name__ == "__main__":
    clear()
    multirice()
