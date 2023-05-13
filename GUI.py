import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv
import tkinter as tk
from tkinter import filedialog, ttk
import promptlib
import glob
import os
import sys
import pandas as pd
import numpy as np
from math import sqrt
from functools import partial
import gc
import json
from scipy import interpolate

fileName=""
sampleRate = None
customPointXY, customPlot, allFiles, lines = [], [], [], []
injectionPointXY = []
ipt = None
# User Interface
def GUI():
    gui.geometry("1280x750")
    gui.bind("<Control-q>", sys.exit)
    gui.mainloop()

# Graphs a .CSV file
def plot(graphData, startTime, stopTime):
    graph.clear()
    global lined, lines
    ts, pl, pc, pr, mag = [], [], [], [], []
    ts, pl, pc, pr, mag = appendElements(ts, pl, pc, pr, mag, graphData)
    ts, pl, pc, pr, mag = startStopTimes(ts, pl, pc, pr, mag, startTime, stopTime)
    lPlot, = graph.plot(ts, pl, "-r", label="P Left") 
    cPlot, = graph.plot(ts, pc, "-b", label="P Center")
    rPlot, = graph.plot(ts, pr, "-k", label="P Right")
    mPlot, = graph.plot(ts, mag, "-r", label="Acc XYZ", linewidth=.8)
    lines = [lPlot, cPlot, rPlot, mPlot]
    lined = {}
    injectionPointDef(pl, ts)
    setLegend()

    graph.set_title(fileName)
    graph.set_xlabel("Time [s]")
    graph.set_ylabel("Pressure [mbar]")
    canvas.mpl_connect('button_press_event', onRightClick)
    canvas.draw()
    toolbar.update()
    toolbar.place(relx=.7, rely=0)
    displayCustomPlot()
    graphOptions()
    gc.collect()

# Creates the legend for graph
def setLegend():
    global lined
    lined = {}
    legend = graph.legend(loc="upper right")
    for leg, orig in zip(legend.get_lines(), lines): # Make all plots in legend clickable
        # https://matplotlib.org/stable/gallery/event_handling/legend_picking.html#sphx-glr-gallery-event-handling-legend-picking-py
        leg.set_picker(True)
        leg.set_pickradius(5)
        lined[leg] = orig
    fig.canvas.mpl_connect('pick_event', onClickLegend)

# Handles clicks on legend, hides/unhides a plot
def onClickLegend(event):
    legend = event.artist
    line = lined[legend]
    visible = line.get_visible()
    line.set_visible(not visible)
    legend.set_alpha(1.0 if not visible else 0.2)
    canvas.draw()

# Exports points of interest and filename to a .CSV file
def exportToCSV():
    createFolder("Export")
    listChildren = customPointList.get_children()
    header, rowHeader = ["File Name,", "INJECTION"], []
    values = []
    values.append(fileName)
    data = readCSV(2)
    rowHeader = data.pop(0)
    data.pop(0)
    data = getDataAtCustomValue(data, listChildren, rowHeader)
    temp3 = []
    if injectionPointXY: values.append(injectionPointXY[0])
    else: values.append("-")
    for child in listChildren:
        temp = customPointList.item(child)
        values.append(temp["values"][2])
        header.extend([temp["values"][1]])
    if values != None:
        try:
            os.chdir(".\\Export")
            with open("ROI_values_"+fileName, 'w', newline="") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerow(values)
                for i in range(len(data)):
                    for j in range(len(data[i])):
                        temp3.append(data[i][j])
                for i in range(len(rowHeader)):
                    arr = [rowHeader[i], temp3[i]]
                    extension = []
                    k = 1
                    for j in range(len(getAllIds())):
                        if(values[j+2] != "-"):
                            index = i+k*len(rowHeader)
                            extension.append(temp3[index])
                            k = k + 1
                        else:
                            extension.append("-")
                            k = k + 1
                    arr.extend(extension)
                    writer.writerow(arr)
                os.chdir("..")
        except Exception as e:
            print(e)

# Exports full data between two custom points
def exportCroppedCSV():
    createFolder("Export")
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
                os.chdir(".\\Export")
                with open(exportName, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    for row in newData:
                        writer.writerow(row)
                os.chdir("..")
            except Exception as e:
                print(e)

# Creates a folder in current directory if it does not exist
def createFolder(name):
    if not os.path.exists(name):
        os.mkdir(name)

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
        menu.add_command(label="Cancel")
        x, y = canvas.get_tk_widget().winfo_pointerxy() # x,y values for where the menu will show up
        menu.post(x, y)

# Gets all data from CSV file at custom point timestamp and returns all of it in one array
def getDataAtCustomValue(data, listChildren, rowHeader):
    tempValues, values = [], []
    if injectionPointXY: 
        # Get injection point data first
        Inj = float(injectionPointXY[0])
        for i in range(len(data)-1):
            diffInj = abs(float(Inj) - float(data[i][0]))
            if diffInj < 0.005:
                for j in range(len(data[i])):
                    tempValues.append(data[i][j])
                values.append(tempValues)
                tempValues = []
                break
    else: 
        tempArr = []
        for i in range(len(rowHeader)):
            tempArr.append("-")
        values.append(tempArr)
    
    for child in listChildren:
        temp = customPointList.item(child)
        timeValue = temp["values"][2]
        if (timeValue != "-"):
            for i in range(len(data)-1):
                tempValues = []
                diff = abs(float(timeValue) - float(data[i][0]))
                if diff < 0.005:
                    for j in range(len(data[i])):
                        tempValues.append(data[i][j])
                    break
        values.append(tempValues)    
    return values
            

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
    customPlot[index][0] = graph.plot(customPointXY[index][0], customPointXY[index][1], "or").pop(0)
    customPlot[index][1] = graph.annotate(id, xy=(customPointXY[index][0], customPointXY[index][1]), xytext=(customPointXY[index][0], customPointXY[index][1]), color="green")
    setLegend()
    canvas.draw()
    listChildren = customPointList.get_children()
    for child in listChildren:
        temp = customPointList.item(child)
        if temp["values"][0] == id:
            tempValues = temp["values"]
            customPointList.item(child, values=(tempValues[0], tempValues[1], customPointXY[index][0]))
            break

# Displays custom points on graph when the graph is updated
def displayCustomPlot():
    for i in range(len(getAllIds())):
        if(customPlot[i][0] != None): 
            customPlot[i][0].remove(), customPlot[i][1].remove()
            customPlot[i] = [None, None, customPlot[i][2]]
            customPlot[i][0] = graph.plot(customPointXY[i][0], customPointXY[i][1], "or").pop(0)
            customPlot[i][1] = graph.annotate(customPlot[i][2], xy=(customPointXY[i][0], customPointXY[i][1]), xytext=(customPointXY[i][0], customPointXY[i][1]), color="green")
            canvas.draw()

# Reads the "points.json" file for ROI points and automatically inserts them to the visible list
def readCustomJSON():
    global customPointXY
    data = readJSON()
    customPointList.delete(*customPointList.get_children())
    for point in data:
        customPointXY.append([None, None, point['id']])
        customPlot.append([None, None, point['id']])
        customPointList.insert("", "end", text=point['id'], values=(point['id'], point['name'], "-"))

# Saves a newly made ROI point to the "points.json" file
def saveCustomToJSON(id, name, comment):
    newPoint = {"id": id, "name": name, "comment": comment}
    data = readJSON()
    data.append(newPoint)
    with open(__file__.rsplit("GUI.py",1)[0]+"\points.json", "w") as file:    
        json.dump(data, file)

# Returns the data from "points.json" file
def readJSON():
    with open(__file__.rsplit("GUI.py",1)[0]+"\points.json", "r") as file:
        return json.load(file)

# Window for creating new custom points
def createCustomPoint():
    crtPoint = tk.Toplevel(gui)
    crtPoint.title("Add new point")
    crtPoint.geometry("300x250")
    num = crtPoint.register(checkIfNum)

    lblId = tk.Label(crtPoint, text="ID (number):")
    lblId.grid(row=0, column=0, padx=25, pady=25)
    txtId = tk.Entry(crtPoint, validate='all', validatecommand=(num, '%P'))
    txtId.grid(row=0, column=1)

    lblName = tk.Label(crtPoint, text="Name (text)*:")
    lblName.grid(row=1, column=0)
    txtName = tk.Entry(crtPoint)
    txtName.grid(row=1, column=1)

    lblComment = tk.Label(crtPoint, text="Comment (text):")
    lblComment.grid(row=2, column=0)
    txtComment = tk.Entry(crtPoint)
    txtComment.grid(row=2, column=1, pady=25)

    lblError = tk.Label(crtPoint, text="Name cannot be empty", fg="red", font=12)
    lblCreated = tk.Label(crtPoint, text="Point created", fg="green", font=12)
    labels = [lblError, lblCreated]

    crtPoint.bind('<Return>', lambda x: listCustomPoint(txtId.get(), txtName.get(), txtComment.get(), labels)) # Can use the Enter key
    addBtn = tk.Button(crtPoint, text="   ADD   ", font=(12), command=lambda: listCustomPoint(txtId.get(), txtName.get(), txtComment.get(), labels))
    addBtn.grid(row=3, column=1)

# Checks if the inputted key is a number or not
def checkIfNum(entry):
    if str.isdigit(entry) or entry == "":
        return True
    else:
        return False
    
# Checks if everything is correct in the custom point creation inputs, also updates values in list
def listCustomPoint(id, name, comment, labels):
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
        saveCustomToJSON(id, name, comment)

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

# Checks if a number is a float or not. Used for startTime & stopTime
def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

# Reads the data from .CSV and inserts into each corresponding variable
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
    editScenarioBtn.place(relx=.05,rely=.21)
    lblScenario.place(relx=.051, rely=.25)
    lblScenarioText.place(relx=.12, rely=.25)
    lblFileName.config(text="File Name: {}".format(fileName))
    lblFileName.place(relx=.051,rely=.33)
    lblInjectionPoint.place(relx=.051,rely=.38)
    lblCustomPoints.place(relx=.05, rely=.42)
    customPointList.place(relx=.05, rely=.46)
    createPointBtn.place(relx=.05, rely=.655)

    lblStartStopGuide.place(relx=.05,rely=.71)
    lblStartStopID.place(relx=.05,rely=.75)
    txtStartCustom.place(relx=.07,rely=.75) 
    txtStopCustom.place(relx=.1,rely=.75)
    customStartStopBtn.place(relx=.12, rely=.745)
    customStartStopResetBtn.place(relx=.155, rely=.745)
    customStartStopExportBtn.place(relx=.193, rely=.745)

    nextGraphBtn.place(relx=.15,rely=.01)
    previousGraphBtn.place(relx=.12,rely=.01)

    saveAsCSVbtn.place(relx=.05,rely=.8)
    canvas.draw()


# Opens a .CSV file for further processing
def readCSV(e):
    if e == 1:
        global fileName
        path, fileName = filedialog.askopenfilename().rsplit("/",1)
        os.chdir(path)
        getAllCSV()
        readCustomJSON()
    data = readFile(fileName)
    global sampleRate
    sampleRate = getSampleRate(data[0])
    if (e != 2): # Need headers for some exports
        data.pop(0) # data[0] is .CSV headers
    if (e == 1):
        resetLabels()
        resetOnNewFile(e)
    return data

# Reads all data from open csv file and returns it
def readFile(name):
    file = open(name, "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

# Gets all .CSV files in a folder for further use in easily changing to next/previous file
def getAllCSV():
    global allFiles
    allFiles = glob.glob("*.{}".format("csv"))

# Changes current file to the next/previous file in folder
def changeFile(event):
    global fileName
    if event == "next":
        for i in range(len(allFiles)-1):
            if (fileName == allFiles[i]) and i != len(allFiles)-1:
                fileName = allFiles[i+1]
                data = readFile(fileName)
                break
    if event == "prev":
        for i in range(len(allFiles)):
            if (fileName == allFiles[i]) and i != 0: 
                fileName = allFiles[i-1]
                data = readFile(fileName)
                break
    try:
        resetOnNewFile(1)
        data.pop(0)
        plt.close()
        plot(data, "None", "None")
    except:
        None

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

# When a new file is opened all previously set values for points of interest are reset
def resetOnNewFile(e):
    if e != 0:
        global injectionPointXY, customPointXY, customPlot
        injectionPointXY = []
        lblScenarioText.config(text="")
        lblInjectionPoint.config(text="Injection Point: -")
        for i in range(len(customPointXY)):
            customPointXY[i] = [None, None, customPointXY[i][2]]
            customPlot[i] = [None, None, customPlot[i][2]]
        listChildren = customPointList.get_children()
        for child in listChildren:
            temp = customPointList.item(child)
            tempValues = temp["values"]
            customPointList.item(child, values=(tempValues[0], tempValues[1], "-"))

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
        global ipt
        if ipt: ipt.remove() # clears previous injection point from graph
        ipt, = graph.plot(injectionPointXY[0],injectionPointXY[1], "oc", label="Injection Point")
        if len(lines) == 4: lines.append(ipt)
        else: lines[len(lines)-1] = ipt
        setLegend()
        canvas.draw()
        lblInjectionPoint.config(text="Injection Point: {} [s]".format(injectionPointXY[0]))


# Suggests an injection point automatically by comparing a pressure to it's following pressure
def getInjectionPointAuto(pl, ts):
    for i in range(len(pl)-1):
        if abs(pl[i] - pl[i+1]) > int(insertSlider.get()):
                global injectionPointXY, ipt, lines
                if ipt: ipt.remove()
                tsIn = ts[i]
                plIn = pl[i]
                ipt, = graph.plot(tsIn,plIn, "oc", label="Injection Point")
                if len(lines) == 4: lines.append(ipt)
                else: lines[len(lines)-1] = ipt
                setLegend()
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
    insertAutoBtn.place(relx=.05,rely=.08)
    insertSlider.place(relx=.05, rely=.14)
    insertSlider.set(2)
    lblInsertText.place(relx=.05,rely=.12)

# Resets the values of labels to their default state when loading in a new file
def resetLabels():
    lblFileName.config(text="File Name: -")
    lblInjectionPoint.config(text="Injection Point: -")


# Function for editing the file's scenario
def editScenario(e):
    if (e == 0):
        lblScenarioText.place_forget()
        txtScenario.delete("1.0", tk.END)
        txtScenario.place(relx=.12, rely=.25)
        text = lblScenarioText.cget("text")
        text = text.rstrip("\n")
        txtScenario.insert(tk.END, text)
        editScenarioBtn.place_forget()
        saveScenarioBtn.place(relx=.05,rely=.21)
    else:
        lblScenarioText.config(text=txtScenario.get("1.0", tk.END))
        lblScenarioText.place(relx=.12, rely=.25)
        txtScenario.place_forget()
        saveScenarioBtn.place_forget()
        editScenarioBtn.place(relx=.05,rely=.21)

# Class for the confidence graphs
class confidenceGraph:
    # Class GUI
    def menu(self):
        self.confGUI = tk.Toplevel()
        self.confGUI.geometry("1280x900")
        self.confGUI.title("Confidence Graph")
        self.confGUI.grab_set() # Force the focus to stay on confidence graph window

        self.figConf, self.graphConf = plt.subplots(2, figsize=(11,7.5), sharex=True)
        self.canvasConf = FigureCanvasTkAgg(self.figConf, self.confGUI)

        self.toolbarConf = NavigationToolbar2Tk(self.canvasConf, self.confGUI, pack_toolbar=False)
        self.toolbarConf.config(background="white")
        self.toolbarConf._message_label.config(background="white", highlightbackground="white")

        self.toolbarConf.place(relx=0.5,rely=0.01)
        self.canvasConf.get_tk_widget().pack()

        self.Buttons()
        self.confGUI.mainloop()

    # Graphs the confidence graph onto the class window
    def graphPressureConf(self, df_combined):
        self.graphConf[0].clear()
        self.graphConf[0].set_title(os.getcwd().rsplit("\\", 1)[1]) # Title is current folder name
        self.setResolution()
        # Normalize time from 0 to 1
        df_combined['Time [ms]'] = (df_combined['Time [ms]']-np.min(df_combined['Time [ms]']))/(np.max(df_combined['Time [ms]'])-np.min(df_combined['Time [ms]']))
        tsNormalised = np.arange(0, 1, 1/int(self.txtRes.get())) # normalised time from 0 to 1 where user can set resolution?

            
        df_grouped = df_combined.groupby('Time [ms]')['PL [hPa]'].agg(['mean', 'std', 'median']) # get mean & standard deviation
        df_grouped.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
        median_std = df_grouped['std'].median()
        df_grouped['std'].fillna(median_std, inplace=True) # changing NaN std values to median std

        fMean = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['mean'])
        fMedian = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['median'])
        fStd = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['std'])
        newMean = fMean(tsNormalised)
        newMedian = fMedian(tsNormalised)
        newStd = fStd(tsNormalised)

        lowerBound = newMean - newStd
        upperBound = newMean + newStd

        self.graphConf[0].set_xlabel('Normalised time')
        self.graphConf[0].set_ylabel('Pressure (mbar)')

        self.graphConf[0].fill_between(tsNormalised, lowerBound, upperBound, color='b', alpha=0.2)

        for filename in set(df_combined['filename']): # Normalised time graphing one file dataset at a time
            file_data = df_combined[df_combined['filename'] == filename]

            f = interpolate.interp1d(file_data['Time [ms]'], file_data['PL [hPa]'])
            try:
                onePressureNew = f(tsNormalised)
            except ValueError:
                self.lblErr.place(relx=.65, rely=.9)
                break
            self.graphConf[0].plot(tsNormalised, onePressureNew, color="gray", linewidth=0.4)
        self.meanPlot, = self.graphConf[0].plot(tsNormalised, newMean, color='b', alpha=1, linewidth=5)
        self.medianPlot, = self.graphConf[0].plot(tsNormalised, newMedian, color='b', alpha=1, linewidth=5)
        self.medianPlot.set_visible(not self.medianPlot.get_visible()) # by default show mean not median

        self.canvasConf.draw()
        self.meanOrMedian()
        gc.collect()

    # Graphs the magnitude graph onto the class window
    def graphMagnitudeConf(self, df_combined):
        self.graphConf[1].clear()
        self.setResolution()
        # Normalize time from 0 to 1
        df_combined['Time [ms]'] = (df_combined['Time [ms]']-np.min(df_combined['Time [ms]']))/(np.max(df_combined['Time [ms]'])-np.min(df_combined['Time [ms]']))
        tsNormalised = np.arange(0, 1, 1/int(self.txtRes.get())) # normalised time from 0 to 1 where user can set resolution?
        df_combined['mag'] = np.sqrt(pow(df_combined['AX [m/s2]'],2) + pow(df_combined['AY [m/s2]'],2) + pow(df_combined['AZ [m/s2]'],2)) # acceleration magnitude
        

        df_grouped = df_combined.groupby('Time [ms]')['mag'].agg(['mean', 'std', 'median']) # get mean & standard deviation
        df_grouped.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
        median_std = df_grouped['std'].median()
        df_grouped['std'].fillna(median_std, inplace=True) # changing NaN std values to median std

        fMean = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['mean'])
        fMedian = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['median'])
        fStd = interpolate.interp1d(df_grouped['Time [ms]'], df_grouped['std'])
        newMean = fMean(tsNormalised)
        newMedian = fMedian(tsNormalised)
        newStd = fStd(tsNormalised)

        lowerBound = newMean - newStd
        upperBound = newMean + newStd

        self.graphConf[1].set_xlabel('Normalised time')
        self.graphConf[1].set_ylabel('Acceleration magnitude (m/s\u00b2)')

        self.graphConf[1].fill_between(tsNormalised, lowerBound, upperBound, color='r', alpha=0.2)

        for filename in set(df_combined['filename']): # Normalised time graphing one file dataset at a time
            file_data = df_combined[df_combined['filename'] == filename]

            f = interpolate.interp1d(file_data['Time [ms]'], file_data['mag'])
            try:
                onePressureNew = f(tsNormalised)
            except ValueError:
                self.lblErr.place(relx=.65, rely=.9)
                break
            self.graphConf[1].plot(tsNormalised, onePressureNew, color="gray", linewidth=0.4)
        self.meanPlotMag, = self.graphConf[1].plot(tsNormalised, newMean, color='r', alpha=1, linewidth=5)
        self.medianPlotMag, = self.graphConf[1].plot(tsNormalised, newMedian, color='r', alpha=1, linewidth=5)
        self.medianPlotMag.set_visible(not self.medianPlotMag.get_visible()) # by default show mean not median

        self.canvasConf.draw()
        gc.collect()

    # Swaps which plot is visible on the graph - either mean or median
    def meanOrMedian(self):
        self.switchBtn.pack_forget()
        self.switchBtn.pack()

    # Swaps the text on button to represent which is visible currently on graph
    def swapText(self):
        if self.switchBtn['text'] == "Median":
            self.switchBtn.config(text=" Mean ")
        else:
            self.switchBtn.config(text="Median")

    # Defines the buttons used in confidence graph window
    def Buttons(self):
        openBtn = tk.Button(
            self.confGUI,
            text="Select Folder with Grouped CSVs",
            command=lambda: self.readFolder()
        )
        openBtn.pack(pady=10)
        self.switchBtn = tk.Button(
            self.confGUI,
            text=" Mean ",
            command=lambda: [
                self.meanPlot.set_visible(not self.meanPlot.get_visible()),
                self.medianPlot.set_visible(not self.medianPlot.get_visible()),
                self.meanPlotMag.set_visible(not self.meanPlotMag.get_visible()),
                self.medianPlotMag.set_visible(not self.medianPlotMag.get_visible()),
                self.canvasConf.draw(),
                self.swapText()
            ]
        )

    # 1. Prompts the user to select a folder with a group of CSV files and gets data from all possible CSV files in folder
    def readFolder(self):
        prmt = promptlib.Files()
        dir = prmt.dir()
        os.chdir(dir)
        dfTemp = []
        for filename in os.listdir(dir): # making a list of all files in folder and reads all data into one dataframe
            if filename.endswith('.csv'):
                filePath = os.path.join(dir, filename)
                df = pd.read_csv(filePath)
                df['filename'] = filename
                dfTemp.append(df)
        self.dataArr = pd.concat(dfTemp)
        self.graphPressureConf(self.dataArr)
        self.graphMagnitudeConf(self.dataArr)

    # Makes a textbox where the user can set desired resolution for confidence graph
    def setResolution(self):
        num = self.confGUI.register(checkIfNum)

        try: self.txtRes.winfo_exists() # if it doesn't exist then this will throw an error prompting the code to create it in except:
        except: 
            self.txtRes = tk.Entry(self.confGUI, validate='all', validatecommand=(num, '%P'))
            self.txtRes.place(relx=.65, rely=.85)
            lblRes = tk.Label(self.confGUI, text="Resolution:")
            lblRes.place(relx=.59, rely=.85)
            btnRedraw = tk.Button(self.confGUI, text="Redraw", command=lambda: [self.graphPressureConf(self.dataArr), self.graphMagnitudeConf(self.dataArr)])
            btnRedraw.place(relx=.75, rely=.85)
            self.lblErr = tk.Label(self.confGUI, text="Change the resolution", fg="red")
        if self.txtRes.get() == "":
            self.txtRes.insert(tk.END, "1000")   
        self.lblErr.place_forget()

# GUI elements and their placement
gui = tk.Tk()
fig, graph = plt.subplots(figsize=(9,7.6))
canvas = FigureCanvasTkAgg(fig, gui)
canvas.get_tk_widget().place(relx=.3,rely=0)
toolbar = NavigationToolbar2Tk(canvas, gui, pack_toolbar=False)
toolbar.config(background="white")
toolbar._message_label.config(background="white", highlightbackground="white")
numbersOnly = gui.register(checkIfNum)

lblScenario = tk.Label(gui, text="Scenario:", font=("Arial bold",12))
lblScenarioText = tk.Label(gui, text="", font=("Arial bold",12))
lblFileName = tk.Label(gui, text="File Name: -", font=("Arial bold",12))
lblInjectionPoint = tk.Label(gui, text="Injection Point: -", font=("Arial bold",12))
lblCustomPoints = tk.Label(gui, text="ROI points: ", font=("Arial", 14))
txtScenario = tk.Text(gui, width=20, height=2, font=("Arial bold",12))
lblStartStopGuide = tk.Label(gui, text="Crop Graph between two ROI points:")
lblStartStopID = tk.Label(gui, text="ID:")
txtStartCustom = tk.Entry(gui, width=3, validate='all', validatecommand=(numbersOnly, '%P'))
txtStopCustom = tk.Entry(gui, width=3, validate='all', validatecommand=(numbersOnly, '%P'))
insertSlider = tk.Scale(gui, from_=0, to=10, orient="horizontal")
lblInsertText = tk.Label(gui, text="Pressure change [mbar]:")
newGraphBtn = tk.Button(
    gui, 
    text="New Graph", 
    command=lambda: [plt.close(), plot(readCSV(1), "None", "None")]
    )
nextGraphBtn = tk.Button(
    gui,
    text="Next",
    command=lambda: changeFile("next")
)
previousGraphBtn = tk.Button(
    gui,
    text="Prev.",
    command=lambda: changeFile("prev")
)
confidenceGraphBtn = tk.Button(
    gui,
    text="Confidence Graphs",
    command=lambda: confidenceGraph().menu()
)
editScenarioBtn = tk.Button(
    gui,
    text="Edit Scenario",
    command=lambda: editScenario(0)
    )
saveScenarioBtn = tk.Button(
    gui,
    text="Save Scenario",
    command=lambda: editScenario(1)
)
saveAsCSVbtn = tk.Button(
    gui,
    text="Save All Values in ROI points to CSV",
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
#savedGraphsBtn.place(relx=.2,rely=0)
confidenceGraphBtn.place(relx=.2,rely=.01)
newGraphBtn.place(relx=.05, rely=.01)
customPointList = ttk.Treeview(gui, column=("ID", "Name", "Time[s]"), show="headings", height=6)
customPointList.column("ID", width=20)
customPointList.heading("ID", text="ID")
customPointList.column("Name", width=100)
customPointList.heading("Name", text="Name")
customPointList.column("Time[s]", width=60)
customPointList.heading("Time[s]", text="Time[s]")

if __name__ == "__main__":
    GUI()