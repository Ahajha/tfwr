from utils import move_to, visit_rectangle


def _grow_pumpkin(size_x, size_y, init):
    # Grows a size * size pumpkin at the current location
    def plant_pumpkin():
        if init:
            till()
        plant(Entities.Pumpkin)

    visit_rectangle(size_x, size_y, plant_pumpkin)

    redo_spots = []

    def analyze():
        while True:
            if can_harvest():
                break
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                redo_spots.append((get_pos_x(), get_pos_y()))
                break

    visit_rectangle(size_x, size_y, analyze)

    while len(redo_spots) > 0:
        # Weird concurrent modification stuff, just reconstruct the list each time
        new_redo_spots = []
        for spot in redo_spots:
            move_to(spot[0], spot[1])
            # Since we look at things in the same order each time, it doesn't really make sense
            # to skip over something that isn't ready.
            while not can_harvest() and get_entity_type() != Entities.Dead_Pumpkin:
                if get_water() < 0.5:
                    use_item(Items.Water)
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                new_redo_spots.append(spot)
        redo_spots = new_redo_spots


def pumpkin_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    init = True
    while True:
        move_to(start_x, start_y)
        _grow_pumpkin(size, size, init)
        harvest()
        init = False


def _move_and_grow(x, y, size_x, size_y, init):
    move_to(x, y)
    _grow_pumpkin(size_x, size_y, init)


def mega_pumpkin():
    # Grow a 32x32 pumpkin
    init = True

    while True:
        drones = []
        for i in range(8):
            for j in range(4):
                if i == 0 and j == 0:
                    continue
                drones.append(spawn_drone(_move_and_grow, i * 4, j * 8, 4, 8, init))  # type: ignore

        move_to(0, 0)
        _grow_pumpkin(4, 8, init)
        for drone in drones:
            wait_for(drone)

        harvest()
        init = False


if __name__ == "__main__":
    clear()
    mega_pumpkin()
