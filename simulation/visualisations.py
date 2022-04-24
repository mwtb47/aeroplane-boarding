from math import ceil, floor
import os
import sys

from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt

from simulation.objects import AeroPlane


def progress_bar(current: int, total: int, frame_combination: str, job: str = None):
    if frame_combination == 'frame':
        finish_message = "\nRendering GIF from frames..."
    else:
        finish_message = f"\nCompleted iterations of steps by {job}"

    progress = int(80 * (current + 1) / total)
    remaining = 80 - progress
    sys.stdout.write(f"\r|{'█'* progress}{' ' * remaining}|   {frame_combination.capitalize()} {current + 1} of {total}")
    sys.stdout.flush()
    if current + 1 == total:
        print(finish_message)


def set_passenger_colours(plane: AeroPlane) -> AeroPlane:
    """Create a list of colours the same length as the number of 
    passengers.
    """
    colours = ['#003f5c', '#374c80', '#7a5195', '#bc5090', '#ef5675', '#ff764a', '#ffa600']
    colours_list = colours * (plane.n_passengers // len(colours)) + colours[:plane.n_passengers % len(colours)]
    for colour, passenger in zip(colours_list, plane.passengers):
        passenger.colour = colour
    return plane

    
def create_GIF_lists(frames: list) -> list:
    """For each frame, a list of each passenger's current coordinates
    is created. The list of colours is also repeated for each frame 
    of the annimation.
    """
    positions = []
    for plane_frame in frames:
        temp = []
        for passenger in plane_frame.passengers:
            seat = passenger.seat
            current_position = passenger.position
            if passenger.seated:
                passenger.current_location = seat
                temp.append([current_position[0], current_position[1]])
            else:
                passenger.current_location = current_position
                temp.append([current_position[0], current_position[1]])
        positions.append(temp)
    return positions
    
    
def plot_boarding_order(plane: AeroPlane, filename: str, dpi: int):
    """Save a png file showing the order of boarding for a given 
    boarding method.
    """
    print("Plotting boarding order...")
    abreast = sum(plane.abreast)
    x = [passenger.seat[0] for passenger in plane.passengers]
    y = [passenger.seat[1] for passenger in plane.passengers]
    
    fig = plt.figure(figsize=(12, 12 * (abreast / plane.rows)), dpi=dpi)
    plt.axes(
        xlim=(0.5, plane.rows + 0.5), 
        ylim=(0.5, abreast + len(plane.walkway_aisles) + 0.5)
    )
    plt.xticks([])
    plt.yticks([])
    
    # Add squares to represent the seats and colour by boarding 
    # order.
    marker_area = (864 * abreast / plane.rows / (abreast + 4)) ** 2
    plt.scatter(
        x, 
        y, 
        s=marker_area, 
        marker='s', 
        c=list(range(plane.n_passengers)), 
        cmap='BuGn', 
        linewidths=1, 
        edgecolors='black',
    )
    
    # Add text labels showing the order in which each passenger 
    # boards.
    text_colour = (['black'] * ceil(0.5 * plane.n_passengers) 
                    + ['white'] * floor(0.5 * plane.n_passengers))
    for x_coord, y_coord, text, colour in zip(x, y, list(range(plane.n_passengers)), text_colour):
        plt.text(
            x_coord, 
            y_coord, 
            s=text+1, 
            color=colour, 
            size=(864 * abreast / plane.rows / (abreast + 4)) / 2,
            horizontalalignment='center', 
            verticalalignment='center',
        )
        
    for a in plane.walkway_aisles:
        # Add dashed lines to show the centre aisle.
        plt.hlines(
            y=a-0.5, 
            xmin=0.5,
            xmax=plane.rows+0.5, 
            linestyle='--',
        )
        plt.hlines(
            y=a+0.5,
            xmin=0.5, 
            xmax=plane.rows+0.5, 
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
            size=(864 * abreast / plane.rows / (abreast + 4)/3),
            horizontalalignment='center', 
            verticalalignment='center',
        )
        plt.text(
            x=plane.rows, 
            y=a, 
            s='Rear', 
            size=(864 * abreast / plane.rows / (abreast + 4)/3),
            horizontalalignment='center',
            verticalalignment='center',
        )
    
    fig.tight_layout()

    filename = filename if filename.endswith('.png') else filename.split('.')[0] + '.png'
    fig.savefig(filename, dpi=dpi)
    print("Boarding order plotted\n")
    

def create_GIF(plane: AeroPlane, frames: list, boarding_method: str, filename: str, dpi: int):
    """Create a GIF where each frame of the animation represents the 
    position of each passenger after each passenger has had the 
    opportunity to make one step.
    """
    positions = create_GIF_lists(frames)
    colour_lists = [[passenger.colour for passenger in frame.passengers] for frame in frames]
    abreast = sum(plane.abreast)
    
    x = [passenger.seat[0] for passenger in plane.passengers]
    y = [passenger.seat[1] for passenger in plane.passengers]
    
    # Create a list of seat labels. E.g. 1A, 1B, 1C, etc.
    aisle_labels = 'ABCDEFGHJKLMN'
    seats = [str(row) + str(aisle_labels[plane.seat_aisles.index(aisle)]) for row, aisle in zip(x, y)]

    fig = plt.figure(
        figsize=(12, 12 * ((abreast + len(plane.abreast) - 1 ) / plane.rows)),
        dpi=dpi)
    plt.axes(
        xlim=(0.5, plane.rows + 0.5), 
        ylim=(0.5, abreast + len(plane.abreast) - 0.5)
    )
    
    # Not sure why but without this the title font is heavily 
    # pixelated.
    fig.patch.set_facecolor('white')
    title_str = ('Method: ' + boarding_method + '  -  Steps: ' + str(len(frames)))
    plt.title(title_str, loc='left')
    
    # Add squares to represent the seats and add text to show their 
    # number.
    marker_area = (864 * abreast / plane.rows / (abreast + 4)) ** 2
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
    for a in plane.walkway_aisles:
        plt.hlines(
            y=a-0.5,
            xmin=0.5,
            xmax=plane.rows+0.5, 
            linestyle='--',
        )
        plt.hlines(
            y=a+0.5,
            xmin=0.5,
            xmax=plane.rows+0.5, 
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
        frames=len(frames), 
        interval=300,
        fargs=(colour_lists, positions, scat)
    )

    filename = filename if filename.endswith('.gif') else filename.split('.')[0] + '.gif'
    print("Creating GIF...")
    anim.save(
        filename,
        writer='pillow', 
        dpi=dpi, 
        progress_callback=lambda current_frame, total_frames: progress_bar(current_frame, total_frames, 'frame'))
    plt.close()
    print(f"GIF saved as {filename} ({os.path.getsize(filename) / 1000000:.2f}Mb)\n")