def move_to(x, y, current_x=None, current_y=None, size=None):
	# In case we know where we are already, we can save 2 ticks.
	if current_x == None:
		current_x = get_pos_x()
	if current_y == None:
		current_y = get_pos_y()
	if size == None:
		size = get_world_size()
	# The world is a torus, so normalize negatives to a positive number of moves
	west_len = (current_x - x) % size
	if west_len < size / 2:
		ew_dir = West
		ew_distance = west_len
	else:
		ew_dir = East
		ew_distance = size - west_len
	for _ in range(ew_distance):
		move(ew_dir)

	north_len = (current_y - y) % size
	if north_len < size / 2:
		ns_dir = South
		ns_distance = north_len
	else:
		ns_dir = North
		ns_distance = size - north_len
	for _ in range(ns_distance):
		move(ns_dir)


def opposite(dir):
	if dir == North:
		return South
	if dir == South:
		return North
	if dir == East:
		return West
	return East


def visit_rectangle(size_x, size_y, action):
	# Visits every spot in a rectangle and applies an action.
	# Goes in this order (6x6 for example):
	#
	# v<<<<<
	# v>>>>^
	# v^<<<<
	# v>>>>^
	# v^<<<<
	# >>>>>^
	#
	# Assumes starting in the lower-left corner, and returns there.
	action()
	move(East)
	size_y_1 = size_y - 1
	size_x_2 = size_x - 2
	is_east = True
	for i in range(size_y):
		if is_east:
			dir = East
		else:
			dir = West

		for _ in range(size_x_2):
			action()
			move(dir)
		action()
		if i < size_y_1:
			move(North)
		is_east = not is_east
	move(West)
	for _ in range(size_y_1):
		action()
		move(South)


def visit_square(size, action):
	visit_rectangle(size, size, action)


def visit_spiral(x_size, y_size, x_dir, y_dir, action):
	# First is special
	for _ in range(x_size - 1):
		action()
		move(x_dir)
	x_dir_opp = opposite(x_dir)
	y_dir_opp = opposite(y_dir)
	is_x_opposite = True
	for i in range(1, min(x_size, y_size) + 2):
		if is_x_opposite:
			xd = x_dir_opp
			yd = y_dir
		else:
			xd = x_dir
			yd = y_dir_opp
		if y_size == i:
			break
		for _ in range(y_size - i):
			action()
			move(yd)
		if x_size == i:
			break
		for _ in range(x_size - i):
			action()
			move(xd)
		is_x_opposite = not is_x_opposite

	action()
