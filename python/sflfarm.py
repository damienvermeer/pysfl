from os import set_inheritable
from shapely.geometry import *
from shapely.geometry.point import PointAdapter
from shapely.ops import *
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
import copy

class Farm:

    def __init__(self, shape_points, settings):
        self.polygon = Polygon(shape_points)
        self.settings = settings
        self.pre_setback_polygon = None
        self.strips = []
        self.rotation_point = None
        self.rotation = 0
        self.mphs = []
        self.next_road_id = 0
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

    def deleteDuplicates(self):   
        #temporary workaround - the layout shouldnt create dupes anyway! 
        for strip in self.strips:
            for element in strip.getDataArray():
                if element.getDataType() == e_d.SOLAR_ROW:
                    for elm in strip.getDataArray():
                        if elm.getDataType() == e_d.SOLAR_ROW and elm != element:
                            intersect = not elm.getPoly().intersection(element.getPoly()).is_empty
                            if intersect: #means a duplicate
                                strip.removeFromDataArray(elm)        


    def processRoadOnBoundary(self, setback):
        ls_boundary = self.polygon.boundary.parallel_offset(setback/2, 'left')

        #travel along boundary interpolating
        road_points = []
        for f in range(0, int(np.ceil(ls_boundary.length)) + 1):
            road_points.append(ls_boundary.interpolate(f).coords[0])
        road_points.append(road_points[0])

        #create road handler
        new_mph = MultiPointHandler.MultiPointHandler(self.settings, type_in=e.MultiPointDataTypes.RING_ROAD)
        new_mph.setCoords(road_points)
        new_mph.updatePoly()
        self.mphs.append(new_mph)

    def getBoundaryPoly(self):
        return self.polygon

    def getPreSetbackPoly(self):
        return self.pre_setback_polygon

    def createStrips(self):

        #create strips as an array of StripPolys
        print("--|strip generator starting") if self.settings['debug'] == True else False

        #calc polygon data
        if len(self.polygon.bounds) < 2: return
        poly_width = self.polygon.bounds[2] - self.polygon.bounds[0]
        poly_height = self.polygon.bounds[3] - self.polygon.bounds[1]

        #calc number of strips to make
        num_strips = int(poly_width/self.settings['layout/post2post'])
        print("--|# strips = " + str(num_strips+1)) if self.settings['debug'] == True else False

        #iterate over strips creating each of them
        print("--|creating strips") if self.settings['debug'] == True else False
        # print(np.linspace(self.polygon.bounds[0], num_strips*self.settings['layout/post2post'], num=num_strips))
        
        x_min = self.polygon.bounds[0] + (self.settings['layout/post2post']/2)
        if 'general/row/setback/target' in self.settings:
            x_min += self.settings['general/row/setback/target']

        while True:
            #generate strip polygon
            y_min = self.polygon.bounds[1]
            strip_poly = box(x_min, y_min, x_min+self.settings['module/height'], y_min+poly_height)
            
            x_min += self.settings['layout/post2post']

            if x_min > self.polygon.bounds[2]:
                break

            #calculate intersection
            strip_intersection = None
            try:
                strip_intersection = self.polygon.intersection(strip_poly)
            except Exception:
                pass

            if strip_intersection is None or strip_intersection.is_empty:
                continue
            
            if strip_intersection.geom_type == "MultiPolygon":
                for poly in strip_intersection:
                    new_strip = StripPoly.StripPoly(strip_poly, poly, self)
                    new_strip.setLeftNeighbour(self.strips[-1]) if len(self.strips) > 1 else False
                    self.strips.append(new_strip)
            elif strip_intersection.geom_type == "Polygon":
                new_strip = StripPoly.StripPoly(strip_poly, strip_intersection, self)
                new_strip.setLeftNeighbour(self.strips[-1]) if len(self.strips) > 1 else False
                self.strips.append(new_strip)
                                

        #set right neighbours
        print("--|assigning right neighbours") if self.settings['debug'] == True else False 
        for i,e in enumerate(self.strips[:-1]):
            e.setRightNeighbour(self.strips[i+1])


                       










    def populateAllSolarRows(self):
        print("--|solar row layout generator starting") if self.settings['debug'] == True else False

        #check we have some strips to work on
        if len(self.strips) < 1:
            return
            # raise ValueError("!!! Fatal error - Cannot populate solar rows with no strips")
        

        firstpass = True
        while True:
            #enter repeat loop

            #1 - loop over each strip to check if we need to draw_road

            #for each strip
            draw_road = False
            for stripcount, strip in enumerate(self.strips):

                print("--|processing strip " + str(stripcount+1) +"/"+str(len(self.strips))) if stripcount % 10 == 0 and self.settings['debug'] == True else False 

                #check if polygon area is less than smallest row area, continue
                # if self.settings['layout/post2post']*min(self.settings['row/lengths']) > strip.getIntersectionPoly().area:
                #     continue #too small to fit anything in

                #draw solar row, returns True if need to put a road node down
                if strip.recalc or firstpass:
                    strip.recalc = False
                    if self.placeSolarRow(strip, self.next_road_id):
                        draw_road = True
                        
            
            firstpass = False
            
            if not draw_road:
                break
            else:
                #need to process roads

                #create new road
                new_mph = MultiPointHandler.MultiPointHandler(self.settings) #defaults to non-radial road
                self.mphs.append(new_mph)

                #process roads from midpoint
                left_strip_list = self.strips[len(self.strips)//2:] #middle to left
                right_strip_list = self.strips[:len(self.strips)//2][::-1] #middle to right
                self.processRoads(left_strip_list, self.next_road_id, new_mph)
                self.processRoads(right_strip_list, self.next_road_id, new_mph)
                self.next_road_id += 1

                #create the road mph
                new_mph.sortByX()
                self.extrapolateRoads()
                new_mph.updatePoly()
                    

                    
                #check for clashes with solar rows
                for strip in self.strips:
                    for element in strip.getDataArray():
                        if element.getDataType() == e_d.SOLAR_ROW:
                            while not element.getPoly().intersection(self.mphs[-1].getPolygon()).is_empty:
                                #remove everything with y above this element
                                #this is because they arent being moved with this strip
                                #so will cause duplicates
                                for elm in strip.getDataArray():
                                    if elm.getDataType() == e_d.SOLAR_ROW:
                                        if elm.getYTop() > element.getYTop():
                                            strip.removeFromDataArray(elm)
                                
                                if not element.reduceRowSize(strip.anchor):
                                    #no smaller sizes so delete this element
                                    strip.removeFromDataArray(element)

                                    #and finally break
                                    break

                #then calculate strips again based on strips
                for strip in self.strips:
                    strip_intersection = strip.getIntersectionPoly().intersection(self.mphs[-1].getPolygon())
                    if strip_intersection is None or strip_intersection.is_empty:
                        continue
                    else:
                        #remove everything with y above this element
                        #this is because they arent being moved with this strip
                        #so will cause duplicates
                        for elm in strip.getDataArray():
                            if elm.getDataType() == e_d.SOLAR_ROW:
                                if elm.getYTop() > strip_intersection.bounds[3]:
                                    strip.removeFromDataArray(elm)
                        
                        strip.master_offset = strip_intersection.bounds[3]
                        strip.recalc = True


                
              


                


    #returns True if creates a road node
    #returns False if no road node created
    def placeSolarRow(self, strip, id, align='bottom'):

        #first get centroid of intersect_poly
        intersect_poly = strip.getIntersectionPoly()
        x_corner = intersect_poly.bounds[0]
        centroidy = intersect_poly.centroid.xy[1][0]

        #get largest y value below centroid
        y_minbound = -np.inf
        for point in intersect_poly.exterior.coords:
            if point[1] < centroidy and point[1] > y_minbound:
                y_minbound = point[1]

        #check for master offset
        y_minbound = max(y_minbound, strip.master_offset)

        #get smallest y value above centroid
        y_maxbound = np.inf
        for point in intersect_poly.exterior.coords:
            if point[1] > centroidy and point[1] < y_maxbound:
                y_maxbound = point[1]

        #working space calc
        ws = y_maxbound - y_minbound

        if min(self.settings['row/lengths']) > ws:
            return False #too small to fit anything in

        #else go on to alignment

        if align == 'bottom':
            
            yoffset = self.settings['layout/endrowspace']

            strip.setAnchor(align)

            #TODO make this more flexible for different row lengths
            
            #check if first row is 1long flag set to true
            if c.FIRST_ROW_1LONG_ROAD and len(strip.data) == 0:
                
                #test 1 long and a road
                num_1long_with_road = int(ws / (max(self.settings['row/lengths']) + self.settings['layout/endrowspace'] + self.settings['roads/internal/clearwidth']))
                    
                #if we have at least 1 then update to the remainder
                if num_1long_with_road != 0:
                    ws = ws % (max(self.settings['row/lengths']) + self.settings['layout/endrowspace'] + self.settings['roads/internal/clearwidth'])
                
                #add row and road
                new_row = SolarRow.SolarRow(x_corner, y_minbound+yoffset, self.settings['module/height'], max(self.settings['row/lengths']), self.settings['row/nmodules'][self.settings['row/lengths'].index(max(self.settings['row/lengths']))], self, settings=self.settings, align='bottom', )
                
                while not new_row.getPoly().within(self.polygon):
                    if not new_row.reduceRowSize(strip.anchor):
                        break         

                strip.addToDataArray(new_row)
                yoffset += max(self.settings['row/lengths']) + self.settings['layout/endrowspace']
                
                #process road point
                strip.addToDataArray(POI.POI([new_row.getXMidpoint(), new_row.getYTop() + self.settings['roads/internal/clearwidth']/2 + self.settings['roads/internal/sep/road2rows']], self.next_road_id))
                yoffset += self.settings['roads/internal/clearwidth']
                return True
                    
                    

            #test 2 long and a road
            num_2long_with_road = int(ws / (max(self.settings['row/lengths'])*2 + self.settings['layout/endrowspace'] + self.settings['roads/internal/clearwidth']))
            
            #if we have at least 1 then update to the remainder
            if num_2long_with_road != 0:
                ws = ws % (max(self.settings['row/lengths'])*2 + self.settings['layout/endrowspace'] + self.settings['roads/internal/clearwidth'])

            for _ in range(num_2long_with_road):
                #add two new rows 
                for n2 in [0,1]:
                    new_row = SolarRow.SolarRow(x_corner, y_minbound+yoffset, self.settings['module/height'], max(self.settings['row/lengths']), self.settings['row/nmodules'][self.settings['row/lengths'].index(max(self.settings['row/lengths']))], self, self.settings, align='bottom')
                    
                    while not new_row.getPoly().within(self.polygon):
                        if not new_row.reduceRowSize(strip.anchor):
                            break         

                    strip.addToDataArray(new_row)
                    yoffset += max(self.settings['row/lengths']) + self.settings['layout/endrowspace']
                    if n2 == 1:
                        #process road point
                        strip.addToDataArray(POI.POI([new_row.getXMidpoint(), new_row.getYTop() + self.settings['roads/internal/clearwidth']/2 + self.settings['roads/internal/sep/road2rows']], self.next_road_id))
                        yoffset += self.settings['roads/internal/clearwidth']
                        return True
                        

            #now test single rows 
            for row_length in self.settings['row/lengths']:
                #first try with end-end width
                num_row_add = int(ws / (row_length + self.settings['layout/endrowspace']))

                #if we have at least 1 then update to the remainder
                if num_row_add != 0:
                    ws = ws % (row_length + self.settings['layout/endrowspace'])         

                for n in range(num_row_add):
                    new_row = SolarRow.SolarRow(x_corner, y_minbound+yoffset, self.settings['module/height'], row_length, self.settings['row/nmodules'][self.settings['row/lengths'].index(row_length)], self, self.settings, align='bottom')
                                      
                    while not new_row.getPoly().within(self.polygon):
                        if not new_row.reduceRowSize(strip.anchor):
                            break           
                    
                    strip.addToDataArray(new_row)
                    yoffset += row_length + self.settings['layout/endrowspace']

                #then retry without end-end width
                num_row_add = int(ws / (row_length))

                #if we have at least 1 then update to the remainder
                if num_row_add != 0:
                    ws = ws % (row_length)         

                for n in range(num_row_add):
                    new_row = SolarRow.SolarRow(x_corner, y_minbound+yoffset, self.settings['module/height'], row_length, self.settings['row/nmodules'][self.settings['row/lengths'].index(row_length)], self, self.settings, align='bottom')
                                      
                    while not new_row.getPoly().within(self.polygon):
                        if not new_row.reduceRowSize(strip.anchor):
                            break         

                    strip.addToDataArray(new_row)
                    yoffset += row_length
        else:
            raise ValueError("Not implemented anything other than \'bottom\' align yet.")






    def plotFarm(self, id, plot_strips=False, plot_strip_ints=True, to_image=False, plot_sf_rows=True, filesuffix=""):
        plt.rcParams['axes.linewidth'] = .2
        plt.rcParams['lines.linewidth'] = .2
        plt.rcParams['patch.linewidth'] = .2

        #plot to screen
        print("--|Starting to plot") if c.DEBUG == True else False
        nplot = 0

        #iterate over strips
        if plot_strips or plot_strip_ints or plot_sf_rows:
            for strip in self.strips:
                if self.settings['debug']:
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

                        # plot solar rows
                        if element.getDataType() == e_d.SOLAR_ROW:
                            if self.rotation_point == None:
                                plt.fill(*element.getPoly().exterior.xy,'orange',alpha=0.75)
                            else:
                                tempplot = affinity.rotate(element.getPoly(), -self.rotation, origin=self.rotation_point)
                                plt.fill(*tempplot.exterior.xy,'orange',alpha=0.75)
                        
                        #DEBUG only plots duplicates
                        if element.getDataType() == e_d.SOLAR_ROW:
                            plot = False
                            # for sp in self.strips:
                            for elm in strip.getDataArray():
                                    if elm.getDataType() == e_d.SOLAR_ROW and elm != element:
                                        plot = not elm.getPoly().intersection(element.getPoly()).is_empty
                            if plot:
                                if self.rotation_point == None:
                                    plt.plot(*element.getPoly().exterior.xy,'r',alpha=1)
                                else:
                                    tempplot = affinity.rotate(element.getPoly(), -self.rotation, origin=self.rotation_point)
                                    plt.plot(*tempplot.exterior.xy,'r',alpha=1)
                     
                    for element in strip.getDataArray():

                        # plot solar rows
                        if element.getDataType() == e_d.SOLAR_ROW:
                            if self.rotation_point == None:
                                plt.fill(*element.getPoly().exterior.xy,'orange',alpha=0.75)
                            else:
                                tempplot = affinity.rotate(element.getPoly(), -self.rotation, origin=self.rotation_point)
                                plt.fill(*tempplot.exterior.xy,'orange',alpha=0.75)
            
            
                                             
            # point_list = []            
            # print("--|Generating mmr for inverters") if c.DEBUG == True else False   
            
            # mmrs = ['start'] 
            # loopnum = 0
            
            # for cur_mmr in mmrs:
            #     if cur_mmr == 'start':
            #         #first loop
            #         for strip in self.strips:
            #             for element in strip.getDataArray():
            #                 if element.getDataType() == e_d.SOLAR_ROW:
            #                     ytop, ybottom = [element.getYTop(), element.getYBottom()]
            #                     # if self.rotation_point == None:
            #                     #     plt.scatter(element.getXMidpoint(),ytop,c='r',alpha=0.9)
            #                     #     plt.scatter(element.getXMidpoint(),ybottom,c='r',alpha=0.9)
            #                     # else:
            #                     #     tempplot1 = affinity.rotate(Point([element.getXMidpoint(), ytop]), -self.rotation, origin=self.rotation_point)
            #                     #     tempplot2 = affinity.rotate(Point([element.getXMidpoint(), ybottom]), -self.rotation, origin=self.rotation_point)
            #                     #     plt.scatter(*tempplot1.xy,c='r',alpha=0.9)
            #                     #     plt.scatter(*tempplot2.xy,c='r',alpha=0.9)

            #                     xmid = element.getXMidpoint()
            #                     point_list.append((xmid,ytop))
            #                     point_list.append((xmid,ybottom))
                    
            #         #generate mmr
            #         mrr = MultiPoint(point_list).minimum_rotated_rectangle
                    
            #         #plot mmr
            #         # if self.rotation_point == None:
            #         #     plt.plot(*mrr.exterior.xy,'b',alpha=0.75)
            #         # else:
            #         #     tempplot = affinity.rotate(mrr, -self.rotation, origin=self.rotation_point)
            #         #     plt.plot(*tempplot.exterior.xy,'b',alpha=0.75)
                    
            #         #split mmr on longest side
            #         sidecalc = []
            #         extcoords = list(mrr.exterior.coords)
            #         for i,_ in enumerate(extcoords[:-1]):
            #             midpoint = LineString([extcoords[i],extcoords[i+1]]).interpolate(0.5, normalized=True)
            #             sidecalc.append([LineString([extcoords[i],extcoords[i+1]]).length,midpoint])
                    
            #         #sort by length, then disregard the first two (these are the diagonals)
            #         sidecalc.sort(key=lambda x: x[0], reverse=True)
            #         print(sidecalc)
                            
            #         #plot green and red dots for now. green = line to split
            #         # for i,x in enumerate(sidecalc):
            #         #     x = x[1]
            #         #     col = 'r' if i < 2 else 'g'
            #         #     if self.rotation_point == None:
            #         #         plt.scatter(x,ytop,c=col,alpha=0.9)
            #         #     else:
            #         #         tempplot1 = affinity.rotate(Point(x), -self.rotation, origin=self.rotation_point)
            #         #         plt.scatter(*tempplot1.xy,c=col,alpha=0.9)
                
            #         #create line between 'green dots'
            #         spliceline_pointslist = []
            #         for x in sidecalc[0:2]: spliceline_pointslist.append(x[1])
            #         spliceline = LineString(spliceline_pointslist) #first two points
                    
            #         # if self.rotation_point == None:
            #         #     plt.scatter(*spliceline.xy,c='k',alpha=0.9,linewidths=5)
            #         # else:
            #         #     tempplot1 = affinity.rotate(spliceline, -self.rotation, origin=self.rotation_point)
            #         #     plt.scatter(*tempplot1.xy,c='k',alpha=0.9,linewidths=5)
                    
            #         left,right = split(mrr,spliceline)
            #         for x in [left,right]:
            #             if self.rotation_point == None:
            #                 plt.plot(*x.exterior.xy,'g',alpha=0.75)
            #             else:
            #                 tempplot = affinity.rotate(x, -self.rotation, origin=self.rotation_point)
            #                 plt.plot(*tempplot.exterior.xy,'g',alpha=0.75)
                            
            #         mmrs.append(left)
            #         mmrs.append(right)
            #     else:
            #         #second loop
            #         point_list = []
            #         del mrr
            #         del spliceline
            #         for strip in self.strips:
            #             for element in strip.getDataArray():
            #                 if element.getDataType() == e_d.SOLAR_ROW:
            #                     ytop, ybottom = [element.getYTop(), element.getYBottom()]
            #                     xmid = element.getXMidpoint()
                                
            #                     point1 = Point((xmid,ytop))
            #                     if cur_mmr.contains(point1) or cur_mmr.intersects(point1):
            #                         point_list.append(point1)
                                
            #                     point2 = Point((xmid,ybottom))
            #                     if cur_mmr.contains(point2) or cur_mmr.intersects(point2):
            #                         point_list.append(point2)
                                
            #         #generate mmr
            #         mrr = MultiPoint(point_list).minimum_rotated_rectangle
                    
            #         # #plot mmr
            #         # if self.rotation_point == None:
            #         #     plt.plot(*mrr.exterior.xy,'k',alpha=0.75, linewidth=2)
            #         # else:
            #         #     tempplot = affinity.rotate(mrr, -self.rotation, origin=self.rotation_point)
            #         #     plt.plot(*tempplot.exterior.xy,'k',alpha=0.75, linewidth=2)
                    
            #         #split mmr on longest side
            #         sidecalc = []
            #         extcoords = list(mrr.exterior.coords)
            #         for i,_ in enumerate(extcoords[:-1]):
            #             midpoint = LineString([extcoords[i],extcoords[i+1]]).interpolate(0.5, normalized=True)
            #             sidecalc.append([LineString([extcoords[i],extcoords[i+1]]).length,midpoint])
                    
            #         #sort by length, then disregard the first two (these are the diagonals)
            #         sidecalc.sort(key=lambda x: x[0], reverse=True)
            #         print(sidecalc)
                            
            #         #plot green and red dots for now. green = line to split
            #         # for i,x in enumerate(sidecalc):
            #         #     x = x[1]
            #         #     col = 'r' if i < 2 else 'g'
            #         #     if self.rotation_point == None:
            #         #         plt.scatter(x,ytop,c=col,alpha=0.9)
            #         #     else:
            #         #         tempplot1 = affinity.rotate(Point(x), -self.rotation, origin=self.rotation_point)
            #         #         plt.scatter(*tempplot1.xy,c=col,alpha=0.9)
                
                    
                
            #         #create line between 'green dots'
            #         spliceline_pointslist = []
            #         for x in sidecalc[0:2]: spliceline_pointslist.append(x[1])
            #         spliceline = LineString(spliceline_pointslist) #first two points                  

            #         # if self.rotation_point == None:
            #         #     plt.scatter(*spliceline.xy,c='b',alpha=0.9,linewidths=0.5)
            #         # else:
            #         #     tempplot1 = affinity.rotate(spliceline, -self.rotation, origin=self.rotation_point)
            #         #     plt.scatter(*tempplot1.xy,c='b',alpha=0.9,linewidths=0.5)
                    
            #         plt.savefig(r"C:\Users\Damien.Vermeer\Desktop\zLINKS\TEMP\sflayout"+"\\"+str(id)+str(filesuffix)+".png", bbox_inches='tight', dpi=600)                 
            #         results = split(mrr,snap(spliceline,mrr,0.1))
            #         for x in list(results):
            #             if self.rotation_point == None:
            #                 plt.plot(*x.exterior.xy,alpha=0.75, linewidth=1)
            #             else:
            #                 tempplot = affinity.rotate(x, -self.rotation, origin=self.rotation_point)
            #                 plt.plot(*tempplot.exterior.xy,alpha=0.75, linewidth=1)
                            
            #         mmrs.append(results[0])
            #         mmrs.append(results[1])
            #         loopnum += 1
            #         if loopnum == 6: break

                    
                    
                    
                    
                    
                    

                        
                        #plot road nodes
                        #elif element.getDataType() == e_p.ROAD_NODE:
                        #    if self.rotation_point == None:
                        #        plt.scatter(element.getCoords()[0],element.getCoords()[1],c='y',alpha=0.9)
                        #    else:
                        #        tempplot = affinity.rotate(element.getCoordsAsPoint(), -self.rotation, origin=self.rotation_point)
                        #        plt.scatter(*tempplot.xy,c='y',alpha=0.9)
        # #debug
        # coords = self.getBoundaryToLine(self.getBoundaryPoly(), self.polygon.centroid.xy[1][0])
        # temp_poly = LineString(coords).buffer(self.settings['roads/internal/clearwidth']/2, resolution=32, join_style=2)
        # plt.plot(*temp_poly.exterior.xy ,c='purple',alpha=0.9)
        # # temp_poly = LineString(coords).buffer(self.settings['roads/internal/clearwidth']/2, resolution=32, join_style=2)
        # # yoffset = 2*max(self.settings['row/lengths'])+self.settings['layout/endrowspace']+self.settings['roads/internal/clearwidth']
        # # plt.plot(*affinity.translate(temp_poly, xoff=0, yoff=yoffset).exterior.xy,'purple',linestyle='dashed')

        # #plot roads
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
            if self.pre_setback_polygon is not None: plt.plot(*self.pre_setback_polygon.exterior.xy,'k',linestyle='dashed')
        else:
            tempplot1 = affinity.rotate(self.polygon, -self.rotation, origin=self.rotation_point)
            plt.plot(*tempplot1.exterior.xy,'k',linestyle='dashed')
            if self.pre_setback_polygon is not None: tempplot2 = affinity.rotate(self.pre_setback_polygon, -self.rotation, origin=self.rotation_point)
            if self.pre_setback_polygon is not None: plt.plot(*tempplot2.exterior.xy,'k',linestyle='dashed')
        
        if self.settings['plot/title'] == '':
            plt.title("ID # " + str(id) + " - F3 = " + str(round(self.getF3()*100,2)) + "%")
        else:
            plt.title(self.settings['plot/title'])
        
        plt.gca().set_aspect('equal', adjustable='box')
        # axes = plt.gca()
        # axes.set_xlim([self.pre_setback_polygon.bounds[0]*1.3,self.pre_setback_polygon.bounds[2]*1.1])
        # axes.set_ylim([self.pre_setback_polygon.bounds[1]*1.3,self.pre_setback_polygon.bounds[3]*1.1])
        # plt.show()
        plt.savefig(f"{self.settings['output/directory']}\\{id}{filesuffix}.png", bbox_inches='tight', dpi=600)
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

    def getAspectRatio(self):
        x, y = self.polygon.minimum_rotated_rectangle.exterior.xy
        # get length of bounding box edges
        edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
        length = max(edge_length)
        width = min(edge_length)
        return length/width

    def addRoads(self, method='numlongrows', parameter=2, reverse=False):
        
        #TODO fix reverse implementation

        if reverse:
            stripsiter = self.strips[::-1]
        else:
            stripsiter = self.strips

        #step 1 - process and add road POI markers
        # print("--|road layout starting") if self.settings['debug'] == True else False

        # if method == 'numlongrows':
        #     print("--|road layout method numlongrows") if self.settings['debug'] == True else False
        #     #add a POI road marker every 2nd long row
        #     for strip in stripsiter:
        #         counter = 0
        #         if strip.anchor == 'bottom':
        #             dataarray = strip.getDataArray()
        #         else:
        #             dataarray = strip.getDataArray()[::-1]

        #         for element in dataarray:
        #             if element.getDataType() == e_d.SOLAR_ROW:
        #                 #this is a solar row
        #                 if element.getNumberModules() == max(self.settings['row/nmodules']):
        #                     #this is a (max) long row
        #                     counter += 1
        #                     if counter == parameter:
        #                         #this is the 'parameterth' long row adjacent, add a road calc node
        #                         counter = 0
        #                         if strip.anchor == 'bottom':
        #                             coords = [element.getXMidpoint(),element.getYTop()+0.001]
        #                         else:
        #                             coords = [element.getXMidpoint(),element.getYBottom()-0.001]
        #                         strip.addToDataArray(POI.POI(coords))
        #                 else:
        #                     counter = 0
        # elif method == 'minspace':
        #     raise ValueError("minspace road placement not yet implemented")
        # else:
        #     raise ValueError("addRoads not given valid method")

        #step 2 - check there are no POI  road nodes on the end of the stip list
        # print("--|cleaning up excess road markers") if self.settings['debug'] == True else False
        # for strip in stripsiter:
        #     dataarray = strip.getDataArray()

        #     if len(dataarray) == 0:
        #         continue
            
        #     if dataarray[-1].getDataType() == e_p.ROAD_NODE:
        #         strip.removeFromDataArray(dataarray[-1])
        #         print("---/Debug/Removed ROAD_NODE POI from end") if c.DEBUG == True else False

        #     if dataarray[0].getDataType() == e_p.ROAD_NODE:
        #         strip.removeFromDataArray(dataarray[0])
        #         print("---/Debug/Removed ROAD_NODE POI from start") if c.DEBUG == True else False
                                                        
        #once we get to here, we have road markers everywhere
        #step 3 - get road poi nodes within some delta (NEW_ROAD_DELTA)
        print("--|connecting road nodes") if self.settings['debug'] == True else False
        for strip in stripsiter:
            poly = strip.getIntersectionPoly()
            for rp in strip.getDataArray():
                if rp.getDataType() == e_p.ROAD_NODE and not rp.getProcessedFlag():
                    if rp.handler == None:
                        #create new road - defaults to radial road
                        new_mph = MultiPointHandler.MultiPointHandler(settings=self.settings)
                        new_mph.addCoord([rp.getX(),rp.getYTop()])
                        rp.handler = new_mph
                        self.mphs.append(new_mph)
                        
                    mindist = np.inf
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
                            prlength = self.settings['roads/internal/sep/ydelta']*self.settings['row/lengths'][self.settings['row/nmodules'].index(nmod)]
                            compdist = np.sqrt(np.power(self.settings['layout/post2post'],2)+np.power(prlength,2))

                            #check for minimum angle
                            curr_angle = math.degrees(math.atan2(deltay,deltax))
                            if len(rp.handler.coords_array) > 1:
                                prev_angle = math.degrees(math.atan2(rp.getYTop()-rp.handler.coords_array[-2][1], rp.getX()-rp.handler.coords_array[-2][0]))
                            else:
                                prev_angle = curr_angle  

                            #find min distance rp
                            if dist <= compdist:
                                if np.abs(prev_angle-curr_angle) < self.settings['roads/internal/deltangle']:
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
        print("--|cleaning before extrapolation") if self.settings['debug'] == True else False
        remove_list = []
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                if i.getNumCoords() >= 2:
                    i.removeSpikes()    #remove spikes
                    if i.getMaxSlope() > self.settings['roads/internal/deltangle']:
                        remove_list.append(i)   #road is too steep in section
                    #else is valid
                else:
                    remove_list.append(i)   #road is too short

        for delete in remove_list:
            self.mphs.remove(delete) 

        #step 4b - perform extrapolation
        print("--|road layout extrapolating") if self.settings['debug'] == True else False
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
        print("--|road layout creating road polys") if self.settings['debug'] == True else False 
        remove_list = []
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                if i.getNumCoords() >= 2:
                    i.removeSpikes()    #else will fail slope test normally 
                    if not i.getMaxSlope() > self.settings['roads/internal/deltangle']:
                        i.updatePoly()
                    else:
                        remove_list.append(i)
                else:
                    remove_list.append(i)

        for delete in remove_list:
            self.mphs.remove(delete)
  
        #step 6 - offset roads TODO fix this so it works
        print("--|road layout offsetting roads & moving solar rows") if self.settings['debug'] == True else False
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
                        strip.processRoadShift(strip.getIntersectionPoly(), yshiftcoord, strip.anchor, maxyshift - self.settings['layout/endrowspace'])
                
                #process each road
                for road in self.mphs:
                    if road.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                        if road is i:
                            road.shift(0,maxyshift/2)
                        else:
                            if road.getPolygon().centroid.xy[1] > i.getPolygon().centroid.xy[1]:
                                #check if road vertically above TODO fix this properly (look at strips etc)
                                road.shift(0,maxyshift - self.settings['layout/endrowspace'])

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

        print("--|road layout done") if self.settings['debug'] == True else False
        

    # def getBoundaryToLine(self, polygonin, y, mode='below'):

    #     polygonin = polygonin.boundary.parallel_offset(0, 'left')

    #     #travel along boundary interpolating
    #     return_points = []
    #     for f in range(0, int(np.ceil(polygonin.length)) + 1):
    #         ycoord = polygonin.interpolate(f).coords[0][1]
    #         if mode == 'below':
    #             if ycoord < y:
    #                 return_points.append(polygonin.interpolate(f).coords[0])

    #     #median x and y
    #     # median_x = np.median(return_points[0])
    #     # median_y = np.median(return_points[1])

    #     # #calc median slope
    #     # slopes = []
    #     # for i, e in enumerate(return_points):
    #     #     if i == 0:
    #     #         continue 

    #     #     deltax = e[0] - return_points[i-1][0]
    #     #     deltay = e[1] - return_points[i-1][1]
    #     #     slopes.append(math.degrees(math.atan2(deltay,deltax)))

    #     # #get median slope
    #     # median_slope = np.mean(slopes)

    #     # #loop through fixing slope
    #     # for i, e in enumerate(return_points):
    #     #     if i == 0:
    #     #         continue 

    #     #     deltax = e[0] - return_points[i-1][0]
    #     #     deltay = e[1] - return_points[i-1][1]
            
    #     #     # check if too steep (angle > median + delta)
    #     #     curr_slope = math.degrees(math.atan2(deltay,deltax))
    #     #     max_slope = median_slope + self.settings['roads/internal/deltangle']
    #     #     min_slope = median_slope - self.settings['roads/internal/deltangle']
    #     #     # print("current angle = " + str(curr_slope))
    #     #     # print("max_slope = " + str(max_slope))
    #     #     # print("min_slope = " + str(min_slope))
    #     #     if curr_slope > max_slope or curr_slope < min_slope:
    #     #         print("changing y from = "+str(return_points[i-1][1])+"to = " + str(return_points[i-1][1] - (deltax * np.tan(np.deg2rad(self.settings['roads/internal/deltangle'])))))
    #     #         #too steep, assume X is fixed and change y
    #     #         return_points[i-1] = [return_points[i-1][0], return_points[i-1][1] - (deltax * np.tan(np.deg2rad(self.settings['roads/internal/deltangle'])))]
    #     #     # print("--")
    #     #     x=0
        
    #     # for point in return_points:
    #     #     print(point)            
    #     return return_points
    # def addRoads2(self):
    #     #get the left-right orientation of the bounding box
    #     x = self.polygon.minimum_rotated_rectangle.exterior.xy[0]
    #     y = self.polygon.minimum_rotated_rectangle.exterior.xy[1]
    #     cx = self.polygon.minimum_rotated_rectangle.centroid.xy[0][0]
    #     cy = self.polygon.minimum_rotated_rectangle.centroid.xy[1][0]      

    #     new_mph = MultiPointHandler.MultiPointHandler()

    #     for a in x:
    #         for b in y:
    #             if a < cx and b < cy:
    #                 new_mph.addCoord([a,b])
    #             if a > cx and b < cy:
    #                 new_mph.addCoord([a,b])  

    #     print(new_mph.coords_array)  

    #     new_mph.updatePoly()
    #     self.mphs.append(new_mph)


    def processRoads(self, stripsin, id, mph_in):
        print("--|get list of all road nodes with correct id") if self.settings['debug'] == True else False
        
        #get list of road pois
        road_point_list = []
        for strip in stripsin:
            for rp in strip.getDataArray():     #for rp in dataarray
                if rp.getDataType() == e_p.ROAD_NODE: #ff road nod
                    if not rp.getProcessedFlag(): #if not processed
                        if rp.getID() == id: #if id matches 
                            road_point_list.append(rp)

        for i, rp in enumerate(road_point_list):
            if i < 2:
                #just add the first two, dont check
                mph_in.addCoord(rp.getCoords())
                rp.handler = mph_in
            else:
                #check for minimum angle
                delta_x_prev = road_point_list[i-2].getX() - road_point_list[i-1].getX()
                delta_y_prev = road_point_list[i-2].getYTop() - road_point_list[i-1].getYTop()
                delta_x_curr = road_point_list[i-1].getX() - road_point_list[i].getX()
                delta_y_curr = road_point_list[i-1].getYTop() - road_point_list[i].getYTop() 
                
                curr_angle = math.degrees(math.atan2(delta_y_curr,delta_x_curr))
                prev_angle = math.degrees(math.atan2(delta_y_prev,delta_x_prev))
            
                max_allowed_angle = prev_angle + self.settings['roads/internal/deltangle']
                min_allowed_angle = prev_angle - self.settings['roads/internal/deltangle']

                #if too steep, change y
                if curr_angle > max_allowed_angle or curr_angle < min_allowed_angle:
                    yshift = delta_y_curr - delta_y_prev
                    road_point_list[i].shift(0,yshift)

                mph_in.addCoord(road_point_list[i].getCoords())
                rp.handler = mph_in
                rp.setAsProcessed()


        print("--|road layout done") if self.settings['debug'] == True else False
        

        
    #step 4b - perform extrapolation
    def extrapolateRoads(self):
        print("--|road layout extrapolating") if self.settings['debug'] == True else False
        for i in self.mphs:
            if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                #use np to polyfit
                if i.extrapolate(0,1,self.polygon.bounds[0]) != None:
                    yval = i.extrapolate(0,1,self.polygon.bounds[0])
                    i.addCoord([self.polygon.bounds[0], yval],loc='start')
                
                #use np to polyfit
                length = i.getNumCoords()
                if i.extrapolate(length-2,length-1,self.polygon.bounds[2]) != None:
                    yval = i.extrapolate(length-2,length-1,self.polygon.bounds[2])
                    i.addCoord([self.polygon.bounds[2], yval])   

    def getF3(self):
        #returns the factility fill factor (F3)
        #the ratio of module area to area
        array_area = self.getModuleNumber()*self.settings['module/height']*self.settings['module/width']
        total_area = self.polygon.area
        return array_area/total_area

