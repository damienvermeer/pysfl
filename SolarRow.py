from shapely import geometry
import numpy as np
import SolarRow

class SolarRow:

    def __init__(
                self,                                     
                idchar = '_',
                settings = None,
                minx = -1, 
                miny = -1, 
                maxx = -1,
                maxy = 1,
                type = None
                ):
        """
        TODO docustring & review inputs
        """
        
        #Create box strip
        self.asset_poly = geometry.box(
                            minx, 
                            miny, 
                            maxx,
                            maxy) 
        self.type = type #TODO enum via asset?

        #TODO needs to know how many modules there are?
        #TODO how about drawing individual modules rather than rows?

    # def getNumberModules(self):
    #     return self.num_modules

    # def shift(self, x, y):
    #     self.polygon = affinity.translate(self.polygon, xoff=x, yoff=y)
    #     self.y_coord = self.polygon.bounds[1]

    # def reduceRowSize(self, anchor):
    #     #get number of modules
    #     i = self.settings['row/nmodules'].index(self.num_modules)

    #     if i == len(self.settings['row/lengths'])-1:  #cant make it any smaller
    #         return False
    #     else:
    #         if(anchor == 'bottom'):
    #             self.num_modules = self.settings['row/nmodules'][i+1]
    #             x_min = self.polygon.bounds[0]
    #             y_min = self.polygon.bounds[1]
    #             width = self.polygon.bounds[2] - self.polygon.bounds[0]
    #             height = self.settings['row/lengths'][i+1]

    #             #set polygon
    #             self.polygon = box(x_min, y_min, x_min+width, y_min+height)
    #             return True
    #         else:   #if anchor is top
    #             self.num_modules = self.settings['row/nmodules'][i+1]
    #             x_min = self.polygon.bounds[0]
    #             y_max = self.polygon.bounds[3]
    #             width = self.settings['module/height']
    #             height = self.settings['row/lengths'][i+1]

    #             #set polygon
    #             self.polygon = box(x_min, y_max, x_min+width, y_max-height)
    #             return True

