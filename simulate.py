import argparse
from copy import deepcopy

from simulation.boarding_methods import set_boarding_order
from simulation.objects import AeroPlane, Passenger
from simulation.visualisations import  create_GIF, plot_boarding_order


class BoardingSim:
    """Class to simulate the boarding of a plane using different
    boarding methods and produce a GIF to animate the boarding process.
    
    Arguments
        rows - the numbers of rows in the aircraft
        abreast - arrangement of seats in a row as a list, each element 
                  being a cluster of seats not separated by an aisle.
                  e.g. 2 seats, aisle, 2 seats is [2,2], 
                  2 seats, aisle, 3 seats, aisle, 2 seats is [2,3,2]
        boarding_method - the boarding method used
            random - passengers board in a random order
            back-to-front - passengers are sorted by row starting with 
                            the rear, aisle order is random
            front-to-back - passengers are sorted by row starting with 
                            the front, aisle order is random
            WMA - passengers are sorted by aisles, starting with the 
                  window seats and ending with the aisle seats. Within 
                  each aisle the order is random. 
            front-to-back WMA - passengers are sorted by row starting 
                                at the front. Within each row,
                                passengers are sorted so those in window
                                seats enter first and those in aisle 
                                seats last.
            back-to-front WMA - passengers are sorted by row starting at
                                the front. Within each row, passengers 
                                are sorted so those in window seats 
                                enter first and those in aisle seats
                                last.
            optimal - passengers are sorted by aisle, starting by window 
                      seats and ending with aisle seats. Within each 
                      aisle passengers are sorted by rear row to front 
                      row.
        bag_percent - the proportion of passengers with bags
        slow_medium_fast - list of proportion of passengers who are
                           slow, medium and fast at boarding. 
                           e.g. [0.2, 0.4, 0.4]
        n_groups - the number of groups in which passengers board.
    """
    
    def __init__(
            self,
            rows: int,
            abreast: int,
            boarding_method: str,
            bag_percent: float, 
            slow_average_fast: list,
            n_groups: int):
        self.rows = rows
        self.abreast = abreast
        self.boarding_method = boarding_method
        self.bag_percent = bag_percent
        self.slow_percent = slow_average_fast[0]
        self.fast_percent = slow_average_fast[2]
        self.n_groups = n_groups
    
    def create_aeroplane(self) -> AeroPlane:
        """Return an instance of the AeroPlane class.
        """
        plane = AeroPlane(self.abreast, self.rows)
        plane = set_boarding_order(plane, self.boarding_method, self.n_groups)
        plane.passengers = [Passenger(seat) for seat in plane.seats]
        plane.set_boarding_aisles()
        plane.assign_bags(self.bag_percent)
        plane.assign_boarding_speeds(self.slow_percent, self.fast_percent)
        plane.set_passenger_colours()
        return plane

    def board_plane(self):
        """Iterate through each passenger and run the update_passenger 
        method on them until there are no passengers left unseated. At
        the end of each iteration through the list of passengers, append 
        the plane dictionary to a list. These dictionaries in this list 
        represent one frame of the GIF animation. 
        """
        print('Boarding plane...')
        plane = self.create_aeroplane()
        self.frames = []
        while not plane.check_all_seated():
            for passenger in plane.passengers:
                plane = passenger.move(plane)
            self.frames.append(deepcopy(plane))

        self.plane = plane

    def boarding_steps(self):
        """Iterate through each passenger and run the update_passenger 
        method on them until there are no passengers left unseated. At
        the end of each iteration through the list of passengers, append 
        the plane dictionary to a list. These dictionaries in this list 
        represent one frame of the GIF animation. 
        """
        steps = 0
        plane = self.create_aeroplane()
        while not plane.check_all_seated():
            for passenger in plane.passengers:
                plane = passenger.move(plane)
            steps += 1
        return steps


def print_boarding_summary(args: argparse.Namespace, n_frames: int):
    lines = [
        "\nAeroplane boarding simulation",
        "-----------------------------",
        f"Rows             - {args.rows}",
        f"Abreast          - {args.abreast}",
        f"Boarding method  - {args.boarding_method}",
        f"Bag percentage   - {args.bag_percent}%",
        f"Slow medium fast - {', '.join(str(i) + '%' for i in args.slow_medium_fast.split(','))}",
        f"Number of groups - {args.groups}\n",
        "\nResults",
        "-------",
        f"Number of steps  - {n_frames}\n",
    ]
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', required=False, default=15, type=int, help="Number of rows in plane (default: 10)")
    parser.add_argument('--abreast', required=False, default="3,3", type=str, help="Comma separated seat blocks. e.g. '3,3' for 3 seats, aisle, 3 seats (default: '3,3'")
    parser.add_argument('--boarding-method', required=False, default="random", type=str, help="Boarding method (default: random)")
    parser.add_argument('--bag-percent', required=False, default=50, type=int, help="Percentage of passengers with bags (default: 50)")
    parser.add_argument('--slow-medium-fast', required=False, default="30,40,30", type=str, help="Percentage of slow, medium, and fast boarders (default: '30,40,30')")
    parser.add_argument('--groups', required=False, default=1, type=int, help="Number of boarding groups (default: number of rows)")
    parser.add_argument('--plot-boarding-order', required=False, action='store_true', help="Plot boarding order")
    parser.add_argument('--boarding-order-filename', required=False, type=str, help="Filename of boarding order plot")
    parser.add_argument('--boarding-order-dpi', required=False, default=100, type=int, help="dpi of boarding order plot")
    parser.add_argument('--create-GIF', required=False, action='store_true', help="Create GIF animation of boarding")
    parser.add_argument('--GIF-filename', required=False, type=str, help="Filename of GIF")
    parser.add_argument('--GIF-dpi', required=False, default=100, type=int, help="dpi of GIF")
    args = parser.parse_args()

    rows = args.rows
    abreast = [int(i) for i in args.abreast.split(',')]
    boarding_method = args.boarding_method
    bag_percent = args.bag_percent / 100
    slow_medium_fast = [int(i) / 100 for i in args.slow_medium_fast.split(',')]
    n_groups = args.groups

    boarding = BoardingSim(rows, abreast, boarding_method, bag_percent, slow_medium_fast, n_groups)
    boarding.board_plane()
    print_boarding_summary(args, len(boarding.frames))

    if args.plot_boarding_order:
        if args.boarding_order_filename:
            filename = args.boarding_order_filename
        else:
            filename = f"boarding_order_{args.boarding_method}.png"
        plot_boarding_order(boarding.plane, filename, args.boarding_order_dpi)
    if args.create_GIF:
        if args.GIF_filename:
            filename = args.GIF_filename
        else:
            filename = f"{args.boarding_method}.gif"
        create_GIF(boarding.plane, boarding.frames, boarding.boarding_method, filename, args.GIF_dpi)

        
if __name__ == "__main__":
    main()