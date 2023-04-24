import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import promptlib
import os
import pandas as pd
import numpy as np
import gc

def menu():
    confGUI = tk.Tk()
    confGUI.geometry("800x800")
    global figConf, graphConf, canvasConf
    figConf, graphConf = plt.subplots()
    canvasConf = FigureCanvasTkAgg(figConf, confGUI)
    canvasConf.get_tk_widget().pack()

    openGroupBtn(confGUI)
    confGUI.mainloop()

# Graphs the confidence graph onto the class window
def graph1(df_combined):
    graphConf.clear()
    # Normalize time from 0 to 1
    df_combined['Time [ms]'] = (df_combined['Time [ms]']-np.min(df_combined['Time [ms]']))/(np.max(df_combined['Time [ms]'])-np.min(df_combined['Time [ms]']))
    
    df_grouped = df_combined.groupby('Time [ms]')['PL [hPa]'].agg(['mean', 'std']) # get mean & standard deviation
    df_grouped.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
    median_std = df_grouped['std'].median()
    df_grouped['std'].fillna(median_std, inplace=True) # changing NaN std values to median std

    # Smoothing out the mean into a rolling mean. Otherwise it looks bad on graph
    window_size = 100
    df_grouped['rolling_mean'] = df_grouped['mean'].rolling(window_size, center=True).mean()
    df_grouped['lower'] = df_grouped['mean']-df_grouped['std']
    df_grouped['upper'] = df_grouped['mean']+df_grouped['std']

    graphConf.set_xlabel('Normalised time')
    graphConf.set_ylabel('Pressure (mbar)')

    graphConf.fill_between(df_grouped['Time [ms]'], df_grouped['lower'], df_grouped['upper'], color='red', alpha=0.2)
    # separate plots for each file
    for filename in set(df_combined['filename']):
        file_data = df_combined[df_combined['filename'] == filename]
        graphConf.plot(file_data['Time [ms]'], file_data['PL [hPa]'], color="gray", linewidth=0.5)
    graphConf.plot(df_grouped['Time [ms]'], df_grouped['rolling_mean'], color='r', alpha=1, linewidth=5)

    canvasConf.draw()
    gc.collect()

# Button for prompting the user to choose a folder
def openGroupBtn(confGUI):
    openBtn = tk.Button(
        confGUI,
        text="Select Folder with Grouped CSVs",
        command=lambda: readFolder()
    )
    openBtn.pack()

# 1. Prompts the user to select a folder with a group of CSV files and gets data from all possible CSV files in folder
def readFolder():
    prmt = promptlib.Files()
    dir = prmt.dir()
    os.chdir(dir)
    dfTemp, dataArr, df = [], [], []
    for filename in os.listdir(dir): # making a list of all files in folder and reads all data into one dataframe
        if filename.endswith('.csv'):
            filePath = os.path.join(dir, filename)
            df = pd.read_csv(filePath)
            df['filename'] = filename
            dfTemp.append(df)
    dataArr = pd.concat(dfTemp)
    graph1(dataArr)

if __name__ == "__main__":
    menu()