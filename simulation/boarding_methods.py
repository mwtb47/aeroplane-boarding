from random import shuffle

from simulation.objects import AeroPlane
        
def set_boarding_order(plane: AeroPlane, boarding_method: str, n_groups: int) -> list:
    """Sort the list of passengers according to the specified 
    boarding method. For front and reverse WMA methods the 
    passenger list is created from scratch.
    """
    if boarding_method == 'random':
        shuffle(plane.seats)
    elif boarding_method == 'back-to-front':
        shuffle(plane.seats)
        plane.seats.sort(key=lambda a: a[0], reverse=True)
        plane.seats = group_back_front(plane, n_groups)
    elif boarding_method == 'front-to-back':
        shuffle(plane.seats)
        plane.seats.sort(key=lambda a: a[0], reverse=False)
        plane.seats = group_back_front(plane, n_groups)
    elif boarding_method == 'WMA':
        shuffle(plane.seats)
        plane.seats.sort(key=lambda a: plane.aisle_order.index(a[1]), reverse=False)
    elif boarding_method == 'front-to-back WMA':
        plane.seats = group_WMA(plane, boarding_method, n_groups)
    elif boarding_method == 'back-to-front WMA':
        plane.seats = group_WMA(plane, boarding_method, n_groups)
    elif boarding_method == 'optimal':
        plane.seats.sort(key=lambda a: [plane.aisle_order[::-1].index(a[1]), a[0]], reverse=True)
    return plane


def group_back_front(plane: AeroPlane, n_groups: int) -> list:
    """Group passengers for back-to-front and front-to-back 
    boarding methods.
    """
    group_sizes = [plane.rows // n_groups] * n_groups
    remainder = plane.rows % n_groups
    for i in range(remainder):
        group_sizes[i] = group_sizes[i] + 1

    total = 0
    group_index = [0]
    for i in group_sizes:
        total += i * sum(plane.abreast)
        group_index.append(total)

    groups = []
    for i in range(len(group_index) - 1):
        group = plane.seats[group_index[i]: group_index[i+1]]
        shuffle(group)
        groups.append(group)

    return [passenger for group in groups for passenger in group]


def group_WMA(plane: AeroPlane, boarding_method: str, n_groups: int) -> list:
    """Return passenger list for grouped WMA boarding."""
    group_sizes = [plane.rows // n_groups] * n_groups
    remainder = plane.rows % n_groups
    for i in range(remainder):
        group_sizes[i] = group_sizes[i] + 1

    total = 0
    group_index = [0]
    for i in group_sizes:
        total += i 
        group_index.append(total)

    groups = []
    for k,i in enumerate(group_index[1:]):
        for aisle in plane.aisle_order:
            to_shuffle = []
            for row in range(group_index[k], i):
                if boarding_method == 'back-to-front WMA':
                    to_shuffle.append((plane.rows - row, aisle))
                else:
                    to_shuffle.append((row + 1, aisle))
                shuffle(to_shuffle)
            groups.append(to_shuffle)
    return [passenger for group in groups for passenger in group]