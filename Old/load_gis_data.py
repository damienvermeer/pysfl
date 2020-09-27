import shapefile
from shapely.geometry import Polygon
from shapely.geometry import LineString, Point, box
import matplotlib.pyplot as plt
import time
from shapely import affinity
import math
from descartes import PolygonPatch

#constants
SPACING = 15
END_END_SPACE = 0.5
ROW_LENGTHS = [91.2, 60.7, 30.4]   #rough dimensions for NX horizon 
NUM_MODULES = [87, 58, 29]          #3 strings, 2 strings, 1 string
DELTA = 0.01
SETBACK = 10
ROAD_WIDTH = 5

def calculateRows(poly_intersect, spacing, row_lengths, delta, direction, xspace, master_road_poly_list):
    #calculates the rows for each single slice
    return_solar_rows = []
    return_modules = 0
    
    #if slice polygon area is less than a row area, continue
    if spacing*min(row_lengths) > poly_intersect.area:
        return [0,None,None]

    #get all y values
    data = []
    for point in poly_intersect.exterior.coords:
        if point not in data:
            data.append(point)
    
    #sort data
    data.sort(key=lambda tup: tup[1])
    for point in data:
        #roadcounter
        rc = 0
        firstrow = None

        yoffset = 0.01
        for i, e in enumerate(ROW_LENGTHS):
            ROW_LENGTH = e
            num_mod_to_add = NUM_MODULES[i]
            while True:
                if direction == 'bu':
                    new_solar_row = Polygon([Point(xspace, yoffset+point[1]),Point(xspace, yoffset+point[1]+ROW_LENGTH),Point(xspace+SPACING, yoffset+point[1]+ROW_LENGTH), Point(xspace+SPACING, yoffset+point[1])])
                else:
                    new_solar_row = Polygon([Point(xspace, point[1]-yoffset),Point(xspace, point[1]-yoffset-ROW_LENGTH),Point(xspace+SPACING, point[1]-yoffset-ROW_LENGTH), Point(xspace+SPACING, point[1]-yoffset)])
                if poly.contains(new_solar_row):
                    #this is a valid row

                    if i == 0:
                        #longest row size, add to row count
                        rc += 1

                    if rc >= 2:
                        #second longest row (in a vertical line)
                        #increase spacing
                        miny_s = firstrow.bounds[1]
                        miny_p = data[0][1]

                        row_offset = abs(miny_s-miny_p)+ROAD_WIDTH

                        rc = 0
                        if direction == 'bu':
                            new_road = Point(xspace+spacing/2, yoffset+point[1]+ROW_LENGTH+row_offset/2)
                        else:
                            new_road = Point(xspace+spacing/2, point[1]-yoffset-ROW_LENGTH-row_offset/2)

                        yoffset += row_offset

                        master_road_poly_list.append(new_road)

                    #add to rows
                    if new_solar_row not in return_solar_rows:
                        return_solar_rows.append(new_solar_row)
                        return_modules += num_mod_to_add
                        if firstrow == None:
                            firstrow = new_solar_row
                    
                    # increment offset
                    yoffset += ROW_LENGTH + END_END_SPACE
                else:
                    #not a valid row
                    # plt.plot(*new_solar_row.exterior.xy,'g')
                    break
    return [return_modules, return_solar_rows, master_road_poly_list]

def generateLayout(poly, spacing, row_lengths, delta=0.01, angle = 0, direction='td'):
    #return solar rows 
    rsr = []
    ret_num_modules = 0
    roads = []

    #newpoly = box(poly.bounds[0],poly.bounds[1],poly.bounds[2],poly.bounds[3])
    #plt.plot(*newpoly.exterior.xy,'g')

    #generate poly parameters
    left_right_width = poly.bounds[2] - poly.bounds[0]
    up_down_width = poly.bounds[3] - poly.bounds[1]

    #output to screen
    num_slices = int((left_right_width+spacing)/spacing)
    print("Layout Generator - Total # Slices = " + str(num_slices))
    print("Starting...")
    curslice = 0

    #draw lines every SPACING
    for xspace in range(0,int(left_right_width+spacing),spacing):
    
        #output to screen
        curslice += 1      
        if curslice % 10 == 0:
            print("Calculated slice " + str(curslice) + "/" + str(num_slices))

        #create 'slice' and check for intersection
        poly_test = Polygon([Point(xspace, 0),Point(xspace, up_down_width+poly.bounds[0]),Point(xspace+SPACING, up_down_width+poly.bounds[0]), Point(xspace+SPACING, 0)])
        #plt.plot(*poly_test.exterior.xy,'k')
        try:
            intersect = poly_test.intersection(poly)
        except:
            print('Intersection error')
            break
        
        #if no intersection, continue
        if intersect.is_empty:
            continue

        #if multipolygon consider each in turn
        if intersect.geom_type == "MultiPolygon":
            for poly_intersect in intersect:
                #call new function
                num_modules, rowback, roadsback = calculateRows(poly_intersect, spacing, row_lengths, delta, direction,xspace,master_road_poly_list)
                if rowback is not None:
                    rsr = [*rsr,*rowback]
                    ret_num_modules += num_modules
                    roads = [*roads,*roadsback]
        elif intersect.geom_type == "Polygon": 
            num_modules, rowback, roadsback = calculateRows(intersect, spacing, row_lengths, delta, direction,xspace,master_road_poly_list)
            if rowback is not None:
                rsr = [*rsr,*rowback]
                ret_num_modules += num_modules
                roads = [*roads,*roadsback]
    return [ret_num_modules, rsr, roads]

#--------- main
sf = shapefile.Reader(r"C:\Users\Damien\Desktop\SDM773066\ll_gda94\sde_shape\whole\VIC\VMPROP\layer\parcel_mp.dbf")

skipcount = 0
for shape in sf.iterShapes():
    #create shape and bounds
    poly = Polygon(shape.points)

    #scale to simple units and move to (0,0)
    poly = affinity.scale(poly, xfact=1000000, yfact=1000000)
    poly = affinity.translate(poly, xoff=-poly.bounds[0], yoff=-poly.bounds[1])
    minrec = poly.minimum_rotated_rectangle
    up_down_width = poly.bounds[3]-poly.bounds[1]
    left_right_width = poly.bounds[2]-poly.bounds[0]

    if up_down_width > 5000 or left_right_width > 5000 or up_down_width < 1000:
        skipcount += 1
        print("Skipped #" + str(skipcount))
        continue
        
    # if poly.area / minrec.area > 0.5:
        # continue
        
    #save pre-setback poly
    pre_move_poly = poly
    
    #setback for polygon
    poly = poly.buffer(-SETBACK).buffer(10, join_style=1, resolution=12800).buffer(-10, join_style=1, resolution=12800)

    #setup master_road_poly_list
    master_road_poly_list = []

    #call generate layout
    print("\n\nStarting to generate layout")
    [modules, rsr, roads] = generateLayout(poly, SPACING, ROW_LENGTHS, master_road_poly_list, direction='bu')
    
    #plot rows
    for row in rsr:
        if row is not None:
            plt.plot(*row.exterior.xy,'r')
     
    #plot roads
    xs = [point.x for point in roads]
    ys = [point.y for point in roads]
    ss = [10 for point in roads]
    plt.scatter(xs, ys, s=ss)

    #plt.plot(xs,ys, linewidth = ROAD_WIDTH)


    #plot the boundary
    plt.plot(*pre_move_poly.exterior.xy,'b',linestyle='dashed')

    #and plot the outer poly
    if poly.geom_type == "MultiPolygon":
        for polyplot in poly:
            plt.plot(*polyplot.exterior.xy)
    else:
        plt.plot(*poly.exterior.xy)
    plt.title("N Modules = " + str(modules) + "() ~= "f'{modules*0.4/1000:.2f}' + " MWdc)")
    plt.show()
    print("Done!")
    plt.clf()
