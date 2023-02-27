import tkinter as tk
import db
import GUI

# GUI for graphs saved in local database
def openWindow():
    global root
    root = tk.Tk()
    root.geometry("500x300")
    root.title("Saved Graphs")
    root.resizable(False,False)
    makeAList()
    root.mainloop()

# Gets all saved graphs and displays them in a list
def makeAList():
    global tableList
    tableLabel, tableList, tableScroll = config()
    tables = db.getAllTables()
    tableList.place(relx=.02,rely=.2)
    tableLabel.grid(row=0,column=0, pady=35, padx=10)
    for i in range(len(tables)):
        table = " " + tables[i] + ".csv"
        tableList.insert(i, table)
    for i in range(40):
        tableList.insert(tk.END, (" " + str(i)))
    tableList.config(yscrollcommand=tableScroll.set)
    tableList.bind('<Double-Button-1>', getSelectedGraph)
    tableScroll.place(relx=.4,rely=.2)

# GUI elements
def config():
    tableLabel = tk.Label(root, text="Saved Tables:")
    tableList = tk.Listbox(root, width=30, height=14, activestyle="none", selectmode="extended")
    tableScroll = tk.Scrollbar(root, command= tableList.yview)
    return tableLabel, tableList, tableScroll

def getSelectedGraph(e):
    for i in tableList.curselection():
        GUI.plotFromDB(tableList.get(i))
    root.destroy()

if __name__ == "__main__":
    openWindow()