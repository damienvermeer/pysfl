# Solar Farm Layout (SFL)

#imports
# import shapefile
import Constants as c
import Farm
import time
import inverterlocate
# code starts here --------

from pykml import parser
import utm

fname = r"C:\Users\Damien.Vermeer\Downloads\Untitled layer.kml"
with open(fname, 'r', encoding = 'unicode_escape') as f:
  root = parser.parse(f).getroot()
namespace = {"kml": 'http://www.opengis.net/kml/2.2'}
pms = root.xpath(".//kml:Placemark[.//kml:Polygon]", namespaces=namespace)
for p in pms:
    x = str(p.Polygon.outerBoundaryIs.LinearRing.coordinates)
    x = [y.strip() for y in x.split('\n')]
    coords = []

    for line in x:
        if line != '':
            a,b = line.split(',')[:2]
            x1, y1 = list(utm.from_latlon(float(b), float(a)))[:2]
            coords.append((float(x1),float(y1)))
    
    
print(coords)      

# #load the first shape
farm = None
# count = 0

print("---------------------------")
print("Solar Farm Layout Tool V0.1")
print("---------------------------")

# #create Farm:
print("--|creating farm boundary") if c.VERBOSE == True else False
# farm = Farm.Farm(coords)  #create farm
farm = Farm.Farm([(0,0),(200,0),(400,400),(0,400)])  #create farm
# print("--|scaling farm boundary") if c.VERBOSE == True else False
# farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
farm.moveCentroidToOrigin() #set before choose azimuth
farm.setAzimuth(0)
print("--|moving to origin & setting azimuth") if c.VERBOSE == True else False

print("--|creating setback")    
farm.setbackFarmBoundary(c.SF_SETBACK)
farm.plotFarm(1, plot_strips=False, plot_strip_ints=False, plot_sf_rows=False, filesuffix="orig")
farm.createStrips()
farm.populateAllSolarRows()
print(farm.printModuleNumber())
farm.plotFarm(1, plot_strips=False, plot_strip_ints=False)
# inverterlocate.calculate_inv_locations(farm)













# #load DBF file
# sf = shapefile.Reader(r"C:\Users\Damien\Desktop\SDM773066\solar\parcel_mp.dbf")

# #load the first shape
# farm = None
# count = 0
# for shape in sf.iterShapes():

#     count += 1
#     # if count < 10000:  #skip to ID
#     #     continue

#     print("---------------------------")
#     print("Solar Farm Layout Tool V0.1")
#     print("---------------------------")

#     #create Farm:
#     print("--|creating farm boundary") if c.VERBOSE == True else False
#     farm = Farm.Farm(shape.points)  #create farm
#     print("--|scaling farm boundary") if c.VERBOSE == True else False
#     farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
#     farm.moveCentroidToOrigin() #set before choose azimuth
#     farm.setAzimuth(0)
#     print("--|moving to origin & setting azimuth") if c.VERBOSE == True else False

#     print("--|creating setback") if c.VERBOSE == True else False        
#     if not farm.setbackFarmBoundary(c.SF_SETBACK):
#         continue  #setback from edge, handle multistring
#     farm.plotFarm(count, plot_strips=False, plot_strip_ints=False, plot_sf_rows=False, filesuffix="orig")
#     farm.createStrips()
#     farm.populateAllSolarRows()
#     print(farm.printModuleNumber())
#     farm.plotFarm(count, plot_strips=False, plot_strip_ints=False)







#         # maxpanel = 0
#         # bestazi = 0
#         # for azi in range(-90,90,10):
#             # print(azi)
#             # farm = Farm.Farm(shape.points)  #create farm
#             # farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
#             # farm.moveCentroidToOrigin()
#             # farm.setAzimuth(azi)
#             # farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
#             # farm.createStrips()
#             # farm.populateAllSolarRows()
#             # farm.printModuleNumber()
#             # if farm.getModuleNumber() > maxpanel:
#                 # maxpanel = farm.getModuleNumber()
#                 # bestazi = azi
        
#         # print("end. best azi = " + str(bestazi) + " with #" + str(maxpanel) + " modules")
#         # farm = Farm.Farm(shape.points)  #create farm
#         # farm.scaleFarmBoundary(c.SCALE_FACTOR_FROM_DBF) #scale based on shapefile
#         # farm.moveCentroidToOrigin()
#         # farm.setAzimuth(bestazi)
#         # farm.setbackFarmBoundary(c.SF_SETBACK)  #setback from edge
#         # farm.createStrips()
#         # farm.populateAllSolarRows()
#         # farm.plotFarm()
        


    


