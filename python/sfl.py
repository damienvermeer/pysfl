# Solar Farm Layout (SFL)

#imports
import shapefile
import Constants as c
import Farm
import time

# code starts here --------

#load DBF file
sf = shapefile.Reader(r"C:\Users\Damien\Desktop\SDM773066\solar\parcel_mp.dbf")

#load the first shape
farm = None
for shape in sf.iterShapes():
    
    print("---------------------------")
    print("Solar Farm Layout Tool V0.1")
    print("---------------------------")

    #create Farm:
    print("-creating farm boundary") if c.VERBOSE == True else False
    farm = Farm.Farm(shape.points)  #create farm
    farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
    
    if farm.getArea() > 100000:
        farm.moveCentroidToOrigin()
        farm.setAzimuth(58)
        farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
        farm.createStrips()
        farm.populateAllSolarRows()
        farm.plotFarm()






        # maxpanel = 0
        # bestazi = 0
        # for azi in range(-90,90,10):
            # print(azi)
            # farm = Farm.Farm(shape.points)  #create farm
            # farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
            # farm.moveCentroidToOrigin()
            # farm.setAzimuth(azi)
            # farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
            # farm.createStrips()
            # farm.populateAllSolarRows()
            # farm.printModuleNumber()
            # if farm.getModuleNumber() > maxpanel:
                # maxpanel = farm.getModuleNumber()
                # bestazi = azi
        
        # print("end. best azi = " + str(bestazi) + " with #" + str(maxpanel) + " modules")
        # farm = Farm.Farm(shape.points)  #create farm
        # farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
        # farm.moveCentroidToOrigin()
        # farm.setAzimuth(bestazi)
        # farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
        # farm.createStrips()
        # farm.populateAllSolarRows()
        # farm.plotFarm()
        


    


