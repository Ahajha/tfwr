from maze import maze, solve_maze
from pumpkin import grow_pumpkin
from utils import move_to


# Useful for the early upgrades
def harvest_until(item: Item, n: int, crop: Entity | None = None):
    while num_items(item) < n:
        while not can_harvest():
            pass
        harvest()
        if crop:
            plant(crop)
        move(North)


def harvest_until_unlock(unlock_: Unlock, crop: Entity | None = None):
    while not unlock(unlock_):
        while not can_harvest():
            pass
        harvest()
        if crop:
            plant(crop)
        move(North)


def polyculture_square(size):
    for i in range(size):
        for j in range(size):
            # 1/2 trees, 1/4 carrots, 1/4 hay
            if i % 2 == j % 2:
                # Trees
                if get_entity_type() != Entities.Tree:
                    plant(Entities.Tree)
                else:
                    while not can_harvest():
                        pass
                    harvest()
                    plant(Entities.Tree)
            elif i % 2 == 0:
                # Grass
                while not can_harvest():
                    pass
                harvest()
            else:
                # Carrots
                if get_entity_type() != Entities.Carrot:
                    till()
                    plant(Entities.Carrot)
                else:
                    while not can_harvest():
                        pass
                    harvest()
                    plant(Entities.Carrot)
            move(North)
        move(East)


def run():
    # Basic initial unlocks
    harvest_until_unlock(Unlocks.Speed)
    harvest_until_unlock(Unlocks.Expand)
    harvest_until_unlock(Unlocks.Plant)

    # Stock up for carrots
    harvest_until(Items.Hay, 150)

    for _ in range(3):
        plant(Entities.Bush)
        move(North)

    # Another set
    harvest_until_unlock(Unlocks.Speed, Entities.Bush)
    harvest_until_unlock(Unlocks.Carrots, Entities.Bush)
    harvest_until_unlock(Unlocks.Expand, Entities.Bush)

    # 30 for Expand 3
    # 50 for Trees 1
    # 30 for Expand 2
    # Plus some stock for carrots
    harvest_until(Items.Wood, 150, Entities.Bush)

    # Trees 1
    harvest_until(Items.Wood, 50, Entities.Bush)

    for _ in range(3):
        harvest()
        till()
        plant(Entities.Carrot)
        move(North)

    harvest_until_unlock(Unlocks.Trees, Entities.Carrot)
    harvest_until_unlock(Unlocks.Expand, Entities.Carrot)

    # We can now get a ton of things while just iterating on polyculture
    unlocks = [
        # Speed stuff, order not optimized
        Unlocks.Grass,
        Unlocks.Grass,
        Unlocks.Grass,
        Unlocks.Trees,
        Unlocks.Speed,
        Unlocks.Speed,
        Unlocks.Carrots,
        Unlocks.Expand,
        Unlocks.Grass,
        Unlocks.Trees,
        Unlocks.Fertilizer,  # Let this one build up
        Unlocks.Carrots,
        Unlocks.Speed,
        Unlocks.Grass,
        Unlocks.Trees,
        Unlocks.Carrots,
        Unlocks.Trees,
        # Stuff for after
        Unlocks.Watering,
        Unlocks.Watering,
        Unlocks.Pumpkins,
        Unlocks.Pumpkins,
        Unlocks.Sunflowers,
    ]

    for unlock_ in unlocks:
        while not unlock(unlock_):
            polyculture_square(get_world_size())

    clear()
    init = True
    while not unlock(Unlocks.Expand):
        move_to(0, 0)
        grow_pumpkin(get_world_size(), get_world_size(), init)
        harvest()
        init = False
    init = True
    while not unlock(Unlocks.Cactus):
        move_to(0, 0)
        grow_pumpkin(get_world_size(), get_world_size(), init)
        harvest()
        init = False

    while num_items(Items.Pumpkin) < 20000:
        move_to(0, 0)
        grow_pumpkin(get_world_size(), get_world_size(), init)
        harvest()

    unlock(Unlocks.Expand)

    while num_items(Items.Weird_Substance) < 2000:
        plant(Entities.Tree)
        use_item(Items.Fertilizer)
        while not can_harvest():
            pass
        harvest()
    harvest()
    unlock(Unlocks.Mazes)

    while maze():
        solve_maze()

    unlock(Unlocks.Megafarm)
    unlock(Unlocks.Megafarm)
    unlock(Unlocks.Polyculture)
    unlock(Unlocks.Fertilizer)

    clear()
    unlocks = [
        Unlocks.Grass,
        Unlocks.Trees,
        Unlocks.Carrots,
        Unlocks.Pumpkins,
        Unlocks.Pumpkins,
        Unlocks.Fertilizer,
        Unlocks.Fertilizer,
        Unlocks.Watering,
        Unlocks.Watering,
        Unlocks.Watering,
        Unlocks.Carrots,
    ]
    for unlock_ in unlocks:
        while not unlock(unlock_):
            polyculture_square(get_world_size())

    while num_items(Items.Carrot) < 20000:
        polyculture_square(get_world_size())

    clear()
    while num_items(Items.Weird_Substance) < 120000:
        plant(Entities.Tree)
        use_item(Items.Fertilizer)
        while not can_harvest():
            pass
        harvest()
    harvest()

    while maze():
        solve_maze()
        unlock(Unlocks.Megafarm)

    while True:
        pass


if __name__ == "__main__":
    run()
