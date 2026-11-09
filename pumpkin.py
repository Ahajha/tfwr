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
            # When doing a large farm, it may end up that the mega-pumpkin is harvested before
            # this drone realizes it's done. In that case, if we "lose" the pumpkin, then
            # we're actually done and can start again.
            while not can_harvest() and get_entity_type() == Entities.Pumpkin:
                if get_water() < 0.5:
                    use_item(Items.Water)
            if get_entity_type() not in [Entities.Pumpkin, Entities.Dead_Pumpkin]:
                return
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


def _mega_pumpkin_thread(start_x, start_y, size_x, size_y):
    move_to(start_x, start_y)
    init = True
    while True:
        _grow_pumpkin(size_x, size_y, init)

        # Wait for the main drone to harvest
        move_to(start_x, start_y)
        init = False
        while can_harvest():
            pass


def mega_pumpkin():
    # Grow a 32x32 pumpkin
    init = True

    for i in range(4):
        for j in range(8):
            if i == 0 and j == 0:
                continue
            spawn_drone(_mega_pumpkin_thread, i * 8, j * 4, 8, 4)  # type: ignore

    move_to(0, 0)
    while True:
        _grow_pumpkin(8, 4, init)
        move_to(0, 0)

        while True:
            # Wait until the corners are of equal value, then it's ready to harvest
            move(South)
            move(West)
            ne_corner_value = measure()
            move(North)
            move(East)
            sw_corner_value = measure()

            if ne_corner_value == sw_corner_value:
                break
        harvest()
        init = False


if __name__ == "__main__":
    clear()
    mega_pumpkin()
