from utils import move_to, opposite


def get_weird_substance(leader=True, x=0):
    move_to(x, 0)
    if leader:
        for i in range(get_world_size() - 1):
            spawn_drone(get_weird_substance, False, i + 1)

    if x % 2 == 1:
        move(North)
    while True:
        if can_harvest():
            harvest()
        plant(Entities.Tree)
        use_item(Items.Fertilizer)
        move(North)
        move(North)


def maze(size=None) -> bool:
    if size == None:
        size = get_world_size()
    plant(Entities.Bush)
    substance = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    return use_item(Items.Weird_Substance, substance)


def solve_maze():
    stack = [[]]

    while get_entity_type() != Entities.Treasure:
        if len(stack[-1]) < 4:
            for dir in [North, South, East, West]:
                if dir in stack[-1]:
                    continue
                stack[-1].append(dir)
                if move(dir):
                    stack.append([opposite(dir)])
                    break
        else:
            move(stack[-1][0])
            stack.pop()

    harvest()


def get_candidates(exclude=None):
    # Randomized so that if a bunch of drones take the same path, they're more likely to split up
    result_candidates = [North, South, East, West]
    result = []
    for _ in range(4):
        index = (random() * len(result_candidates)) // 1
        dir = result_candidates[index]  # type: ignore

        if can_move(dir) and dir != exclude:
            result.append(dir)
        result_candidates.remove(dir)
    return result


# Each item in the outer list is is a cell
# Each item in the inner list is a tuple of (candidates, direction to return or none)
# stack: list[tuple[list[Direction], Optional[Direction]]]
def solve_maze_multithreaded(stack=[]):
    # There is an odd phenomena where drones sometimes cover the same path many times.
    # However, I think this is a consequence of drones not really getting killed
    # when treasure is found.

    if stack == []:
        stack = [(get_candidates(), None)]

    while True:
        while get_entity_type() != Entities.Treasure:
            while len(stack[-1][0]) > 0 and get_entity_type() != Entities.Treasure:
                # Always use the last element so we can just pop and move on
                dir = stack[-1][0][-1]
                # If this is the last element, we always want to do this ourselves
                if len(stack[-1][0]) > 1 and spawn_drone(
                    solve_maze_multithreaded, [([dir], None)]
                ):
                    # Fire and forget
                    stack[-1][0].pop()
                else:
                    # Do it ourselves
                    if not move(dir):
                        # Invalidated, fail-fast
                        return
                    stack[-1][0].pop()
                    opp = opposite(dir)
                    # Add back when the main bug is fixed
                    if len(stack[-1][0]) == 0 and stack[-1][1] == None:
                        # No more things to check here, no need to backtrack
                        stack.pop()
                        stack.append((get_candidates(opp), None))
                    else:
                        stack.append((get_candidates(opp), opp))

            if get_entity_type() == Entities.Treasure:
                break

            if stack[-1][1] == None:
                # Explicit end of the stack
                return
            if not move(stack[-1][1]):
                # Invalidated, fail-fast
                return
            stack.pop()

        harvest()
        maze()
        stack = [(get_candidates(), None)]


DUMB_MAZE_SIZE = 5


def dumb_mazes(init=True, x=0, y=0):
    set_world_size(DUMB_MAZE_SIZE)
    substance_amount = DUMB_MAZE_SIZE * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    if init:
        clear()
        for i in range(DUMB_MAZE_SIZE):
            for j in range(DUMB_MAZE_SIZE):
                if i == 0 and j == 0:
                    # This thread
                    continue
                spawn_drone(dumb_mazes, False, i, j)
        do_a_flip()
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, substance_amount)
    move_to(x, y)

    while True:
        if measure() == (x, y):
            if not use_item(Items.Weird_Substance, substance_amount):
                harvest()
                plant(Entities.Bush)
                use_item(Items.Weird_Substance, substance_amount)


def measure_treasure() -> tuple[int, int]:
    return measure()  # type: ignore


DIRS = [North, East, South, West]


def maze_tree(start_x, start_y, size):
    move_to(start_x, start_y)
    maze(size)

    # Might be weird with odd numbers
    x_offset = start_x - size / 2
    y_offset = start_y - size / 2

    # As we explore the maze, we build a virtual tree of the layout.
    # Note that as we reuse the maze, cycles can form. We will try to handle these.
    # For each cell, we track a tuple (distance, dir), which is the distance from
    # the root, and the direction towards the root (for the root, this is (0/None)).

    layout: list[list[tuple[int, Direction | None]]] = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append((-1, None))
        layout.append(row)

    # We traverse the whole maze, marking what we see. Use the "hug left wall" strategy.
    dir = 0

    n_marked = 0
    current_distance = 0
    while n_marked != size * size:
        pos_x = get_pos_x() - x_offset
        pos_y = get_pos_y() - y_offset

        # If you've discovered something new, you're always going away from the root.
        # This also means that the direction to the root is always the opposite of the
        # direction you came from.
        if layout[pos_x][pos_y][0] == -1:
            current_distance += 1
            n_marked += 1
            layout[pos_x][pos_y] = (current_distance, opposite(DIRS[dir]))
        else:
            current_distance = layout[pos_x][pos_y][0]

        # Note this doesn't work in 1x1 mazes
        # Prioritize Left, Straight, Right. Only go back if you have to.
        for i in [3, 0, 1, 2]:
            if can_move(DIRS[(dir + i) % 4]):
                dir = (dir + i) % 4
                break

        move(DIRS[dir])

    for _ in range(300):
        # Then, for each treasure, we trace two paths:
        # 1. Ourselves towards the root
        # 2. The treasure towards the root
        # Eventually, these paths will meet.
        self_towards_root = [(get_pos_x() - x_offset, get_pos_y() - y_offset)]
        tr_x, tr_y = measure_treasure()
        treasure_towards_root = [(tr_x - x_offset, tr_y - y_offset)]

        while self_towards_root[-1] != treasure_towards_root[-1]:
            self_distance, self_dir = layout[self_towards_root[-1][0]][
                self_towards_root[-1][1]
            ]
            treasure_distance, treasure_dir = layout[treasure_towards_root[-1][0]][
                treasure_towards_root[-1][1]
            ]

            if self_distance >= treasure_distance:
                px, py = self_towards_root[-1]
                if self_dir == North:
                    self_towards_root.append((px, py + 1))
                elif self_dir == East:
                    self_towards_root.append((px + 1, py))
                elif self_dir == South:
                    self_towards_root.append((px, py - 1))
                elif self_dir == West:
                    self_towards_root.append((px - 1, py))
            if treasure_distance >= self_distance:
                px, py = treasure_towards_root[-1]
                if treasure_dir == North:
                    treasure_towards_root.append((px, py + 1))
                elif treasure_dir == East:
                    treasure_towards_root.append((px + 1, py))
                elif treasure_dir == South:
                    treasure_towards_root.append((px, py - 1))
                elif treasure_dir == West:
                    treasure_towards_root.append((px - 1, py))

        # Finally, we take path 1 plus the reverse of path 2.
        # Skip the last element of first and first element of the second.
        for pos_x, pos_y in self_towards_root[:-1]:
            if not move(layout[pos_x][pos_y][1]):
                print("Failed to move")
        for i in range(len(treasure_towards_root) - 2, -1, -1):
            pos_x, pos_y = treasure_towards_root[i]
            if not move(opposite(layout[pos_x][pos_y][1])):
                print("Failed to move")

        substance = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        use_item(Items.Weird_Substance, substance)


def maze_at(x, y, size, stop_condition):
    quick_print("Starting at ", x, y)
    move_to(x, y)
    do_a_flip()
    do_a_flip()
    while not stop_condition():
        maze_tree(x, y, size)
        quick_print("Resetting at ", x, y)
        harvest()
        move_to(x, y)


def never():
    return False


def many_mazes(stop_condition=never):
    # When a drone spawns a maze, it tries to center itself in it.
    # Place the coords so that the mazes align with the grid we're making.
    MAZES = [
        # A 4x4 grid of 6x6s
        (3, 3, 6),
        (9, 3, 6),
        (15, 3, 6),
        (21, 3, 6),
        (3, 9, 6),
        (9, 9, 6),
        (15, 9, 6),
        (21, 9, 6),
        (3, 15, 6),
        (9, 15, 6),
        (15, 15, 6),
        (21, 15, 6),
        (3, 21, 6),
        (9, 21, 6),
        (15, 21, 6),
        (21, 21, 6),
        # Then 4 8x8s along one edge
        (28, 4, 8),
        (28, 12, 8),
        (28, 20, 8),
        (28, 28, 8),
        # And fill the rest with 4x4s (12 total)
        (2, 26, 4),
        (2, 30, 4),
        (6, 26, 4),
        (6, 30, 4),
        (10, 26, 4),
        (10, 30, 4),
        (14, 26, 4),
        (14, 30, 4),
        (18, 26, 4),
        (18, 30, 4),
        (22, 26, 4),
        (22, 30, 4),
    ]

    for x, y, size in MAZES[:-1]:
        spawn_drone(maze_at, x, y, size, stop_condition)
    maze_at(MAZES[-1][0], MAZES[-1][1], MAZES[-1][2], stop_condition)


if __name__ == "__main__":
    clear()
    many_mazes()
