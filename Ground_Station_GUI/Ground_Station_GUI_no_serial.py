import matplotlib.pyplot as plt
import sys
import glob
import serial
import re
import utm
import math

if __name__ == "__main__":
    # Declare plot variables.
    ydata = [0]
    xdata = [0]
    text = None

    # Create plot.
    fig, ax = plt.subplots()
    line, = ax.plot(xdata, ydata)
    plt.show(block=False)
    fig.canvas.draw()

    # Set to fullscreen.
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    plt.gca().set_aspect("equal", adjustable="box")
    
    # Set labels and create grid.
    ax.set_title("Launch Vehicle Drift")
    ax.set_xlabel("East (m)")
    ax.set_ylabel("North (m)")
    ax.grid(color="k", linestyle="-", linewidth=0.5)

    # Regex for extracting time, latitude, and longitude.
    time_pattern = re.compile(r"([0-9]{2})([0-9]{2})([0-9]{2}\.[0-9]{3}),A")
    lat_pattern  = re.compile(r"([0-9]{2})([0-9]{2}\.[0-9]+),(N|S)")
    lon_pattern  = re.compile(r"([0-9]{3})([0-9]{2}\.[0-9]+),(E|W)")

    # Defines paramaters for distance/angle text box.
    props = dict(boxstyle="square", facecolor="aliceblue", alpha=0.5)

    # Flag for whether or not the origin has been read.
    read_origin = False

    # Opens a file named output.txt for writing GPS data to.
    output = open("output.txt", "w")

    # Name of file to read data from.
    input_file = "GPRMC_Locked_2Mile_ATU_Tracking_data_noNewline.txt"
    
    with open(input_file, "r") as filestream:
        while True:
             # Read characters until we find the "@" delimiter.
            c = filestream.read(1)
            while c and c != "@":
                c = filestream.read(1)

            # Break at end of file.
            if not c:
                break

            # Read a line of GPS data.
            cur_line = filestream.read(50)

            # Skip data sent while ATU is not locked.
            if cur_line.endswith("0000.0000,N,00000.0000,E,000.0"):
                continue

            # Extract the time and break into hours, minutes, seconds.
            match = re.search(time_pattern, cur_line)
            if match is not None:
                hour   = int(match.group(1))
                minute = int(match.group(2))
                second = float(match.group(3))

            # If the data does not match the expected format, skip it.
            else:
                continue

            # Extract the latitude and convert to decimal degree form.
            match = re.search(lat_pattern, cur_line)
            if match is not None:
                deg = float(match.group(1))
                min = float(match.group(2))
                lat = deg + (min / 60)
                if str(match.group(3)) == "S":
                    lat = -lat

            # If the data does not match the expected format, skip it.
            else:
                continue

            # Extract the longitude and convert to decimal degree form.
            match = re.search(lon_pattern, cur_line)
            if match is not None:
                deg = float(match.group(1))
                min = float(match.group(2))
                lon = deg + (min / 60)
                if str(match.group(3)) == "W":
                    lon = -lon

            # If the data does not match the expected format, skip it.
            else:
                continue

            # Write time, latitude, and longitude to stdout and output file.
            second_str = "{0:.3f}".format(second).zfill(6)
            output_str = "{0:02d}:{1:02d}:{2} -> {3:.4f}, {4:.4f}"
            output.write(output_str.format(hour, minute, second_str, lat, lon) + "\n")
            print(output_str.format(hour, minute, second_str, lat, lon))

            # Convert lat/lon into UTM (standardized 2D cartesian projection).
            x, y, _, _ = utm.from_latlon(lat, lon)

            # Set first point as origin (0,0).
            if not read_origin:
                x_origin = x
                y_origin = y
                read_origin = True

            # All other points are relative to this origin.
            else:
                x = x - x_origin
                y = y - y_origin

                # Add new data point.
                xdata.append(x)
                ydata.append(y)
                line.set_xdata(xdata)
                line.set_ydata(ydata)

                # Redraw plot and adjust axes.
                ax.draw_artist(ax.patch)
                ax.draw_artist(line)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()

                # Compute and print absolute distance and angle from origin.
                dist  = math.sqrt(x**2 + y**2)
                angle = math.degrees(math.atan2(y,x))
                if text is not None:
                    text.remove()
                data_str = "Distance: {0:.2f} m\nAngle: {1:.2f}$^\circ$".format(dist, angle)
                text = ax.text(0.05, 0.05, data_str, fontsize=12, transform=ax.transAxes, bbox=props)
        
    # Close the output file.
    output.close()
        
    # Prompt user to save the figure.
    file_name = input("Save figure as: ")
    plt.savefig(file_name)
