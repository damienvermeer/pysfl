from shapely.geometry import *
from shapely import affinity
import Constants as c

class StripPoly:



    def __init__(self, x_corner, y_offset, height, intersect_poly, farm):
        #create polygon strip
        self.polygon = Polygon([Point(x_corner, 0),Point(x_corner, height+y_offset),Point(x_corner+c.SR_POST_POST_WIDTH, height+y_offset), Point(x_corner+c.SR_POST_POST_WIDTH, 0)])
        self.intersection = None
        self.farm = farm
        self.left_strip = None
        self.right_strip = None

        #calculate intersection
        try:
            self.intersection = self.polygon.intersection(intersect_poly)
            if intersection.is_empty:
                print("---/No intersection in StripPoly") if c.DEBUG == True else False
            else:
                print("---/Found intersection: " + str(intersection)) if c.DEBUG == True else False
        except:
            print("---/Error during intersect in StripPoly") if c.DEBUG == True else False

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
