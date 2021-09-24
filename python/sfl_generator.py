import copy
from sflfarm import Farm
import numpy as np

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
        
        #check general sf settings
        if isinstance(self.settings['general/azimuth/tolerance'], list):
            if self.settings['general/azimuth/tolerance'] != [0,0]:
                #some tolerance to apply
                for working_settings in copy.copy(settings_to_run):
                    _ = working_settings['general/azimuth/tolerance']
                    for x in np.linspace(min(_), max(_),100):
                        new_settings = copy.deepcopy(working_settings)
                        new_settings['general/azimuth/target'] = x + new_settings['general/azimuth/target']
                        settings_to_run.append(new_settings)
        
        if self.settings['layout/align'] == 'auto':
            for working_settings in copy.copy(settings_to_run):
                for x in [0,180]:
                    new_settings = copy.deepcopy(working_settings)
                    new_settings['general/azimuth/target'] = x + new_settings['general/azimuth/target']
                    settings_to_run.append(new_settings)
        
        #run
        results = []
        for i,e in enumerate(settings_to_run):
            sf = Farm(self.poly, settings=e)
            sf.moveCentroidToOrigin()
            sf.setAzimuth(e['general/azimuth/target'])
            if e['general/global/setback'] > 0: sf.setbackFarmBoundary(e['general/global/setback'])
            sf.createStrips()
            sf.populateAllSolarRows()
            # sf.plotFarm(f"Run #{i+1} - Nmodule = {sf.getModuleNumber()}", plot_strips=False, plot_strip_ints=False)
            results.append([sf.getModuleNumber(), sf])
        
        #sort and plot top 3, or if less than 3 just plot the top
        results_sorted = sorted(results, key=lambda x: x[0], reverse=True)
        plot_results = results_sorted[0:3] if len(results_sorted) > 3 else results_sorted
        for plot_sf in plot_results:
            nmodules,plot_sf_inst = plot_sf
            for i,e in enumerate(results): 
                if e[1] is plot_sf_inst: plot_sf_inst.plotFarm(f"Run #{i} - Nmodule = {nmodules}", plot_strips=False, plot_strip_ints=False)