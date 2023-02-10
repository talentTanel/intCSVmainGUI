import matplotlib.pyplot as plt
import csv
import tkinter as tk

gui = tk.Tk()

def main():
    data = readCSV()
    data.pop(0)
    GUI(data)

# User Interface code
def GUI(data):
    gui.geometry("500x500")
    #startTime = tk.Text()
    startTime = tk.Entry()
    stopTime = tk.Entry()
    startTime.place(relx= .1, rely= .1)
    stopTime.place(relx= .1, rely= .2)
    start = tk.Button(text="Show Graph", command=lambda: [plt.close(), plot(data, startTime.get(), stopTime.get())])
    start.place(relx= .1, rely= 0)
    gui.mainloop()

# Graphs a .CSV file
def plot(data, startTime, stopTime):
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

# Makes two lists the same length for graphing
def sameLength(X, Y, type):
    while len(X) != len(Y):
        if(type == "end"):
            Y.pop()
        else:
            Y.pop(0)
    return Y
    
    

if __name__ == "__main__":
    main()