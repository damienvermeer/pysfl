from shapely.geometry import *
from shapely import affinity
import Constants as c
import matplotlib.pyplot as plt
import StripPoly
import SolarRow
import numpy as np

class Farm:

    def __init__(self, shape_points):
        self.polygon = Polygon(shape_points)
        self.pre_setback_polygon = None
        self.strips = []

    def scaleFarmBoundary(self, scale):
        self.polygon = affinity.scale(self.polygon, xfact=scale, yfact=scale)
        
    def translateFarmBoundaryToOrigin(self):
        self.polygon = affinity.translate(self.polygon, xoff=-self.polygon.bounds[0], yoff=-self.polygon.bounds[1])

    def getArea(self):
        return self.polygon.area

    def getPerimeter(self):
        return self.polygon.perimeter

    def setbackFarmBoundary(self, setback):
        self.pre_setback_polygon = self.polygon #back this up
        self.polygon = self.polygon.buffer(-setback)

    def getBoundaryPoly(self):
        return self.polygon

    def getPreSetbackPoly(self):
        return self.pre_setback_polygon

    def createStrips(self):

        #create strips as an array of StripPolys
        print("--stip generator starting") if c.VERBOSE == True else False

        #calc polygon data
        poly_width = self.polygon.bounds[2] - self.polygon.bounds[0]
        poly_height = self.polygon.bounds[3] - self.polygon.bounds[1]

        #calc number of strips to make
        num_strips = int((poly_width + c.SR_POST_POST_WIDTH)/c.SR_POST_POST_WIDTH)
        print("--|# Strips = " + str(num_strips)) if c.VERBOSE == True else False

        #iterate over strips creating each of them
        print("--|creating strips") if c.VERBOSE == True else False 
        for snum in np.arange(self.polygon.bounds[0],poly_width+c.SR_POST_POST_WIDTH,c.SR_POST_POST_WIDTH):

            #create strip
            new_strip = StripPoly.StripPoly(snum, self.polygon.bounds[0], poly_height, self.polygon, self)
            self.strips.append(new_strip)

            #set left neighbour
            if len(self.strips) > 1:
                new_strip.setLeftNeighbour(self.strips[-1])

        #set right neighbours
        print("--|assigning neighbours") if c.VERBOSE == True else False 
        for i,e in enumerate(self.strips[:-1]):
            e.setRightNeighbour(self.strips[i+1])

    def populateSolarRow(self, strip, intersect_poly):
        
        #process one solar row
        xypoints_to_test = []
        for point in intersect_poly.exterior.coords:
            if point not in xypoints_to_test:
                xypoints_to_test.append([strip.getStripPoly().bounds[0], point[1]])
                #uses strip's x strip offset

        #sort smallest to largest
        xypoints_to_test.sort(key=lambda tup: tup[1])

        #for each point
        for point in xypoints_to_test:

            #for each row type in the acceptable list
            yoffset = c.SR_END_DELTA
            for count, rowtest in enumerate(c.SR_ROW_LENGTHS):

                #repeat adding rows until we run out of space
                while True:
                
                    #create new row
                    new_solar_row = SolarRow.SolarRow(point[0], point[1]+yoffset, c.SR_POST_POST_WIDTH, rowtest, c.SR_NUM_MODULES_PER_ROW[count], self)

                    #test if fits
                    if not intersect_poly.contains(new_solar_row.getPoly()):
                        break

                    #fits if get here
                    if new_solar_row not in strip.data:
                        strip.data.append(new_solar_row)
                        yoffset += rowtest + c.SR_END_END_WIDTH


    def populateAllSolarRows(self):
        print("--|starting to populate solar rows") if c.VERBOSE == True else False 
        
        #check we have some strips to work on
        if len(self.strips) < 1:
            raise ValueError("!!! Fatal error - Cannot populate solar rows with no strips")
        else:
            #for each strip
            for stripcount, strip in enumerate(self.strips):

                print("--|processing strip " + str(stripcount+1) +"/"+str(len(self.strips))) if stripcount % 10 == 0 and c.VERBOSE == True else False 

                #check if polygon area is less than smallest row area, continue
                if c.SR_POST_POST_WIDTH*min(c.SR_ROW_LENGTHS) > strip.getIntersectionPoly().area:
                    continue #too small to fit anything in

                #get all y coords of intersect poly
                if strip.getIntersectionPoly().geom_type == "MultiPolygon":
                    for geom in strip.getIntersectionPoly():
                        self.populateSolarRow(strip, geom)
                else:
                    self.populateSolarRow(strip, strip.getIntersectionPoly())
                 

    def plotFarm(self, plot_strips=False, plot_strip_ints=True, to_image=False, plot_sf_rows=True):
        #plot to screen
        print("--|Starting to plot") if c.DEBUG == True else False
        nplot = 0

        #iterate over strips
        if plot_strips or plot_strip_ints or plot_sf_rows:
            for strip in self.strips:
                if c.VERBOSE:
                    nplot += 1
                    print("--|Plotting "+str(nplot)+"/"+str(len(self.strips))) if nplot % 10 == 0 else False
                
                if plot_strips:
                    plt.plot(*strip.getStripPoly().exterior.xy,'g',alpha=0.2)

                #possible to have multipolys here
                if plot_strip_ints:
                    if strip.getIntersectionPoly().geom_type == "MultiPolygon":
                        for strip_poly in strip.getIntersectionPoly():
                            plt.plot(*strip_poly.exterior.xy,'b')
                    else:
                        if not strip.getIntersectionPoly().is_empty:
                            plt.plot(*strip.getIntersectionPoly().exterior.xy,'b')

                #plot rows          
                if plot_sf_rows:     
                    for element in strip.getDataArray():
                        #todo check if row
                        plt.plot(*element.getPoly().exterior.xy,'r',alpha=0.9)

        #plot boundary
        plt.plot(*self.polygon.exterior.xy,'k',linestyle='dashed')
        plt.plot(*self.pre_setback_polygon.exterior.xy,'k',linestyle='dashed')
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()


    def getModuleNumber(self):
    #returns the number of solar modules in the farm
        num_modules = 0
        for strip in self.strips:
            for element in strip.data:
                #todo check is solar row
                num_modules += element.getNumberModules()

        return num_modules

    def printModuleNumber(self):
        print("-Number of modules = " + str(self.getModuleNumber()))
            
