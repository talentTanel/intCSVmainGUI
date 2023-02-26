import tkinter as tk

def create_window():
    global root
    root = tk.Tk()

    # Create the Listbox and add items to it
    listbox = tk.Listbox(root)
    listbox.pack()
    listbox.insert(tk.END, "Item 1")
    listbox.insert(tk.END, "Item 2")
    listbox.insert(tk.END, "Item 3")

    # Bind the double-click event to the on_double_click function
    listbox.bind("<Double-Button-1>", on_double_click)

    # Start the tkinter event loop
    root.mainloop()

def on_double_click(event):
    root.destroy()

# Call the create_window function to create and display the window
create_window()