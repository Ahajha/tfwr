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


def maze():
    plant(Entities.Bush)
    substance = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)


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


DUMB_MAZE_SIZE = 4


def dumb_mazes(init=True, x=0, y=0):
    if init:
        clear()
        for i in range(DUMB_MAZE_SIZE):
            for j in range(DUMB_MAZE_SIZE):
                if i == 0 and j == 0:
                    # This thread
                    continue
                spawn_drone(dumb_mazes, False, i, j)

    move_to(x, y)

    while True:
        if init:
            plant(Entities.Bush)
            substance = DUMB_MAZE_SIZE * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
            use_item(Items.Weird_Substance, substance)
        if get_entity_type() == Entities.Treasure:
            harvest()
