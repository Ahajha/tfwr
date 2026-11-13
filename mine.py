from utils import move_to


def always_dig(x, y):
    move_to(x, y)
    while True:
        dig()


def multimine():
    DIG_SITES = [
        (4, 12),
        (4, 20),
        (4, 28),
        (12, 4),
        (12, 12),
        (12, 20),
        (12, 28),
        (20, 4),
        (20, 12),
        (20, 20),
        (20, 28),
        (28, 4),
        (28, 12),
        (28, 20),
        (28, 28),
    ]
    for x, y in DIG_SITES:
        spawn_drone(always_dig, x, y)
    always_dig(4, 4)


if __name__ == "__main__":
    clear()
    multimine()
