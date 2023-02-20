import tkinter as tk
import db

# This file is for when you press the button in GUI.py to show saved graphs
def main():
    root.mainloop()

def makeAList():
    tables = db.getAllTables()
    tableList.place(relx=0,rely=.2)
    tableLabel.place(relx=0,rely=.13)
    for i in range(len(tables)):
        table = tables[i] + ".csv"
        tableList.insert(i, table)
    for i in range(40):
        tableList.insert(tk.END, i)
    tableList.config(yscrollcommand=tableScroll.set)
    tableScroll.config(command= tableList.yview)

# GUI elements and their placement
root = tk.Tk()
root.geometry("500x300")
root.title("Saved Graphs")

tableLabel = tk.Label(text="Tables:")
tableList = tk.Listbox(width=30, height=14, activestyle="none", selectmode="extended")
tableScroll = tk.Scrollbar(root)
#tableScroll.place(relx=.37,rely=.2)
tableScroll.pack(side = tk.RIGHT, fill = tk.BOTH)
btn = tk.Button(
    text="all tables",
    command=lambda: makeAList()
)
btn.place(x=.1,y=.1)
if __name__ == "__main__":
    main()