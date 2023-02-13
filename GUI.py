import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import csv
import tkinter as tk

gui = tk.Tk()

# User Interface
def GUI():
    gui.geometry("1280x720")
    gui.mainloop()

# Graphs a .CSV file
def plot(data, startTime, stopTime):
    fig, graph = plt.subplots()
    ts = []
    pl = []
    pc = []
    pr = []
    dataLength = len(data)
    for i in range(dataLength):
        ts.append(float(data[i][0]))
        pl.append(float(data[i][1]))
        pc.append(float(data[i][3]))
        pr.append(float(data[i][5]))
    if(startTime.isnumeric()): 
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl = sameLength(ts,pl,"0") # Removing all values from pressure before startTime
        pc = sameLength(ts,pc,"0")
        pr = sameLength(ts,pr,"0")
    if(stopTime.isnumeric()): 
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl = sameLength(ts,pl,"end") # Removing all values from pressure after stopTime
        pc = sameLength(ts,pc,"end")
        pr = sameLength(ts,pr,"end")
    graph.plot(ts, pl, "-r", label="Left") 
    graph.plot(ts, pc, "-b", label="Center")
    graph.plot(ts, pr, "-k", label="Right")
    getInsertionPointAuto(pl, ts, 2)
    graph.legend()
    canvas = FigureCanvasTkAgg(fig, gui)
    canvas.draw()
    #canvas.get_tk_widget().place(relx=.5,rely=.1)
    canvas.get_tk_widget().pack(side=tk.RIGHT)
    toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)
    toolbar.update()
    toolbar.pack(side=tk.RIGHT, fill=tk.X)
    #plt.show()
        
# Opens a .CSV file for further processing
def readCSV():
    file = open("C660913142637.csv","r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    data.pop(0) # data[0] is .CSV headers
    return data

# Makes two lists the same length for graphing
def sameLength(X, Y, type):
    while len(X) != len(Y):
        if(type == "end"):
            Y.pop()
        else:
            Y.pop(0)
    return Y
    
# Suggests an insertion point by the user's given pressure
def getInsertionPoint(pl, ts):
    if insertPoint.get().isnumeric():
        nr = round(float(insertPoint.get()),2)
        for i in range(len(pl)):
            if abs(nr - round(pl[i],2)) < 1:
                tsIn = ts[i]
                plIn = pl[i]
                plt.plot(tsIn,plIn, "or", label="Insertion Point")
                return tsIn, plIn

# Suggests an insertion point automatically by comparing a pressure to it's following pressure
def getInsertionPointAuto(pl, ts, accuracy):
    for i in range(len(pl)-1):
        if abs(pl[i] - pl[i+1]) > accuracy:
                print(pl[i], pl[i+1])
                tsIn = ts[i]
                plIn = pl[i]
                plt.plot(tsIn,plIn, "or", label="Insertion Point")
                break

# GUI elements and their placement
startTime = tk.Entry()
stopTime = tk.Entry()
insertPoint = tk.Entry()
graphBtn = tk.Button(
    text="Show Graph", 
    command=lambda: [plt.close(), plot(readCSV(), startTime.get(), stopTime.get())]
    )
insertBtn = tk.Button(
    text="Suggest"
    )
insertText = tk.Label(
    gui, 
    text="Insertion Point [mbar]: "
    )
insertPoint.insert(0, 1002)

insertPoint.place(relx=.1, rely= .3)
insertBtn.place(relx=.3, rely= .3)
insertText.place(relx= 0, rely= .3)
graphBtn.place(relx= .1, rely= 0)
startTime.place(relx= .1, rely= .1)
stopTime.place(relx= .1, rely= .2)

if __name__ == "__main__":
    GUI()