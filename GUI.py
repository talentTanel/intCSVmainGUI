import matplotlib.pyplot as plt
import csv
import tkinter as tk

def main():
    data = readCSV()
    GUI(data)

# User Interface code
def GUI(data):
    gui = tk.Tk()
    startTime = tk.Text()
    start = tk.Button(text="Show Graph", command=lambda: plot(data, startTime))
    startTime.pack()
    start.pack()
    gui.mainloop()

# Graphs a .CSV file
def plot(data, time):
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
    plt.plot(ts, pl, "-r", label="Left", rasterized=True) 
    plt.plot(ts, pc, "-b", label="Center", rasterized=True)
    plt.plot(ts, pr, "-k", label="Right", rasterized=True)
    plt.show()
        
# Opens a .CSV file for further processing
def readCSV():
    file = open("C660913142637.csv","r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

if __name__ == "__main__":
    main()