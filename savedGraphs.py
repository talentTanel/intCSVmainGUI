import tkinter as tk
import db

# GUI for graphs saved in local database
def openWindow():
    root = tk.Tk()
    root.geometry("500x300")
    root.title("Saved Graphs")
    root.resizable(False,False)
    makeAList(root)
    root.mainloop()

# Gets all saved graphs and displays them in a list
def makeAList(root):
    tableLabel, tableList, tableScroll = config(root)
    tables = db.getAllTables()
    tableList.place(relx=.02,rely=.2)
    tableLabel.grid(row=0,column=0, pady=35, padx=10)
    for i in range(len(tables)):
        table = " " + tables[i] + ".csv"
        tableList.insert(i, table)
    for i in range(40):
        tableList.insert(tk.END, (" " + str(i)))
    tableList.config(yscrollcommand=tableScroll.set)
    tableScroll.place(relx=.4,rely=.2)

# GUI elements
def config(root):
    tableLabel = tk.Label(root, text="Saved Tables:")
    tableList = tk.Listbox(root, width=30, height=14, activestyle="none", selectmode="extended")
    tableScroll = tk.Scrollbar(root, command= tableList.yview)
    return tableLabel, tableList, tableScroll

if __name__ == "__main__":
    openWindow()