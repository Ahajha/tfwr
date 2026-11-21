from utils import move_to, visit_rectangle


def dig_to_dynamite_action():
    while get_ground_type() != Grounds.Dynamite:
        dig()


def dig_to_dynamite(x, y, size_x, size_y):
    move_to(x, y)
    visit_rectangle(size_x, size_y, dig_to_dynamite_action)


def dynamite():
    size = get_world_size()
    drones = []
    for x in range(0, get_world_size(), 4):
        for y in range(0, get_world_size(), 8):
            if x == 0 and y == 0:
                continue
            drones.append(spawn_drone(dig_to_dynamite, x, y, 4, 8))
    dig_to_dynamite(0, 0, 4, 8)
    for drone in drones:
        wait_for(drone)

    move_to(size / 2, size / 2)

    dig()


if __name__ == "__main__":
    jump(Unlocks.Dynamite)
    dynamite()
