import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# create the Tkinter window
root = tk.Tk()

# create a Matplotlib figure and canvas
fig = Figure()
ax = fig.subplots()


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# function to clear the canvas and redraw the graph
def redraw_graph():
    # clear the canvas
    canvas.get_tk_widget().delete("all")
    
    # do graphing here
    # ...
    ax.plot([1,2,3],[4,5,6])
    # redraw the canvas
    canvas.draw()

# create a button to call the redraw_graph function
button = tk.Button(root, text="Redraw Graph", command=redraw_graph)
button.pack()

# start the Tkinter event loop
root.mainloop()
