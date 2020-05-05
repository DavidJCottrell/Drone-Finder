import numpy as np
import matplotlib.pyplot as plt
import random
from time import perf_counter

from drones_list import L
from contains import contains

def createDrones(num):
    DroneInfo = []
    for _ in range(0, num):
        x = random.randrange(0, 1200) #Random X coordinate between 0 and 1200
        y = random.randrange(0, 700) #Random Y coordinate between 0 and 700
        RCS = L[random.randrange(0, len(L))][5] #Get a random radar cross section from the drone list
        DroneInfo.append( [ (x, y), RCS, ["", ""], False ] )
    return DroneInfo

def getMakeModel(sortedDroneList, l, r, RCS): 
    while l <= r: 
        mid = l + (r - l)//2
        if sortedDroneList[mid][5] == RCS:
            return [sortedDroneList[mid][0], sortedDroneList[mid][1]]
        elif sortedDroneList[mid][5] < RCS: 
            l = mid + 1
        else: 
            r = mid - 1
    raise ValueError("Error: RCS not found")

# Determine if drone is within polygons and add its coordinates and name to the appropriate arrays
def findDrones(sortedDroneList, Drones):
    for Drone in Drones:
        # coordinates inside a polygon
        if contains(AirpoirtMain, np.array(Drone[0])) or contains(AirpoirtRunway, np.array(Drone[0])):
            Drone[3] = True
        # coordinates outside a polygon
        else:
            Drone[3] = False
        Drone[2] = getMakeModel(sortedDroneList, 0, len(sortedDroneList)-1, Drone[1])


def showAnnotation(ind, graph, list, annotation):
    pos = graph.get_offsets()[ind["ind"][0]]
    annotation.xy = pos
    if list == "trueList":
        text = "Within airport\nDrone make: {}\nDrone model: {}\nRadar Cross Section: {}\nCoordinates: ({}, {})".format(
            Drones[int(ind["ind"])][2][0],
            Drones[int(ind["ind"])][2][1],
            Drones[int(ind["ind"])][1],
            Drones[int(ind["ind"])][0][0],
            Drones[int(ind["ind"])][0][1]
        )
    else:
        text = "Outside airport\nDrone make: {}\nDrone model: {}\nRadar Cross Section: {}\nCoordinates: ({}, {})".format(
            Drones[int(ind["ind"])][2][0],
            Drones[int(ind["ind"])][2][1],
            Drones[int(ind["ind"])][1],
            Drones[int(ind["ind"])][0][0],
            Drones[int(ind["ind"])][0][1]
        )

    annotation.set_text(text)


def hover(event, figure, axes, annotation, scatter1, scatter2):
    # Hover event over points within scatter1
    if scatter1.contains(event)[0]:
        contains, index = scatter1.contains(event)
        # If points are very close to eachother, it combines both indexes into an array
        if contains and len(index["ind"]) == 1:
            showAnnotation(index, scatter1, "trueList", annotation)
            annotation.set_visible(True)
    
    # Hover event over points within scatter2
    elif scatter2.contains(event)[0]:
        contains, index = scatter2.contains(event)
        if contains and len(index["ind"]) == 1:
            showAnnotation(index, scatter2, "falseList", annotation)
            annotation.set_visible(True)
    
    # Hide annotation when mouse left point
    else:
        annotation.set_visible(False)
    
    # Show changes on canvas
    figure.canvas.draw_idle()


def showPlot(AirpoirtMain, AirpoirtRunway, Drones):
    # Prepare polygon data for matplotlib
    AirpoirtMain = AirpoirtMain.tolist()
    AirpoirtMain.append(AirpoirtMain[0])
    mainX, mainY = zip(*AirpoirtMain)

    AirpoirtRunway = AirpoirtRunway.tolist()
    AirpoirtRunway.append(AirpoirtRunway[0])
    RunwayX, RunwayY = zip(*AirpoirtRunway)

    # graph setup
    figure = plt.figure()
    axes = figure.add_subplot()

    insideCoords = [[], []]
    outsideCoords = [[], []]

    for Drone in Drones:
        if(Drone[3] == True):
            insideCoords[0].append(Drone[0][0])
            insideCoords[1].append(Drone[0][1])
        else:
            outsideCoords[0].append(Drone[0][0])
            outsideCoords[1].append(Drone[0][1])

    scatter1 = axes.scatter(insideCoords[0], insideCoords[1], color='red', s=10) # Add scatter graph for drones found to be within either airport polygon
    scatter2 = axes.scatter(outsideCoords[0], outsideCoords[1], color='blue', s=10) # Add scatter graph for drones not in either airport polygon

    axes.plot(mainX, mainY, RunwayX, RunwayY) # Draw polygons

    annotation = axes.annotate("", xy=(0,0), xytext=(-100,20), textcoords="offset points", color=(1, 1, 1), bbox=dict(fc=(0, 0, 0, 1), ec='none', pad=0.5, boxstyle="round"), arrowprops=dict(arrowstyle="->")) # Annotation style
    annotation.set_visible(False) # Hide annotation

    figure.canvas.mpl_connect("motion_notify_event", lambda event: hover(event, figure, axes, annotation, scatter1, scatter2) ) # Listen for hover events
    plt.show() # Show plot


def timeAnalysis(sortedDroneList):
    timeList = []
    lengthList = []
    averageTimeList = []

    #0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200
    for i in range(0, 11):
        for _ in range(0, 500):
            Drones = createDrones(i*20)

            start_time = perf_counter()
            findDrones(sortedDroneList, Drones)
            end_time = perf_counter()

            time = 1000 * (end_time - start_time)
            timeList.append(time)

        averageTimeList.append(sum(timeList) / len(timeList))
        lengthList.append(i*20)
        print("Average for", i*20, "drones is", sum(timeList) / len(timeList))
        timeList = []

    plt.plot(lengthList, averageTimeList, '--bo')
    plt.xlabel('Length of Drones list')
    plt.ylabel('Time (ms)')
    plt.show()

AirpoirtMain = np.array(( 
    [100, 650], [375, 675], [400, 600], [525, 625], [775, 575], [1050, 550], [1050, 350], [700, 200], [0, 200], [-50, 350], [25, 500], [100, 550] 
)) # Polygon for aiport

AirpoirtRunway = np.array(( 
    [-100, 150], [-175, 75], [-100, 0], [1150, 0], [1200, 75], [1125, 150] 
)) # Polygon for runway


sortedDroneList = sorted(L, key=lambda x: x[5])

#timeAnalysis(sortedDroneList)

Drones = createDrones(30) # Create 30 drones

findDrones(sortedDroneList, Drones)
    
showPlot(AirpoirtMain, AirpoirtRunway, Drones)
