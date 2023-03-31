import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
from tkinter import filedialog, ttk
import os
import db
import sys
from math import sqrt
from functools import partial

fileName=""
sampleRate = None
customPointXY, customPlot = [], []
injectionPointXY, maxPointXY, minPointXY = [], [], []
annIp, ipPlot = None, None
# User Interface
def GUI():
    gui.geometry("1280x750")
    gui.bind("<Control-q>", sys.exit)
    gui.mainloop()

# Graphs a .CSV file
def plot(graphData, startTime, stopTime):
    graph.clear()
    global plots
    ts, pl, pc, pr, mag = [], [], [], [], []
    ts, pl, pc, pr, mag = appendElements(ts, pl, pc, pr, mag, graphData)
    ts, pl, pc, pr, mag = startStopTimes(ts, pl, pc, pr, mag, startTime, stopTime)
    lPlot, = graph.plot(ts, pl, "-r", label="P Left") 
    cPlot, = graph.plot(ts, pc, "-b", label="P Center")
    rPlot, = graph.plot(ts, pr, "-k", label="P Right")
    mPlot, = graph.plot(ts, mag, "-r", label="Acc XYZ", linewidth=.8)
    injectionPointDef(pl, ts)
    getRange(pl, ts)
    graph.legend(loc="upper right")
    graph.set_xlabel("Time [s]")
    graph.set_ylabel("Pressure [mbar]")
    canvas.mpl_connect('button_press_event', onRightClick)
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    saveGraph(ts, pl, pc, pr)
    graphOptions()
    plots = lPlot, cPlot, rPlot, mPlot

# Gets the visibility of a plot and reverses it when corresponding button is pressed
def GetVisibility(label):
    if label == "Hide P left":
        plots[0].set_visible(not plots[0].get_visible())
    elif label == "Hide P center":
        plots[1].set_visible(not plots[1].get_visible())
    elif label == "Hide P right":
        plots[2].set_visible(not plots[2].get_visible())
    elif label == "Hide Acc Mag":
        plots[3].set_visible(not plots[3].get_visible())
    canvas.draw()

# Exports points of interest and filename to a .CSV file
def exportToCSV():
    listChildren = customPointList.get_children()
    header = ["File Name,", "INJECTION"]
    data = []
    data.append(fileName)
    try:
        data.append(injectionPointXY[0])
        for child in listChildren:
            temp = customPointList.item(child)
            data.append(temp["values"][2])
            header.extend([temp["values"][1]])
    except:
        data = None
        tk.messagebox.showerror("Error", "Please set all points before exporting")
    if data != None:
        try:
            with open("export_"+fileName, 'w', newline="") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerow(data)
        except Exception as e:
            print(e)

# Exports full data between two custom points
def exportCroppedCSV():
    id1 = txtStartCustom.get()
    id2 = txtStopCustom.get()
    if (id1 != "" and id2 != ""):
        data = readCSV(2)
        header = data[0]
        data.pop(0)
        exportName = "Cropped_{}_{}_{}.csv".format(fileName.rsplit(".",2)[0], getCustomPointName(id1), getCustomPointName(id2))
        newData = customPointDataCropping(id1, id2, data)
        if (newData != data):
            try:
                with open(exportName, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    for row in newData:
                        writer.writerow(row)
            except Exception as e:
                print(e)

# Sets the options and commands for each item in the right-click menu on the plot
def onRightClick(event):
    if event.inaxes is not None and event.button == 3: # 'inaxes' to check if the right click was over graph. Button 3 is right mouse click
        menu = tk.Menu(gui, tearoff=0)
        menu.add_command(label="Injection Point", command=lambda: manualInjectionPoint(event))
        listChildren = customPointList.get_children()
        for child in listChildren:
            temp = customPointList.item(child)
            tempValues = temp["values"]
            partialCustom = partial(setCustomPoint, event, tempValues[0])
            useLabel = "{} - {}".format(tempValues[0],tempValues[1])
            menu.add_command(label=useLabel, command= partialCustom)
        menu.add_separator()
        menu.add_command(label="Cancel", command=lambda: setCustomPoint(event, 1))
        x, y = canvas.get_tk_widget().winfo_pointerxy() # x,y values for where the menu will show up
        menu.post(x, y)

# For displaying custom points
def setCustomPoint(event, id):
    global customPointXY
    for i in range(len(customPointXY)):
        if(customPointXY[i][2] == id):
            index = i
            customPointXY[i] = [round(event.xdata, 2), round(event.ydata, 2), id]
    createCustomPlot(id, index)

# All custom points have a numeric identifier, this searches for all the ones that are in use
def getAllIds():
    ids = []
    for i in range(len(customPointXY)):
        ids.append(customPointXY[i][2])
    return ids

# Gets the name value of a custom point
def getCustomPointName(id):
    listChildren = customPointList.get_children()
    for child in listChildren:
        temp = customPointList.item(child)
        if(temp["values"][0] == int(id)):
            return temp["values"][1]
    return None

# Creates the plot and annotation on the visible graph for a custom point
def createCustomPlot(id, index):
    global customPlot
    if(customPlot[index][0]): customPlot[index][0].remove(), customPlot[index][1].remove()
    customPlot[index] = [None, None, id]
    customPlot[index][0] = graph.plot(customPointXY[index][0], customPointXY[index][1], "or", label=id).pop(0)
    customPlot[index][1] = graph.annotate(id, xy=(customPointXY[index][0], customPointXY[index][1]), xytext=((50+customPointXY[index][0]/2.5, customPointXY[index][1]-250)), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    listChildren = customPointList.get_children()
    for child in listChildren:
        temp = customPointList.item(child)
        if temp["values"][0] == id:
            tempValues = temp["values"]
            customPointList.item(child, values=(tempValues[0], tempValues[1], customPointXY[index][0]))
            break

# Window for creating new custom points
def createCustomPoint():
    crtPoint = tk.Toplevel(gui)
    crtPoint.title("Add new point")
    crtPoint.geometry("300x200")
    num = crtPoint.register(checkIfNum)

    lblId = tk.Label(crtPoint, text="ID (number):")
    lblId.grid(row=0, column=0, padx=25, pady=25)
    txtId = tk.Entry(crtPoint, validate='all', validatecommand=(num, '%P'))
    txtId.grid(row=0, column=1)

    lblName = tk.Label(crtPoint, text="Name (text):")
    lblName.grid(row=1, column=0)
    txtName = tk.Entry(crtPoint)
    txtName.grid(row=1, column=1)

    lblError = tk.Label(crtPoint, text="Name cannot be empty", fg="red", font=12)
    lblCreated = tk.Label(crtPoint, text="Point created", fg="green", font=12)
    labels = [lblError, lblCreated]

    crtPoint.bind('<Return>', lambda x: listCustomPoint(txtId.get(), txtName.get(), labels))
    addBtn = tk.Button(crtPoint, text="   ADD   ", font=(12), command=lambda: listCustomPoint(txtId.get(), txtName.get(), labels))
    addBtn.grid(row=2, column=1, pady=25)

    

# Checks if the inputted key is a number or not
def checkIfNum(entry):
    if str.isdigit(entry) or entry == "":
        return True
    else:
        return False
    
# Checks if everything is correct in the custom point creation inputs and gives feedback, also updates values in list
def listCustomPoint(id, name, labels):
    if (name == ""): 
        labels[0].place(relx=.35,rely=.8)
        labels[1].place_forget()
    else: 
        labels[0].place_forget()
        labels[1].place(relx=.35,rely=.8)
        if (id == ""): id = len(customPointXY)
        else: id = int(id)
        listChildren = customPointList.get_children()
        count = 0
        if len(listChildren) == 0:
            customPointList.insert("", "end", text=id, values=(id, name, "-"))
        for child in listChildren:
            count = count + 1
            if customPointList.item(child)["values"][0] == id:
                temp = customPointList.item(child)
                tempValues = temp["values"]
                customPointList.insert("", "end", text=id, values=(tempValues[0],name, "-"))
                customPointList.item(child, values=(len(customPointXY)+1, tempValues[1], tempValues[2]))
                sortCustomList()
                break
            elif (count == len(listChildren)):
                customPointList.insert("", "end", text=id, values=(id, name, "-"))
                sortCustomList()
        saveCustomPoint(id)

# Sorts the items in the treeview list by ID
def sortCustomList():
    children = customPointList.get_children()
    sortedChildren = sorted(children, key=getID)
    customPointList.set_children("", *sortedChildren)

def getID(row):
    return int(customPointList.set(row, "ID"))

# Saves the new custom point values to two arrays and if needed it swaps values
def saveCustomPoint(id):
    global customPointXY, customPlot
    ids = getAllIds()
    if (id not in ids):
        customPointXY.append([None, None, id])
        customPlot.append([None, None, id])
    elif (id in ids):
        for i in range(len(customPointXY)): # If an ID is already in use, but a new one is saved with it
            if(customPointXY[i][2] == id): # then it gives the old ID owner a new ID
                temp = customPointXY[i]
                customPointXY[i] = [None, None, len(customPointXY)+1]
                customPointXY.append(temp)
                temp = customPlot[i]
                customPlot[i] = [None, None, len(customPlot)+1]
                customPlot.append(temp)


# Sets the XY values for the injection point and graphs it
def manualInjectionPoint(event):
    global injectionPointXY
    injectionPointXY = [round(event.xdata, 2), round(event.ydata, 2)]
    displayInjectionPoint(0)

# If a start or stop time has been set this function removes everything not in those ranges
def startStopTimes(ts, pl, pc, pr, mag, startTime, stopTime):
    if(isFloat(startTime) == True):
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        pl, pc, pr, mag = sameLength(ts,pl,pc,pr,mag,"0") # Removing all values from pressure before startTime
    if(isFloat(stopTime) == True):
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        pl, pc, pr, mag = sameLength(ts,pl,pc,pr,mag,"end") # Removing all values from pressure after stopTime
    return ts, pl, pc, pr, mag

# Crops the file data to only save data from between two custom points
def customPointDataCropping(id1, id2, data):
    listChildren = customPointList.get_children()
    newData = data
    for child in listChildren:
        temp = customPointList.item(child)
        tempValues = temp["values"]
        if (tempValues[2] != "-"):
            if (int(id1) == tempValues[0]):
                startTime = tempValues[2]
                newData = [x for x in newData if float(x[0]) >= float(startTime)]
            elif (int(id2) == tempValues[0]):
                stopTime = tempValues[2]
                newData = [x for x in newData if float(x[0]) <= float(stopTime)]
    return newData

# Get graph between two custom points by their id
def customStartStopTimes():
    startID = txtStartCustom.get()
    stopID = txtStopCustom.get()
    if (startID != "" and stopID != ""):
        startID, stopID = int(startID), int(stopID)
        startTime, stopTime = None, None
        if (startID < stopID):
            listChildren = customPointList.get_children()
            for child in listChildren:
                temp = customPointList.item(child)
                tempValues = temp["values"]
                if (startID == tempValues[0]):
                    startTime = tempValues[2]
                elif (stopID == tempValues[0]):
                    stopTime = tempValues[2]
                if (startTime and stopTime and startTime != "-" and stopTime != "-"):
                    plt.close()
                    plot(readCSV(0), startTime, stopTime)
    else:
        plt.close()
        plot(readCSV(0), "None", "None")    

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

# Places all needed GUI elements when a graph is plotted or updated
def graphOptions():
    editScenarioBtn.place(relx=.67,rely=.73)
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
    lblCustomPoints.place(relx=.85, rely=.72)
    customPointList.place(relx=.85, rely=.76)
    createPointBtn.place(relx=.85, rely=.955)

    lblStartStopGuide.place(relx=.1,rely=.41)
    lblStartStopID.place(relx=.1,rely=.45)
    txtStartCustom.place(relx=.12,rely=.45) 
    txtStopCustom.place(relx=.15,rely=.45)
    customStartStopBtn.place(relx=.17, rely=.445)
    customStartStopResetBtn.place(relx=.205, rely=.445)
    customStartStopExportBtn.place(relx=.243, rely=.445)

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
    if (e != 2): # Need headers for some exports
        data.pop(0) # data[0] is .CSV headers
    if (e == 1):
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
        global annIp, ipPlot, injectionPointXY, maxPointXY, minPointXY
        injectionPointXY, maxPointXY, minPointXY = [], [], []
        annIp, ipPlot = None, None
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
        lblInjectionPoint.config(text="Injection Point: {} [s]".format(injectionPointXY[0]))

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
                lblInjectionPoint.config(text="Injection Point: {} [s]".format(tsIn))
                break
        
# Suggests an injection point when a specific button is pressed
def injectionPointBtn(pl, ts):
    insertAutoBtn = tk.Button(
    gui, 
    text="Suggest injection point",
    command=lambda: getInjectionPointAuto(pl, ts)
    )
    insertAutoBtn.place(relx=.1,rely=.25)
    insertSlider.place(relx=.11, rely=.3)
    insertSlider.set(2)
    lblInsertText.place(relx=0,rely=.325)

# Resets the values of labels to their default state when loading in a new file
def resetLabels():
    lblFileName.config(text="File Name: -")
    lblInjectionPoint.config(text="Injection Point: -")

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
        txtScenario.place(relx=.52, rely=.73)
        text = lblScenarioText.cget("text")
        text = text.rstrip("\n")
        txtScenario.insert(tk.END, text)
        editScenarioBtn.place_forget()
        saveScenarioBtn.place(relx=.67,rely=.73)
    else:
        lblScenarioText.config(text=txtScenario.get("1.0", tk.END))
        lblScenarioText.place(relx=.52, rely=.72)
        txtScenario.place_forget()
        saveScenarioBtn.place_forget()
        editScenarioBtn.place(relx=.67,rely=.73)

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
numbersOnly = gui.register(checkIfNum)

lblScenario = tk.Label(gui, text="Scenario:", font=("Arial",14))
lblScenarioText = tk.Label(gui, text="", font=("Arial",14))
lblFileName = tk.Label(gui, text="File Name: -", font=("Arial",14))
lblInjectionPoint = tk.Label(gui, text="Injection Point: -", font=("Arial",14))
lblCustomPoints = tk.Label(gui, text="Custom points: ", font=("Arial", 14))
txtScenario = tk.Text(gui, width=20, height=2, font=("Arial",13))
txtStartTime = tk.Entry(gui)
lblStartTime = tk.Label(gui, text="Start time:")
txtStopTime = tk.Entry(gui)
lblStartStopGuide = tk.Label(gui, text="Crop Graph between two custom points:")
lblStartStopID = tk.Label(gui, text="ID:")
txtStartCustom = tk.Entry(gui, width=3, validate='all', validatecommand=(numbersOnly, '%P'))
txtStopCustom = tk.Entry(gui, width=3, validate='all', validatecommand=(numbersOnly, '%P'))
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
createPointBtn = tk.Button(
    gui,
    text="Create New",
    font=("Arial",12),
    command=lambda: createCustomPoint()
)
customStartStopBtn = tk.Button(
    gui,
    text="Crop",
    command=lambda: customStartStopTimes()
)
customStartStopResetBtn = tk.Button(
    gui,
    text="Clear",
    command=lambda: [txtStartCustom.delete(0, tk.END), txtStopCustom.delete(0, tk.END), plot(readCSV(0), "None", "None")]
)
customStartStopExportBtn = tk.Button(
    gui,
    text="Export Cropped",
    command=lambda: exportCroppedCSV()
)
rax = plt.axes([0.79, 0.12, 0.2, 0.2])
rax.set_visible(False)
check = CheckButtons(rax, ("Hide P left", "Hide P center", "Hide P right", "Hide Acc Mag"), (False, False, False, False))
check.on_clicked(GetVisibility)
savedGraphsBtn.place(relx=.2,rely=0)
newGraphBtn.place(relx= .1, rely= 0)
customPointList = ttk.Treeview(gui, column=("ID", "Name", "Time[s]"), show="headings", height=6)
customPointList.column("ID", width=20)
customPointList.heading("ID", text="ID")
customPointList.column("Name", width=100)
customPointList.heading("Name", text="Name")
customPointList.column("Time[s]", width=60)
customPointList.heading("Time[s]", text="Time[s]")

if __name__ == "__main__":
    GUI()