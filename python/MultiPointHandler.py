import Constants as c
from shapely.geometry import *
from shapely import affinity
import Enums as e
import numpy as np

class MultiPointHandler:

    #class to define a radial element
    #such as a road, string/array/HV cable

    def __init__(self, type_in=e.MultiPointDataTypes.RADIAL_ROAD):
        self.coords_array = []
        self.datatype = type_in
        self.poly = None

    def getDataType(self):
        return self.datatype
    
    def getPolygon(self):
        return self.poly

    def shift(self, x, y):
        self.poly = affinity.translate(self.polygon, xoff=x, yoff=y)

    def getYTop(self):
        return self.polygon.bounds[3]

    def getYBottom(self):
        return self.polygon.bounds[1]

    def getNumCoords(self):
        return len(self.coords_array)

    def addCoord(self, coord):
        self.coords_array.append(coord)  #coord is a 2-array [x,x]
        #TODO fix this and setCoords seems to use different data structures?

    def setCoords(self, coords):
        self.coords_array = coords

    def updatePoly(self, buffer=0):
        self.removeSpikes()
        if self.datatype == e.MultiPointDataTypes.RING_ROAD:
            self.poly = LinearRing(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=32, join_style=2)
        else:
            self.poly = LineString(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=32, join_style=2)

    def removeSpikes(self):
        remove_list = []
        for i,elem in enumerate(self.coords_array):
            if i == 0 or i == len(self.coords_array)-1:
                continue
            else:
                delta_y1 = elem[1] - self.coords_array[i-1][1]
                delta_y2 = self.coords_array[i+1][1] - elem[1]

                if np.abs(delta_y1) > c.SPIKE_MIN and np.abs(delta_y2) > c.SPIKE_MIN:
                    remove_list.append(elem)

        for elem in remove_list:
            self.coords_array.remove(elem)
                      

