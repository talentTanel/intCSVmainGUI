import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
from tkinter import filedialog
import os
import db

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
    ts, pl, pc, pr = [], [], [], []
    ts, pl, pc, pr = appendElements(ts, pl, pc, pr, graphData)
    ts, pl, pc, pr = startStopTimes(ts, pl, pc, pr, startTime, stopTime)
    graph.plot(ts, pl, "-r", label="Left") 
    graph.plot(ts, pc, "-b", label="Center")
    graph.plot(ts, pr, "-k", label="Right")
    insertionPointDef(pl, ts)
    maximumPoint(pl, ts)
    minimumPoint(pl, ts)
    getRange(pl, ts)
    graph.legend(loc="upper right")
    graph.set_xlabel("Time [s]")
    graph.set_ylabel("Pressure [mbar]")
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    saveGraph(ts, pl, pc, pr)
    graphOptions()

# If a start or stop time has been set this function removes everything not in those ranges
def startStopTimes(ts, pl, pc, pr, startTime, stopTime):
    if(isFloat(startTime) == True):
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"0") # Removing all values from pressure before startTime
    if(isFloat(stopTime) == True):
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl, pc, pr = sameLength(ts,pl,pc,pr,"end") # Removing all values from pressure after stopTime
    return ts, pl, pc, pr

# Automatically finds the region of interest in graph from maximum pressure point
def findRange(pl ,ts):
    maxPl = max(pl)
    startTs = ts[pl.index(maxPl)]-40
    stopTs = ts[pl.index(maxPl)]+50
    startTime.delete(0, tk.END)
    stopTime.delete(0, tk.END)
    startTime.insert(0, round(startTs))
    stopTime.insert(0, round(stopTs))
    plt.close()
    plot(readCSV(0), startTime.get(), stopTime.get())

# Button for finding area of interest
def getRange(pl, ts):
    getRangeBtn = tk.Button(
        gui,
        text="Get area of interest",
        command= lambda: findRange(pl, ts)
    )
    getRangeBtn.place(relx=.21, rely=.15)
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
    lblFileName.config(text="File Name: {}".format(fileName))
    lblFileName.place(relx=.5,rely=.75)
    lblInsertionPoint.place(relx=.5,rely=.8)
    lblMaximumPoint.place(relx=.5,rely=.85)
    lblMinimumPoint.place(relx=.5,rely=.9)

# Gets graph from database data
def plotFromDB(table):
    graph.clear()
    tableName = table.rsplit(".",2)[0]
    data, ipX, ipY, maxX, maxY, minX, minY = db.getTable(tableName)
    if ipX:
        global insertionPointXY
        insertionPointXY = [ipX, ipY]
    if maxX:
        global maxPointXY
        maxPointXY = [maxX, maxY]
    if minX:
        global minPointXY
        minPointXY = [minX, minY]
    global fileName
    fileName = tableName + ".csv"
    fileName = fileName.replace(" ", "")
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
    resetLabels()
    if e != 0:
        global annIp, ip, annMax, maximum, annMin, minimum, insertionPointXY, maxPointXY, minPointXY
        insertionPointXY, maxPointXY, minPointXY = [], [], []
        annIp, ip, annMax, maximum, annMin, minimum = None, None, None, None, None, None
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
        lblMaximumPoint.config(text="Maximum Pressure [mbar]: {}".format(maxPointXY[1]))

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
    lblMaximumPoint.config(text="Maximum Pressure [mbar]: {}".format(maxPl))

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
        annmin = graph.annotate("Minimum Point", xy=(minPointXY[0], minPointXY[1]), xytext=(minPointXY[0]-tsPlace, minPointXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()
        lblMinimumPoint.config(text="Minimum Pressure [mbar]: {}".format(minPointXY[1]))

# Finds the lowest pressure in variable and that is the minimum point. Displays it on the graph
def getMinimumPoint(pl, ts):
    minPl = min(pl)
    minTs = ts[pl.index(minPl)]
    
    global annmin, minimum, minPointXY
    minimumt = graph.plot(minTs, minPl, "or", label="minimum point")
    minimum = minimumt.pop(0)
    tsPlace = ts[len(ts)-1] / 8
    annmin = graph.annotate("Minimum Point", xy=(minTs, minPl), xytext=(minTs-tsPlace, minPl-259), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    minPointXY = [minTs, minPl]
    lblMinimumPoint.config(text="Minimum Pressure [mbar]: {}".format(minPl))

# Checks if an insertion point is already available, if there is - displays it
def insertionPointDef(pl, ts):
    insertionPointBtn(pl, ts)
    if insertionPointXY:
        global annIp, ip
        ipt = graph.plot(insertionPointXY[0],insertionPointXY[1], "or", label="Insertion Point")
        ip = ipt.pop(0)
        annIp = graph.annotate("Insertion Point", xy=(insertionPointXY[0], insertionPointXY[1]), xytext=((ts[0]+insertionPointXY[0])/2.5,insertionPointXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()
        lblInsertionPoint.config(text="Insertion Point: {} [mbar] {} [second]".format(insertionPointXY[1], insertionPointXY[0]))

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
                lblInsertionPoint.config(text="Insertion Point: {} [mbar] {} [second]".format(plIn, tsIn))
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

# Resets the values of labels to their default state when loading in a new file
def resetLabels():
    lblFileName.config(text="File Name: -")
    lblInsertionPoint.config(text="Insertion Point: -")
    lblMaximumPoint.config(text="Maximum Pressure [mbar]: -")
    lblMinimumPoint.config(text="Minimum Pressure [mbar]: -")

# Saves graph and points of interest on it to database
def saveGraph(ts, pl, pc, pr):
    saveGraphBtn = tk.Button(
    gui, 
    text="Save Graph",
    command=lambda: db.insertToTable(fileName.rsplit(".",2)[0], ts, pl, pc, pr, insertionPointXY, maxPointXY, minPointXY)
    )
    saveGraphBtn.place(relx=.6, rely=0)

# This class is for getting all the locally saved graphs and listing them
class SavedGraphs:
    # GUI for graphs saved in local database
    def savedGraphsGUI(self):
        self.savedGUI = tk.Toplevel()
        self.savedGUI.geometry("500x300")
        self.savedGUI.title("Saved Graphs")
        self.savedGUI.resizable(False,False)
        self.savedGraphsList()
        self.savedGUI.mainloop()

    # Gets all saved graphs and displays them in a list
    def savedGraphsList(self):
        tableLabel, self.tableList, tableScroll = self.savedGraphsElements()
        tables = db.getAllTables()
        self.tableList.place(relx=.02,rely=.2)
        tableLabel.grid(row=0,column=0, pady=35, padx=10)
        for i in range(len(tables)):
            table = " " + tables[i] + ".csv"
            self.tableList.insert(i, table)
        for i in range(20):
            self.tableList.insert(tk.END, (" " + str(i)))
        self.tableList.config(yscrollcommand=tableScroll.set)
        self.tableList.bind('<Double-Button-1>', self.getSelectedGraph)
        tableScroll.place(relx=.4,rely=.2)

    # GUI elements for saved graphs
    def savedGraphsElements(self):
        tableLabel = tk.Label(self.savedGUI, text="Saved Tables:")
        tableList = tk.Listbox(self.savedGUI, width=30, height=14, activestyle="none", selectmode="extended")
        tableScroll = tk.Scrollbar(self.savedGUI, command= tableList.yview)
        return tableLabel, tableList, tableScroll

    # Gets the double-clicked element from the list and finds it in the local database
    def getSelectedGraph(self, e):
        for i in self.tableList.curselection():
            plotFromDB(self.tableList.get(i))
        self.savedGUI.destroy()

# GUI elements and their placement
gui = tk.Tk()
fig, graph = plt.subplots()
canvas = FigureCanvasTkAgg(fig, gui)
canvas.get_tk_widget().place(relx=.5,rely=.05)
toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)

lblFileName = tk.Label(gui, text="File Name: -", font=("Arial",14))
lblInsertionPoint = tk.Label(gui, text="Insertion Point: -", font=("Arial",14))
lblMaximumPoint = tk.Label(gui, text="Maximum Pressure [mbar]: -", font=("Arial",14))
lblMinimumPoint = tk.Label(gui, text="Minimum Pressure [mbar]: -", font=("Arial",14))
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
savedGraphsBtn = tk.Button(
    gui, 
    text="Show saved graphs", 
    command=lambda: SavedGraphs().savedGraphsGUI()
    )
updateGraphBtn = tk.Button(
    gui, 
    text="Update Graph",
    command=lambda: [plt.close(), plot(readCSV(0), startTime.get(), stopTime.get())]
)
savedGraphsBtn.place(relx=.2,rely=0)
newGraphBtn.place(relx= .1, rely= 0)

if __name__ == "__main__":
    GUI()