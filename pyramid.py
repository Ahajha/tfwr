from utils import move_to, opposite, visit_rectangle


def determine_bound(dir, limestone_layer) -> tuple[int, int]:
    while True:
        if get_pos_z() <= limestone_layer:
            if get_ground_type() != Grounds.Limestone:
                # The logic gets really confusing if we wrap around the world
                move(opposite(dir))
                return (get_pos_x(), get_pos_y())
            else:
                move(dir)
        else:
            dig()


def remove_one_layer(start_x, start_y, x, y) -> tuple[int, int] | None:
    result = []

    def action():
        if get_ground_type() != Grounds.Sand:
            dig()
        if get_ground_type() in (Grounds.Sand, Grounds.Limestone):
            result.append((get_pos_x(), get_pos_y()))

    move_to(start_x, start_y)
    visit_rectangle(x, y, action)
    if len(result) > 0:
        return result[0]
    else:
        return None


def fill_sand(height: int):
    for _ in range(height - get_pos_z()):
        place(Grounds.Sand)


def height_at(
    center: tuple[int, int],
    limestone_layer: int,
    corner_length: int,
) -> int:
    x = get_pos_x()
    y = get_pos_y()
    x_distance = center[0] - x
    if x_distance < 0:
        x_distance = -x_distance
    y_distance = center[1] - y
    if y_distance < 0:
        y_distance = -y_distance
    distance_from_center: int = max(x_distance, y_distance)  # type: ignore

    # Distance at the center == limestone_layer + corner_length + 1
    return limestone_layer + corner_length + 1 - distance_from_center


def restore_line(
    start_x, start_y, dir, layer, length, center, limestone_layer, corner_length
):
    move_to(start_x, start_y)
    for _ in range(length):
        while get_ground_type() not in (Grounds.Sand, Grounds.Limestone):
            if get_pos_z() < limestone_layer:
                [][0]
            dig()
        height: int = min(  # type: ignore
            limestone_layer + layer,
            height_at(center, limestone_layer, corner_length),
        )
        fill_sand(height)
        move(dir)


def restore_corner_layer(
    center: tuple[int, int],
    x_dir: int,  # 1 or -1
    y_dir: int,  # 1 or -1
    layer: int,  # Offset from the limestone layer
    limestone_layer: int,
    corner_length: int,  # 6 for a 13x13, for example
):
    # Assumption: The outer edge is always restored, so we can safely include or exclude it at will

    diag_distance = corner_length + 1 - layer

    corners = (
        (center[0] + x_dir, center[1] + y_dir),
        (center[0] + x_dir * diag_distance, center[1] + y_dir * diag_distance),
    )

    # visit_rectangle expects to start in the lower-left corner
    start_x = min(corners[0][0], corners[1][0])
    start_y = min(corners[0][1], corners[1][1])

    x_distance = diag_distance
    y_distance = diag_distance
    if y_distance % 2 == 1:
        if y_dir > 0:
            start_y -= 1
        y_distance += 1

    def restore_action():
        while get_ground_type() not in (Grounds.Sand, Grounds.Limestone):
            dig()
        height: int = min(  # type: ignore
            limestone_layer + layer,
            height_at(center, limestone_layer, corner_length),
        )
        fill_sand(height)

    move_to(start_x, start_y)

    visit_rectangle(x_distance, y_distance, restore_action)


def pyramid():
    sand_spot: tuple[int, int] | None = None
    while sand_spot == None:
        drones = []
        for x in range(0, get_world_size(), 4):
            for y in range(0, get_world_size(), 8):
                if x == 0 and y == 0:
                    continue
                drones.append(spawn_drone(remove_one_layer, x, y, 4, 8))
        results = [remove_one_layer(0, 0, 4, 8)]
        for drone in drones:
            results.append(wait_for(drone))

        for result in results:
            if result != None:
                sand_spot = result

    move_to(sand_spot[0], sand_spot[1])

    while get_ground_type() != Grounds.Limestone:
        dig()

    limestone_layer = get_pos_z()

    drones = [
        spawn_drone(determine_bound, North, limestone_layer),
        spawn_drone(determine_bound, South, limestone_layer),
        spawn_drone(determine_bound, East, limestone_layer),
        spawn_drone(determine_bound, West, limestone_layer),
    ]

    # Offset slightly since it goes past the edge
    n_bound = wait_for(drones[0])[1]
    s_bound = wait_for(drones[1])[1]
    e_bound = wait_for(drones[2])[0]
    w_bound = wait_for(drones[3])[0]

    center = ((e_bound + w_bound) // 2, (n_bound + s_bound) // 2)

    quick_print(center)

    # Pyramid is (edge_length + 1) square and (edge_length // 2 + 1) tall
    edge_length = e_bound - w_bound

    corner_length = edge_length // 2
    for drone in [
        spawn_drone(
            restore_line,
            e_bound,
            n_bound,
            South,
            1,
            edge_length,
            center,
            limestone_layer,
            corner_length,
        ),
        spawn_drone(
            restore_line,
            e_bound,
            s_bound,
            West,
            1,
            edge_length,
            center,
            limestone_layer,
            corner_length,
        ),
        spawn_drone(
            restore_line,
            w_bound,
            s_bound,
            North,
            1,
            edge_length,
            center,
            limestone_layer,
            corner_length,
        ),
        spawn_drone(
            restore_line,
            w_bound,
            n_bound,
            East,
            1,
            edge_length,
            center,
            limestone_layer,
            corner_length,
        ),
    ]:
        wait_for(drone)

    for layer in range(1, edge_length // 2 + 1):
        fill_sand(limestone_layer + layer)
        for drone in [
            spawn_drone(
                restore_corner_layer,
                center,
                1,
                1,
                layer,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_corner_layer,
                center,
                1,
                -1,
                layer,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_corner_layer,
                center,
                -1,
                1,
                layer,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_corner_layer,
                center,
                -1,
                -1,
                layer,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_line,
                center[0] + 1,
                center[1],
                East,
                layer,
                corner_length - 1,
                center,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_line,
                center[0] - 1,
                center[1],
                West,
                layer,
                corner_length - 1,
                center,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_line,
                center[0],
                center[1] + 1,
                North,
                layer,
                corner_length - 1,
                center,
                limestone_layer,
                corner_length,
            ),
            spawn_drone(
                restore_line,
                center[0],
                center[1] - 1,
                South,
                layer,
                corner_length - 1,
                center,
                limestone_layer,
                corner_length,
            ),
        ]:
            wait_for(drone)
    fill_sand(limestone_layer + edge_length // 2 + 1)
    do_a_flip()
    do_a_flip()
    harvest()


if __name__ == "__main__":
    clear()

    move_to(16, 16)
    jump(Unlocks.Pyramid)
    pyramid()
