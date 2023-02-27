# Checks if an minimum point is already available, if there is - displays it
def minimumPoint(pl, ts):
    minimumPointBtn = tk.Button(
        gui, 
        text="Suggest Minimum point",
        command=lambda: getminimumPoint(pl, ts)
        )
    minimumPointBtn.place(relx=.1, rely=.42)
    if minPointXY:
        global annmin, minimum
        minimumt = graph.plot(minPointXY[0], minPointXY[1], "or", label="minimum point")
        minimum = minimumt.pop(0)
        tsPlace = ts[len(ts)-1] / 8
        annmin = graph.annotate("Minimum Point", xy=(minPointXY[0], minPointXY[1]), xytext=(minPointXY[0]-tsPlace, minPointXY[1]+200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
        canvas.draw()

# Finds the lowest pressure in variable and that is the minimum point. Displays it on the graph
def getminimumPoint(pl, ts):
    minPl = min(pl)
    minTs = ts[pl.index(minPl)]
    
    global annmin, minimum, minPointXY
    minimumt = graph.plot(minTs, minPl, "or", label="minimum point")
    minimum = minimumt.pop(0)
    tsPlace = ts[len(ts)-1] / 8
    annmin = graph.annotate("Minimum Point", xy=(minTs, minPl), xytext=(minTs-tsPlace, minPl+200), color="green", arrowprops= dict(facecolor="green", headwidth=8))
    canvas.draw()
    minPointXY = [minTs, minPl]