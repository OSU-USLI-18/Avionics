import matplotlib.pyplot as plt
import sys, glob, serial, re, utm, math

# Helper function for discovering serial ports
def find_serial_ports():
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
    return result

if __name__ == '__main__':
    # Detername name of serial port
    ports = find_serial_ports()
    if len(ports) == 0:
        raise Exception("No serial ports found")
    elif len(ports) > 1:
        print("Multiple serial ports found: ", ports)
        port_name = input("Enter the port you would like to use: ")
        while port_name not in ports:
            print("Error: not a port name")
            port_name = input("Enter the port you would like to use: ")
    else:
        port_name = ports[0]

    # Declare plot variables
    ydata, xdata = [0], [0]
    text = None

    # Create plot
    fig, ax = plt.subplots()
    line, = ax.plot(xdata, ydata)
    plt.show(block=False)
    fig.canvas.draw()

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

    # Defines paramaters for distance/angle text box
    props = dict(boxstyle="square", facecolor="aliceblue", alpha=0.5)
    
    # Flag for whether or not the origin has been read
    read_origin = False

    # Opens a file named output.txt for writing the serial data to
    data = open("output.txt", 'wb')

    # Opens serial port at port_name with 9600 baud and 3 second timeout
    ser = serial.Serial(port_name, 9600, timeout=30)

    while True:
        # Read characters until we find the "@" delimiter
        while ser.read() != b'@':
            pass

        # Read a line of GPS data
        ser_line = ser.read(50)

        # If we get empty data (meaning a timeout), exit
        if len(ser_line) == 0:
            break

        # Try to decode the line, report a malformed line and skip it if we can't
        try:
            cur_line = ser_line.decode("utf-8")
            print(cur_line)
        except UnicodeDecodeError:
            print("Malformed line")
            continue
        
        # Write the serial data to our output text file
        data.write(ser_line)

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

        # Set first point as origin (0,0)
        if not read_origin:
            x_origin = x
            y_origin = y
            read_origin = True

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
            dist  = math.sqrt(x**2 + y**2)
            angle = math.degrees(math.atan2(y,x))
            if text is not None:
                text.remove()
            text = ax.text(0.05, 0.05, "Distance: {0:.2f} m\nAngle: {1:.2f}$^\circ$".format(dist, angle), fontsize=12, transform=ax.transAxes, bbox=props)
      
    # Close serial port and file stream
    data.close()
    ser.close()

    # Prompt user to exit
    input("Press enter to exit.")
