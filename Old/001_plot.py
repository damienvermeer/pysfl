from shapely.geometry import Point, Polygon
from shapely import affinity
import matplotlib.pyplot as plt
import numpy as np

#generate single solar row from modules and angle
def returnRowPolygon (curcorx, curcory, nModulesPerRow, angle):
    srp1 = Point(curcorx, curcory)
    srp2 = Point(curcorx+nModulesPerRow, curcory)
    srp3 = Point(curcorx+nModulesPerRow,curcory+2)
    srp4 = Point(curcorx,curcory+2)

    return affinity.rotate(Polygon([srp1,srp2,srp3,srp4]),angle, origin=(0,0))
     

def generateSolarRowGrid(site_boundary,angle,deltax,deltay,deltabounds,nModulesPerRow,nEndEndRowSpace,nRowRowSpace):
    #Generates array of solar rows
    #INPUTS
    # site_boundary (Polygon) Site boundary for solar farm
    # angle (float) degrees of solar row rotation
    # deltax (float) x offset for site layout
    # deltay (float) y offset for site layout
    # deltabounds (float) site overreach multipler 
    # nModulesPerRow (float) as per global
    # nEndEndRowSpace (float) as per global
    # nRowRowSpace (float) as per global
    #RETURNS solarRows (Polygon[])
    # s
    
    #calc bounds
    area_bounds = site_boundary.bounds
    solarRows = []

    #bounds to minx, miny, maxx, maxy
    startx = area_bounds[0]*deltabounds
    endx = area_bounds[2]*deltabounds+deltax
    starty = (area_bounds[1] - area_bounds[2]*np.sin(angle*np.pi/180))*deltabounds+deltay
    endy = area_bounds[3]*deltabounds
    
    #create layout
    for x in np.arange(startx, endx,nEndEndRowSpace+nModulesPerRow): 
        for y in np.arange(starty, endy, nRowRowSpace+nEndEndRowSpace+1):     
            #generate solar row
            srow = returnRowPolygon(x,y,nModulesPerRow,angle)
            
            #check if in bounds
            if srow.within(poly):
                #plt.plot(*srow.exterior.xy,'g')
                solarRows.append(srow)
            #else:
                #plt.plot(*srow.exterior.xy,'r',linestyle='dashed')        
    return solarRows






#set up boundaries
p1 = Point(0, 0)
p2 = Point(20, 0)
p3 = Point(70, 20)
p4 = Point(70, 100)
p5 = Point(50, 80)
p6 = Point(0, 50)
coords = [p1,p2,p3,p4,p5,p6]
poly = Polygon(coords)

#plot poly
x,y = poly.exterior.xy
plt.plot(x,y,'k')

#plot example
test = generateSolarRowGrid(site_boundary=poly,angle=0,deltax=0,deltay=0,deltabounds=1.1,nModulesPerRow=15,nEndEndRowSpace=1,nRowRowSpace=5)
print(len(test))
for row in test:
    plt.plot(*row.exterior.xy,'g')
plt.show()

#solar farm parameters
nModulesPerRow = 15
nEndEndRowSpace = 1
nRowRowSpace = 5

best_arrangement = []

for angle_var in np.arange(90, -0.1, -5):
    for delta_x_var in np.arange(0, nModulesPerRow/2, 0.5):
        for delta_y_var in np.arange(0, (nRowRowSpace+nEndEndRowSpace+1)/2, 0.5):

            output = generateSolarRowGrid(site_boundary=poly,angle=angle_var,deltax=delta_x_var,deltay=delta_y_var,deltabounds=1.1,nModulesPerRow=15,nEndEndRowSpace=1,nRowRowSpace=5)
               
            if len(output) > len(best_arrangement):
                best_arrangement = output
                print("**found new best, " + str(len(output)) + " rows || angle_var = " + str(angle_var) + ",delta_x_var = " + str(delta_x_var) + ",delta_y_var = " + str(delta_y_var))

#plot best
x,y = poly.exterior.xy
plt.plot(x,y,'k')
for row in best_arrangement:
    plt.plot(*row.exterior.xy,'g')
plt.show()

    # site_boundary (Polygon) Site boundary for solar farm
    # angle (float) degrees of solar row rotation
    # deltax (float) x offset for site layout
    # deltay (float) y offset for site layout
    # deltabounds (float) site overreach multipler 
    # nModulesPerRow (float) as per global
    # nEndEndRowSpace (float) as per global
    # nRowRowSpace (float) as per global
           
                # #plot temp
                # x,y = poly.exterior.xy
                # plt.plot(x,y)
                # for row in solarRows:
                    # plt.plot(*row.exterior.xy,'g')
                # plt.show()
        
        #check for best
        # if len(solarRows) > maxDCPeak:
            # print("new best")
            # maxDCPeak = len(solarRows)
            # best_startx = startx
            # best_starty = starty
            # best_solarRows = solarRows
       
       
    

#plot one solar row


