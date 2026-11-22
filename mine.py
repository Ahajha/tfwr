from dynamite import dynamite

# from mushroom import mushroom
from pyramid import pyramid
from treasure import treasure
from utils import move_to


def mine_for_activities():
	move_to(get_world_size() // 2, get_world_size() // 2)

	while True:
		ground = get_ground_type()
		if ground == Grounds.Basalt:
			treasure()
			move_to(get_world_size() // 2, get_world_size() // 2)
		elif ground == Grounds.Dynamite:
			dynamite()
			move_to(get_world_size() // 2, get_world_size() // 2)
		# elif ground == Grounds.Mushroom:
		# mushroom()
		# move_to(get_world_size() // 2, get_world_size() // 2)
		elif ground in (Grounds.Sand, Grounds.Limestone):
			pyramid()
			move_to(get_world_size() // 2, get_world_size() // 2)
			# Need to make sure we get rid of the limestone
			dig()
		else:
			dig()


if __name__ == "__main__":
	mine_for_activities()
