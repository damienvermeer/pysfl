from shapely.geometry import *
from shapely import affinity
import Constants as c
import matplotlib.pyplot as plt
import StripPoly
import copy

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
        cur_strip = 0
        for snum in range(int(self.polygon.bounds[0]),int(poly_width+c.SR_POST_POST_WIDTH),c.SR_POST_POST_WIDTH):

            #screen output
            cur_strip += 1
            print("--|creating strip " + str(cur_strip) + "/" + str(num_strips)) if c.VERBOSE == True and (cur_strip % 10 == 0 or cur_strip == num_strips or cur_strip == 1) else False 

            #create strip
            new_strip = StripPoly.StripPoly(snum, self.polygon.bounds[0], poly_height, self.polygon, self)
            self.strips.append(new_strip)


    def plotFarm(self, plot_strips=False, plot_strip_ints=True, to_image=False):
        #plot to screen
        print("--|Starting to plot") if c.DEBUG == True else False
        nplot = 0

        #iterate over strips
        if plot_strips or plot_strip_ints:
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

        #plot boundary
        plt.plot(*self.polygon.exterior.xy,'k',linestyle='dashed')
        plt.plot(*self.pre_setback_polygon.exterior.xy,'k',linestyle='dashed')
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()