import tkinter as tk

gui = tk.Tk()

lblScenarioText = tk.Label(gui, text="test222", font=("Arial",14))
lblScenarioText.place(relx=.5,rely=.5)

def getshit():
    print (lblScenarioText.cget("text"))


getshit()
gui.mainloop()