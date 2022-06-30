from shapely.geometry import box as Box
import numpy as np

class SolarRow:

    def __init__(
                self,                                     
                idchar = '_',
                super = None,
                minx = -1, 
                miny = -1, 
                maxx = -1,
                maxy = 1,
                asset_type = None,
                ):
        """
        TODO docustring & review inputs
        """
        
        #Create box strip
        self.asset_poly = Box(
                            minx, 
                            miny, 
                            maxx,
                            maxy) 
        #Set super and id references
        self.super = super
        self.idchar = idchar
        self.row_settings = super._internal_convert_idchar_to_row_settings(idchar)
        self.asset_type = asset_type #TODO enum via asset?
        self.asset_properties = {
                'n_strings' : self.row_settings['strings-on-row'],
                'n_modules' : self.row_settings['strings-on-row']
                * self.super.settings['strings']['mods-per-string']
                }
        self.sub_asset_polys = []
        #Generate extra polygons to render a pretty version if enabled 
        if self.super.settings['render']['render-all-modules']:
            #Get right side length to use
            if self.super.settings['rows']['portrait-mount']:
                panel_vert_dist = self.super.settings['module']['dim-width']
            else:
                panel_vert_dist = self.super.settings['module']['dim-length']  
            #Check if single axis tracker
            if True: #change to if single-axis tracker
                self.sub_asset_polys = []
                extra_space_added = False
                #Generate polygons to represent each panel
                y_mod_top = maxy
                space_beteen_mods =  self.row_settings['space-between-modules']
                for n in range(self.asset_properties['n_modules']):
                    self.sub_asset_polys.append(
                                                Box(
                                                    minx, 
                                                    y_mod_top - panel_vert_dist, 
                                                    maxx,
                                                    y_mod_top)
                                                )
                    #Remove width of module from the y_mod_top tracker
                    y_mod_top -= panel_vert_dist
                    if n >= self.asset_properties['n_modules']/2-1 and not extra_space_added:
                        #Create the torque tube representation
                        self.sub_asset_polys.append(
                                                Box(
                                                    (maxx+minx)/2-0.1, 
                                                    y_mod_top - self.row_settings['extra-space'], 
                                                    (maxx+minx)/2+0.1,
                                                    y_mod_top)
                                                )
                        #Now remove this space
                        y_mod_top -= self.row_settings['extra-space']
                        extra_space_added = True
                    else:
                        #Note we wont generate a small section of torque tube
                        #as it creates many more polygons, makes dxf too big
                        y_mod_top -= space_beteen_mods

            else: #TODO change to fixed tilt
                pass