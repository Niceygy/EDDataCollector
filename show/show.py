import matplotlib.pyplot as plt
import datetime

with open("mpm.txt", "r") as f:
    data = f.read()
    lines = data.splitlines()
    plotarr = []
    for line in lines:
        count, time = line.split(",")
        plotarr.append([int(count), datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f').timestamp()])
    
    plt.plot([x[1] for x in plotarr], [x[0] for x in plotarr])
    print("save")
    plt.savefig("plot.png")
    f.close()