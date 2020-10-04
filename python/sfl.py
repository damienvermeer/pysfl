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
count = 0
for shape in sf.iterShapes():

    count += 1
    if count < 250:  #skip to ID
        continue

    print("---------------------------")
    print("Solar Farm Layout Tool V0.1")
    print("---------------------------")

    #create Farm:
    print("--|creating farm boundary") if c.VERBOSE == True else False
    farm = Farm.Farm(shape.points)  #create farm
    print("--|scaling farm boundary") if c.VERBOSE == True else False
    farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
    farm.moveCentroidToOrigin() #set before choose azimuth
    farm.setAzimuth(0)
    print("--|moving to origin & setting azimuth") if c.VERBOSE == True else False

    if farm.getMBBRatio() < 0.8:
        print("--|creating setback") if c.VERBOSE == True else False        
        if not farm.setbackFarmBoundary(c.SF_SETBACK):
            continue  #setback from edge, handle multistring
        farm.createStrips()
        farm.populateAllSolarRows()
        farm.addRoads()
        farm.plotFarm(plot_strips=False)






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
        


    


