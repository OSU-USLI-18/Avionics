import matplotlib.pyplot as plt
import numpy as np
import time

ydata = [0]
xdata = [0]
fig, ax = plt.subplots()
line, = ax.plot(xdata, ydata)
plt.show(block=False)

tstart = time.time()
num_plots = 0
ax.set_title("Launch Vehicle Altitude Over Time")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Altitude (ft.)")
ax.set_xlim([0,60])
ax.set_ylim([0,5300])

with open("data.txt", "r") as filestream:
	for cur_line in filestream:
		data_pair = cur_line.split(",")
		xdata.append(data_pair[0])
		ydata.append(data_pair[1])
		line.set_xdata(xdata)
		line.set_ydata(ydata)
		ax.draw_artist(ax.patch)
		ax.draw_artist(line)
		fig.canvas.draw()
		fig.canvas.flush_events()
		num_plots += 1
