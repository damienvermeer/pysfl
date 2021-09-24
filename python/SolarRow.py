from shapely.geometry import *
from shapely import affinity
import Constants as c
from Enums import POITypes as e_p
from Enums import SPDataTypes as e_d

class SolarRow:

    def __init__(self, x_corner, y_corner, row_width, row_height, num_modules, strip, settings, align='bottom'):
        #create polygon strip
        if align == 'bottom':
            self.polygon = Polygon([Point(x_corner, y_corner),Point(x_corner+row_width, y_corner),Point(x_corner+row_width, y_corner+row_height), Point(x_corner, y_corner+row_height)])
            self.y_coord = y_corner
        else:
            self.polygon = Polygon([Point(x_corner, y_corner),Point(x_corner+row_width, y_corner),Point(x_corner+row_width, y_corner-row_height), Point(x_corner, y_corner-row_height)])
            self.y_coord = y_corner-row_height
        self.num_modules = num_modules
        self.strip = strip
        self.datatype = e_d.SOLAR_ROW
        self.settings = settings
        

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

    def getYBottom(self):
        return self.polygon.bounds[1]

    def shift(self, x, y):
        self.polygon = affinity.translate(self.polygon, xoff=x, yoff=y)
        self.y_coord = self.polygon.bounds[1]

    def reduceRowSize(self, anchor):
        #get number of modules
        i = self.settings['row/nmodules'].index(self.num_modules)

        if i == len(self.settings['row/lengths'])-1:  #cant make it any smaller
            return False
        else:
            if(anchor == 'bottom'):
                self.num_modules = self.settings['row/nmodules'][i+1]
                x_min = self.polygon.bounds[0]
                y_min = self.polygon.bounds[1]
                width = self.polygon.bounds[2] - self.polygon.bounds[0]
                height = self.settings['row/lengths'][i+1]

                #set polygon
                self.polygon = box(x_min, y_min, x_min+width, y_min+height)
                return True
            else:   #if anchor is top
                self.num_modules = self.settings['row/nmodules'][i+1]
                x_min = self.polygon.bounds[0]
                y_max = self.polygon.bounds[3]
                width = self.settings['module/height']
                height = self.settings['row/lengths'][i+1]

                #set polygon
                self.polygon = box(x_min, y_max, x_min+width, y_max-height)
                return True



        
        
