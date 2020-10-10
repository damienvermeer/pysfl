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
import Enums as e 
import MultiPointHandler
import math

class Farm:

    def __init__(self, shape_points):
        self.polygon = Polygon(shape_points)
        self.pre_setback_polygon = None
        self.strips = []
        self.rotation_point = None
        self.rotation = 0
        self.mphs = []

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
        if self.polygon.boundary.geom_type == 'MultiLineString':
            return False
        else:
            self.processRoadOnBoundary(setback)
            return True

    def processRoadOnBoundary(self, setback):
        ls_boundary = self.polygon.boundary.parallel_offset(setback/2, 'left')

        #travel along boundary interpolating
        road_points = []
        for f in range(0, int(np.ceil(ls_boundary.length)) + 1):
            road_points.append(ls_boundary.interpolate(f).coords[0])
        road_points.append(road_points[0])

        #create road handler
        new_mph = MultiPointHandler.MultiPointHandler(type_in=e.MultiPointDataTypes.RING_ROAD)
        new_mph.setCoords(road_points)
        new_mph.updatePoly()
        self.mphs.append(new_mph)

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
        for snum in np.arange(self.polygon.bounds[0],self.polygon.bounds[2],c.SR_POST_POST_WIDTH):
          
            #generate strip polygon
            x_min = snum
            y_min = self.polygon.bounds[1]
            strip_poly = box(x_min, y_min, x_min+c.SR_POST_POST_WIDTH, y_min+poly_height)
            
            #calculate intersection
            strip_intersection = None
            try:
                strip_intersection = self.polygon.intersection(strip_poly)
            except Exception:
                pass

            if strip_intersection.geom_type == "MultiPolygon":
                for poly in strip_intersection:
                    new_strip = StripPoly.StripPoly(strip_poly, poly, self)
                    self.strips.append(new_strip)
            else:
                new_strip = StripPoly.StripPoly(strip_poly, strip_intersection, self)
                self.strips.append(new_strip)

            #set left neighbour
            if len(self.strips) > 1:
                new_strip.setLeftNeighbour(self.strips[-1])

        #set right neighbours
        print("--|assigning right neighbours") if c.VERBOSE == True else False 
        for i,e in enumerate(self.strips[:-1]):
            e.setRightNeighbour(self.strips[i+1])



    def populateAllSolarRows(self):
        print("--|solar row layout generator starting") if c.VERBOSE == True else False

        #check we have some strips to work on
        if len(self.strips) < 1:
            raise ValueError("!!! Fatal error - Cannot populate solar rows with no strips")
        
        #for each strip
        for stripcount, strip in enumerate(self.strips):

            print("--|processing strip " + str(stripcount+1) +"/"+str(len(self.strips))) if stripcount % 10 == 0 and c.VERBOSE == True else False 

            #check if polygon area is less than smallest row area, continue
            if c.SR_POST_POST_WIDTH*min(c.SR_ROW_LENGTHS) > strip.getIntersectionPoly().area:
                continue #too small to fit anything in

            #get all y coords of intersect poly
            self.placeSolarRow(strip)
                


    #can be bottom, top, centre or auto for alignment
    def placeSolarRow(self, strip, align='bottom'):

        #first get centroid of intersect_poly
        intersect_poly = strip.getIntersectionPoly()
        x_corner = intersect_poly.bounds[0]
        centroidy = intersect_poly.centroid.xy[1][0]

        #get largest y value below centroid
        y_minbound = -99999999999999999
        for point in intersect_poly.exterior.coords:
            if point[1] < centroidy and point[1] > y_minbound:
                y_minbound = point[1]

        #get smallest y value above centroid
        y_maxbound = 99999999999999999
        for point in intersect_poly.exterior.coords:
            if point[1] > centroidy and point[1] < y_maxbound:
                y_maxbound = point[1]

        #working space calc
        ws = y_maxbound - y_minbound

        if min(c.SR_ROW_LENGTHS) > ws:
            return False #too small to fit anything in

        #else go on to alignment

        if align == 'bottom':
            
            yoffset = c.SR_END_DELTA

            #TODO make this more flexible for different row lengths

            #test 2 long and a road
            num_2long_with_road = int(ws / (max(c.SR_ROW_LENGTHS)*2 + c.SR_END_END_WIDTH + c.SR_ROADWAY_WIDTH))
            
            #if we have at least 1 then update to the remainder
            if num_2long_with_road != 0:
                ws = ws % (max(c.SR_ROW_LENGTHS)*2 + c.SR_END_END_WIDTH + c.SR_ROADWAY_WIDTH)

            for n in range(num_2long_with_road):
                #add two new rows
                strip.addToDataArray(SolarRow.SolarRow(x_corner, y_minbound+yoffset, c.SR_POST_POST_WIDTH, max(c.SR_ROW_LENGTHS), c.SR_NUM_MODULES_PER_ROW[c.SR_ROW_LENGTHS.index(max(c.SR_ROW_LENGTHS))], self, align='bottom'))
                yoffset += max(c.SR_ROW_LENGTHS) + c.SR_END_END_WIDTH
                strip.addToDataArray(SolarRow.SolarRow(x_corner, y_minbound+yoffset, c.SR_POST_POST_WIDTH, max(c.SR_ROW_LENGTHS), c.SR_NUM_MODULES_PER_ROW[c.SR_ROW_LENGTHS.index(max(c.SR_ROW_LENGTHS))], self, align='bottom'))
                yoffset += max(c.SR_ROW_LENGTHS) + c.SR_END_END_WIDTH + c.SR_ROADWAY_WIDTH
            
            #now test single rows 
            for row_length in c.SR_ROW_LENGTHS:
                #first try with end-end width
                num_row_add = int(ws / (row_length + c.SR_END_END_WIDTH))

                #if we have at least 1 then update to the remainder
                if num_row_add != 0:
                    ws = ws % (row_length + c.SR_END_END_WIDTH)         

                for n in range(num_row_add):
                    strip.addToDataArray(SolarRow.SolarRow(x_corner, y_minbound+yoffset, c.SR_POST_POST_WIDTH, row_length, c.SR_NUM_MODULES_PER_ROW[c.SR_ROW_LENGTHS.index(row_length)], self, align='bottom'))
                    yoffset += row_length + c.SR_END_END_WIDTH

                #then retry without end-end width
                num_row_add = int(ws / (row_length))

                #if we have at least 1 then update to the remainder
                if num_row_add != 0:
                    ws = ws % (row_length)         

                for n in range(num_row_add):
                    strip.addToDataArray(SolarRow.SolarRow(x_corner, y_minbound+yoffset, c.SR_POST_POST_WIDTH, row_length, c.SR_NUM_MODULES_PER_ROW[c.SR_ROW_LENGTHS.index(row_length)], self, align='bottom'))
                    yoffset += row_length           

        else:
            raise ValueError("Not implemented anything other than \'bottom\' align yet.")






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
        #plot roads
        for mph in self.mphs:
            if self.rotation_point == None:
                plt.plot(*mph.getPolygon().exterior.xy,'y',linestyle='dashed')
                for interior in mph.getPolygon().interiors:
                    plt.plot(*interior.xy,'y',linestyle='dashed')
            else:
                tempplot = affinity.rotate(mph.getPolygon(), -self.rotation, origin=self.rotation_point)
                plt.plot(*tempplot.exterior.xy,'y',linestyle='dashed')
                for interior in tempplot.interiors:
                    plt.plot(*interior.xy,'y',linestyle='dashed')

            
                        
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
                if element.getDataType() == e.SPDataTypes.SOLAR_ROW:
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

    def addRoads(self, method='numlongrows', parameter=2, reverse=False):
        
        #TODO fix reverse implementation

        if reverse:
            stripsiter = self.strips[::-1]
        else:
            stripsiter = self.strips

        #step 1 - process and add road POI markers
        print("--|road layout starting") if c.VERBOSE == True else False

        if method == 'numlongrows':
            print("--|road layout method numlongrows") if c.VERBOSE == True else False
            #add a POI road marker every 2nd long row
            for strip in stripsiter:
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
        print("--|cleaning up excess road markers") if c.VERBOSE == True else False
        for strip in stripsiter:
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
        #step 3 - get road poi nodes within some delta (NEW_ROAD_DELTA)
        print("--|connecting road nodes") if c.VERBOSE == True else False
        for strip in stripsiter:
            for poly in strip.getIntersectionPoly(type='list'): #handles multipolyon
                for rp in strip.getDataArray():
                    if rp.getDataType() == e_p.ROAD_NODE and not rp.getProcessedFlag():
                        if rp.handler == None:
                            #create new road - defaults to radial road
                            new_mph = MultiPointHandler.MultiPointHandler()
                            new_mph.addCoord([rp.getX(),rp.getYTop()])
                            rp.handler = new_mph
                            self.mphs.append(new_mph)
                            
                        mindist = 999
                        mindistrp = None

                        if reverse:
                            neigiter = strip.getLeftNeighbour()
                        else:
                            neigiter = strip.getRightNeighbour()

                        for i, test_rp in enumerate(neigiter.getDataArray()):
                            if test_rp.getDataType() == e_p.ROAD_NODE:
                                #calculate distance from the current point
                                deltax = test_rp.getX() - rp.getX()
                                deltay = test_rp.getYTop() - rp.getYTop()
                                dist = np.sqrt(np.power(deltax,2)+np.power(deltay,2))

                                #calculate acceptable offset
                                nmod = neigiter.getDataArray()[i-1].getNumberModules()
                                prlength = c.ROAD_Y_DELTA*c.SR_ROW_LENGTHS[c.SR_NUM_MODULES_PER_ROW.index(nmod)]
                                compdist = np.sqrt(np.power(c.SR_POST_POST_WIDTH,2)+np.power(prlength,2))

                                #check for minimum angle
                                curr_angle = math.degrees(math.atan2(deltay,deltax))
                                if len(rp.handler.coords_array) > 1:
                                    prev_angle = math.degrees(math.atan2(rp.getYTop()-rp.handler.coords_array[-2][1], rp.getX()-rp.handler.coords_array[-2][0]))
                                else:
                                    prev_angle = curr_angle  

                                #find min distance rp
                                if dist <= compdist:
                                    if np.abs(prev_angle-curr_angle) < c.MAX_ROAD_DELTA_ANGLE:
                                        if dist < mindist:
                                            mindist = dist
                                            mindistrp = test_rp
                                            print("---/Debug/New min distance") if c.DEBUG == True else False
                                        else:
                                            print("---/Debug/not smaller than mindist") if c.DEBUG == True else False

                        #use the min distance rp
                        #this is a valid road point which we can
                        #build a road with rp
                        if not mindistrp == None:
                            rp.handler.addCoord([mindistrp.getX(), mindistrp.getYTop()])
                            mindistrp.handler = rp.handler
                            rp.setAsProcessed()

                        
        #step 4a - clean roads for extrapolation
        print("--|cleaning before extrapolation") if c.VERBOSE == True else False
        remove_list = []
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                if i.getNumCoords() >= 2:
                    i.removeSpikes()    #remove spikes
                    if i.getMaxSlope() > c.MAX_ROAD_DELTA_ANGLE:
                        remove_list.append(i)   #road is too steep in section
                    #else is valid
                else:
                    remove_list.append(i)   #road is too short

        for delete in remove_list:
            self.mphs.remove(delete) 

        #step 4b - perform extrapolation
        print("--|road layout extrapolating") if c.VERBOSE == True else False
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                
                #use np to polyfit
                yval = i.extrapolate(0,1,self.polygon.bounds[0])
                i.addCoord([self.polygon.bounds[0], yval],loc='start')
                
                #use np to polyfit
                length = i.getNumCoords()
                yval = i.extrapolate(length-2,length-1,self.polygon.bounds[2])
                i.addCoord([self.polygon.bounds[2], yval])   
  
        #step 5 - create road polygons
        print("--|road layout creating road polys") if c.VERBOSE == True else False 
        remove_list = []
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                if i.getNumCoords() >= 2:
                    i.removeSpikes()    #else will fail slope test normally 
                    if not i.getMaxSlope() > c.MAX_ROAD_DELTA_ANGLE:
                        i.updatePoly()
                    else:
                        remove_list.append(i)
                else:
                    remove_list.append(i)

        for delete in remove_list:
            self.mphs.remove(delete)
  
        #step 6 - offset roads TODO fix this so it works
        print("--|road layout offsetting roads & moving solar rows") if c.VERBOSE == True else False
        maxyshift = 0
        #first pass - determine max y shift
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                #check each strip
                for strip in self.strips:
                    #check if road intersects with poly
                    inttest = strip.getIntersectionPoly().intersects(i.getPolygon())
                    if inttest: #if intersect
                        cross = strip.getIntersectionPoly().intersection(i.getPolygon())
                        ywidthint = cross.bounds[3] - cross.bounds[1]   #heigh  of intersection
                        
                        if ywidthint > maxyshift:
                            maxyshift = ywidthint
        
        #second pass - actually shift
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                #process strips
                for strip in self.strips:
                    #check if road intersects with poly
                    inttest = strip.getIntersectionPoly().intersects(i.getPolygon())
                    if inttest: #if intersect
                        cross = strip.getIntersectionPoly().intersection(i.getPolygon())
                        yshiftcoord = cross.bounds[1] #min y of the intersection
                        #shift everything in strip data array u[]
                        strip.processRoadShift(strip.getIntersectionPoly(), yshiftcoord, strip.anchor, maxyshift - c.SR_END_END_WIDTH)
                
                #process each road
                for road in self.mphs:
                    if road.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                        if road is i:
                            road.shift(0,maxyshift/2)
                        else:
                            if road.getPolygon().centroid.xy[1] > i.getPolygon().centroid.xy[1]:
                                #check if road vertically above TODO fix this properly (look at strips etc)
                                road.shift(0,maxyshift - c.SR_END_END_WIDTH)

        #step 7 - delete out of bounds stuff
        remove_list = []
        for i in self.mphs: #oob mphs
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:  
                if not self.polygon.intersects(i.getPolygon()):
                    remove_list.append(i)

        for item in remove_list:    #delete
            self.mphs.remove(item)
            
 
        for strip in self.strips:   #oob road poi points
            for rp in strip.getDataArray():
                    if rp.getDataType() == e_p.ROAD_NODE:
                        if not self.polygon.contains(rp.getCoordsAsPoint()):
                            strip.removeFromDataArray(rp)

        print("--|road layout done") if c.VERBOSE == True else False
        