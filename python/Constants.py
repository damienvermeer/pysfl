SCALE_FACTOR_FROM_DBF = 3000000             #ratio to scale the DBF / shape file by
SR_POST_POST_WIDTH = 7                      #width between posts for solar farm rows
SR_MODULE_HEIGHT = 2                      #height of the solar module used
SR_END_DELTA = 0.1                          #set-back from edge of farm boundary for first row
SR_END_END_WIDTH = 1                        #spacing between ends of rows
SR_ROW_LENGTHS = [99.7, 67.8, 35.9]         #roughly nx horizon
SR_NUM_MODULES_PER_ROW = [87, 58, 29]       #roughly nx horizon
SR_ROADWAY_WIDTH = 4                        #roadway width (not road width) between rows
SF_SETBACK = 10                             #solar farm boundary setback
VERBOSE = True                              #print all output
DEBUG = False                                #print lots of output
ROAD_Y_DELTA = 1  #temp see if new line idea works
SPIKE_MIN = 10
MAX_ROAD_DELTA_ANGLE = 40
#TODO implement some way to store 'road every second long row'