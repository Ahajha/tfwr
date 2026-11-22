from utils import move_to


def treasure():
	while get_ground_type() != Grounds.Basalt:
		dig()

	result: tuple[int, int] = measure()  # type: ignore

	quick_print(result)

	move_to(result[0], result[1])

	while get_ground_type() != Grounds.Basalt:
		dig()
	dig()

	result: str = measure()  # type: ignore
	quick_print(result)

	for d in result:  # type: ignore
		if d == "D":
			dig()
		elif d == "N":
			move(North)
		elif d == "S":
			move(South)
		elif d == "E":
			move(East)
		elif d == "W":
			move(West)

	harvest()


if __name__ == "__main__":
	jump(Unlocks.Treasure_Map)
	treasure()
