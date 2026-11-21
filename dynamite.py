from utils import move_to, visit_rectangle


def dig_to_dynamite_action():
    while get_ground_type() != Grounds.Dynamite:
        dig()


def dig_to_dynamite(x, y, size_x, size_y):
    move_to(x, y)
    visit_rectangle(size_x, size_y, dig_to_dynamite_action)


def measure_soot() -> int | None:
    return measure()  # type: ignore


DYNAMITE = 9


def get_neighbors(
    x: int,
    y: int,
    size: int,
) -> set[tuple[int, int]]:
    neighbors = set()
    can_go_east = x + 1 < size
    can_go_north = y + 1 < size
    can_go_west = x > 0
    can_go_south = y > 0
    if can_go_east:
        if can_go_north:
            neighbors.add((x + 1, y + 1))
        neighbors.add((x + 1, y))
        if can_go_south:
            neighbors.add((x + 1, y - 1))
    if can_go_north:
        neighbors.add((x, y + 1))
    if can_go_south:
        neighbors.add((x, y - 1))
    if can_go_west:
        if can_go_north:
            neighbors.add((x - 1, y + 1))
        neighbors.add((x - 1, y))
        if can_go_south:
            neighbors.add((x - 1, y - 1))
    return neighbors


def analyze_cell(
    x: int,
    y: int,
    size: int,
    info: list[list[int | None]],
    to_resolve: list[tuple[int, int]],
    defer: list[tuple[int, int]],
    xor_groups: dict[tuple[int, int], set[tuple[int, int]]],
) -> int:
    # Analyzes and potentially makes progress on a cell.
    # Returns true if progress was made.

    # For each disjoint XOR pair surrounding a cell,
    # we ignore the pair and remove one from the hint.
    neighbors = get_neighbors(x, y, size)
    made_progress = False

    excluded = set()
    for neighbor in neighbors:
        if neighbor in xor_groups and neighbor not in excluded:
            # Get just the first item from the set. Single iteration loop
            # If the set is empty it's a noop anyways.
            # Maybe TODO: If there are multiple pairs, we can interpret different ways.
            for xor in xor_groups[neighbor]:
                # We only care about the xors that are neighbors and that we haven't already excluded
                if xor in excluded:
                    continue
                if xor not in neighbors:
                    continue
                # made_progress = True # ???
                excluded.add(xor)
                excluded.add(neighbor)
                break

    if len(excluded) % 2 != 0:
        [][0]

    if info[x][y] == DYNAMITE:
        return True

    remaining_dynamite: int = info[x][y] - len(excluded) // 2  # type: ignore
    for exclude in excluded:
        if exclude in neighbors:
            neighbors.remove(exclude)

    adj_unknowns = []
    for i, j in neighbors:
        if info[i][j] == None:
            adj_unknowns.append((i, j))
        elif info[i][j] == DYNAMITE:
            remaining_dynamite -= 1

    # If the # of unknowns == remaining_dynamite, mark all unknowns as dynamite
    if len(adj_unknowns) == remaining_dynamite:
        for i, j in adj_unknowns:
            info[i][j] = DYNAMITE

            neighbor = (i, j)
            to_resolve.append(neighbor)

            # Remove any xor groups this was in.
            # They'll get auto-resolved in the next pass
            if neighbor in xor_groups:
                for item in xor_groups.pop(neighbor):
                    xor_groups[item].remove(neighbor)

        if excluded:
            defer.append((x, y))

        return True

    # If remaining_dynamite == 0, dig the rest
    elif remaining_dynamite == 0:
        made_progress = True
        for i, j in adj_unknowns:
            move_to(i, j)

            dig()
            measure_result = measure_soot()
            if measure_result == None:
                return True
            info[i][j] = measure_result

            neighbor = (i, j)
            to_resolve.append((i, j))

            # Remove any xor groups this was in.
            # They'll get auto-resolved in the next pass
            if neighbor in xor_groups:
                for item in xor_groups.pop(neighbor):
                    xor_groups[item].remove(neighbor)

        if excluded:
            defer.append((x, y))

        return True

    # If we're short one, add an XOR group
    elif len(adj_unknowns) == 2:
        if remaining_dynamite != 1:
            # I think this is a precondition
            [][0]
        defer.append((x, y))

        n1 = adj_unknowns[0]
        n2 = adj_unknowns[1]
        if n1 in xor_groups:
            if n2 not in xor_groups[n1]:
                made_progress = True
                xor_groups[n1].add(n2)
        else:
            made_progress = True
            xor_groups[n1] = set([n2])

        if n2 in xor_groups:
            if n1 not in xor_groups[n2]:
                made_progress = True
                xor_groups[n2].add(n1)
        else:
            made_progress = True
            xor_groups[n2] = set([n1])

    # Otherwise, not enough information, defer
    else:
        defer.append((x, y))

    return made_progress


def find_any_unknown(info, size) -> tuple[int, int]:
    for x in range(size):
        for y in range(size):
            if info[x][y] == None:
                return (x, y)

    # This should never happen
    return (-1, -1)


def dynamite():
    size = get_world_size()
    if get_ground_type() != Grounds.Dynamite:
        drones = []
        for x in range(0, get_world_size(), 4):
            for y in range(0, get_world_size(), 8):
                if x == 0 and y == 0:
                    continue
                drones.append(spawn_drone(dig_to_dynamite, x, y, 4, 8))
        dig_to_dynamite(0, 0, 4, 8)
        move_to(size / 2, size / 2)
        for drone in drones:
            wait_for(drone)
    else:
        move_to(size / 2, size / 2)

    dig()

    # Each item is 0-9, or None. 0-8 is empty with a hint, 9 is a marked bomb. None is unknown.
    info: list[list[int | None]] = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        info.append(row)

    # Map from any cell to any cells that are dynamite XOR the other isn't
    xor_groups: dict[tuple[int, int], set[tuple[int, int]]] = {}

    info[get_pos_x()][get_pos_y()] = measure()  # type: ignore

    to_resolve = [(get_pos_x(), get_pos_y())]

    while to_resolve:
        made_progress = False
        # Concurrent modification nonsense
        defer = []
        while to_resolve:
            x, y = to_resolve.pop()
            if analyze_cell(x, y, size, info, to_resolve, defer, xor_groups):
                made_progress = True
                if measure_soot() == None:
                    return

        to_resolve = defer

        if not made_progress or (not to_resolve and measure_soot() != None):
            # If we've gotten here, we haven't finished. Just go to an
            # unmarked spot and dig it :shrug:

            # Or, if we're about to stop but the puzzle is not solved, there must be tucked away elements still
            x, y = find_any_unknown(info, size)
            quick_print("guessing", x, y)
            move_to(x, y)
            dig()
            if get_ground_type() != Grounds.Soot:
                # Oh no! Anyways...
                return
            else:
                measure_result: int | None = measure()  # type: ignore
                if measure_result == None:
                    return
                info[x][y] = measure_result
                to_resolve.append((x, y))


if __name__ == "__main__":
    jump(Unlocks.Dynamite)
    dynamite()
