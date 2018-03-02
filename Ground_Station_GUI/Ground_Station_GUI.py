import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
import time
import sys
import glob
import serial
import re
import utm
import math

def serial_port():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result[0]

if __name__ == '__main__':
    ydata = [0]
    xdata = [0]
    x = 0
    y = 0
    num_plots = 0
    text = None

    # Create plot
    fig, ax = plt.subplots()
    line, = ax.plot(xdata, ydata)
    plt.show(block=False)

    # Set to fullscreen
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.gca().set_aspect('equal', adjustable='box')
    
    # Set labels and create grid
    ax.set_title("Launch Vehicle Drift")
    ax.set_xlabel("East (m)")
    ax.set_ylabel("North (m)")
    ax.grid(color="k", linestyle="-", linewidth=0.5)

    # Regex for extracting latitude and longitude
    lat_pattern = re.compile(r"([0-9]{2})([0-9]{2}\.[0-9]+),(N|S)")
    lon_pattern = re.compile(r"([0-9]{3})([0-9]{2}\.[0-9]+),(E|W)")

    props = dict(boxstyle="square", facecolor="aliceblue", alpha=0.5)
    
    with open("example_data.txt", "r") as filestream:
        for i, cur_line in enumerate(filestream):
            # Extract the latitude and convert to decimal degree form
            match = re.search(lat_pattern, cur_line)
            if match is not None:
                deg = float(str(match.group(1)))
                min = float(str(match.group(2)))
                lat = deg + (min / 60)
                if str(match.group(3)) == "S":
                    lat = -lat

            # Extract the longitude and convert to decimal degree form
            match = re.search(lon_pattern, cur_line)
            if match is not None:
                deg = float("{}".format(match.group(1)))
                min = float("{}".format(match.group(2)))
                lon = deg + (min / 60)
                if str(match.group(3)) == "W":
                    lon = -lon

            # Convert lat/lon into UTM (standardized 2D cartesian projection)
            x, y, _, _ = utm.from_latlon(lat, lon)

            # Set first point as origin (0,0)
            if i == 0:
                x_origin = x
                y_origin = y

            # All other points are relative to this origin
            else:
                x = x - x_origin
                y = y - y_origin

                # Add new data point
                xdata.append(x)
                ydata.append(y)
                line.set_xdata(xdata)
                line.set_ydata(ydata)

                # Redraw plot and adjust axes
                ax.draw_artist(ax.patch)
                ax.draw_artist(line)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
                num_plots += 1

                # Compute and print absolute distance and angle from origin
                dist = math.sqrt(x**2 + y**2)
                angle = math.degrees(math.atan2(y,x))
                if text is not None:
                    text.remove()
                text = ax.text(0.05, 0.05, "Distance: {0:.2f} m\nAngle: {1:.2f}$^\circ$".format(dist, angle), fontsize=12, transform=ax.transAxes, bbox=props)
        
        # Prompt user to save the figure
        file_name = input("Save figure as: ")
        plt.savefig(file_name)

