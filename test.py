import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# create the tkinter window and a matplotlib figure
root = tk.Tk()
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

# plot some data on the figure
ax.plot([1, 2, 3], [4, 5, 6])

# create a canvas widget to display the matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# define a function to handle the right-click event
def on_right_click(event):
    # check if the right-click was over the matplotlib graph and the button was right
    if event.inaxes is not None and event.button == 3:
        # create a right-click menu
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Option 1")
        menu.add_command(label="Option 2")
        menu.add_command(label="Option 3")
        # display the menu at the location of the right-click event
        menu.post(event.x_root, event.y_root)

# bind the function to the "button_press_event" event of the canvas
cid = canvas.mpl_connect('button_press_event', on_right_click)

# start the tkinter event loop
tk.mainloop()
