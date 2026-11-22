from utils import move_to


def create_info(size) -> list[list[Direction | None]]:
	info = []
	for _ in range(size):
		row = []
		for _ in range(size):
			row.append(None)
		info.append(row)
	return info


def treasure():
	size = get_world_size()
	while get_ground_type() != Grounds.Basalt:
		dig()

	result: tuple[int, int] = measure()  # type: ignore

	quick_print(result)

	move_to(result[0], result[1])

	while get_ground_type() != Grounds.Basalt:
		dig()
	dig()

	result_str = measure()
	quick_print(result)

	info = create_info(size)

	x = get_pos_x()
	y = get_pos_y()
	for d in result_str:  # type: ignore
		if d == "N":
			info[x][y] = North
			y += 1
		elif d == "S":
			info[x][y] = South
			y -= 1
		elif d == "E":
			info[x][y] = East
			x += 1
		elif d == "W":
			info[x][y] = West
			x -= 1
		elif d == "D":
			info[x][y] = None
			x = get_pos_x()
			y = get_pos_y()
			while info[x][y] != None:
				move(info[x][y])  # type: ignore
				x = get_pos_x()
				y = get_pos_y()
			dig()
	harvest()


if __name__ == "__main__":
	jump(Unlocks.Treasure_Map)
	treasure()
