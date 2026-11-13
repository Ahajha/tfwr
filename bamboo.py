from utils import visit_square


def plant_bamboo():
    dig()
    plant(Entities.Bamboo)


def noop():
    pass


def bamboo():
    clear()

    visit_square(16, plant_bamboo)

    height = 2
    while True:
        hover(height)
        height += 1
        visit_square(16, noop)


if __name__ == "__main__":
    bamboo()
