# Solar Farm Layout (SFL) Generator

#imports
from sfl_generator import SFL_Generator

#firstly define the polygon to use for the solar farm layout
new_boundary = [(0,0),(750,156),(1537,894),(1609,1685),(1205,2105),(811,1129),(241,906)]
scale = 0.2
new_boundary = [(x[0]*scale,x[1]*scale) for x in new_boundary]

#create a generator 
sf_generator = SFL_Generator(new_boundary)

#get the default settings any modify as desired
sf_settings = sf_generator.getSettings()

#set options as desired
sf_settings['general/azimuth/target'] = 0 #0 deg typically for single axis tracking, 90deg for fixed tilt
sf_settings['general/azimuth/tolerance'] = [-10, 10] #list of tolerance to consider away from true N (sat) or E (ft)
sf_settings['general/azimuth/tolerance/steps'] = 0 #number of steps to iterate over for azimuth
sf_settings['general/global/setback'] = 10 #in m, if non-zero, boundary (set-back) area between boundary and solar farm area
sf_settings['general/row/setback'] = [0, 3]  #in m, min and maxset-back from edge of farm boundary for first rows
sf_settings['general/row/setback/steps'] = 3 #number of steps to iterate over for setback

sf_settings['module/height'] = 2 #height of the solar module used in m
sf_settings['module/stc'] = 500 #output power of the module selected in watts

sf_settings['row/lengths'] = [88, 60, 32] #total lengths of rows to consider in m
sf_settings['row/nmodules'] = [84, 56, 28] #list of modules per row in m

sf_settings['layout/post2post'] = 6 #width between posts for solar farm rows
sf_settings['layout/endrowspace'] = 0.5 #spacing between ends of rows
sf_settings['layout/align'] = 'bottom' #'auto' test both, 'bottom' = align with rotated azimuth of 0deg. 'top' align with rotated azimuth of 180deg

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

sf_settings['plot/best'] = -1  #top XX to plot, or -1 to plot all

sf_settings['debug'] = False #True to display debug output

sf_settings['output/directory'] = r"C:\Users\verme\Desktop\zTEMP" #directory to output


#use the 'generate' task using the target flag
sf_generator.applySettings(sf_settings)
best_layout = sf_generator.generate(target='n_modules') #n_modules will search for the highest number of modules





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