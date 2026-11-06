from __builtins__ import (
    East,
    Entities,
    Items,
    North,
    South,
    West,
    can_harvest,
    do_a_flip,
    get_entity_type,
    get_pos_x,
    get_pos_y,
    get_water,
    harvest,
    move,
    plant,
    till,
    use_item,
)
from utils import move_to


def pumpkin_thread_action(analyze_mode, redo_spots):
    if analyze_mode:
        while True:
            if can_harvest():
                break
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                redo_spots.append((get_pos_x(), get_pos_y()))
                break
    else:
        if get_entity_type() != Entities.Pumpkin:
            if not plant(Entities.Pumpkin):
                till()
                plant(Entities.Pumpkin)


def pumpkin_thread(start_x, start_y, size):
    if size % 2 != 0:
        print("must be even")
        do_a_flip()
        return
    while True:
        move_to(start_x, start_y)
        harvest()

        analyze_mode = False
        redo_spots = []

        for _ in range(2):
            for i in range(size):
                for _ in range(size - 2):
                    pumpkin_thread_action(analyze_mode, redo_spots)
                    if i % 2 == 0:
                        move(East)
                    else:
                        move(West)
                pumpkin_thread_action(analyze_mode, redo_spots)
                if i == 0:
                    move(East)
                    pumpkin_thread_action(analyze_mode, redo_spots)
                if i < size - 1:
                    move(North)
                else:
                    move(West)
                    while get_pos_y() != start_y:
                        pumpkin_thread_action(analyze_mode, redo_spots)
                        move(South)
            analyze_mode = True

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
