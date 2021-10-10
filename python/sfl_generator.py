import copy
from sflfarm import Farm
import numpy as np
import warnings
warnings.simplefilter('ignore', np.RankWarning)
import os

class SFL_Generator():
    
    def __init__(self, poly):
        self.poly = poly
        self.settings = copy.deepcopy({
            'test':5
        })

    def getSettings(self):
        return self.settings
    
    def applySettings(self, settings_in):
        self.settings = settings_in
        
    def generate(self, target='n_modules'):
        """
        Generate multiple solar farm layouts based on a target and return the solar farm object
        """
        settings_to_run = [copy.deepcopy(self.settings)]
        
        #handle tolerance on azimuth
        if isinstance(self.settings['general/azimuth/tolerance'], list):
            if self.settings['general/azimuth/tolerance'] != [0,0]:
                #some tolerance to apply
                for working_settings in copy.copy(settings_to_run):
                    _ = working_settings['general/azimuth/tolerance']
                    for x in np.linspace(min(_), max(_),self.settings['general/azimuth/tolerance/steps']):
                        new_settings = copy.deepcopy(working_settings)
                        new_settings['general/azimuth/target'] = x + new_settings['general/azimuth/target']
                        settings_to_run.append(new_settings)
        
        #handle tolerance on setback
        if isinstance(self.settings['general/row/setback'], list):
            #some tolerance to apply
            if self.settings['general/row/setback/steps'] == 1:
                #just apply
                for x in settings_to_run:
                    x['general/row/setback/target'] = self.settings['general/row/setback'][0]
            else:
                #need to apply them
                for working_settings in copy.copy(settings_to_run):
                    _ = working_settings['general/row/setback']
                    for x in np.linspace(min(_), max(_),self.settings['general/row/setback/steps']):
                        new_settings = copy.deepcopy(working_settings)
                        new_settings['general/row/setback/target'] = x
                        settings_to_run.append(new_settings)
                
        if self.settings['layout/align'] == 'auto':
            for working_settings in copy.copy(settings_to_run):
                for x in [180]: #'bottom' already in, make this neater
                    new_settings = copy.deepcopy(working_settings)
                    new_settings['general/azimuth/target'] = x + new_settings['general/azimuth/target']
                    settings_to_run.append(new_settings)
        
        #run
        results = []
        min_modules = 0
        for i,e in enumerate(settings_to_run):
            sf = Farm(self.poly, settings=e)
            sf.scaleFarmBoundary(0.5)
            # if i == 0: sf.plotFarm('original', plot_strips=False, plot_strip_ints=False, plot_sf_rows=False, filesuffix="orig")
            # sf.moveCentroidToOrigin()
            sf.setAzimuth(e['general/azimuth/target'])
            if e['general/global/setback'] > 0: sf.setbackFarmBoundary(e['general/global/setback'])
            sf.createStrips()
            sf.populateAllSolarRows()
            sf.deleteDuplicates() #temp workaround
            # sf.plotFarm(f"Run #{i+1} - Nmodule = {sf.getModuleNumber()}", plot_strips=False, plot_strip_ints=False)
            
            #minimise memory - only store if better than previous
            if sf.getModuleNumber() > min_modules:
                min_modules = sf.getModuleNumber()
            
            #store result
            results.append([sf.getModuleNumber(), sf])
            
            #display progress
            percent_complete = (i+1)/len(settings_to_run)*100
            print(f'Complete {percent_complete:.2f}% (Completed {i+1} of {len(settings_to_run)})')
        
        #sort and plot top 3, or if less than 3 just plot the top
        results_sorted = sorted(results, key=lambda x: x[0], reverse=True)
        if e['plot/best'] != -1:
            plot_results = results_sorted[0:e['plot/best']] if len(results_sorted) > e['plot/best'] else results_sorted
        else:
            plot_results = results_sorted
        
        for ix,plot_sf in enumerate(plot_results):
            nmodules,plot_sf_inst = plot_sf
            for i,e in enumerate(results): 
                if e[1] is plot_sf_inst: plot_sf_inst.plotFarm(self.settings['plot/filename'], plot_strips=False, plot_strip_ints=False)

        # print(str(results_sorted[0][1].settings))

        return results_sorted[0][1] 