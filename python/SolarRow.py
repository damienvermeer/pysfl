from shapely.geometry import *
from shapely import affinity
import Constants as c

class SolarRow:

    def __init__(self, x_corner, y_corner, row_width, row_height, num_modules, strip):
        #create polygon strip
        self.polygon = Polygon([Point(x_corner, y_corner),Point(x_corner+row_width, y_corner),Point(x_corner+row_width, y_corner+row_height), Point(x_corner, y_corner+row_height)])
        self.num_modules = num_modules
        self.strip = strip

    def getPoly(self):
        return self.polygon

    def getNumberModules(self):
        return self.num_modules

    def getStrip(self):
        return self.strip
    
