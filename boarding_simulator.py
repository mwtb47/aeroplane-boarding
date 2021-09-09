from ast import literal_eval
from copy import deepcopy
from itertools import product
from random import choice, shuffle
from math import ceil, floor

from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt
import numpy as np


class Boarding:
    """Class to simulate the boarding of a plane using different
    boarding methods and produce a GIF to animate the boarding process.
    
    Arguments
        rows - the numbers of rows in the aircraft
        abreast - arrangement of seats in a row as a list, each element 
                  being a cluster of seats not separated by an aisle.
                  e.g. 2 seats, aisle, 2 seats is [2,2], 
                  2 seats, aisle, 3 seats, aisle, 2 seats is [2,3,2]
        method - the boarding method used
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
    
    def __init__(self, rows, abreast, method, bag_percent, slow_average_fast, 
                 n_groups):
        self.rows = rows
        self.abreast = abreast
        self.method = method
        self.bag_percent = bag_percent
        self.slow_percent = slow_average_fast[0]
        self.fast_percent = slow_average_fast[2]
        self.n_groups = n_groups
        
    def boarding_method(self, passengers):
        """Sort the list of passengers according to the specified 
        boarding method. For front and reverse WMA methods the 
        passenger list is created from scratch.
        """
        if self.method == 'random':
            shuffle(passengers)
        elif self.method == 'back-to-front':
            shuffle(passengers)
            passengers.sort(key=lambda a: a[0], reverse=True)
            passengers = self.group_back_front(passengers)
        elif self.method == 'front-to-back':
            shuffle(passengers)
            passengers.sort(key=lambda a: a[0], reverse=False)
            passengers = self.group_back_front(passengers)
        elif self.method == 'WMA':
            shuffle(passengers)
            passengers.sort(key=lambda a: self.aisle_order.index(a[1]), 
                            reverse=False)
        elif self.method == 'front-to-back WMA':
            return self.group_WMA()
        elif self.method == 'back-to-front WMA':
            return self.group_WMA()
        elif self.method == 'optimal':
            passengers.sort(
                key=lambda a: [self.aisle_order[::-1].index(a[1]), a[0]], 
                reverse=True)
        return passengers
    
    
    def set_boarding_aisles(self, passengers):
        """Return a list which contains the boarding aisles for each
        passenger. For each passenger, the distance to each aisle is 
        calculated. If the minimum distance occurs once, the closest 
        aisle is assigned as the boarding aisle. If the minimum distance 
        occurs more than once, the boarding aisle is chosen at random 
        from the closest aisles.
        """
        boarding_aisles = []
        for p in passengers:
            distances = [abs(p[1] - aisle) for aisle in self.aisles]
            min_distance = min(distances)
            if distances.count(min_distance) == 1:
                boarding_aisles.append(
                    (0, self.aisles[distances.index(min_distance)])
                )
            else:
                min_aisles = [self.aisles[i] for i in range(len(self.aisles)) 
                              if distances[i] == min_distance]
                boarding_aisles.append((0, choice(min_aisles)))
        return boarding_aisles
    
    def set_characteristics(self, plane):
        """Randomly assign bags to the specified proportion of 
        passengers. Also, randomly assign bag loading speeds to the 
        specified proportions of slow, average and fast passengers.
        """
        n_bags = ceil(len(plane) * self.bag_percent)
        bags = [True] * n_bags + [False] * (len(plane) - n_bags)
        shuffle(bags)
        
        n_slow = ceil(len(plane) * self.slow_percent)
        n_fast = ceil(len(plane) * self.fast_percent)
        n_average = len(plane) - n_slow - n_fast
        speeds = [3] * n_slow + [2] * n_average + [1] * n_fast
        shuffle(speeds)
        
        for passenger, (bag, speed) in enumerate(zip(bags, speeds)):
            plane[passenger]['bag_countdown'] = speed
            if not bag:
                plane[passenger]['bag_countdown'] = 0
                
        return plane
    
    def group_back_front(self, passengers):
        """Group passengers for back-to-front and front-to-back 
        boarding methods.
        """
        group_sizes = [self.rows // self.n_groups] * self.n_groups
        remainder = self.rows % self.n_groups
        for i in range(remainder):
            group_sizes[i] = group_sizes[i] + 1

        total = 0
        group_index = [0]
        for i in group_sizes:
            total += i * sum(self.abreast)
            group_index.append(total)
            
        groups = [passengers[group_index[i]: group_index[i+1]] 
                  for i in range(len(group_index)-1)]
        for group in groups:
            shuffle(group)
        return [passenger for group in groups for passenger in group]
    
    def group_WMA(self):
        """Return passenger list for grouped WMA boarding."""
        group_sizes = [self.rows // self.n_groups] * self.n_groups
        remainder = self.rows % self.n_groups
        for i in range(remainder):
            group_sizes[i] = group_sizes[i] + 1

        total = 0
        group_index = [0]
        for i in group_sizes:
            total += i 
            group_index.append(total)

        groups = []
        for k,i in enumerate(group_index[1:]):
            for aisle in self.aisle_order:
                to_shuffle = []
                for row in range(group_index[k], i):
                    if self.method == 'back-to-front WMA':
                        to_shuffle.append((self.rows - row, aisle))
                    else:
                        to_shuffle.append((row + 1, aisle))
                    shuffle(to_shuffle)
                groups.append(to_shuffle)
        return [passenger for group in groups for passenger in group]
    
    def create_passengers(self):
        """Return a dictionary of passengers with the following 
        structure, ordered according the the boarding method:
        
        Key - passenger number (0 to n-1)
        
        Value - dictionary containing:
            target - the passenger's seat as a tuple (e.g. (1,2))
            row - the row the passenger is currently in (0 if either not
                  yet on the plane or already seated)
            seated - whether the passenger is seated or not yet
            bag_countdown - represents the number of steps to put the 
                            bag away. 0 represents no bag to put away. 
                            1, 2 or 3 are assigned depending on whether 
                            the passenger is slow, average or fast. 
        """
        seats = list(range(1, sum(self.abreast) + len(self.abreast)))
        count = 0
        aisles = []
        for a in self.abreast[:-1]:
            count += a
            aisles.append(seats[count])
            del seats[count]
        self.aisles = aisles
        self.seats = seats
        
        # Order of aisles by proximity to middle aisle
        seat_dict = {}
        for seat in seats:
            distances = []
            for aisle in self.aisles:
                distance = abs(seat - aisle)
                distances.append(distance)
            seat_dict[seat] = min(distances)
        self.aisle_order = seats.copy()
        self.aisle_order.sort(key=lambda x: seat_dict[x], reverse=True)

        # Coordinates of all seats on the plane, sorted by boarding method.
        passengers = list(product(range(1, self.rows + 1), seats))
        passengers = self.boarding_method(passengers)
        boarding_aisles = self.set_boarding_aisles(passengers)

        plane = [{'target': i, 'position': k, 'seated': False, 
                  'bag_countdown': None} 
                 for i,k in zip(passengers, boarding_aisles)]
        plane = {k:v for k,v in zip(range(0, len(plane)), plane)}
        
        plane = self.set_characteristics(plane)
        
        return plane

    def get_occupied(self, plane):
        """Return a list of aisle positions currently occupied."""
        return [plane[passenger]['position'] for passenger in plane]

    def check_all(self, plane):
        """True if all passengers are seated, else False."""
        return all([plane[passenger]['seated'] for passenger in plane])

    def blocked(self, seat, current_position):
        """Return a list of seats in a passenger's row which they must 
        pass to reach their seat from the aisle. (This does not check 
        whether the seats are occupied or not.)
        """
        row = seat[0]
        seat_aisle = seat[1]
        current_aisle = current_position[1]
        if seat_aisle > current_aisle:
            blocked = [(row, a) 
                       for a in range(current_aisle + 1, seat_aisle + 1)]
        else:
            blocked = [(row, a) for a in range(seat_aisle, current_aisle)]
        blocked.remove(seat)
        
        return blocked
    
    def update_passenger(self, plane, passenger):
        """Update the status of a given passenger if the passenger is not
        already seated and has the option to move. Return the updated 
        dictionary of all passengers.
        """
        # Check if the passenger is seated or not.
        if not plane[passenger]['seated']:
            current_position = plane[passenger]['position']
            current_bag = plane[passenger]['bag_countdown']
            seat_row = plane[passenger]['target'][0]
            
            # If the passenger has reached their row and they have a 
            # bag, their bag count is reduced by one. If this makes 
            # their count 0, their bag is now put away, otherwise the 
            # passenger is one step closer to putting the bag away.
            if current_position[0] == seat_row and current_bag >= 1:
                plane[passenger]['bag_countdown'] = current_bag - 1
            
            # If the passenger has reached their row and doesn't have a 
            # bag to put away, any other passengers blocking access to
            # the seat move back out into the aisle and the passenger
            # sits down.
            elif current_position[0] == seat_row and current_bag == 0:
                blocked_seats = self.blocked(plane[passenger]['target'], 
                                             current_position)
                for person in plane:
                    if (plane[person]['target'] in blocked_seats 
                        and plane[person]['seated']
                       ):
                        plane[person]['seated'] = False
                        plane[person]['position'] = current_position
                plane[passenger]['seated'] = True
                plane[passenger]['position'] = (0, current_position[1])
            
            # If the next row of the aisle is free, move the passenger to 
            # that row. 
            elif ((current_position[0] + 1, current_position[1])
                  not in self.get_occupied(plane)):
                plane[passenger]['position'] = (current_position[0] + 1, 
                                                current_position[1])
            
            # There are no possible actions for the passenger to take. 
            else:
                pass
        
        return plane
    
    def board_plane(self):
        """Iterate through each passenger and run the update_passenger 
        method on them until there are no passengers left unseated. At
        the end of each iteration through the list of passengers, append 
        the plane dictionary to a list. These dictionaries in this list 
        represent one frame of the GIF animation. 
        """
        plane = self.create_passengers()
        self.plane = plane
        self.frames = []
        while not self.check_all(plane):
            for passenger in plane.keys():
                plane = self.update_passenger(plane, passenger)
            self.frames.append(deepcopy(plane))
        
    def set_colours(self):
        """Create a list of colours the same length as the number of 
        passengers.
        """
        colours = [
            'teal', 'blue', 'green', 'firebrick', 'orange', 'purple', 'tan',
            'mediumslateblue', 'darkorchid', 'lightblue',  'olive', 'salmon',
            'chocolate', 'steelblue', 'magenta', 'seagreen', 'darkviolet',
            'lightseagreen',
        ]
        colours = ['#003f5c', '#374c80', '#7a5195', '#bc5090', '#ef5675',
                   '#ff764a', '#ffa600']
        colours = colours * (len(self.plane) // len(colours) + 1)
        self.colours = colours[:len(self.plane)]
            
    def create_GIF_lists(self):
        """For each frame, a list of each passenger's current coordinates
        is created. The list of colours is also repeated for each frame 
        of the annimation.
        """
        positions = []
        for plane in self.frames:
            temp = []
            for passenger in plane:
                seat = plane[passenger]['target']
                current_position = plane[passenger]['position']
                
                if plane[passenger]['seated']:
                    plane[passenger]['location'] = seat
                    temp.append([seat[0], seat[1]])
                else:
                    plane[passenger]['location'] = current_position
                    temp.append([current_position[0], current_position[1]])
            positions.append(temp)
        
        self.positions = positions
        self.colour_list = [self.colours for i in range(len(self.positions))]
        
        
    def plot_boarding_order(self, dpi):
        """Save a png file showing the order of boarding for a given 
        boarding method.
        """
        abreast = sum(self.abreast)
        
        plane = self.create_passengers()
        x = [plane[passenger]['target'][0] for passenger in plane]
        y = [plane[passenger]['target'][1] for passenger in plane]
        
        fig = plt.figure(figsize=(12, 12 * (abreast / self.rows)), 
                         dpi=dpi)
        plt.axes(
            xlim=(0.5, self.rows + 0.5), 
            ylim=(0.5, abreast + len(self.aisles) + 0.5)
        )
        plt.xticks([])
        plt.yticks([])
        
        # Add squares to represent the seats and colour by boarding 
        # order.
        marker_area = (864 * abreast / self.rows / (abreast + 4)) ** 2
        plt.scatter(
            x, 
            y, 
            s=marker_area, 
            marker='s', 
            c=list(plane.keys()), 
            cmap='BuGn', 
            linewidths=1, 
            edgecolors='black',
        )
        
        # Add text labels showing the order in which each passenger 
        # boards.
        text_colour = (['black'] * ceil(0.5 * len(plane)) 
                       + ['white'] * floor(0.5 * len(plane)))
        for x_coord, y_coord, text, colour in zip(x, y, plane.keys(), text_colour):
            plt.text(
                x_coord, 
                y_coord, 
                s=text+1, 
                color=colour, 
                size=(864 * abreast / self.rows / (abreast + 4)) / 2,
                horizontalalignment='center', 
                verticalalignment='center',
            )
            
        for a in self.aisles:
            # Add dashed lines to show the centre aisle.
            plt.hlines(
                y=a-0.5, 
                xmin=0.5,
                xmax=self.rows+0.5, 
                linestyle='--',
            )
            plt.hlines(
                y=a+0.5,
                xmin=0.5, 
                xmax=self.rows+0.5, 
                linestyle='--',
            )

            # Add arrow showing the boarding direction
            plt.arrow(
                x=2, 
                y=a, 
                dx=1,
                dy=0, 
                width=0.01, 
                head_width=0.2,
                head_length=0.2, 
                length_includes_head=True,
                overhang=0.5
            )

            # Add text labeling the front and the rear of the plane
            plt.text(
                x=1, 
                y=a, 
                s='Front', 
                size=(864 * abreast / self.rows / (abreast + 4)/3),
                horizontalalignment='center', 
                verticalalignment='center',
            )
            plt.text(
                x=self.rows, 
                y=a, 
                s='Rear', 
                size=(864 * abreast / self.rows / (abreast + 4)/3),
                horizontalalignment='center',
                verticalalignment='center',
            )
        
        fig.tight_layout()
        filename = self.method + '.png'
        filename = filename.replace(' ', '_')
        fig.savefig(filename, dpi=dpi)
        
    def create_GIF(self, dpi):
        """Create a GIF where each frame of the animation represents the 
        position of each passenger after each passenger has had the 
        opportunity to make one step.
        """
        self.board_plane()
        self.set_colours()
        self.create_GIF_lists()
        abreast = sum(self.abreast)
        
        x = [self.plane[passenger]['target'][0] for passenger in self.plane]
        y = [self.plane[passenger]['target'][1] for passenger in self.plane]
        
        # Create a list of seat labels. E.g. 1A, 1B, 1C, etc.
        aisle_labels = 'ABCDEFGHJKLMN'
        seats = [str(row) + str(aisle_labels[self.seats.index(aisle)]) 
                 for row,aisle in zip(x,y)]
    
        fig = plt.figure(
            figsize=(12, 12 * ((abreast + len(self.abreast) - 1 )/ self.rows)),
            dpi=dpi)
        plt.axes(
            xlim=(0.5, self.rows + 0.5), 
            ylim=(0.5, abreast + len(self.abreast) - 0.5)
        )
        
        # Not sure why but without this the title font is heavily 
        # pixelated.
        fig.patch.set_facecolor('white')
        title_str = ('Method: ' + self.method + '  -  Steps: ' 
                     + str(len(self.frames)))
        plt.title(title_str, loc='left')
        
        # Add squares to represent the seats and add text to show their 
        # number.
        marker_area = (864 * abreast / self.rows / (abreast + 4)) ** 2
        plt.scatter(
            x, 
            y, 
            s=marker_area,
            marker='s', 
            color='white', 
            linewidths=1, 
            edgecolors='black',
        )
        for x_coord, y_coord, text in zip(x,y,seats):
            plt.text(
                x_coord, 
                y_coord, 
                s=text, 
                horizontalalignment='center', 
                verticalalignment='center',
            )
        
        # Add dashed lines to show the centre aisles.
        for a in self.aisles:
            plt.hlines(
                y=a-0.5,
                xmin=0.5,
                xmax=self.rows+0.5, 
                linestyle='--',
            )
            plt.hlines(
                y=a+0.5,
                xmin=0.5,
                xmax=self.rows+0.5, 
                linestyle='--',
            )
        
        plt.xticks([])
        plt.yticks([])
        scat = plt.scatter(x, y, s=marker_area)

        def animate(frame, data, points, scat):
            """Set the position and colours of the passengers in a given 
            frame.
            """
            scat.set_offsets(points[frame])
            scat.set_color(data[frame])
            return scat,
        
        fig.tight_layout()

        anim = FuncAnimation(
            fig, 
            animate, 
            frames=len(self.frames), 
            interval=300,
            fargs=(self.colour_list, self.positions, scat)
        )
        anim.save(self.method + '.gif', writer='pillow', dpi=dpi)
        plt.close()
    
    def return_steps(self):
        """Run the boarding simulation and return the number of steps taken
        to board the plane.
        """
        self.board_plane()
        return len(self.frames)


def main(output):
    """Initiate the Boarding class and run methods to either produce a 
    GIF of the boarding process or a png file showing the order in which 
    passengers will board for a given method.
    """
    rows = int(input("Number of rows: "))
    abreast= literal_eval(input("Seats per row: "))
    method = input("Boarding method: ")
    bag_percent = float(input("Proportion of passengers with bags: "))
    slow_average_fast = literal_eval(
        input("Proportions of slow, average, fast passengers: "))
    n_groups = int(input("Number of groups: "))
    dpi = int(input("GIF dpi: "))
    
    aero = Boarding(rows, abreast, method, bag_percent, slow_average_fast, 
                    n_groups)
    
    if output == 'GIF':
        aero.create_GIF(dpi)
    elif output == 'boarding order':
        aero.plot_boarding_order(dpi)
    else:
        print("Choose 'GIF' or 'boarding order'")

        
if __name__ == "__main__":
    output = input("'GIF' or 'boarding order'")
    main(output)