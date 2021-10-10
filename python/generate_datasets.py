import shapefile
from shapely.geometry import *
from shapely.geometry.point import PointAdapter
from shapely.ops import *
from shapely import affinity
import matplotlib.pyplot as plt 
import numpy as np
import os

SHAPEFILE_PATH = r"C:\Users\verme\Desktop\SDM773066\solar\parcel_mp.dbf"
DBF_SCALE = 10e3
TOLERANCE = 0.1
MIN_AREA = 157e3 #approx 10MWDC
MAX_AREA = 2355e3 #approx 150MWDC
MAX_ASPECT_RATIO = 3.0 #3:1 for length to width

#load DBF file
sf = shapefile.Reader(SHAPEFILE_PATH)
shapefileid = 0

#data point info
raw_data = []
n_datapoints = 1000
output_file = r"C:\Users\verme\Desktop\outputdataset.shape"

#area scaling
area_scale = list(np.linspace(MIN_AREA,MAX_AREA,n_datapoints+1))
rotation_target = list(np.linspace(0,360,n_datapoints+1))

for shape in sf.iterShapes():

    #ui update
    os.system('cls' if os.name=='nt' else 'clear')
    shapefileid += 1
    print(f"Testing shape file id #{shapefileid}")
    print(f"# of polygons stored {len(raw_data)}")

    #check to see if we should stop
    if len(raw_data) > n_datapoints:
        break

    #generate polygon
    newpoly = Polygon(shape.points)
    
    #check max aspect ratio
    # get coordinates of polygon vertices
    x, y = newpoly.minimum_rotated_rectangle.exterior.xy
    # get length of bounding box edges
    edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
    length = max(edge_length)
    width = min(edge_length)
    if length/width > MAX_ASPECT_RATIO: continue


    #check if similar poly already stored
    #scale polygon to area of 1
    scalepoly = affinity.translate(newpoly, xoff=-newpoly.centroid.xy[0][0], yoff=-newpoly.centroid.xy[1][0])
    scalepoly = affinity.scale(scalepoly, xfact=np.sqrt(1/scalepoly.area), yfact=np.sqrt(1/scalepoly.area))
    #iterate over all stored polygons   
    distances = [] 
    match = False
    for x in raw_data[-100:]:
        xpoly = affinity.scale(x, xfact=np.sqrt(1/x.area), yfact=np.sqrt(1/x.area)) #scale to area 1
        if len(list(xpoly.exterior.coords)) != len(list(scalepoly.exterior.coords)): continue #skip if not same # points
        if len(list(xpoly.exterior.coords)) > 10: continue
        for testpoint in list(xpoly.exterior.coords):
            for newpoint in list(scalepoly.exterior.coords):
                distances.append(Point(testpoint).distance(Point(newpoint)))
                
        #sort distances from small to big
        distances = sorted(distances)
        mask = [x < TOLERANCE for x in distances]
        if sum(mask) == len(list(scalepoly.exterior.coords)):
            #this is a match
            # print(f'match to {x}')
            match = True
            # plt.plot(*xpoly.exterior.xy,'r')
            # plt.plot(*scalepoly.exterior.xy,'b')
            # plt.show()
            break #skip

    if not match:
        #scale to origin, scale to correct scale & store
        target_area = area_scale[len(raw_data)]
        newpoly = affinity.translate(newpoly, xoff=-newpoly.centroid.xy[0][0], yoff=-newpoly.centroid.xy[1][0]) #move to centroid
        newpoly = affinity.rotate(newpoly, rotation_target[len(raw_data)], origin=newpoly.centroid)
        newpoly = affinity.scale(newpoly, xfact=np.sqrt(target_area/newpoly.area), yfact=np.sqrt(target_area/newpoly.area)) #scale to 
        
        
        raw_data.append(newpoly)

for x in raw_data:
    plotpoly = affinity.scale(x, xfact=np.sqrt(1/x.area), yfact=np.sqrt(1/x.area)) #scale to 
    plt.plot(*plotpoly.exterior.xy,'k', alpha = 0.1)

plt.axis('equal')

plt.show()