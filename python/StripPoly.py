from shapely.geometry import *
from shapely import affinity
import Constants as c
from Enums import POITypes as e_p
from Enums import SPDataTypes as e_d
import operator
import matplotlib.pyplot as plt
import numpy as np

class StripPoly:

    def __init__(self, strip_poly, intersect_poly, farm):
        #create polygon strip
        self.polygon = strip_poly
        self.intersection = intersect_poly
        self.farm = farm
        self.left_strip = None
        self.right_strip = None
        self.data = []
        self.anchor = "none"

    def setLeftNeighbour(self, strip_poly):
        self.left_strip = strip_poly

    def setRightNeighbour(self, strip_poly):
        self.right_strip = strip_poly       

    def getArea(self):
        return self.intersection.area

    def getPerimeter(self):
        return self.intersection.perimeter

    def getStripPoly(self):
        return self.polygon

    def getIntersectionPoly(self, type=None):
        return self.intersection

    def getLeftNeighbour(self):
        return self.left_strip
        
    def getRightNeighbour(self):
        return self.right_strip

    def getDataArray(self):
        return self.data

    def addToDataArray(self, element):
        self.data.append(element)
        self.sortDataArray()

    def removeFromDataArray(self, element):
        self.data.remove(element)
        self.sortDataArray()    #likely unneded

    def setAnchor(self, anchorin):
        self.anchor = anchorin

    def sortDataArray(self, sortby='ycoord', direction='small_to_big'):
        if sortby == 'ycoord':
            if direction == 'small_to_big':
                self.data.sort(key=operator.attrgetter('y_coord'))

    def processRoadShift(self, strip_intersect_poly_in, ycoord, anchor, shiftin):
        for element in self.data:
            if anchor == 'bottom':
                if element.getYBottom() > ycoord:
                    #this is completely above the point so move it up
                    element.shift(0, shiftin)
            else:  #if anchor is top
                if element.getYTop() < ycoord:
                    #this is completely below the point so move it down
                    element.shift(0, -shiftin)

        #then process for intersections with the boundary
        for element in self.data:
            if element.getDataType() == e_d.SOLAR_ROW:
                
                #check if it is still valid
                #dont need to check for self intersections as already done
                while not strip_intersect_poly_in.contains(element.getPoly()):
                    success = element.reduceRowSize(anchor)

                    if not success:
                        #row cannot fit so remove all together
                        self.removeFromDataArray(element)
                        break




