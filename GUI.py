import matplotlib.pyplot as plt
import csv
import tkinter as tk

def main():
    data = readCSV()
    GUI(data)

# User Interface code
def GUI(data):
    gui = tk.Tk()
    gui.geometry("500x500")
    #startTime = tk.Text()
    startTime = tk.Entry()
    stopTime = tk.Entry()
    startTime.place(relx= .1, rely= 0)
    stopTime.place(relx= .1, rely= .1)
    start = tk.Button(text="Show Graph", command=lambda: plot(data, startTime.get(), stopTime.get()))
    start.pack()
    gui.mainloop()

# Graphs a .CSV file
def plot(data, startTime, stopTime):
    dataLength = len(data)
    ts = []
    pl = []
    pc = []
    pr = []
    for i in range(dataLength):
        try:
            ts.append(float(data[i][0]))
            pl.append(float(data[i][1]))
            pc.append(float(data[i][3]))
            pr.append(float(data[i][5]))
        except:
            pass #data[0] is .CSV headers
    old = len(ts)
    dif = 0
    try:
        ts = [x for x in ts if x >= float(startTime)] # Removing all values from timestamp before startTime
        dif = old - len(ts)
    except:
        pass
    for i in range (dif):
        pl.pop(0) # Removing all values from pressure before startTime
        pc.pop(0)
        pr.pop(0)
    old = len(ts)
    dif = 0
    try:
        ts = [x for x in ts if x <= float(stopTime)] # Removing all values from timestamp after stopTime
        dif = old - len(ts)
    except:
        pass
    for i in range (dif):
        pl.pop(len(pl)-1) # Removing all values from pressure after stopTime
        pc.pop(len(pc)-1)
        pr.pop(len(pr)-1)
    
    plt.plot(ts, pl, "-r", label="Left") 
    plt.plot(ts, pc, "-b", label="Center")
    plt.plot(ts, pr, "-k", label="Right")
    plt.show()
        
# Opens a .CSV file for further processing
def readCSV():
    file = open("C660913142637.csv","r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

if __name__ == "__main__":
    main()