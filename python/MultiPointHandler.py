import Constants as c
from shapely.geometry import *
from shapely import affinity
import Enums as e
import numpy as np
import math

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
        self.poly = affinity.translate(self.poly, xoff=x, yoff=y)

    def getYTop(self):
        return self.poly.bounds[3]

    def getYBottom(self):
        return self.poly.bounds[1]

    def getNumCoords(self):
        return len(self.coords_array)

    def addCoord(self, coord, loc='end'):
        if (loc == 'end'):
            self.coords_array.append(coord)  #coord is a 2-array [x,x]
        elif (loc == 'start'):
            self.coords_array.insert(0, coord)
        else:
            raise ValueError("addCoord passed invalid location")
        #TODO fix this and setCoords seems to use different data structures?

    def setCoords(self, coords):
        self.coords_array = coords

    def updatePoly(self, buffer=0):
        if self.datatype == e.MultiPointDataTypes.RING_ROAD:
            self.poly = LinearRing(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=32, join_style=2)
        else:
            self.poly = LineString(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=32, join_style=2)

    def removeSpikes(self):
        #flag items for removal based on being too 'spiky'
        remove_list = []
        for i,elem in enumerate(self.coords_array):
            if i == 0 or i == len(self.coords_array)-1:
                continue
            else:
                delta_y1 = elem[1] - self.coords_array[i-1][1]
                delta_y2 = self.coords_array[i+1][1] - elem[1]

                if np.abs(delta_y1) > c.SPIKE_MIN and np.abs(delta_y2) > c.SPIKE_MIN:
                    remove_list.append(elem)
        
        #then remove them
        for elem in remove_list:
            self.coords_array.remove(elem)

    def getMaxSlope(self):
        #returns the maximum slope angle seen (compared to horizontal)
        max_slope = 0
        for i,elem in enumerate(self.coords_array):             

            if i == len(self.coords_array)-1:
                continue
            else:
                x1 = elem[0]
                y1 = elem[1]
                x2 = self.coords_array[i+1][0]
                y2 = self.coords_array[i+1][1]

                angle = np.abs(math.degrees(math.atan2(y2-y1, x2-x1)))
                        
                if angle > max_slope:
                    max_slope = angle

        return max_slope
        

    def extrapolate(self, i1, i2, xresolve):
        if i1 > len(self.coords_array) or i2 > len(self.coords_array):
            return None #handle out of index errors
        else:
            #valid indexes
            x1 = self.coords_array[i1][0]
            y1 = self.coords_array[i1][1]
            x2 = self.coords_array[i2][0]
            y2 = self.coords_array[i2][1]
            xdata = np.array([x1, x2])
            ydata = np.array([y1, y2])

            params = np.polyfit(xdata, ydata, 1) #linear fit

            return np.polyval(params, xresolve) #return extrapolate



                                            

