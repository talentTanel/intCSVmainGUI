import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
import db

fileName="C660913142637.csv"
insertionPointXY = []
ann, ip = None, None
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
    insertionPointDef(pl, ts)
    #insertionPointBtn(pl, ts, 2)
    graph.legend()
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    saveGraph(ts, pl, pc, pr)

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
    
# Checks if an insertion point is already available, if there is - displays it
def insertionPointDef(pl, ts):
    insertionPointBtn(pl, ts)
    if insertionPointXY:
        global ann, ip
        ipt = graph.plot(insertionPointXY[0],insertionPointXY[1], "or", label="Insertion Point")
        ip = ipt.pop(0)
        ann =graph.annotate("Insertion Point", xy=(insertionPointXY[0], insertionPointXY[1]), xytext=((ts[0]+insertionPointXY[0])/2.5,insertionPointXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Suggests an insertion point automatically by comparing a pressure to it's following pressure
def getInsertionPointAuto(pl, ts):
    for i in range(len(pl)-1):
        if abs(pl[i] - pl[i+1]) > int(insertSlider.get()):
                global insertionPointXY, ann, ip
                if ann: ann.remove(), ip.remove()
                tsIn = ts[i]
                plIn = pl[i]
                ipt = graph.plot(tsIn,plIn, "or", label="Insertion Point")
                ip = ipt.pop(0)
                ann = graph.annotate("Insertion Point", xy=(tsIn, plIn), xytext=((ts[0]+tsIn)/2.5,plIn-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
                canvas.draw()
                insertionPointXY = [tsIn, plIn]
                break
        
# Suggests an insertion point when a specific button is pressed
def insertionPointBtn(pl, ts):
    insertAutoBtn = tk.Button(
    text="Suggest new insertion point",
    command=lambda: getInsertionPointAuto(pl, ts)
    )
    insertAutoBtn.place(relx=.1,rely=.3)
    insertSlider.place(relx=.1, rely=.35)
    insertSlider.set(2)
    lblInsertText.place(relx=.027,rely=.375)


# Saves graph and points of interest on it to database
def saveGraph(ts, pl, pc, pr):
    saveGraphBtn = tk.Button(
    text="Save Graph",
    command=lambda: db.insertToTable(fileName.rsplit(".",2)[0], ts, pl, pc, pr, insertionPointXY)
    )
    saveGraphBtn.place(relx=.6, rely=0)

# GUI elements and their placement
gui = tk.Tk()
fig, graph = plt.subplots()
canvas = FigureCanvasTkAgg(fig, gui)
canvas.get_tk_widget().place(relx=.5,rely=.05)
toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)

startTime = tk.Entry()
lblStartTime = tk.Label(text="Start time:")
stopTime = tk.Entry()
lblStopTime = tk.Label(text="Stop time:")
insertSlider = tk.Scale(gui, from_=0, to=10, orient="horizontal")
lblInsertText = tk.Label(text="Pressure change:")
graphBtn = tk.Button(
    text="Show Graph", 
    command=lambda: [plt.close(), plot(readCSV(), startTime.get(), stopTime.get())]
    )
graphBtn.place(relx= .1, rely= 0)
startTime.place(relx= .1, rely= .1)
lblStartTime.place(relx= .05, rely= .1)
stopTime.place(relx= .1, rely= .2)
lblStopTime.place(relx= .05, rely= .2)
if __name__ == "__main__":
    GUI()