# # from shapely.geometry import *
# from shapely import affinity
# import Constants as c
# from Enums import POITypes as e_p
# from Enums import SPDataTypes as e_d
# import operator
# import matplotlib.pyplot as plt
# import numpy as np
from shapely import geometry
import numpy as np

#TODO WIP - NEW CLASS TO CLEAN

class StripPoly:

    def __init__(self, 
                minx = -1, 
                miny = -1, 
                maxx = 1, 
                maxy = 1, 
                strip_id  = -1, 
                settings  = None,
                master_poly = None
                ):
        #TODO docustring
        #TODO validation of dimensions i.e. xright>xleft etc
        #Inputs are valid, create box
        self.box_poly = geometry.box(minx, miny, maxx, maxy)
        self.strip_id = strip_id
        self.settings = settings
        self.intersect_polys = []

        #Now calculate the intersection with the master polygon (land area)
        temp_intersection = self.box_poly.intersection(master_poly)
        #Check for no intersection
        if temp_intersection is None or temp_intersection.is_empty:
            return
        #Check for multipolygon (meaning this strip has multiple sections)
        if temp_intersection.geom_type == "MultiPolygon":
            for x in list(temp_intersection.geoms):
                self.intersect_polys.append(x)
        #Else it it is a single polygon
        else:
            self.intersect_polys.append(temp_intersection)
        #TODO do we care about left and right neighbours anymore? can use index

    def add_solar_rows(self, calc_max_only=False, row_priority_list = []):
        #TODO doc string
        #If calc_max_only, we only idenfiy the maximum available space
        #We dont yet fill.
        if calc_max_only: lengths = []
        #returns the maximum length of all of its intersect poly
        for intersect_poly in self.intersect_polys:
            #Find y centroid
            centroidy = intersect_poly.centroid.xy[1][0]
            #Get a sorted list of all the y coordinates of the intersect poly
            temp_list = list(intersect_poly.exterior.coords)
            ylist = np.array(sorted([y[1] for y in temp_list]))
            #Create the masks based on gt/lt the y centroid
            ytop_mask = np.array([y > centroidy for y in ylist], dtype=np.bool)
            ybottom_mask = np.array([y < centroidy for y in ylist], dtype=np.bool)
            #Calculate the ytop (lowest upper bound) and ybottom 
            # (highest lower bound) for this intersection polygon
            ytop = min(ylist[ytop_mask])
            ybottom = max(ylist[ybottom_mask])
            if calc_max_only: 
                lengths.append(ytop-ybottom)
                continue
            #TODO continue with row allocation
        
        if calc_max_only:
            #Handle case if there are no intersection polys here
            if lengths: return max(lengths)
            else: return 0
            
















    #     #create polygon strip
    #     self.polygon = 
    #     self.intersection = intersect_poly
    #     self.farm = farm
    #     self.left_strip = None
    #     self.right_strip = None
    #     self.data = []
    #     self.anchor = "none"
    #     self.master_offset = -np.inf
    #     self.recalc = False

    # def setLeftNeighbour(self, strip_poly):
    #     self.left_strip = strip_poly

    # def setRightNeighbour(self, strip_poly):
    #     self.right_strip = strip_poly       

    # def getArea(self):
    #     return self.intersection.area

    # def getPerimeter(self):
    #     return self.intersection.perimeter

    # def getStripPoly(self):
    #     return self.polygon

    # def getIntersectionPoly(self, type=None):
    #     return self.intersection

    # def getLeftNeighbour(self):
    #     return self.left_strip
        
    # def getRightNeighbour(self):
    #     return self.right_strip

    # def getDataArray(self):
    #     return self.data

    # def addToDataArray(self, element):
    #     self.data.append(element)
    #     self.sortDataArray()

    # def removeFromDataArray(self, element):
    #     self.data.remove(element)
    #     self.sortDataArray()    #likely unneded

    # def setAnchor(self, anchorin):
    #     self.anchor = anchorin

    # def sortDataArray(self, sortby='ycoord', direction='small_to_big'):
    #     if sortby == 'ycoord':
    #         if direction == 'small_to_big':
    #             self.data.sort(key=operator.attrgetter('y_coord'))

    # def processRoadShift(self, strip_intersect_poly_in, ycoord, anchor, shiftin):
    #     for element in self.data:
    #         if anchor == 'bottom':
    #             if element.getYBottom() > ycoord:
    #                 #this is completely above the point so move it up
    #                 element.shift(0, shiftin)
    #         else:  #if anchor is top
    #             if element.getYTop() < ycoord:
    #                 #this is completely below the point so move it down
    #                 element.shift(0, -shiftin)

    #     #then process for intersections with the boundary
    #     for element in self.data:
    #         if element.getDataType() == e_d.SOLAR_ROW:
                
    #             #check if it is still valid
    #             #dont need to check for self intersections as already done
    #             while not strip_intersect_poly_in.contains(element.getPoly()):
    #                 success = element.reduceRowSize(anchor)

    #                 if not success:
    #                     #row cannot fit so remove all together
    #                     self.removeFromDataArray(element)
    #                     break




