from cactus import mega_cactus
from dinosoar import dinosoar
from maze import many_mazes, maze, maze_tree, solve_maze
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


def maze_tree_wrap(x, y, size):
    do_a_flip()
    # This does all of the drone unlocking at once
    while num_unlocked(Unlocks.Megafarm) < 5:
        maze_tree(x, y, size)
        harvest()
        unlock(Unlocks.Megafarm)


def polyculture_multidrone(x, y, stop_condition):
    move_to(x, y)
    crops = [Entities.Bush, Entities.Tree, Entities.Carrot, None]

    bootstrap = True

    offset = x % 4
    size = get_world_size()
    while not stop_condition():
        for i in range(size):
            if can_harvest():
                harvest()
            elif get_water() < 0.5:
                use_item(Items.Water)
            crop = crops[(i + offset) % 4]
            if crop:
                if crop == Entities.Carrot and bootstrap:
                    till()
                plant(crop)
            move(North)
        bootstrap = False


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

    # Get all the drones
    drones = []
    # Currently a 12x12
    MAZES = [
        (3, 9, 6),
        (9, 3, 6),
        (9, 9, 6),
    ]
    for x, y, size in MAZES:
        drones.append(spawn_drone(maze_tree_wrap, x, y, size))
    maze_tree_wrap(3, 3, 6)
    for drone in drones:
        wait_for(drone)

    # Do some crazy polyculture
    def polyculture_cond():
        # Probably overkill for this run
        unlock(Unlocks.Grass)
        unlock(Unlocks.Trees)
        unlock(Unlocks.Carrots)
        unlock(Unlocks.Pumpkins)
        return (
            num_unlocked(Unlocks.Grass) >= 10
            and num_unlocked(Unlocks.Trees) >= 10
            and num_unlocked(Unlocks.Carrots) >= 10
            and num_items(Items.Carrot) >= 100000000
        )

    drones = []
    for i in range(get_world_size() - 1):
        drones.append(spawn_drone(polyculture_multidrone, i + 1, 0, polyculture_cond))
    polyculture_multidrone(0, 0, polyculture_cond)

    clear()
    for _ in range(3):
        init = True
        while not unlock(Unlocks.Expand):
            move_to(0, 0)
            grow_pumpkin(get_world_size(), get_world_size(), init)
            harvest()
            init = False

    init = True
    while num_items(Items.Pumpkin) < 20000000:
        move_to(0, 0)
        grow_pumpkin(get_world_size(), get_world_size(), init)
        harvest()
        init = False

    while unlock(Unlocks.Cactus):
        pass

    def cactus_condition():
        return num_items(Items.Cactus) >= 5000000

    clear()
    mega_cactus(cactus_condition)

    while unlock(Unlocks.Dinosaurs):
        pass
    while unlock(Unlocks.Mazes):
        pass

    unlock(Unlocks.Hats)
    set_world_size(20)
    dinosoar()
    set_world_size(32)

    def maze_stop_condition():
        unlock(Unlocks.Leaderboard)
        return num_unlocked(Unlocks.Leaderboard) > 0

    clear()
    while num_items(Items.Weird_Substance) < 200000:
        plant(Entities.Tree)
        use_item(Items.Fertilizer)
        while not can_harvest():
            pass
        harvest()
    harvest()

    many_mazes(maze_stop_condition)


if __name__ == "__main__":
    run()
