import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
import db

fileName="C660913142637.csv"

# User Interface
def GUI():
    gui.geometry("1280x720")
    gui.mainloop()

# Graphs a .CSV file
def plot(data, startTime, stopTime):
    graph.clear()
    plt.close("all")
    ts, pl, pc, pr = [], [], [], []
    for i in range(len(data)):
        ts.append(float(data[i][0]))
        pl.append(float(data[i][1]))
        pc.append(float(data[i][3]))
        pr.append(float(data[i][5]))
    if(startTime.isnumeric()): 
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"0") # Removing all values from pressure before startTime
    if(stopTime.isnumeric()): 
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"end") # Removing all values from pressure after stopTime
    graph.plot(ts, pl, "-r", label="Left") 
    graph.plot(ts, pc, "-b", label="Center")
    graph.plot(ts, pr, "-k", label="Right")
    getInsertionPointAuto(pl, ts, 2)
    #insertionPointBtn(pl, ts, 2)
    graph.legend()
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    saveGraphBtn.place(relx=.6, rely=0)

# Opens a .CSV file for further processing
def readCSV():
    file = open(fileName,"r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    data.pop(0) # data[0] is .CSV headers
    return data

# Makes two lists the same length for graphing
def sameLength(X, pl, pc, pr, type):
    while len(X) != len(pl):
        if(type == "end"):
            pl.pop()
            pc.pop()
            pr.pop()
        else:
            pl.pop(0)
            pc.pop(0)
            pr.pop(0)
    return pl, pc, pr
    
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
                tsIn = ts[i]
                plIn = pl[i]
                graph.plot(tsIn,plIn, "or", label="Insertion Point")
                break
        
# Suggests an insertion point when a button is pressed
def insertionPointBtn(pl, ts, accuracy):
    insertAutoBtn = tk.Button(
    text="Suggest insertion point",
    command=lambda: getInsertionPointAuto(pl, ts, accuracy)
    )
    insertAutoBtn.place(relx=.1,rely=.4)

# GUI elements and their placement
gui = tk.Tk()
fig, graph = plt.subplots()
canvas = FigureCanvasTkAgg(fig, gui)
canvas.get_tk_widget().place(relx=.5,rely=.05)
toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)

startTime = tk.Entry()
stopTime = tk.Entry()
insertPoint = tk.Entry()
graphBtn = tk.Button(
    text="Show Graph", 
    command=lambda: [plt.close(), plot(readCSV(), startTime.get(), stopTime.get())]
    )
saveGraphBtn = tk.Button(
    text="Save Graph",
    command=lambda: db.createTable(fileName.rsplit(".",2)[0])
)
insertText = tk.Label(
    gui, 
    text="Insertion Point [mbar]: "
    )
insertPoint.insert(0, 1002)

insertPoint.place(relx=.1, rely= .3)
insertText.place(relx= 0, rely= .3)
graphBtn.place(relx= .1, rely= 0)
startTime.place(relx= .1, rely= .1)
stopTime.place(relx= .1, rely= .2)

if __name__ == "__main__":
    GUI()