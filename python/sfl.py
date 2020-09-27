# Solar Farm Layout (SFL)

#imports
import shapefile
import Constants as c
import Farm

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
    farm.translateFarmBoundaryToOrigin()    #move to origin to make easier to read
    print("-processing setback") if c.VERBOSE == True else False
    farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
    
    #create strips
    if farm.getArea() > 1000000000:
        farm.createStrips()
        farm.plotFarm(plot_strips=True)

    


