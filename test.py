import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons

def plot():
    global plots
    t = [0, 1, 2, 3, 4]
    s1 = [0, 1, 0, 1, 0]
    s2 = [1, 0, 1, 0, 1]
    s3 = [0, 0, 1, 1, 0]

    lPlot, = graph.plot(t, s1, "-r", label="Left") 
    cPlot, = graph.plot(t, s2, "-b", label="Center")
    rPlot, = graph.plot(t, s3, "-k", label="Right")
    plots = lPlot, cPlot, rPlot
	
fig, graph = plt.subplots()
plot()

rax = plt.axes([0.05, 0.4, 0.1, 0.15], facecolor='gray', visible=False)
check = CheckButtons(rax, ('Hide left', 'Hide center', 'Hide right'), (True, True, True))

def show_rax():
    rax.set_visible(True)
    plt.draw()

def func(label):
    if label == 'Hide left':
        plots[0].set_visible(not plots[0].get_visible())
    elif label == 'Hide center':
        plots[1].set_visible(not plots[1].get_visible())
    elif label == 'Hide right':
        plots[2].set_visible(not plots[2].get_visible())
    plt.draw()

check.on_clicked(func)

show_rax()
plt.show()
