# GUI for graphs saved in local database
def savedGraphsGUI():
    global savedGUI
    savedGUI = tk.Toplevel()
    savedGUI.geometry("500x300")
    savedGUI.title("Saved Graphs")
    savedGUI.resizable(False,False)
    savedGraphsList()
    savedGUI.mainloop()

# Gets all saved graphs and displays them in a list
def savedGraphsList():
    global tableList
    tableLabel, tableList, tableScroll = savedGraphsElements()
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

# GUI elements for saved graphs
def savedGraphsElements():
    tableLabel = tk.Label(savedGUI, text="Saved Tables:")
    tableList = tk.Listbox(savedGUI, width=30, height=14, activestyle="none", selectmode="extended")
    tableScroll = tk.Scrollbar(savedGUI, command= tableList.yview)
    return tableLabel, tableList, tableScroll

# Gets the graph that is double-clicked from local database and graphs it
def getSelectedGraph(e):
    for i in tableList.curselection():
        plotFromDB(tableList.get(i))
    savedGUI.destroy()