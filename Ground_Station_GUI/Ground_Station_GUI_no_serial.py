import matplotlib.pyplot as plt
import sys, glob, serial, re, utm, math

if __name__ == '__main__':
    # Declare plot variables
    s_x_data, s_y_data, r_x_data, r_y_data = [0], [0], [0], [0]
    s_text, r_text = None, None

    # Create plot
    fig, (s_ax, r_ax) = plt.subplots(1, 2)
    s_line, = s_ax.plot(s_x_data, s_y_data)
    r_line, = r_ax.plot(r_x_data, r_y_data)
    plt.show(block=False)
    fig.canvas.draw()

    # Set to fullscreen, square axes
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.gca().set_aspect('equal', adjustable='box')
    
    # Set labels and create grid
    s_ax.set_title("Launch Vehicle Drift (Summer)")
    s_ax.set_xlabel("East (m)")
    s_ax.set_ylabel("North (m)")
    s_ax.grid(color="k", linestyle="-", linewidth=0.5)

    r_ax.set_title("Launch Vehicle Drift (Rick)")
    r_ax.set_xlabel("East (m)")
    r_ax.set_ylabel("North (m)")
    r_ax.grid(color="k", linestyle="-", linewidth=0.5)

    # Regex for extracting latitude and longitude
    lat_pattern = re.compile(r"([0-9]{2})([0-9]{2}\.[0-9]+),(N|S)")
    lon_pattern = re.compile(r"([0-9]{3})([0-9]{2}\.[0-9]+),(E|W)")

    # Flags for whether or not the origin has been read
    s_read_origin = False
    r_read_origin = False

    # Defines paramaters for distance/angle text box
    props = dict(boxstyle="square", facecolor="aliceblue", alpha=0.5)
    
    # Opens file with example dat
    with open("twoATU_exampleData.txt", "r") as filestream:
        while True:
            # Read characters until we find the "@" delimiter
            c = filestream.read(1)
            while c and c != '@':
                c = filestream.read(1)

            # Break at end of file
            if not c:
                break

            # Read a line of GPS data and discard the next two characters (?,)
            cur_line = filestream.read(50)
            filestream.read(2)

            # Extract the latitude and convert to decimal degree form
            match = re.search(lat_pattern, cur_line)
            if match is not None:
                deg = float(match.group(1))
                min = float(match.group(2))
                lat = deg + (min / 60)
                if str(match.group(3)) == "S":
                    lat = -lat

            # If the data does not match the expected format, skip it
            else:
                continue

            # Extract the longitude and convert to decimal degree form
            match = re.search(lon_pattern, cur_line)
            if match is not None:
                deg = float(match.group(1))
                min = float(match.group(2))
                lon = deg + (min / 60)
                if str(match.group(3)) == "W":
                    lon = -lon

            # If the data does not match the expected format, skip it
            else:
                continue

            # Convert lat/lon into UTM (standardized 2D cartesian projection)
            x, y, _, _ = utm.from_latlon(lat, lon)

            # Get the name of the ATU
            atu_name = filestream.read(4)

            # If the data came from Summer
            if atu_name == "summ":
                filestream.read(2) # discard "er"

                # Set first point as origin (0,0)
                if not s_read_origin:
                    s_x_origin = x
                    s_y_origin = y
                    s_read_origin = True

                # All other points are relative to this origin
                else:
                    x = x - s_x_origin
                    y = y - s_y_origin

                    # Add new data point
                    s_x_data.append(x)
                    s_y_data.append(y)
                    s_line.set_xdata(s_x_data)
                    s_line.set_ydata(s_y_data)

                    # Compute and print absolute distance and angle from origin
                    dist  = math.sqrt(x**2 + y**2)
                    angle = math.degrees(math.atan2(y,x))
                    if s_text is not None:
                        s_text.remove()
                    text = "Distance: {0:.2f} m\nAngle: {1:.2f}$^\circ$".format(dist, angle)
                    s_text = s_ax.text(0.05, 0.05, text, fontsize=12, transform=s_ax.transAxes, bbox=props)

                    # Redraw plot and adjust axes
                    s_ax.draw_artist(s_ax.patch)
                    s_ax.draw_artist(s_line)
                    s_ax.relim()
                    s_ax.autoscale_view()
                    fig.canvas.draw()
                    fig.canvas.flush_events()
            
            # If the data came from Rick
            elif atu_name == "rick":

                # Set first point as origin (0,0)
                if not r_read_origin:
                    r_x_origin = x
                    r_y_origin = y
                    r_read_origin = True

                # All other points are relative to this origin
                else:
                    x = x - r_x_origin
                    y = y - r_y_origin

                    # Add new data point
                    r_x_data.append(x)
                    r_y_data.append(y)
                    r_line.set_xdata(r_x_data)
                    r_line.set_ydata(r_y_data)

                    # Compute and print absolute distance and angle from origin
                    dist  = math.sqrt(x**2 + y**2)
                    angle = math.degrees(math.atan2(y,x))
                    if r_text is not None:
                        r_text.remove()
                    text = "Distance: {0:.2f} m\nAngle: {1:.2f}$^\circ$".format(dist, angle)
                    r_text = r_ax.text(0.05, 0.05, text, fontsize=12, transform=r_ax.transAxes, bbox=props)

                    # Redraw plot and adjust axes
                    r_ax.draw_artist(r_ax.patch)
                    r_ax.draw_artist(r_line)
                    r_ax.relim()
                    r_ax.autoscale_view()
                    fig.canvas.draw()
                    fig.canvas.flush_events()

            # If neither of names are found, skip to next data set
            else:
                continue
        
        # Prompt user to save the figure
        file_name = input("Save figure as: ")
        plt.savefig(file_name)
