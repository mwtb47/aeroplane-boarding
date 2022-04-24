from itertools import product
from random import choice, shuffle
from math import ceil


class AeroPlane:
    def __init__(self, abreast: list, rows: int):
        self.abreast = abreast
        self.rows = rows
        self._assign_seat_aisles()
        self._assign_walkway_aisles()
        self._distance_to_walkway()
        self._set_seats()
        self._set_number_of_passengers()

    def _assign_seat_aisles(self):
        self.seat_aisles = []
        count = 1
        for seat_block in self.abreast:
            for aisle in range(count, count + seat_block):
                self.seat_aisles.append(aisle)
            count += seat_block + 1
        
    def _assign_walkway_aisles(self):
        self.walkway_aisles = [i for i in range(1, max(self.seat_aisles)) if i not in self.seat_aisles]

    def _distance_to_walkway(self):
        self.distance_to_walkway = {
            k: [abs(aisle - k) for aisle in self.walkway_aisles] for k in self.seat_aisles
        }
        self.aisle_order = sorted(
            self.seat_aisles,
            key=lambda x: self.distance_to_walkway[x],
            reverse=True,
        )

    def _set_seats(self):
        self.seats = list(product(range(1, self.rows + 1), self.seat_aisles))

    def _set_number_of_passengers(self):
        self.n_passengers = len(self.seats)

    def set_boarding_aisles(self):
        """Return a list which contains the boarding aisles for each
        passenger. For each passenger, the distance to each aisle is 
        calculated. If the minimum distance occurs once, the closest 
        aisle is assigned as the boarding aisle. If the minimum distance 
        occurs more than once, the boarding aisle is chosen at random 
        from the closest aisles.
        """
        for passenger in self.passengers:
            distances = [abs(aisle - passenger.seat[1]) for aisle in self.walkway_aisles]
            min_distance = min(distances)
            if distances.count(min_distance) == 1:
                passenger.position = (0, self.walkway_aisles[distances.index(min_distance)])
            else:
                min_aisles = [self.walkway_aisles[i] for i in range(len(self.walkway_aisles)) 
                              if distances[i] == min_distance]
                passenger.position = (0, choice(min_aisles))

    def assign_bags(self, bag_percent: float):
        n_bags = ceil(self.n_passengers * bag_percent)
        bags = [True] * n_bags + [False] * (self.n_passengers - n_bags)
        shuffle(bags)
        for passenger, has_bag in zip(self.passengers, bags):
            passenger.bag = 1 if has_bag else 0

    def assign_boarding_speeds(self, slow_percent: float, fast_percent: float):
        n_slow = ceil(self.n_passengers * slow_percent)
        n_fast = ceil(self.n_passengers * fast_percent)
        n_average = self.n_passengers - n_slow - n_fast
        speeds = [3] * n_slow + [2] * n_average + [1] * n_fast
        shuffle(speeds)
        for passenger, speed in zip(self.passengers, speeds):
            passenger.boarding_speed = speed if passenger.bag == 1 else 0

    def get_occupied(self) -> set:
        """Return a list of walking aisle positions currently occupied."""
        walkway_positions = [(row, aisle) for row, aisle in product(range(1, self.rows + 1), self.walkway_aisles)]
        return set(passenger.position for passenger in self.passengers if passenger.position in walkway_positions)

    def check_all_seated(self) -> bool:
        """Return true if all passengers are seated, else false."""
        return all(passenger.seated for passenger in self.passengers)

    def set_passenger_colours(self):
        """Assign each passenger a colour to be used in GIFs."""
        colours = ['#003f5c', '#374c80', '#7a5195', '#bc5090', '#ef5675', '#ff764a', '#ffa600']
        colours_list = colours * (self.n_passengers // len(colours)) + colours[:self.n_passengers % len(colours)]
        for colour, passenger in zip(colours_list, self.passengers):
            passenger.colour = colour


class Passenger:
    def __init__(self, seat: tuple, position: tuple = None, seated: bool = None, bag: int = None, boarding_speed: int = None):
        self.seat = seat
        self.position = position
        self.seated = seated
        self.bag = bag
        self.boarding_speed = boarding_speed

    def blocked(self) -> list:
        """Return a list of seats in a passenger's row which they must 
        pass to reach their seat from the aisle. This does not check 
        whether the seats are occupied or not.
        """
        row = self.seat[0]
        seat_aisle = self.seat[1]
        current_aisle = self.position[1]
        if seat_aisle > current_aisle:
            blocked = [(row, aisle) for aisle in range(current_aisle + 1, seat_aisle + 1)]
        else:
            blocked = [(row, aisle) for aisle in range(seat_aisle, current_aisle)]
        blocked.remove(self.seat)
        return blocked
    
    def move(self, plane: AeroPlane) -> AeroPlane:
        """Update the status of a given passenger if the passenger is not
        already seated and has the option to move. Return the updated 
        dictionary of all passengers.
        """
        # Check if the passenger is seated or not.
        if not self.seated:
            # If the passenger has reached their row and they have a 
            # bag, their bag count is reduced by one. If this makes 
            # their count 0, their bag is now put away, otherwise the 
            # passenger is one step closer to putting the bag away.
            if self.position[0] == self.seat[0] and self.boarding_speed >= 1:
                self.boarding_speed -= 1
            
            # If the passenger has reached their row and doesn't have a 
            # bag to put away, any other passengers blocking access to
            # the seat move back out into the aisle and the passenger
            # sits down.
            elif self.position[0] == self.seat[0] and self.boarding_speed == 0:
                blocked_seats = self.blocked()
                for passenger in plane.passengers:
                    if passenger.position in blocked_seats and passenger.seated:
                        passenger.seated = False
                        passenger.position = self.position
                self.seated = True
                self.position = self.seat
            
            # If the next row of the aisle is free, move the passenger to 
            # that row. 
            elif (self.position[0] + 1, self.position[1]) not in plane.get_occupied():
                self.position = (self.position[0] + 1, self.position[1])
            
            # There are no possible actions for the passenger to take. 
            else:
                pass
        
        return plane