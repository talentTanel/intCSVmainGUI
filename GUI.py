import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
from tkinter import filedialog
import os
import db, savedGraphs

fileName=""
insertionPointXY, maxPointXY, minPointXY = [], [], []
annIp, ip, annMax, maximum, annMin, minimum = None, None, None, None, None, None
# User Interface
def GUI():
    gui.geometry("1280x720")
    gui.mainloop()

# Graphs a .CSV file
def plot(graphData, startTime, stopTime):
    graph.clear()
    #plt.close("all")
    ts, pl, pc, pr = [], [], [], []
    ts, pl, pc, pr = appendElements(ts, pl, pc, pr, graphData)
    ts, pl, pc, pr = startStopTimes(ts, pl, pc, pr, startTime, stopTime)
    graph.plot(ts, pl, "-r", label="Left") 
    graph.plot(ts, pc, "-b", label="Center")
    graph.plot(ts, pr, "-k", label="Right")
    insertionPointDef(pl, ts)
    maximumPoint(pl, ts)
    minimumPoint(pl, ts)
    graph.legend()
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    saveGraph(ts, pl, pc, pr)
    graphOptions()

# If a start or stop time has been set, then this function removes everything not in those ranges
def startStopTimes(ts, pl, pc, pr, startTime, stopTime):
    if(isFloat(startTime) == True):
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"0") # Removing all values from pressure before startTime
    if(isFloat(stopTime) == True):
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"end") # Removing all values from pressure after stopTime
    return ts, pl, pc, pr

# Checks if a number is a float or not. Used for startTime & stopTime
def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

# Reads the data from .CSV or database and inserts into each corresponding variable
def appendElements(ts, pl, pc, pr, graphData):
    if len(graphData) != 4: # When gotten from db the size is 4
        for i in range(len(graphData)):
            ts.append(float(graphData[i][0]))
            pl.append(float(graphData[i][1]))
            pc.append(float(graphData[i][3]))
            pr.append(float(graphData[i][5]))
    else:
        ts = graphData[0]
        pl = graphData[1]
        pc = graphData[2]
        pr = graphData[3]
    return ts, pl, pc, pr

# Places multiple GUI elements when a graph is plotted for the first time
def graphOptions():
    startTime.place(relx= .1, rely= .1)
    lblStartTime.place(relx= .05, rely= .1)
    stopTime.place(relx= .1, rely= .2)
    lblStopTime.place(relx= .05, rely= .2)
    updateGraphBtn.place(relx=.21,rely=.09)

# Gets graph from database data
def plotFromDB(table):
    graph.clear()
    data, ipX, ipY = db.getTable(table.rsplit(".",2)[0])
    plot(data, data[0][0], data[0][len(data[0])-1])
    #insertionPointFromDB(data[0], ipX, ipY)
    
# Opens a .CSV file for further processing
def readCSV(e):
    if e == 1:
        global fileName
        fileName = os.path.basename(filedialog.askopenfilename())
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
    
# Checks if an maximum point is already available, if there is - displays it
def maximumPoint(pl, ts):
    maximumPointBtn = tk.Button(
        gui, 
        text="Suggest maximum point",
        command=lambda: getMaximumPoint(pl, ts)
        )
    maximumPointBtn.place(relx=.1, rely=.42)
    if maxPointXY:
        global annMax, maximum
        maximumt = graph.plot(maxPointXY[0], maxPointXY[1], "or", label="Maximum point")
        maximum = maximumt.pop(0)
        tsPlace = ts[len(ts)-1] / 8
        annMax = graph.annotate("Maximum Point", xy=(maxPointXY[0], maxPointXY[1]), xytext=(maxPointXY[0]-tsPlace, maxPointXY[1]+200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Finds the highest pressure in variable and that is the maximum point. Displays it on the graph
def getMaximumPoint(pl, ts):
    maxPl = max(pl)
    maxTs = ts[pl.index(maxPl)]
    
    global annMax, maximum, maxPointXY
    maximumt = graph.plot(maxTs, maxPl, "or", label="Maximum point")
    maximum = maximumt.pop(0)
    tsPlace = ts[len(ts)-1] / 8
    annMax = graph.annotate("Maximum Point", xy=(maxTs, maxPl), xytext=(maxTs-tsPlace, maxPl+200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    maxPointXY = [maxTs, maxPl]

# Checks if an minimum point is already available, if there is - displays it
def minimumPoint(pl, ts):
    minimumPointBtn = tk.Button(
        gui, 
        text="Suggest Minimum point",
        command=lambda: getMinimumPoint(pl, ts)
        )
    minimumPointBtn.place(relx=.1, rely=.52)
    if minPointXY:
        global annmin, minimum
        minimumt = graph.plot(minPointXY[0], minPointXY[1], "or", label="Minimum point")
        minimum = minimumt.pop(0)
        tsPlace = ts[len(ts)-1] / 8
        annmin = graph.annotate("Minimum Point", xy=(minPointXY[0], minPointXY[1]), xytext=(minPointXY[0]-tsPlace, minPointXY[1]-200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Finds the lowest pressure in variable and that is the minimum point. Displays it on the graph
def getMinimumPoint(pl, ts):
    minPl = min(pl)
    minTs = ts[pl.index(minPl)]
    
    global annmin, minimum, minPointXY
    minimumt = graph.plot(minTs, minPl, "or", label="minimum point")
    minimum = minimumt.pop(0)
    tsPlace = ts[len(ts)-1] / 8
    annmin = graph.annotate("Minimum Point", xy=(minTs, minPl), xytext=(minTs-tsPlace, minPl-200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    minPointXY = [minTs, minPl]

# Checks if an insertion point is already available, if there is - displays it
def insertionPointDef(pl, ts):
    insertionPointBtn(pl, ts)
    if insertionPointXY:
        global annIp, ip
        ipt = graph.plot(insertionPointXY[0],insertionPointXY[1], "or", label="Insertion Point")
        ip = ipt.pop(0)
        annIp = graph.annotate("Insertion Point", xy=(insertionPointXY[0], insertionPointXY[1]), xytext=((ts[0]+insertionPointXY[0])/2.5,insertionPointXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Gets insertion point from database if it exists
def insertionPointFromDB(tsD, ipX, ipY):
    if ipX:
        global annIp, ip
        ipt = graph.plot(ipX, ipY, "or", label="Insertion Point")
        ip = ipt.pop(0)
        annIp = graph.annotate("Insertion Point", xy=(ipX, ipY), xytext=((tsD[0]+ipX)/2.5,ipY-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Suggests an insertion point automatically by comparing a pressure to it's following pressure
def getInsertionPointAuto(pl, ts):
    for i in range(len(pl)-1):
        if abs(pl[i] - pl[i+1]) > int(insertSlider.get()):
                global insertionPointXY, annIp, ip
                if annIp: annIp.remove(), ip.remove()
                tsIn = ts[i]
                plIn = pl[i]
                ipt = graph.plot(tsIn,plIn, "or", label="Insertion Point")
                ip = ipt.pop(0)
                annIp = graph.annotate("Insertion Point", xy=(tsIn, plIn), xytext=((ts[0]+tsIn)/2.5,plIn-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
                canvas.draw()
                insertionPointXY = [tsIn, plIn]
                break
        
# Suggests an insertion point when a specific button is pressed
def insertionPointBtn(pl, ts):
    insertAutoBtn = tk.Button(
    gui, 
    text="Suggest new insertion point",
    command=lambda: getInsertionPointAuto(pl, ts)
    )
    insertAutoBtn.place(relx=.1,rely=.3)
    insertSlider.place(relx=.11, rely=.35)
    insertSlider.set(2)
    lblInsertText.place(relx=0,rely=.375)


# Saves graph and points of interest on it to database
def saveGraph(ts, pl, pc, pr):
    saveGraphBtn = tk.Button(
    gui, 
    text="Save Graph",
    command=lambda: db.insertToTable(fileName.rsplit(".",2)[0], ts, pl, pc, pr, insertionPointXY)
    )
    saveGraphBtn.place(relx=.6, rely=0)

def openSavedGraphs():
    savedGraphs.openWindow()

# GUI elements and their placement
gui = tk.Tk()
fig, graph = plt.subplots()
canvas = FigureCanvasTkAgg(fig, gui)
canvas.get_tk_widget().place(relx=.5,rely=.05)
toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)

startTime = tk.Entry(gui)
lblStartTime = tk.Label(gui, text="Start time:")
stopTime = tk.Entry(gui)
lblStopTime = tk.Label(gui, text="Stop time:")
insertSlider = tk.Scale(gui, from_=0, to=10, orient="horizontal")
lblInsertText = tk.Label(gui, text="Pressure change [mbar]:")
newGraphBtn = tk.Button(
    gui, 
    text="New Graph", 
    command=lambda: [plt.close(), plot(readCSV(1), "None", "None")]
    )
testBtn = tk.Button(
    gui, 
    text="Show saved graphs", 
    command=lambda: openSavedGraphs()
    )
updateGraphBtn = tk.Button(
    gui, 
    text="Update Graph",
    command=lambda: [plt.close(), plot(readCSV(0), startTime.get(), stopTime.get())]
)
testBtn.place(relx=.2,rely=0)
newGraphBtn.place(relx= .1, rely= 0)

if __name__ == "__main__":
    GUI()