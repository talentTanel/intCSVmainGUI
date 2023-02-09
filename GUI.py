import matplotlib.pyplot as plt
import csv
import random

def main():
    print("Hello")
    data = readCSV()
    plot(data)

# Graphs a .CSV file
def plot(data):
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
            pass #data[0] is headers
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