from utils import move_to, visit_square


def pumpkin_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    while True:
        move_to(start_x, start_y)
        harvest()

        def plant_pumpkin():
            if get_entity_type() != Entities.Pumpkin:
                if not plant(Entities.Pumpkin):
                    till()
                    plant(Entities.Pumpkin)

        visit_square(size, plant_pumpkin)

        redo_spots = []

        def analyze():
            while True:
                if can_harvest():
                    break
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    redo_spots.append((get_pos_x(), get_pos_y()))
                    break

        visit_square(size, analyze)

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
