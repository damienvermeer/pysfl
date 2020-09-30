from shapely.geometry import *
from shapely import affinity
import Constants as c
from Enums import POITypes as e_p
from Enums import SPDataTypes as e_d

class SolarRow:

    def __init__(self, x_corner, y_corner, row_width, row_height, num_modules, strip, align='bottom'):
        #create polygon strip
        if align == 'bottom':
            self.polygon = Polygon([Point(x_corner, y_corner),Point(x_corner+row_width, y_corner),Point(x_corner+row_width, y_corner+row_height), Point(x_corner, y_corner+row_height)])
        else:
            self.polygon = Polygon([Point(x_corner, y_corner),Point(x_corner+row_width, y_corner),Point(x_corner+row_width, y_corner-row_height), Point(x_corner, y_corner-row_height)])
        self.num_modules = num_modules
        self.strip = strip
        self.datatype = e_d.SOLAR_ROW
        self.y_coord = y_corner

    def getPoly(self):
        return self.polygon

    def getNumberModules(self):
        return self.num_modules

    def getStrip(self):
        return self.strip
    
    def getDataType(self):
        return self.datatype

    def getXMidpoint(self):
        return (self.polygon.bounds[0] + self.polygon.bounds[2])/2

    def getYTop(self):
        return self.polygon.bounds[3]
