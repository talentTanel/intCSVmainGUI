import tkinter as tk
arr = []
def create_label():
    # Create a new window to input label options
    label_window = tk.Toplevel(root)
    label_window.title("Create Label")

    # Create input fields for label options
    id_label = tk.Label(label_window, text="ID:")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(label_window)
    id_entry.grid(row=0, column=1)

    text_label = tk.Label(label_window, text="Text:")
    text_label.grid(row=1, column=0)
    text_entry = tk.Entry(label_window)
    text_entry.grid(row=1, column=1)

    value_label = tk.Label(label_window, text="Value:")
    value_label.grid(row=2, column=0)
    value_entry = tk.Entry(label_window)
    value_entry.grid(row=2, column=1)

    # Create button to create label with input options
    create_button = tk.Button(label_window, text="Create", command=lambda: add_label(id_entry.get(), text_entry.get(), value_entry.get()))
    create_button.grid(row=3, column=1)

def add_label(label_id, label_text, label_value):
    # Create a new label with input options and add it to the main window
    arr.append([label_value, label_text, label_id])
    print(arr)
    new_label = tk.Label(root, text=label_text)
    new_label.pack()
    labels[label_id] = {"text": label_text, "value": label_value}

if __name__ == "__main__":
    root = tk.Tk()
    labels = {}
    create_label_button = tk.Button(root, text="Create Label", command=create_label)
    create_label_button.pack()
    root.mainloop()
