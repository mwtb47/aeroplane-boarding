# Boarding Methods

The following provide a description of the different boarding methods and illustrate the order in which passengers board in each method. All passengers board from the front, with passenger 1 boarding first and, in these set ups, either passenger 90 or 105 boarding last.

Animations of boardings using each method can be found in the boarding_animations folder.

## Standard Setup

In the standard setup, there is one boarding aisle and the passengers are not grouped.

#### Back-to-front
Passengers enter the plane in order of their row, starting with the last row. Within each row, the order of the passengers is random.
![alt text for screen readers](Standard/back-to-front.png "Back-to-front boarding method")

#### Front-to-back
Passengers enter the plane in order of their row, starting with the first row. Within each row, the order of the passengers is random.
![alt text for screen readers](Standard/front-to-back.png "Front-to-back boarding method")

#### Window-middle-aisle
Passengers enter the plane starting by window seats and moving towards ailse seats. Within each aisle, passengers enter in a random order.
![alt text for screen readers](Standard/WMA.png "Window-middle-aisle boarding method")

#### Back-to-front window-middle-aisle
Passengers enter the plane in order of their row, starting with the last row. Within each row, passengers are sorted from window seats to aisle seats.
![alt text for screen readers](Standard/back-to-front_WMA.png "Back-to-front window-middle-aisle boarding method")

#### Front-to-back window-middle-aisle
Passengers enter the plane in order of their row, starting with the first row. Within each row, passengers are sorted from window seats to aisle seats.
![alt text for screen readers](Standard/front-to-back_WMA.png "Front-to-back window-middle-aisle boarding method")

#### Random
Passengers enter the plane in a random order.
![alt text for screen readers](Standard/random.png "Random boarding order")

#### Optimal
Passengers enter the plane sorted by aisle and row. Passengers from one window aisle enter, starting with the rear row. The other window aisle follows. Then the next aisle in etc.
![alt text for screen readers](Standard/optimal.png "Optimal boarding method")

## 2 Aisles Setup

In this setup, there are two boarding aisles. Passengers will board via the aisle closest to their seat. When the two aisles are equidistant, as they are for the middle seats in the following examples, the boarding aisle for each passenger is assigned at random. 

#### Back-to-front
Passengers enter the plane in order of their row, starting with the last row. Within each row, the order of the passengers is random.
![alt text for screen readers](2_Aisles/back-to-front_double.png "Back-to-front boarding method double aisle")

#### Front-to-back
Passengers enter the plane in order of their row, starting with the first row. Within each row, the order of the passengers is random.
![alt text for screen readers](2_Aisles/front-to-back_double.png "Front-to-back boarding method double aisle")

#### Window-middle-aisle
Passengers enter the plane starting by window seats and moving towards ailse seats. Within each aisle, passengers enter in a random order.
![alt text for screen readers](2_Aisles/WMA_double.png "Window-middle-aisle boarding method double aisle")

#### Back-to-front window-middle-aisle
Passengers enter the plane in order of their row, starting with the last row. Within each row, passengers are sorted from window seats to aisle seats.
![alt text for screen readers](2_Aisles/back-to-front_WMA_double.png "Back-to-front window-middle-aisle boarding method double aisle")

#### Front-to-back window-middle-aisle
Passengers enter the plane in order of their row, starting with the first row. Within each row, passengers are sorted from window seats to aisle seats.
![alt text for screen readers](2_Aisles/front-to-back_WMA_double.png "Front-to-back window-middle-aisle boarding method double aisle")

#### Random
Passengers enter the plane in a random order.
![alt text for screen readers](2_Aisles/random_double.png "Random boarding order double aisle")

#### Optimal
Passengers enter the plane sorted by aisle and row. Passengers from one window aisle enter, starting with the rear row. The other window aisle follows. Then the next aisle in etc.
![alt text for screen readers](2_Aisles/optimal_double.png "Optimal boarding method double aisle")


## Grouped Setup

Boarding is often done in groups, as opposed to strictly by one row/aisle at a time. Therefore, four of the boarding methods are adapted so that the boarding order is random within the boarding group.

#### Back-to-front
Passengers are grouped by their row and enter starting with the rear group. Within each group, the order of the passengers is random. The below example shows passengers split into 3 groups.
![alt text for screen readers](Grouped/back-to-front_grouped.png "Back-to-front grouped boarding method")

#### Front-to-back
Passengers are grouped by their row and enter starting with the front group. Within each group, the order of the passengers is random. The below example shows passengers split into 3 groups.
![alt text for screen readers](Grouped/front-to-back_grouped.png "Front-to-back grouped boarding method")

#### Back-to-front window-middle-aisle
Passengers are grouped by their row and enter starting with the rear group. Within each group, the window passengers enter first, followed by the middle passengers and lastly the aisle passengers. The row order is random within each group. The below example shows passengers split into 3 groups.

![alt text for screen readers](Grouped/back-to-front_WMA_grouped.png "Back-to-front window-middle-aisle boarding method")

#### Front-to-back window-middle-aisle
Passengers are grouped by their row and enter starting with the front group. Within each group, the window passengers enter first, followed by the middle passengers and lastly the aisle passengers. The row order is random within each group. The below example shows passengers split into 3 groups.
![alt text for screen readers](Grouped/front-to-back_WMA_grouped.png "Front-to-back window-middle-aisle boarding method")