from utils import WORLD_SIZE, move_to, visit_square


def measure_apple() -> tuple[int, int]:
    return measure()  # type: ignore


change_hat(Hats.Cactus_Hat)


def noop():
    pass


move_to(0, 0)

change_hat(Hats.Dinosaur_Hat)

while get_pos_x() == 0 and get_pos_y() == 0:
    visit_square(WORLD_SIZE, noop)


change_hat(Hats.Cactus_Hat)
