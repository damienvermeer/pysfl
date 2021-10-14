# Solar Farm Layout (SFL) Generator

#imports
from sfl_generator import SFL_Generator
import pickle
import os
import argparse



# DATA_FILE = r"C:\Users\verme\GIT\sfl\python\n10000_test.shape"
DATA_FILE = r"C:\Users\verme\Desktop\n500_set1_2021_10_11.shape"


with open(DATA_FILE, 'rb') as f: 
    data_in = pickle.load(f)

parser = argparse.ArgumentParser()
parser.add_argument('--start')
parser.add_argument('--end')
parser.add_argument('--fname')
parser.add_argument('--p2p')
parser.add_argument('--edgeoffset')
parser.add_argument('--azimuthtol')
args = parser.parse_args()

OUTPUT_FILE = r"C:\Users\verme\Desktop\zTEMP" + "\\" + str(args.fname) + ".csv"

with open(OUTPUT_FILE, "w") as myfile:
    myfile.write('id,area,MBBR,aspectratio,F3%,nModules\n')

if 'start' not in args and 'end' not in args:
    data_iterate = data_in
else:
    data_iterate = data_in[int(args.start) : int(args.end)]

for ix,test in enumerate(data_iterate):

    if 'start' in args: ix += int(args.start)
    endint = len(data_iterate)-1
    if 'end' in args: endint += int(args.end)

    os.system('cls' if os.name=='nt' else 'clear')
    print(f'**id {ix} of {endint}')
    
    #create a generator 
    sf_generator = SFL_Generator(test['polygon'])

    #get the default settings any modify as desired
    sf_settings = sf_generator.getSettings()

    #set options as desired
    sf_settings['general/azimuth/target'] = 0 #0 deg typically for single axis tracking, 90deg for fixed tilt
    sf_settings['general/azimuth/tolerance'] = [-float(args.azimuthtol), float(args.azimuthtol)] #list of tolerance to consider away from true N (sat) or E (ft)

    sf_settings['general/azimuth/tolerance/steps'] = 5 #number of steps to iterate over for azimuth
    sf_settings['general/global/setback'] = float(args.edgeoffset) #in m, if non-zero, boundary (set-back) area between boundary and solar farm area
    sf_settings['general/row/setback'] = [0, 3]  #in m, min and maxset-back from edge of farm boundary for first rows
    sf_settings['general/row/setback/steps'] = 4 #number of steps to iterate over for setback

    sf_settings['module/height'] = 2 #height of the solar module used in m
    sf_settings['module/width'] = 1 #width of the solar module used in m NOTE this does not interact with row modules/length
    sf_settings['module/stc'] = 500 #output power of the module selected in watts

    sf_settings['row/lengths'] = [88, 60, 32] #total lengths of rows to consider in m
    sf_settings['row/nmodules'] = [84, 56, 28] #list of modules per row in m

    sf_settings['layout/post2post'] = float(args.p2p) #width between posts for solar farm rows
    sf_settings['layout/endrowspace'] = 0.5 #spacing between ends of rows
    sf_settings['layout/align'] = 'auto' #'auto' test both, 'bottom' = align with rotated azimuth of 0deg. 'top' align with rotated azimuth of 180deg

    sf_settings['roads/perimeter'] = True #true for perimeter road, False to not include perimeter road
    sf_settings['roads/clearwidth'] = 8 #roadway width (not road width) between rows
    sf_settings['roads/internal/enable'] = True #true to include roads, False to disable
    sf_settings['roads/internal/clearwidth'] = 8 #roadway width (not road width) between rows
    sf_settings['roads/internal/deltangle'] = 30 #degrees, max angle for an internal road to take
    sf_settings['roads/internal/align'] = 'middle' #'middle' = roads grow into middle
    sf_settings['roads/internal/sep/road2road'] = 2*max(sf_settings['row/lengths']) #in m, min distance before a road is added
    sf_settings['roads/internal/sep/edge2road'] = 1*max(sf_settings['row/lengths']) #in m, min distance between edge and roadway
    sf_settings['roads/internal/sep/road2rows'] = 1  #additional offset between top of row and row marker
    sf_settings['roads/internal/sep/ydelta'] = 1  #unknown to test?
    sf_settings['roads/internal/spikemin'] = 10  #unknown to test?

    sf_settings['plot/best'] = 1  #top XX to plot, or -1 to plot all
    sf_settings['plot/title'] = f'ID #{ix} Best Result'  #top XX to plot, or -1 to plot all
    sf_settings['plot/filename'] = f'{args.fname}_id_{ix}_best'

    sf_settings['debug'] = False #True to display debug output

    sf_settings['output/directory'] =  r"C:\Users\verme\Desktop\zTEMP\sfoutput"#r"C:\Users\verme\Desktop\zTEMP" #directory to output


    #use the 'generate' task using the target flag
    try:
        sf_generator.applySettings(sf_settings)
        best_layout = sf_generator.generate(target='n_modules') #n_modules will search for the highest number of modules
        
        while True:
            try:
                with open(OUTPUT_FILE, "a") as myfile:
                    myfile.write(f'{ix},{best_layout.getArea()},{best_layout.getMBBRatio()},{best_layout.getAspectRatio()},{best_layout.getF3()*100:.2f},{best_layout.getModuleNumber()}\n')
                break
            except:
                pass
    except Exception as ex: 
        print(str(ex))



    # TODO incorporate
    # for each point on boundary in small steps s_cur & s_next
    # 	for vertical offset in 0 to max_height_sf:
    # 		aspect ratio = 2 to 0.5 in steps of somethimg
    # 		draw rectangle:
    # 			- from s_curr towards s_next of leng
    # 			- length is aspect ratio relative to area
    # 		if rectange intsects boundary = continue
    # 		if rectangle is completely outside boundary: break
    # 		else:
    # 			for each row which intersects the rectangle
    # 				while can reduce length - reduce & recheck
                
    # 			store number removed + rectangle in results