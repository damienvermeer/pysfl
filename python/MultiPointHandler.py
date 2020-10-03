import Constants as c
from shapely.geometry import *
from shapely import affinity
import Enums as e

class MultiPointHandler:

    #class to define a radial element
    #such as a road, string/array/HV cable

    def __init__(self, coords_array, type_in=e.MultiPointDataTypes.RADIAL_ROAD):
        self.coords_array = coords_array
        self.datatype = type_in
        self.poly = None

    def getDataType(self):
        return self.datatype
    
    def getPolygon(self):
        return self.poly

    def shift(self, x, y):
        self.poly = affinity.translate(self.polygon, xoff=x, yoff=y)

    def getYTop(self):
        return self.coords[1]

    def getYBottom(self):
        return self.coords[1]

    def updatePoly(self, buffer=0):
        if self.datatype == e.MultiPointDataTypes.RING_ROAD:
            self.poly = LinearRing(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=16, join_style=2)
        else:
            self.poly = LineString(self.coords_array).buffer(c.SR_ROADWAY_WIDTH/2, resolution=16, join_style=2)

                            

