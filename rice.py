from utils import move_to


def plant_rice():
	while get_ground_type() != Grounds.Clay:
		dig()
	plant(Entities.Rice)


def harvest_rice():
	while not can_harvest():
		pass
	harvest()


def rice(x, y, size):
	move_to(x, y)
	for _ in range(size):
		plant_rice()
		use_item(Items.Water)
		move(North)
	for _ in range(size):
		harvest_rice()
		move(North)
	for _ in range(size):
		plant_rice()
		move(North)
	for _ in range(size):
		harvest_rice()
		move(North)


def multirice():
	size = get_world_size()
	while True:
		drones = []
		for i in range(size - 1):
			drones.append(spawn_drone(rice, i + 1, 0, size))
		rice(0, 0, size)
		for drone in drones:
			wait_for(drone)
		clear()


if __name__ == "__main__":
	clear()
	multirice()
