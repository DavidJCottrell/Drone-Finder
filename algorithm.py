import numpy as np
import matplotlib.pyplot as plt
import random
from time import perf_counter

from drones_list import L
from contains import contains

def createDrones(num):
    DroneCoords = []
    for _ in range(0, num):
        x = random.randrange(0, 1200) #Random X coordinate between 0 and 1200
        y = random.randrange(0, 700) #Random Y coordinate between 0 and 700
        RCS = L[random.randrange(0, len(L))][5] #Get a random radar cross section from the drone list
        DroneCoords.append( [[x, y], RCS] )
    return DroneCoords

def getMakeModel(RCS):
    #Linear search to find its name using its RCS
    for listDrone in L:
        if listDrone[5] == RCS:
            return [listDrone[0], listDrone[1], listDrone[5]]

def binarySearch(sortedDroneList, l, r, RCS): 
    while l <= r: 
        mid = l + (r - l)//2
        # Check if x is present at mid 
        if sortedDroneList[mid][5] == RCS:
            return [sortedDroneList[mid][0], sortedDroneList[mid][1], sortedDroneList[mid][5]]
        # If x is greater, ignore left half 
        elif sortedDroneList[mid][5] < RCS: 
            l = mid + 1
        # If x is smaller, ignore right half 
        else: 
            r = mid - 1
    # If we reach here, then the element was not present 
    return ["Not found", "Not found", -1]

def findDrones(sortedDroneList, Drones):
    # Determine if drone is within polygons and add its coordinates and name to the appropriate arrays
    for Drone in Drones:
        # coordinates inside a polygon
        if contains(AirpoirtMain, np.array(Drone[0])) or contains(AirpoirtRunway, np.array(Drone[0])):
            trueXs.append(Drone[0][0])
            trueYs.append(Drone[0][1])
            trueDroneNames.append(binarySearch(sortedDroneList, 0, len(sortedDroneList)-1, Drone[1])) #Drone[1] -> RCS
            #trueDroneNames.append(getMakeModel(Drone[1])) #Drone[1] -> RCS
        # coordinates outside a polygon
        else:
            falseXs.append(Drone[0][0])
            falseYs.append(Drone[0][1])
            falseDroneNames.append(binarySearch(sortedDroneList, 0, len(sortedDroneList)-1, Drone[1])) #Drone[1] -> RCS
            #falseDroneNames.append(getMakeModel(Drone[1])) #Drone[1] -> RCS


def showAnnotation(ind, graph, list, annotation):
    pos = graph.get_offsets()[ind["ind"][0]]
    annotation.xy = pos
    if list == "trueList":
        text = "Within airport\nDrone make: {}\nDrone model: {}\nRadar Cross Section: {}\nCoordinates: ({}, {})".format(
            trueDroneNames[int(ind["ind"])][0],
            trueDroneNames[int(ind["ind"])][1],
            trueDroneNames[int(ind["ind"])][2], 
            trueXs[int(ind["ind"])],
            trueYs[int(ind["ind"])]
        )
    else:
        text = "Outside airport\nDrone make: {}\nDrone model: {}\nRadar Cross Section: {}\nCoordinates: ({}, {})".format(
            falseDroneNames[int(ind["ind"])][0], 
            falseDroneNames[int(ind["ind"])][1], 
            falseDroneNames[int(ind["ind"])][2], 
            falseXs[int(ind["ind"])], 
            falseYs[int(ind["ind"])]
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


def showPlot(AirpoirtMain, AirpoirtRunway):
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

    scatter1 = axes.scatter(trueXs, trueYs, color='red', s=10) # Add scatter graph for drones found to be within either aiport polygon
    scatter2 = axes.scatter(falseXs, falseYs, color='blue', s=10) # Add scatter graph for drones not in either aiport polygon

    axes.plot(mainX, mainY, RunwayX, RunwayY) # Draw polygons

    annotation = axes.annotate("", xy=(0,0), xytext=(-100,20), textcoords="offset points", color=(1, 1, 1), bbox=dict(fc=(0, 0, 0, 1), ec='none', pad=0.5, boxstyle="round"), arrowprops=dict(arrowstyle="->")) # Annotation style
    annotation.set_visible(False) # Hide annoation

    figure.canvas.mpl_connect("motion_notify_event", lambda event: hover(event, figure, axes, annotation, scatter1, scatter2) ) # Listen for hover events
    plt.show() # Show plot


def timeAnalysis(sortedDroneList):
    timeList = []
    lengthList = []

    for i in range(0, 550):
        Drones = createDrones(i) # Create drones
        start_time = perf_counter()
        findDrones(sortedDroneList, Drones) # Time this
        end_time = perf_counter()
        time = 1000 * (end_time - start_time) # ms
        print("Iteration: ", i, " took: ", time, " ms")
        timeList.append(time)
        lengthList.append(i)

    plt.plot(lengthList, timeList, '--bo')
    plt.xlabel('Length of Drones list')
    plt.ylabel('Time (ms)')
    plt.show()


AirpoirtMain = np.array(( 
    [100, 650], [375, 675], [400, 600], [525, 625], [775, 575], [1050, 550], [1050, 350], [700, 200], [0, 200], [-50, 350], [25, 500], [100, 550] 
)) # Polygon for aiport

AirpoirtRunway = np.array(( 
    [-100, 150], [-175, 75], [-100, 0], [1150, 0], [1200, 75], [1125, 150] 
)) # Polygon for runway

trueXs = [] # X coordinate for coordinates inside a polygon 
trueYs = [] # Y coordinate for coordinates inside a polygon 
trueDroneNames = [] # Make, Model and RCS for coordinates inside a polygon  

falseXs = [] # X coordinate for coordinates outside a polygon 
falseYs = [] # Y coordinate for coordinates outside a polygon 
falseDroneNames = [] # Make, Model and RCS for coordinates outside a polygon  


#Drones = createDrones(30) # Create 30 drones

sortedDroneList = sorted(L, key=lambda x: x[5])
timeAnalysis(sortedDroneList)

#findDrones(sortedDroneList, Drones)
#showPlot(AirpoirtMain, AirpoirtRunway)
