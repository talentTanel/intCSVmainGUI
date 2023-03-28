import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
from tkinter import filedialog
import os
import db
from math import sqrt

fileName=""
sampleRate = None
customPointXY, customPlot = [], []
injectionPointXY, maxPointXY, minPointXY, nadirXY, tailwaterXY = [], [], [], [], []
annIp, ipPlot, annMax, maximum, annMin, minimum, annNadir, nadirPlot, annTailwater, tailwaterPlot = None, None, None, None, None, None, None, None, None, None
# User Interface
def GUI():
    gui.geometry("1280x720")
    gui.mainloop()

# Graphs a .CSV file
def plot(graphData, startTime, stopTime):
    graph.clear()
    global plots
    ts, pl, pc, pr, mag = [], [], [], [], []
    ts, pl, pc, pr, mag = appendElements(ts, pl, pc, pr, mag, graphData)
    ts, pl, pc, pr, mag = startStopTimes(ts, pl, pc, pr, mag, startTime, stopTime)
    lPlot, = graph.plot(ts, pl, "-r", label="Left") 
    cPlot, = graph.plot(ts, pc, "-b", label="Center")
    rPlot, = graph.plot(ts, pr, "-k", label="Right")
    mPlot, = graph.plot(ts, mag, "-r", label="Acc XYZ", linewidth=.8)
    injectionPointDef(pl, ts)
    maximumPoint(pl, ts)
    minimumPoint(pl, ts)
    getRange(pl, ts)
    graph.legend(loc="upper right")
    graph.set_xlabel("Time [s]")
    graph.set_ylabel("Pressure [mbar]")
    canvas.mpl_connect('button_press_event', onRightClick)
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    displayManualPoints(ts)
    saveGraph(ts, pl, pc, pr)
    graphOptions()
    plots = lPlot, cPlot, rPlot, mPlot

# Gets the visibility of a plot and reverses it when corresponding button is pressed
def GetVisibility(label):
    if label == "Hide left":
        plots[0].set_visible(not plots[0].get_visible())
    elif label == "Hide center":
        plots[1].set_visible(not plots[1].get_visible())
    elif label == "Hide right":
        plots[2].set_visible(not plots[2].get_visible())
    elif label == "Hide acc XYZ":
        plots[3].set_visible(not plots[3].get_visible())
    canvas.draw()

# Exports points of interest and filename to a .CSV file
def exportToCSV():
    data = []
    data.append(fileName)
    try:
        data.append(injectionPointXY[0])
        data.append(nadirXY[0])
        data.append(tailwaterXY[0])
    except:
        data = None
        tk.messagebox.showerror("Error", "Please set all points before exporting")
    if data != None:
        try:
            with open("export_"+fileName, 'w', newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["File Name, INJECTION, NADIR, TAILWATER"])
                writer.writerow(data)
        except Exception as e:
            print(e)

# Sets the options and commands for each item in the right-click menu on the plot
def onRightClick(event):
    if event.inaxes is not None and event.button == 3: # 'inaxes' to check if the right click was over graph. Button 3 is right mouse click
        menu = tk.Menu(gui, tearoff=0)
        menu.add_command(label="Injection Point", command=lambda: manualInjectionPoint(event))
        menu.add_command(label="Nadir Pressure", command=lambda: manualNadirPoint(event))
        menu.add_command(label="Tailwater", command=lambda: manualTailwaterPoint(event))
        menu.add_separator()
        menu.add_command(label="Cancel", command=lambda: setCustomPoint(event, 1))
        x, y = canvas.get_tk_widget().winfo_pointerxy() # x,y values for where the menu will show up
        menu.post(x, y)

# For creating and displaying custom points
def setCustomPoint(event, id):
    global customPointXY
    ids = getAllIds()
    if (id not in ids):
        customPointXY.append([round(event.xdata, 2), round(event.ydata, 2), id])
        index = len(customPointXY)-1
    else:
        for i in range(len(customPointXY)):
            if(customPointXY[i][2] == id):
                index = i
                customPointXY[i] == [round(event.xdata, 2), round(event.ydata, 2), id]
    createCustomPlot(id, index)

# All custom points have a numeric identifier, this searches for all the ones that are in use
def getAllIds():
    ids = []
    for i in range(len(customPointXY)):
        ids.append(customPointXY[i][2])
    return ids

def createCustomPlot(id, index):
    global customPlot
    ids = getAllIds()
    if (id in ids and customPlot == []):
        customPlot.append([None, None, id])
    elif(id in ids and customPlot != []):
        customPlot.append([None, None, id])
    else:
        customPlot[index] == [None, None, id]
    if(customPlot[index][0]): customPlot[index][0].remove(), customPlot[index][1].remove()
    customPlot[index][0] = graph.plot(customPointXY[index][0], customPointXY[index][1], "or", label=id).pop(0)
    customPlot[index][1] = graph.annotate(id, xy=(customPointXY[index][0], customPointXY[index][1]), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()

                

# Sets the XY values for the injection point and graphs it
def manualInjectionPoint(event):
    global injectionPointXY
    injectionPointXY = [round(event.xdata, 2), round(event.ydata, 2)]
    displayInjectionPoint(0)

# Sets the XY values for the nadir point and graphs it
def manualNadirPoint(event):
    global nadirXY, annNadir, nadirPlot
    nadirXY = [round(event.xdata, 2), round(event.ydata, 2)]
    temp = 50
    if annNadir: annNadir.remove(), nadirPlot.remove()
    nadirPointT = graph.plot(nadirXY[0],nadirXY[1], "or", label="Nadir Point")
    nadirPlot = nadirPointT.pop(0)
    annNadir = graph.annotate("Nadir Point", xy=(nadirXY[0], nadirXY[1]), xytext=((temp+nadirXY[0])/2.5,nadirXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    lblNadirPoint.config(text="Nadir Point [s]: {}".format(nadirXY[0]))

# Sets the XY values for the tailwater point and graphs it
def manualTailwaterPoint(event):
    global tailwaterXY, annTailwater, tailwaterPlot
    tailwaterXY = [round(event.xdata, 2), round(event.ydata, 2)]
    temp = 50
    if annTailwater: annTailwater.remove(), tailwaterPlot.remove()
    tailwaterPlotT = graph.plot(tailwaterXY[0],tailwaterXY[1], "or", label="Tailwater")
    tailwaterPlot = tailwaterPlotT.pop(0)
    annTailwater = graph.annotate("Tailwater", xy=(tailwaterXY[0], tailwaterXY[1]), xytext=((temp+tailwaterXY[0])/2.5,tailwaterXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    lblTailwater.config(text="Tailwater [s]: {}".format(tailwaterXY[0]))

# If these points exist on updating the graph, then it displays them
def displayManualPoints(ts):
    global nadirXY, annNadir, nadirPlot, tailwaterXY, annTailwater, tailwaterPlot
    if ts == 0: ts[0] = 50
    if annNadir: # Nadir Point
        annNadir.remove(), nadirPlot.remove()
        nadirPointT = graph.plot(nadirXY[0],nadirXY[1], "or", label="Nadir Point")
        nadirPlot = nadirPointT.pop(0)
        annNadir = graph.annotate("Nadir Point", xy=(nadirXY[0], nadirXY[1]), xytext=((ts[0]+nadirXY[0])/2.5,nadirXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()
        lblNadirPoint.config(text="Nadir Point [s]: {}".format(nadirXY[0]))
    if annTailwater: # Tailwater Point
        annTailwater.remove(), tailwaterPlot.remove()
        tailwaterPlotT = graph.plot(tailwaterXY[0],tailwaterXY[1], "or", label="Tailwater")
        tailwaterPlot = tailwaterPlotT.pop(0)
        annTailwater = graph.annotate("Tailwater", xy=(tailwaterXY[0], tailwaterXY[1]), xytext=((ts[0]+tailwaterXY[0])/2.5,tailwaterXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()
        lblTailwater.config(text="Tailwater [s]: {}".format(tailwaterXY[0]))


# If a start or stop time has been set this function removes everything not in those ranges
def startStopTimes(ts, pl, pc, pr, mag, startTime, stopTime):
    if(isFloat(startTime) == True):
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl, pc, pr, mag = sameLength(ts,pl,pc,pr,mag,"0") # Removing all values from pressure before startTime
    if(isFloat(stopTime) == True):
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl, pc, pr, mag = sameLength(ts,pl,pc,pr,mag,"end") # Removing all values from pressure after stopTime
    return ts, pl, pc, pr, mag

# Automatically finds the region of interest in graph from maximum pressure point
def findRange(pl ,ts):
    maxPl = max(pl)
    startTs = ts[pl.index(maxPl)]-40
    stopTs = ts[pl.index(maxPl)]+50
    txtStartTime.delete(0, tk.END)
    txtStopTime.delete(0, tk.END)
    txtStartTime.insert(0, round(startTs))
    txtStopTime.insert(0, round(stopTs))
    plt.close()
    plot(readCSV(0), txtStartTime.get(), txtStopTime.get())

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
def appendElements(ts, pl, pc, pr, mag, graphData):
    tempP = 0
    if len(graphData) != 4: # When gotten from db the size is smaller
        for i in range(len(graphData)):
            ts.append(float(graphData[i][0]))
            pl.append(float(graphData[i][1]))
            pc.append(float(graphData[i][3]))
            pr.append(float(graphData[i][5]))
            if i == 0:
                tempP = pl[0]
            if sampleRate == 100:
                mag.append(tempP-10+sqrt(pow(float(graphData[i][17]),2) + pow(float(graphData[i][18]),2) + pow(float(graphData[i][19]),2)))
            elif sampleRate == 250:
                mag.append(tempP-10+sqrt(pow(float(graphData[i][7]),2) + pow(float(graphData[i][8]),2) + pow(float(graphData[i][9]),2)))
            else:
                mag.append(0)
    else:
        ts = graphData[0]
        pl = graphData[1]
        pc = graphData[2]
        pr = graphData[3]
    return ts, pl, pc, pr, mag

# Places multiple GUI elements when a graph is plotted for the first time
def graphOptions():
    editScenarioBtn.place(relx=.72,rely=.73)
    txtStartTime.place(relx= .1, rely= .1)
    lblStartTime.place(relx= .05, rely= .1)
    txtStopTime.place(relx= .1, rely= .2)
    lblStopTime.place(relx= .05, rely= .2)
    updateGraphBtn.place(relx=.21,rely=.09)
    lblScenario.place(relx=.45, rely=.72)
    lblScenarioText.place(relx=.52, rely=.72)
    lblFileName.config(text="File Name: {}".format(fileName))
    lblFileName.place(relx=.45,rely=.8)
    lblInjectionPoint.place(relx=.45,rely=.85)
    lblMaximumPoint.place(relx=.45,rely=.9)
    lblMinimumPoint.place(relx=.45,rely=.95)
    lblNadirPoint.place(relx=.8,rely=.8)
    lblTailwater.place(relx=.8,rely=.85)
    saveAsCSVbtn.place(relx=.52,rely=0)
    rax.set_visible(True)
    canvas.draw()

# Gets graph from database data
def plotFromDB(table):
    graph.clear()
    tableName = table.rsplit(".",2)[0]
    data, ipX, ipY, maxX, maxY, minX, minY, scenario = db.getTable(tableName)
    if ipX:
        global injectionPointXY
        injectionPointXY = [ipX, ipY]
    if maxX:
        global maxPointXY
        maxPointXY = [maxX, maxY]
    if minX:
        global minPointXY
        minPointXY = [minX, minY]
    startTime = data[0][0]
    stopTime = data[0][len(data[0])-1]
    resetOnPullDB(tableName, scenario, startTime, stopTime)
    plot(data, startTime, stopTime)
    
# Resets & updates GUI element values when getting a new graph from db
def resetOnPullDB(tableName, scenario, startTime, stopTime):
    global fileName
    fileName = tableName.replace(" ", "") + ".csv"
    lblScenarioText.config(text=scenario)
    txtStartTime.delete(0, tk.END)
    txtStartTime.insert(tk.END, round(startTime))
    txtStopTime.delete(0, tk.END)
    txtStopTime.insert(tk.END, round(stopTime))


# Opens a .CSV file for further processing
def readCSV(e):
    if e == 1:
        global fileName
        fileName = os.path.basename(filedialog.askopenfilename())
    file = open(fileName,"r")
    data = list(csv.reader(file, delimiter=","))
    global sampleRate
    sampleRate = getSampleRate(data[0])
    file.close()
    data.pop(0) # data[0] is .CSV headers
    resetLabels()
    resetOnNewFile(e)
    return data

# Gets the sample rate of each opened file, needed to know header element locations
def getSampleRate(headers):
    #print(headers)
    fileHeaders = []
    # 250 Hz headers
    fileHeaders.append(['Time [s]', 'PL [hPa]', 'TL [C]', 'PC [hPa]', 'TC [C]', 'PR [hPa]', 'TR [C]', 'AX [m/s2]', 'AY [m/s2]', 'AZ [m/s2]', 'RX [rad/s]', 'RY [rad/s]', 'RZ [rad/s]', 'CSM', 'CSA', 'CSR', 'CSTOT'])
    # 100 Hz headers
    fileHeaders.append(['Time [s]', 'PL [mbar]', 'TL [C]', 'PC [mbar]', 'TC [C]', 'PR [mbar]', 'TR [C]', 'EX [deg]', 'EY [deg]', 'EZ [deg]', 'QW [-]', 'QX [-]', 'QY [-]', 'QZ [-]', 'MX [microT]', 'MY [microT]', 'MZ [microT]', 'AX [m/s2]', 'AY [m/s2]', 'AZ [m/s2]', 'RX [rad/s]', 'RY [rad/s]', 'RZ [rad/s]', 'CSM', 'CSA', 'CSR', 'CSTOT'])
    if headers == fileHeaders[0]:
        return 250
    elif headers == fileHeaders[1]:
        return 100
    else:
        return 0

# When a new file is opened all previously set values for points of interests are reset
def resetOnNewFile(e):
    if e != 0:
        global annIp, ipPlot, annMax, maximum, annMin, minimum, injectionPointXY, maxPointXY, minPointXY, nadirXY, tailwaterXY, annNadir, nadirPlot, annTailwater, tailwaterPlot
        injectionPointXY, maxPointXY, minPointXY, nadirXY, tailwaterXY = [], [], [], [], []
        annIp, ipPlot, annMax, maximum, annMin, minimum, annNadir, nadirPlot, annTailwater, tailwaterPlot = None, None, None, None, None, None, None, None, None, None
        lblScenarioText.config(text="")

# Makes two lists the same length for graphing
def sameLength(X, pl, pc, pr, mag, type):
    while len(X) != len(pl):
        if(type == "end"):
            pl.pop()
            pc.pop()
            pr.pop()
            mag.pop()
        else:
            pl.pop(0)
            pc.pop(0)
            pr.pop(0)
            mag.pop(0)
    return pl, pc, pr, mag
    
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

# Checks if an injection point is already available, if there is - displays it
def injectionPointDef(pl, ts):
    injectionPointBtn(pl, ts)
    displayInjectionPoint(ts)

def displayInjectionPoint(ts):
    if injectionPointXY: 
        if ts == 0:
            ts = []
            ts.append(50) # placeholder number, need to think of a better way to either replace ts[0] or some other method
        global annIp, ipPlot
        if annIp: annIp.remove(), ipPlot.remove() # clears previous injection point from graph
        ipt = graph.plot(injectionPointXY[0],injectionPointXY[1], "or", label="Injection Point")
        ipPlot = ipt.pop(0)
        annIp = graph.annotate("Injection Point", xy=(injectionPointXY[0], injectionPointXY[1]), xytext=((ts[0]+injectionPointXY[0])/2.5,injectionPointXY[1]-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()
        lblInjectionPoint.config(text="Injection Point: {} [mbar] {} [second]".format(injectionPointXY[1], injectionPointXY[0]))

# Gets injection point from database if it exists
def injectionPointFromDB(tsD, ipX, ipY):
    if ipX:
        global annIp, ipPlot
        ipt = graph.plot(ipX, ipY, "or", label="Injection Point")
        ipPlot = ipt.pop(0)
        annIp = graph.annotate("Injection Point", xy=(ipX, ipY), xytext=((tsD[0]+ipX)/2.5,ipY-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Suggests an injection point automatically by comparing a pressure to it's following pressure
def getInjectionPointAuto(pl, ts):
    for i in range(len(pl)-1):
        if abs(pl[i] - pl[i+1]) > int(insertSlider.get()):
                global injectionPointXY, annIp, ipPlot
                if annIp: annIp.remove(), ipPlot.remove()
                tsIn = ts[i]
                plIn = pl[i]
                ipt = graph.plot(tsIn,plIn, "or", label="Injection Point")
                ipPlot = ipt.pop(0)
                annIp = graph.annotate("Injection Point", xy=(tsIn, plIn), xytext=((ts[0]+tsIn)/2.5,plIn-250), color="green", arrowprops= dict(facecolor="green", headwidth=8))
                canvas.draw()
                injectionPointXY = [tsIn, plIn]
                lblInjectionPoint.config(text="Injection Point: {} [mbar] {} [s]".format(plIn, tsIn))
                break
        
# Suggests an injection point when a specific button is pressed
def injectionPointBtn(pl, ts):
    insertAutoBtn = tk.Button(
    gui, 
    text="Suggest new injection point",
    command=lambda: getInjectionPointAuto(pl, ts)
    )
    insertAutoBtn.place(relx=.1,rely=.3)
    insertSlider.place(relx=.11, rely=.35)
    insertSlider.set(2)
    lblInsertText.place(relx=0,rely=.375)

# Resets the values of labels to their default state when loading in a new file
def resetLabels():
    lblFileName.config(text="File Name: -")
    lblInjectionPoint.config(text="Injection Point: -")
    lblMaximumPoint.config(text="Maximum Pressure [mbar]: -")
    lblMinimumPoint.config(text="Minimum Pressure [mbar]: -")
    lblNadirPoint.config(text="Nadir Point [s]: -")
    lblTailwater.config(text="Tailwater [s]: -")

# Saves graph and points of interest on it to database
def saveGraph(ts, pl, pc, pr):
    saveGraphBtn = tk.Button(
    gui, 
    text="Save Graph",
    command=lambda: db.insertToTable(fileName.rsplit(".",2)[0], ts, pl, pc, pr, injectionPointXY, maxPointXY, minPointXY, lblScenarioText.cget("text"))
    )
    saveGraphBtn.place(relx=.6, rely=0)

# Function for editing the file's scenario
def editScenario(e):
    if (e == 0):
        lblScenarioText.place_forget()
        txtScenario.delete("1.0", tk.END)
        txtScenario.place(relx=.57, rely=.73)
        text = lblScenarioText.cget("text")
        text = text.rstrip("\n")
        txtScenario.insert(tk.END, text)
        editScenarioBtn.place_forget()
        saveScenarioBtn.place(relx=.72,rely=.73)
    else:
        lblScenarioText.config(text=txtScenario.get("1.0", tk.END))
        lblScenarioText.place(relx=.57, rely=.72)
        txtScenario.place_forget()
        saveScenarioBtn.place_forget()
        editScenarioBtn.place(relx=.72,rely=.73)

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

lblScenario = tk.Label(gui, text="Scenario:", font=("Arial",14))
lblScenarioText = tk.Label(gui, text="", font=("Arial",14))
lblFileName = tk.Label(gui, text="File Name: -", font=("Arial",14))
lblInjectionPoint = tk.Label(gui, text="Injection Point: -", font=("Arial",14))
lblMaximumPoint = tk.Label(gui, text="Maximum Pressure [mbar]: -", font=("Arial",14))
lblMinimumPoint = tk.Label(gui, text="Minimum Pressure [mbar]: -", font=("Arial",14))
lblNadirPoint = tk.Label(gui, text="Nadir Point [s]: -", font=("Arial",14))
lblTailwater = tk.Label(gui, text="Tailwater [s]: -", font=("Arial",14))
txtScenario = tk.Text(gui, width=20, height=2, font=("Arial",13))
txtStartTime = tk.Entry(gui)
lblStartTime = tk.Label(gui, text="Start time:")
txtStopTime = tk.Entry(gui)
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
    command=lambda: [plt.close(), plot(readCSV(0), txtStartTime.get(), txtStopTime.get())]
)
editScenarioBtn = tk.Button(
    gui,
    text="EDIT SCENARIO",
    font=("Arial bold",12),
    command=lambda: editScenario(0)
    )
saveScenarioBtn = tk.Button(
    gui,
    text="SAVE SCENARIO",
    font=("Arial bold",12),
    command=lambda: editScenario(1)
)
saveAsCSVbtn = tk.Button(
    gui,
    text="Save As CSV",
    command=lambda: exportToCSV()
)
rax = plt.axes([0.79, 0.12, 0.2, 0.2])
rax.set_visible(False)
check = CheckButtons(rax, ("Hide left", "Hide center", "Hide right", "Hide acc XYZ"), (False, False, False, False))
check.on_clicked(GetVisibility)
savedGraphsBtn.place(relx=.2,rely=0)
newGraphBtn.place(relx= .1, rely= 0)

if __name__ == "__main__":
    GUI()