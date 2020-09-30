from shapely.geometry import *
from shapely import affinity
import Constants as c
from Enums import POITypes as e_p
from Enums import SPDataTypes as e_d
import operator

class StripPoly:

    def __init__(self, x_min, y_min, height, width, intersect_poly, farm):
        #create polygon strip
        self.polygon = box(x_min, y_min, x_min+width, y_min+height)
        #self.polygon = Polygon([Point(x_corner, intersect_poly.bounds[1]),Point(x_corner, height+y_offset),Point(x_corner+c.SR_POST_POST_WIDTH, height+y_offset), Point(x_corner+c.SR_POST_POST_WIDTH, intersect_poly.bounds[1])])
        self.intersection = None
        self.farm = farm
        self.left_strip = None
        self.right_strip = None
        self.data = []

        #calculate intersection
        try:
            self.intersection = self.polygon.intersection(intersect_poly)
            if self.intersection.is_empty:
                print("---/No intersection in StripPoly") if c.DEBUG == True else False
            else:
                print("---/Found intersection: " + str(self.intersection)) if c.DEBUG == True else False
        except:
            print("---/Non-critical error during intersect in StripPoly") if c.DEBUG == True else False

    def setLeftNeighbour(self, strip_poly):
        self.left_strip = strip_poly

    def setRightNeighbour(self, strip_poly):
        self.right_strip = strip_poly       

    def getArea(self):
        return self.polygon.area

    def getPerimeter(self):
        return self.polygon.perimeter

    def getStripPoly(self):
        return self.polygon

    def getIntersectionPoly(self):
        return self.intersection

    def getLeftNeighbour(self):
        return self.left_strip
        
    def getRightNeighbour(self):
        return self.right_strip

    def getDataArray(self):
        return self.data

    def addToDataArray(self, element):
        self.data.append(element)

    def sortDataArray(self, sortby='ycoord', direction='small_to_big'):
        if sortby == 'ycoord':
            if direction == 'small_to_big':
                self.data.sort(key=operator.attrgetter('y_coord'))
