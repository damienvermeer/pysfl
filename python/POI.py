import Constants as c
from Enums import POITypes as e
from shapely.geometry import *

class POI:

    #point of intrest class

    def __init__(self, coords, type_in=e.ROAD_NODE):
        self.coords = coords
        self.datatype = type_in
        self.y_coord = coords[1]
        self.processed_flag = False

    def getDataType(self):
        return self.datatype

    def getCoords(self):
        return self.coords

    def getCoordsAsPoint(self):
        return Point([self.coords[0], self.coords[1]])

    def shift(self, x, y):
        self.coords[0] += x
        self.coords[1] += y
        self.y_coord = self.coords[1]

    def getYTop(self):
        return self.coords[1]

    def getYBottom(self):
        return self.coords[1]

    def getProcessedFlag(self):
        return self.processed_flag

    def setAsProcessed(self):
        self.processed_flag = True

    def reduceRowSize(self, loc='bottom'):
        return False