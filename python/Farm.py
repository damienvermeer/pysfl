from shapely.geometry import *
from shapely import affinity
import Constants as c
import matplotlib.pyplot as plt
import StripPoly
import SolarRow
import POI
import numpy as np
from Enums import POITypes as e_p
from Enums import SPDataTypes as e_d

class Farm:

    def __init__(self, shape_points):
        self.polygon = Polygon(shape_points)
        self.pre_setback_polygon = None
        self.strips = []
        self.rotation_point = None
        self.rotation = 0

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
        print("--|strip generator starting") if c.VERBOSE == True else False

        #calc polygon data
        poly_width = self.polygon.bounds[2] - self.polygon.bounds[0]
        poly_height = self.polygon.bounds[3] - self.polygon.bounds[1]

        #calc number of strips to make
        num_strips = int((poly_width + c.SR_POST_POST_WIDTH)/c.SR_POST_POST_WIDTH)
        print("--|# strips = " + str(num_strips+1)) if c.VERBOSE == True else False

        #iterate over strips creating each of them
        print("--|creating strips") if c.VERBOSE == True else False 
        for snum in np.arange(self.polygon.bounds[0], self.polygon.bounds[2]+c.SR_POST_POST_WIDTH, c.SR_POST_POST_WIDTH):
        #for snum in np.arange(self.polygon.bounds[0],poly_width+c.SR_POST_POST_WIDTH,c.SR_POST_POST_WIDTH):

            #create strip
            new_strip = StripPoly.StripPoly(snum, self.polygon.bounds[1], poly_height, c.SR_POST_POST_WIDTH, self.polygon, self)
            
            self.strips.append(new_strip)

            #set left neighbour
            if len(self.strips) > 1:
                new_strip.setLeftNeighbour(self.strips[-1])

        #set right neighbours
        print("--|assigning neighbours") if c.VERBOSE == True else False 
        for i,e in enumerate(self.strips[:-1]):
            e.setRightNeighbour(self.strips[i+1])

    def populateSolarRow(self, strip, intersect_poly, align='bottom'):
        
        #set anchor property in strip
        strip.anchor = align

        #process one solar row
        xypoints_to_test = []
        for point in intersect_poly.exterior.coords:
            if point not in xypoints_to_test:
                xypoints_to_test.append([strip.getStripPoly().bounds[0], point[1]])
                #uses strip's x strip offset

        #sort smallest to largest
        if align == 'bottom':
            xypoints_to_test.sort(key=lambda tup: tup[1])
        elif align == 'top':
            xypoints_to_test.sort(key=lambda tup: tup[1], reverse=True)
        else:
            raise ValueError("No valid align property passed to populateSolarRow")

        #for each point
        for point in xypoints_to_test:

            #for each row type in the acceptable list
            if align == 'bottom':
                yoffset = c.SR_END_DELTA
            else:
                yoffset = -c.SR_END_DELTA

            for count, rowtest in enumerate(c.SR_ROW_LENGTHS):

                #repeat adding rows until we run out of space
                while True:
                
                    #create new row
                    if align == 'bottom':
                        new_solar_row = SolarRow.SolarRow(point[0], point[1]+yoffset, c.SR_POST_POST_WIDTH, rowtest, c.SR_NUM_MODULES_PER_ROW[count], self, align='bottom')
                    else:
                        new_solar_row = SolarRow.SolarRow(point[0], point[1]+yoffset, c.SR_POST_POST_WIDTH, rowtest, c.SR_NUM_MODULES_PER_ROW[count], self, align='top')

                    #test if valid
                    valid_row = True

                    if not intersect_poly.contains(new_solar_row.getPoly()):
                        valid_row = False

                    #test if intersect with any other rows in strip
                    for element in strip.getDataArray():
                        if element.getDataType() == e_d.SOLAR_ROW:
                            if new_solar_row.getPoly().intersects(element.getPoly()):
                                print("---/Debug/Solar row intersected with another row ") if c.DEBUG == True else False
                                valid_row = False

                    if not valid_row:
                        break

                    #fits if get here
                    if new_solar_row not in strip.data:
                        strip.addToDataArray(new_solar_row)
                        if align == 'bottom':
                            yoffset += rowtest + c.SR_END_END_WIDTH
                        else:
                            yoffset -= rowtest + c.SR_END_END_WIDTH




    def populateSolarRowSmartAlign(self, strip, intersect_poly):
            
        #determine which edge of the intersect poly has the shallowest slope

        #first get centroid of intersect_poly
        centroidy = intersect_poly.centroid.xy[1][0]
        print("---/Centroid is = "+str(centroidy)) if c.DEBUG == True else False
        

        #get all xy values
        xypoints_to_test = []
        for point in intersect_poly.exterior.coords:
            if point not in xypoints_to_test:
                xypoints_to_test.append([strip.getStripPoly().bounds[0], point[1]])
                
            
        #calculate bottom y_vals
        b_y_vals = []
        for point in xypoints_to_test:
            if point[1] < centroidy:
                #this is on the bottom of the intersect_poly
                b_y_vals.append(point[1])

        #calculate top y_vals
        t_y_vals = []
        for point in xypoints_to_test:
            if point[1] > centroidy:
                #this is on the top of the intersect_poly
                t_y_vals.append(point[1])  

        #calculate max deltas
        delta_y_bottom = max(b_y_vals) - min(b_y_vals)
        delta_y_top = max(t_y_vals) - min(t_y_vals)


        if delta_y_bottom >= delta_y_top:
            #this means bigger slope on the bottom then the top
            self.populateSolarRow(strip, intersect_poly, align='top')
            print("---/SmartAlign selected top align") if c.DEBUG == True else False
        else:
            self.populateSolarRow(strip, intersect_poly, align='bottom')
            print("---/SmartAlign selected bottoms align") if c.DEBUG == True else False   



    def populateAllSolarRows(self):
        print("--|solar row layout generator starting") if c.VERBOSE == True else False

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
                        self.populateSolarRowSmartAlign(strip, geom)
                else:
                    self.populateSolarRowSmartAlign(strip, strip.getIntersectionPoly())

                #then sort by y_coord
                #strip.sortDataArray()
                 

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
                    if self.rotation_point == None:
                        plt.plot(*strip.getStripPoly().exterior.xy,'g',alpha=0.2)
                    else:
                        tempplot = affinity.rotate(strip.getStripPoly(), -self.rotation, origin=self.rotation_point)
                        plt.plot(*tempplot.exterior.xy,'g',alpha=0.2)
                    
                #possible to have multipolys here
                if plot_strip_ints:
                    if strip.getIntersectionPoly().geom_type == "MultiPolygon":
                        for strip_poly in strip.getIntersectionPoly():
                            if self.rotation_point == None:
                                plt.plot(*strip_poly.exterior.xy,'b')
                            else:
                                tempplot = affinity.rotate(strip_poly, -self.rotation, origin=self.rotation_point)
                                plt.plot(*tempplot.exterior.xy,'b')

                    else:
                        if not strip.getIntersectionPoly().is_empty:
                            if self.rotation_point == None:
                                plt.plot(*strip.getIntersectionPoly().exterior.xy,'b')
                            else:
                                tempplot = affinity.rotate(strip.getIntersectionPoly(), -self.rotation, origin=self.rotation_point)
                                plt.plot(*tempplot.exterior.xy,'b')
                            
                #plot datapoints          
                if plot_sf_rows:     
                    for element in strip.getDataArray():

                        #plot solar rows
                        if element.getDataType() == e_d.SOLAR_ROW:
                            if self.rotation_point == None:
                                plt.plot(*element.getPoly().exterior.xy,'r',alpha=0.9)
                            else:
                                tempplot = affinity.rotate(element.getPoly(), -self.rotation, origin=self.rotation_point)
                                plt.plot(*tempplot.exterior.xy,'r',alpha=0.9)
                        
                        #plot road nodes
                        elif element.getDataType() == e_p.ROAD_NODE:
                            if self.rotation_point == None:
                                plt.scatter(element.getCoords()[0],element.getCoords()[1],c='y',alpha=0.9)
                            else:
                                tempplot = affinity.rotate(element.getCoordsAsPoint(), -self.rotation, origin=self.rotation_point)
                                plt.scatter(*tempplot.xy,c='y',alpha=0.9)
                       
                        
                        
        #plot boundary
        if self.rotation_point == None:
            plt.plot(*self.polygon.exterior.xy,'k',linestyle='dashed')
            plt.plot(*self.pre_setback_polygon.exterior.xy,'k',linestyle='dashed')
        else:
            tempplot1 = affinity.rotate(self.polygon, -self.rotation, origin=self.rotation_point)
            plt.plot(*tempplot1.exterior.xy,'k',linestyle='dashed')
            tempplot2 = affinity.rotate(self.pre_setback_polygon, -self.rotation, origin=self.rotation_point)
            plt.plot(*tempplot2.exterior.xy,'k',linestyle='dashed')
        
        plt.gca().set_aspect('equal', adjustable='box')
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
            
    def setAzimuth(self, angle):
        if not angle == 0:
            self.rotation_point = self.polygon.centroid
            self.polygon = affinity.rotate(self.polygon, angle, origin=self.rotation_point)
            self.rotation = angle
    
    def moveCentroidToOrigin(self):
        self.polygon = affinity.translate(self.polygon, xoff=-self.polygon.centroid.xy[0][0], yoff=-self.polygon.centroid.xy[1][0])

    def getMBBRatio(self):
        return self.polygon.area / self.polygon.minimum_rotated_rectangle.area

    def addRoads(self, method='numlongrows', parameter=2):
        
        #step 1 - process and add road POI markers
        
        print("--|addding road markers") if c.VERBOSE == True else False

        if method == 'numlongrows':
            #add a POI road marker every 2nd long row
            for strip in self.strips:
                counter = 0
                if strip.anchor == 'bottom':
                    dataarray = strip.getDataArray()
                else:
                    dataarray = strip.getDataArray()[::-1]

                for element in dataarray:
                    if element.getDataType() == e_d.SOLAR_ROW:
                        #this is a solar row
                        if element.getNumberModules() == max(c.SR_NUM_MODULES_PER_ROW):
                            #this is a (max) long row
                            counter += 1
                            if counter == parameter:
                                #this is the 'parameterth' long row adjacent, add a road calc node
                                counter = 0
                                if strip.anchor == 'bottom':
                                    coords = [element.getXMidpoint(),element.getYTop()+0.001]
                                else:
                                    coords = [element.getXMidpoint(),element.getYBottom()-0.001]
                                strip.addToDataArray(POI.POI(coords))
                        else:
                            counter = 0
        elif method == 'minspace':
            raise ValueError("minspace road placement not yet implemented")
        else:
            raise ValueError("addRoads not given valid method")

        #step 2 - check there are no POI  road nodes on the end of the stip list
        for strip in self.strips:
            dataarray = strip.getDataArray()

            if len(dataarray) == 0:
                continue
            
            if dataarray[-1].getDataType() == e_p.ROAD_NODE:
                strip.removeFromDataArray(dataarray[-1])
                print("---/Debug/Removed ROAD_NODE POI from end") if c.DEBUG == True else False

            if dataarray[0].getDataType() == e_p.ROAD_NODE:
                strip.removeFromDataArray(dataarray[0])
                print("---/Debug/Removed ROAD_NODE POI from start") if c.DEBUG == True else False
                                                        
        #once we get to here, we have road markers everywhere
        #step 3 - process road markers and shift rows up/down
        yshiftcoord = 0
        for strip in self.strips:
            for poly in strip.getIntersectionPoly(type='list'): #handles multipolyon
                for element in strip.getDataArray():
                    if element.getDataType() == e_p.ROAD_NODE:
                        if not element.getProcessedFlag():
                            #this is a road node, get its y value
                            yshiftcoord = element.getCoords()[1] #get y value of POI
                            element.setAsProcessed()    #to prevent double up

                            #tell the strip to shift everything up
                            strip.processRoadShift(poly, yshiftcoord, strip.anchor, c.SR_ROADWAY_WIDTH)
                            
            
        