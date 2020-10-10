SCALE_FACTOR_FROM_DBF = 1000000             #ratio to scale the DBF / shape file by
SR_POST_POST_WIDTH = 6                      #width between posts for solar farm rows
SR_END_DELTA = 0.1                          #set-back from edge of farm boundary for first row
SR_END_END_WIDTH = 1                        #spacing between ends of rows
#SR_ROW_LENGTHS = [91.2, 60.7, 30.4]         #rough dimensions for NX horizon 
#SR_NUM_MODULES_PER_ROW = [87, 58, 29]       #3 strings, 2 strings, 1 string
SR_ROW_LENGTHS = [20, 10]            #DEBUG
SR_NUM_MODULES_PER_ROW = [5, 4]       #DEBUG
SR_ROADWAY_WIDTH = 4                        #roadway width (not road width) between rows
SF_SETBACK = 10                             #solar farm boundary setback
VERBOSE = True                              #print all output
DEBUG = False                                #print lots of output
ROAD_Y_DELTA = 1  #temp see if new line idea works
SPIKE_MIN = 10
MAX_ROAD_DELTA_ANGLE = 20
#TODO implement some way to store 'road every second long row'