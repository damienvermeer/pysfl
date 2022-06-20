
#TODO Review below and incorp into road generation?
    # def addRoads(self, method='numlongrows', parameter=2, reverse=False):
        
    #     #TODO fix reverse implementation

    #     if reverse:
    #         stripsiter = self.strips[::-1]
    #     else:
    #         stripsiter = self.strips

    #     #step 1 - process and add road POI markers
    #     # print("--|road layout starting") if self.settings['debug'] == True else False

    #     # if method == 'numlongrows':
    #     #     print("--|road layout method numlongrows") if self.settings['debug'] == True else False
    #     #     #add a POI road marker every 2nd long row
    #     #     for strip in stripsiter:
    #     #         counter = 0
    #     #         if strip.anchor == 'bottom':
    #     #             dataarray = strip.getDataArray()
    #     #         else:
    #     #             dataarray = strip.getDataArray()[::-1]

    #     #         for element in dataarray:
    #     #             if element.getDataType() == e_d.SOLAR_ROW:
    #     #                 #this is a solar row
    #     #                 if element.getNumberModules() == max(self.settings['row/nmodules']):
    #     #                     #this is a (max) long row
    #     #                     counter += 1
    #     #                     if counter == parameter:
    #     #                         #this is the 'parameterth' long row adjacent, add a road calc node
    #     #                         counter = 0
    #     #                         if strip.anchor == 'bottom':
    #     #                             coords = [element.getXMidpoint(),element.getYTop()+0.001]
    #     #                         else:
    #     #                             coords = [element.getXMidpoint(),element.getYBottom()-0.001]
    #     #                         strip.addToDataArray(POI.POI(coords))
    #     #                 else:
    #     #                     counter = 0
    #     # elif method == 'minspace':
    #     #     raise ValueError("minspace road placement not yet implemented")
    #     # else:
    #     #     raise ValueError("addRoads not given valid method")

    #     #step 2 - check there are no POI  road nodes on the end of the stip list
    #     # print("--|cleaning up excess road markers") if self.settings['debug'] == True else False
    #     # for strip in stripsiter:
    #     #     dataarray = strip.getDataArray()

    #     #     if len(dataarray) == 0:
    #     #         continue
            
    #     #     if dataarray[-1].getDataType() == e_p.ROAD_NODE:
    #     #         strip.removeFromDataArray(dataarray[-1])
    #     #         print("---/Debug/Removed ROAD_NODE POI from end") if c.DEBUG == True else False

    #     #     if dataarray[0].getDataType() == e_p.ROAD_NODE:
    #     #         strip.removeFromDataArray(dataarray[0])
    #     #         print("---/Debug/Removed ROAD_NODE POI from start") if c.DEBUG == True else False
                                                        
    #     #once we get to here, we have road markers everywhere
    #     #step 3 - get road poi nodes within some delta (NEW_ROAD_DELTA)
    #     print("--|connecting road nodes") if self.settings['debug'] == True else False
    #     for strip in stripsiter:
    #         poly = strip.getIntersectionPoly()
    #         for rp in strip.getDataArray():
    #             if rp.getDataType() == e_p.ROAD_NODE and not rp.getProcessedFlag():
    #                 if rp.handler == None:
    #                     #create new road - defaults to radial road
    #                     new_mph = MultiPointHandler.MultiPointHandler(settings=self.settings)
    #                     new_mph.addCoord([rp.getX(),rp.getYTop()])
    #                     rp.handler = new_mph
    #                     self.mphs.append(new_mph)
                        
    #                 mindist = np.inf
    #                 mindistrp = None

    #                 if reverse:
    #                     neigiter = strip.getLeftNeighbour()
    #                 else:
    #                     neigiter = strip.getRightNeighbour()

    #                 for i, test_rp in enumerate(neigiter.getDataArray()):
    #                     if test_rp.getDataType() == e_p.ROAD_NODE:
    #                         #calculate distance from the current point
    #                         deltax = test_rp.getX() - rp.getX()
    #                         deltay = test_rp.getYTop() - rp.getYTop()
    #                         dist = np.sqrt(np.power(deltax,2)+np.power(deltay,2))

    #                         #calculate acceptable offset
    #                         nmod = neigiter.getDataArray()[i-1].getNumberModules()
    #                         prlength = self.settings['roads/internal/sep/ydelta']*self.settings['row/lengths'][self.settings['row/nmodules'].index(nmod)]
    #                         compdist = np.sqrt(np.power(self.settings['layout/post2post'],2)+np.power(prlength,2))

    #                         #check for minimum angle
    #                         curr_angle = math.degrees(math.atan2(deltay,deltax))
    #                         if len(rp.handler.coords_array) > 1:
    #                             prev_angle = math.degrees(math.atan2(rp.getYTop()-rp.handler.coords_array[-2][1], rp.getX()-rp.handler.coords_array[-2][0]))
    #                         else:
    #                             prev_angle = curr_angle  

    #                         #find min distance rp
    #                         if dist <= compdist:
    #                             if np.abs(prev_angle-curr_angle) < self.settings['roads/internal/deltangle']:
    #                                 if dist < mindist:
    #                                     mindist = dist
    #                                     mindistrp = test_rp
    #                                     print("---/Debug/New min distance") if c.DEBUG == True else False
    #                                 else:
    #                                     print("---/Debug/not smaller than mindist") if c.DEBUG == True else False

    #                 #use the min distance rp
    #                 #this is a valid road point which we can
    #                 #build a road with rp
    #                 if not mindistrp == None:
    #                     rp.handler.addCoord([mindistrp.getX(), mindistrp.getYTop()])
    #                     mindistrp.handler = rp.handler
    #                     rp.setAsProcessed()

                        
    #     #step 4a - clean roads for extrapolation
    #     print("--|cleaning before extrapolation") if self.settings['debug'] == True else False
    #     remove_list = []
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #             if i.getNumCoords() >= 2:
    #                 i.removeSpikes()    #remove spikes
    #                 if i.getMaxSlope() > self.settings['roads/internal/deltangle']:
    #                     remove_list.append(i)   #road is too steep in section
    #                 #else is valid
    #             else:
    #                 remove_list.append(i)   #road is too short

    #     for delete in remove_list:
    #         self.mphs.remove(delete) 

    #     #step 4b - perform extrapolation
    #     print("--|road layout extrapolating") if self.settings['debug'] == True else False
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
                
    #             #use np to polyfit
    #             yval = i.extrapolate(0,1,self.polygon.bounds[0])
    #             i.addCoord([self.polygon.bounds[0], yval],loc='start')
                
    #             #use np to polyfit
    #             length = i.getNumCoords()
    #             yval = i.extrapolate(length-2,length-1,self.polygon.bounds[2])
    #             i.addCoord([self.polygon.bounds[2], yval])

    #     #step 5 - create road polygons
    #     print("--|road layout creating road polys") if self.settings['debug'] == True else False 
    #     remove_list = []
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #             if i.getNumCoords() >= 2:
    #                 i.removeSpikes()    #else will fail slope test normally 
    #                 if not i.getMaxSlope() > self.settings['roads/internal/deltangle']:
    #                     i.updatePoly()
    #                 else:
    #                     remove_list.append(i)
    #             else:
    #                 remove_list.append(i)

    #     for delete in remove_list:
    #         self.mphs.remove(delete)
  
    #     #step 6 - offset roads TODO fix this so it works
    #     print("--|road layout offsetting roads & moving solar rows") if self.settings['debug'] == True else False
    #     maxyshift = 0
    #     #first pass - determine max y shift
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #             #check each strip
    #             for strip in self.strips:
    #                 #check if road intersects with poly
    #                 inttest = strip.getIntersectionPoly().intersects(i.getPolygon())
    #                 if inttest: #if intersect
    #                     cross = strip.getIntersectionPoly().intersection(i.getPolygon())
    #                     ywidthint = cross.bounds[3] - cross.bounds[1]   #heigh  of intersection
                        
    #                     if ywidthint > maxyshift:
    #                         maxyshift = ywidthint
        
    #     #second pass - actually shift
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #             #process strips
    #             for strip in self.strips:
    #                 #check if road intersects with poly
    #                 inttest = strip.getIntersectionPoly().intersects(i.getPolygon())
    #                 if inttest: #if intersect
    #                     cross = strip.getIntersectionPoly().intersection(i.getPolygon())
    #                     yshiftcoord = cross.bounds[1] #min y of the intersection
    #                     #shift everything in strip data array u[]
    #                     strip.processRoadShift(strip.getIntersectionPoly(), yshiftcoord, strip.anchor, maxyshift - self.settings['layout/endrowspace'])
                
    #             #process each road
    #             for road in self.mphs:
    #                 if road.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #                     if road is i:
    #                         road.shift(0,maxyshift/2)
    #                     else:
    #                         if road.getPolygon().centroid.xy[1] > i.getPolygon().centroid.xy[1]:
    #                             #check if road vertically above TODO fix this properly (look at strips etc)
    #                             road.shift(0,maxyshift - self.settings['layout/endrowspace'])

    #     #step 7 - delete out of bounds stuff
    #     remove_list = []
    #     for i in self.mphs: #oob mphs
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:  
    #             if not self.polygon.intersects(i.getPolygon()):
    #                 remove_list.append(i)

    #     for item in remove_list:    #delete
    #         self.mphs.remove(item)
            
 
    #     for strip in self.strips:   #oob road poi points
    #         for rp in strip.getDataArray():
    #                 if rp.getDataType() == e_p.ROAD_NODE:
    #                     if not self.polygon.contains(rp.getCoordsAsPoint()):
    #                         strip.removeFromDataArray(rp)

    #     print("--|road layout done") if self.settings['debug'] == True else False
        

    # def processRoads(self, stripsin, id, mph_in):
    #     print("--|get list of all road nodes with correct id") if self.settings['debug'] == True else False
        
    #     #get list of road pois
    #     road_point_list = []
    #     for strip in stripsin:
    #         for rp in strip.getDataArray():     #for rp in dataarray
    #             if rp.getDataType() == e_p.ROAD_NODE: #ff road nod
    #                 if not rp.getProcessedFlag(): #if not processed
    #                     if rp.getID() == id: #if id matches 
    #                         road_point_list.append(rp)

    #     for i, rp in enumerate(road_point_list):
    #         if i < 2:
    #             #just add the first two, dont check
    #             mph_in.addCoord(rp.getCoords())
    #             rp.handler = mph_in
    #         else:
    #             #check for minimum angle
    #             delta_x_prev = road_point_list[i-2].getX() - road_point_list[i-1].getX()
    #             delta_y_prev = road_point_list[i-2].getYTop() - road_point_list[i-1].getYTop()
    #             delta_x_curr = road_point_list[i-1].getX() - road_point_list[i].getX()
    #             delta_y_curr = road_point_list[i-1].getYTop() - road_point_list[i].getYTop() 
                
    #             curr_angle = math.degrees(math.atan2(delta_y_curr,delta_x_curr))
    #             prev_angle = math.degrees(math.atan2(delta_y_prev,delta_x_prev))
            
    #             max_allowed_angle = prev_angle + self.settings['roads/internal/deltangle']
    #             min_allowed_angle = prev_angle - self.settings['roads/internal/deltangle']

    #             #if too steep, change y
    #             if curr_angle > max_allowed_angle or curr_angle < min_allowed_angle:
    #                 yshift = delta_y_curr - delta_y_prev
    #                 road_point_list[i].shift(0,yshift)

    #             mph_in.addCoord(road_point_list[i].getCoords())
    #             rp.handler = mph_in
    #             rp.setAsProcessed()


    #     print("--|road layout done") if self.settings['debug'] == True else False
        

        
    # #step 4b - perform extrapolation
    # def extrapolateRoads(self):
    #     print("--|road layout extrapolating") if self.settings['debug'] == True else False
    #     for i in self.mphs:
    #         if i.getDataType() == e.MultiPointDataTypes.RADIAL_ROAD:
    #             #use np to polyfit
    #             if i.extrapolate(0,1,self.polygon.bounds[0]) != None:
    #                 yval = i.extrapolate(0,1,self.polygon.bounds[0])
    #                 i.addCoord([self.polygon.bounds[0], yval],loc='start')
                
    #             #use np to polyfit
    #             length = i.getNumCoords()
    #             if i.extrapolate(length-2,length-1,self.polygon.bounds[2]) != None:
    #                 yval = i.extrapolate(length-2,length-1,self.polygon.bounds[2])
    #                 i.addCoord([self.polygon.bounds[2], yval])   

    # def getF3(self):
    #     #returns the factility fill factor (F3)
    #     #the ratio of module area to area
    #     array_area = self.getModuleNumber()*self.settings['module/height']*self.settings['module/width']
    #     total_area = self.polygon.area
    #     return array_area/total_area

