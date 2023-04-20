import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

# create a sample plot
fig, ax = plt.subplots()
line1, = ax.plot([1, 2, 3], [4, 5, 6], label='Line 1')
line2, = ax.plot([1, 2, 3], [6, 5, 4], label='Line 2')

# set the picker property for the Line2D objects
line1.set_picker(True)
line2.set_picker(True)

# create a legend
legend = ax.legend()

# create a tkinter window and embed the plot in it
root = tk.Tk()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# define a function to toggle plot visibility on legend click
def on_legend_click(event):
    artist = event.artist
    if isinstance(artist, plt.Line2D):
        visibility = not artist.get_visible()
        artist.set_visible(visibility)
        event.canvas.draw()

# bind the legend click event to the function
fig.canvas.mpl_connect('pick_event', on_legend_click)

# start the tkinter event loop
root.mainloop()
