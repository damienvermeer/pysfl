#psuedocode for inverter location algo
from Enums import SPDataTypes as e_d
from shapely.geometry import *

def calculate_inv_locations(farm):
    
    # for every row
    point_list = []
    for element in farm.strips.getDataArray():
        if element.getDataType() == e_d.SOLAR_ROW:
            
            ytop, ybottom = [element.getYTop(), element.getYBottom()]
            xmid = element.getXMidpoint()
            point_list.append((xmid,ytop))
            point_list.append((xmid,ybottom))

    mrr = MultiPoint(point_list).minimum_rotated_rectangle
        
        
        #store in list
        
    
#for all points in the above list
    #find bounding box (rotated)
    #count number of rows which fall inside the xy tight bounding box (minimum rotated rectangle)
    #if the number of rows * modules * module rating is > max for a single inverter
    #split the bounding box into two bounding boxes, splitting along its long axis like below
    
    # ----------------------------------------
    # |                 |split here           |
    # ----------------------------------------
    #repeat the above until we have a list of bounding boxes which have at most the rows * modules * module rating = max inverter rating
    #then for each bounding box
        #find the centroid
        #find the nearest road segement for that centroid
        #the inverter gets placed at the nearest road segment
        #for every row in bounding box - set the inverter number to the number of this inverter