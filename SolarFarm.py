#Built-in imports
import math
import copy
import re
from pathlib import Path

#External imports via pip/conda
from shapely.geometry import Polygon
# from shapely.ops import *
from shapely import affinity
import numpy as np
import yaml
import matplotlib.pyplot as plt
import ezdxf

#Internal to pysfl imports
import StripPoly

#Class defs start
#-------------------------------------------------------------------------------
class SolarFarmDataValidationError(Exception):
    """
    SolarFarm class Data Validation Error
    Used whenever invalid validation is identified in pysfl
    Custom class used to distinguish from other errors
    """
#-------------------------------------------------------------------------------
class SolarFarm:

    def __init__(self, poly_coords, settings='default', cost_data='default'):
        """
        SolarFarm class instance constructor

        :param poly_coords: A list of 2-float-tuples which defines a 
                            2-dimensional polygon that represents the land area 
                            for the solar farm.
        :type poly_coords: list[tuple(float,float)]
        :param settings: A settings dictionary which follows a YAML file 
                        structure, which defines how the solar farm layout 
                        should be generated.
        :type settings: dict
        :param cost_data: A cost dictionary which follows a YAML file 
                        structure, which defines the cost of each asset within 
                        the solar farm, used for optimisation.
        :type cost_data: dict
        :return: A SolarFarm class instance
        :rtype: SolarFarm
        :raises SolarFarmDataValidationError: If poly_coords are not a list of
                                            2-tuples, or the settings or cost 
                                            data dictionaries do not match the 
                                            YAML representation.
        """
        #Check polygon is valid before applying
        if SolarFarm.is_data_valid(poly_coords, datatype='polygon'):
            self.polygon = Polygon(poly_coords)
        #Check settings is valid before applying, use default if not provided
        if settings == 'default':
            self.settings = SolarFarm.generate_default_settings()
        elif SolarFarm.is_data_valid(settings, datatype='settings'):
            self.settings = settings
        #Check cost_data is valid before applying, use default if not provided
        if cost_data == 'default':
            self.cost_data = SolarFarm.generate_default_cost_data()
        elif SolarFarm.is_data_valid(cost_data, datatype='cost_data'):
            self.cost_data = cost_data

        #internal class instance variables declaration
        self.strips = []
        self.assets = []
         
    def replace_settings(self, settings):
        """
        Replaces the settings of an existing SolarFarm instance with a new one

        :param settings: A settings dictionary which follows a YAML file 
                        structure, which defines how the solar farm layout 
                        should be generated.
        :type settings: dict
        :rtype: None
        :raises SolarFarmDataValidationError: If settingsdict does not match 
                                            the YAML representation.
        """
        if SolarFarm.is_data_valid(settings, datatype='settings'):
            self.settings = settings 

    def update_single_setting(self, setting_key, setting_val):
        """
        Updates a single setting value of an existing SolarFarm instance

        :param setting_key: A key of the YAML settings dictionary to update
        :type setting_key: str
        :param setting_val: The value of the YAML settings dictionary to set
        :type setting_key: float or string or int or bool
        :rtype: None
        :raises SolarFarmDataValidationError: If updated setting does not match 
                                            the YAML representation.
        """        
        temp_settings = copy.deepcopy(self.settings)
        temp_settings[setting_key] = setting_val 
        #TODO review with dict implementation
        if SolarFarm.is_data_valid(temp_settings): self.settings = temp_settings  


    def generate_debug_plot(self, generate_dxf=False):
        """
        TODO docustring
        """
        if generate_dxf:
            #Create a new DXF document.
            doc = ezdxf.new(dxfversion="R2010")
            #Create new layer for boundary and add
            doc.layers.add("BOUNDARY", color=0)
            doc.modelspace().add_polyline2d(
                list(self.polygon.exterior.coords),
                dxfattribs={"layer": "BOUNDARY",
                            'color':0}
            )
            #Create new layer for solar rows & add
            doc.layers.add("SOLAR_ROWS", color=2)
            for asset in self.assets:
                if asset.type == 'solar_row':
                    doc.modelspace().add_polyline2d(
                        list(asset.asset_poly.exterior.coords),
                        dxfattribs={"layer": "SOLAR_ROWS",
                                    'color':2}
                    )
            #Save the dxf to file
            doc.saveas("sfl_test.dxf")
        plt.plot(*self.polygon.exterior.xy,'k',linestyle='dashed')
        # plt.plot(*self._original_polygon.exterior.xy,'k',linestyle='dashed')
        for strip in self.strips:
            # plt.plot(*strip.box_poly.exterior.xy,'g',alpha=0.2)
            for x in strip.intersect_polys:
                plt.plot(*x.exterior.xy,'g',alpha=0.2)
        for asset in self.assets:
            if asset.type == 'solar_row':
                plt.plot(*asset.asset_poly.exterior.xy,'r',alpha=0.5)
            elif asset.type == 'road':
                plt.plot(asset.x, asset.y,'b*',alpha=0.5)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    def _internal_convert_idchar_to_row_settings(self,idchar):
        """
        Converts a single id char to a row settings dict.
        Internal to generate funciton use only

        :param idchar: A string of length one equal to the row id
        :type setting_key: str
        """
        #Validate input
        if len(idchar) != 1:
            raise SolarFarmDataValidationError(
            ("Was expecting single char to be passed to convert_idchar" 
            f", got \'{idchar}\' which is not a single char"
            ))
        #Get a list of all row settings
        all_rsettings =  self.settings['solar']['rows']['types']
        for row in all_rsettings:
            #Check for a match
            if row['id'] == idchar: return row
        #If we get here we could not find a match
        raise SolarFarmDataValidationError(
            f"Could not match row id char \'{idchar}\' to any row"
            )
        
    def _internal_calc_row_length(self,idchar):
        """
        TODO docustring
        """
        #Convert ID char to row settings
        rsettings = self._internal_convert_idchar_to_row_settings(idchar)
        #Use dim-width if portrait, else use dim-length
        if self.settings['solar']['rows']['portrait-mount']:
            mod_length = 'dim-width'
        else:
            mod_length = 'dim-length'
        #Calculate and return the length of this segment
        return (
                #Module side * num modules per string * num strings
                self.settings['solar']['module'][mod_length]
                * self.settings['solar']['strings']['mods-per-string']
                * rsettings['strings-on-row']
                #And extra space, once off per row
                + rsettings['extra-space']
                #One less module as there are N-1 spaces between N modules
                + rsettings['space-between-modules']
                * (
                    self.settings['solar']['strings']['mods-per-string']
                    * rsettings['strings-on-row']
                    - 1
                )
        )

    def generate(self):
        """
        Generates a single solar farm layout

        :param ????? TODO
        """  
        #DEBUG only rescale TODO revert or create option
        self.polygon = affinity.scale(self.polygon, xfact=2, yfact=2)
        #Move centroid to origin to handle rotating
        self.polygon = affinity.translate(self.polygon, 
                                        xoff=-self.polygon.centroid.xy[0][0], 
                                        yoff=-self.polygon.centroid.xy[1][0]
                                        )
        #Save a backup copy of original polygon perimeter for setback plotting
        self._original_polygon = copy.deepcopy(self.polygon)
        #Set site azimuth (rotate entire polygon)
        self.polygon = affinity.rotate(self.polygon,
                                        self.settings['site']['azimuth'],
                                        origin=self.polygon.centroid
                                        )
        #Apply boundary offset by shrinking the polygon
        if self.settings['site']['setback'] > 0:
            self.polygon = self.polygon.buffer(
                                            -self.settings['site']['setback'],
                                            single_sided=True
                                            )
        #(If set) generate perimeter road
        if self.settings['roads']['perimeter'] != 0:
            pass #TODO implement
        #Calculate how wide each strip needs to be
        if self.settings['solar']['rows']['portrait-mount']:
            row_width = self.settings['solar']['module']['dim-width']
        else:
            row_width = self.settings['solar']['module']['dim-length']  
        #Create strips, note the polygon has been resized by offset already
        strip_xcoords = np.arange(
                        self.polygon.bounds[0] + row_width,
                        self.polygon.bounds[2],
                        self.settings['solar']['spacing']['post-to-post']
                        ) + self.settings['solar']['spacing']['edge-offset']
        #Generate a StripPoly for each strip based on the xcoords.
        #Handle if multiple modules up/down (like 2-up portrait trackers)
        row_width *= self.settings['solar']['rows']['n-modules-updown']                  
        #Now create the strips
        for strip_id,xcoord in enumerate(strip_xcoords):
            #The strip generates its own intersections with self.polygon
            self.strips.append(StripPoly.StripPoly(
                                            minx = xcoord - row_width,
                                            miny = self.polygon.bounds[1],
                                            maxx = xcoord + row_width,
                                            maxy = self.polygon.bounds[3],
                                            strip_id = strip_id,
                                            super_solarfarm = self
                                            )
                                )
        #Check we have some strips to process
        if len(self.strips) == 0: 
            raise SolarFarmDataValidationError(
                ("Solar farm cannot be generated, no rows could be generated " 
                ", confirm correct land scale, solar module sizing & spacing"
                ))
        #Prepare to generate solar layout
        #Get the max length of the strip intersection polygon
        #So we know where to stop the iteration
        max_intpoly_length = max(
                                [x.add_solar_rows(calc_max_only=True) 
                                for x in self.strips]
                                )
        #Generate the expanded layout list now we know the max length
        self.expanded_layout_list = []
        self.expanded_length_list = []
        for layout in self.settings['solar']['rows']['layout-templates']:
            #Split on square brackets, only one square bracket per row
            if '[' in layout and ']' in layout:
                #There is a square bracket to expand
                layout_start, layout_temp = layout.split('[')
                layout_loop, layout_end = layout_temp.split(']')
                #Loop over the square brackets until the length is greater
                #than the maximum poly length
                exp_count = 1
                # row_types = self.settings['solar']['rows']['types']
                while True:
                    #Create the layout code
                    layout_code = (layout_start 
                                + layout_loop*exp_count 
                                + layout_end)
                    #Calculate its length
                    length = 0
                    for char in layout_code:
                        if char == 'r':
                            length += self.settings['roads']['perimeter']['clear-width']
                        else:
                            #TODO validate, assume is char
                            length += self._internal_calc_row_length(char)
                    #Check if length is too long
                    if length < max_intpoly_length:
                        #Store as valid and repeat the while true loop
                        #With the next iteration up (i.e. [3r]3 = 3r3 valid, 
                        # try 3r3r3)
                        exp_count += 1
                        self.expanded_layout_list.append(layout_code)
                        self.expanded_length_list.append(length)
                    else:
                        #This is longer than the poly, no more iters needed
                        break  
            else:
                #This is a non-iterative layout option, so check if it is 
                #shorter than max length and if so add it
                length = 0
                for char in layout:
                    if char == 'r':
                        length += self.settings['roads']['perimeter']['clear-width']
                    else:
                        #TODO validate, assume is char
                        length += self._internal_calc_row_length(char)
                #Check if length is too long
                if length < max_intpoly_length:
                    #Store as a valid option
                    self.expanded_layout_list.append(layout)
                    self.expanded_length_list.append(length)
        #Each strip now uses expanded_layout_list and expanded_length_list
        #to create the solar rows
        for strip in self.strips:
            strip.add_solar_rows(
                                calc_max_only=False,  
                                expanded_layout_list = self.expanded_layout_list,
                                expanded_length_list = self.expanded_length_list,
                                )
        #TODO review below actions in line with pipeline
        #generate perimeter road if set
        #place main substation area
        #create strips
        #create rows
        #create roads
        #place inverters
        #place combiner boxes
        #place string cables
        #place hv cables
        #cleanup (check for duplicates etc)
        #return results data
        results_data = {
            'generation_time': 0,
            'n_modules' : 123,
            'mwp' : 456,
            'total_cost' : 100000
        }
        #If rotated rotate all objects back to original
        if abs(self.settings['site']['azimuth']) > 0:
            #internal helper function for neater code
            def _rotate_helper(poly_in):
                return affinity.rotate(poly_in,
                                -self.settings['site']['azimuth'],
                                origin=self.polygon.centroid
                                )
            #Rotate the main polygon back to original
            self.polygon = _rotate_helper(self.polygon)
            #Rotate each strip and intersection strip to original
            for strip in self.strips:
                strip.box_poly = _rotate_helper(strip.box_poly) 
                for ipoly,poly in enumerate(strip.intersect_polys):
                    strip.intersect_polys[ipoly] = _rotate_helper(poly)
            #Rotate assets to original
            for asset in self.assets:
                asset.asset_poly = _rotate_helper(asset.asset_poly)
            
        #all complete
        return True

#STATIC METHODS OF SolarFarm CLASS BEGIN---------------------------------------
    @staticmethod
    def is_data_valid(poly_coords, datatype='polygon'):
        if datatype == 'polygon':
            #Check for a list being passed as input.
            if not isinstance(poly_coords, list): 
                raise SolarFarmDataValidationError(
                    ("Solar farm cannot be generated, coordinate " 
                    "points need to be in list of tuples format"
                    ))
            #Check for at least three items in the list.
            if len(poly_coords) < 3: 
                raise SolarFarmDataValidationError(
                    ("Solar farm cannot be generated, number of "
                    "coordinates passed to generator needs to be at least 3"
                    ))
            #Check that each item in the list is a tuple. 
            if any([not isinstance(x,tuple) for x in poly_coords]): 
                raise SolarFarmDataValidationError(
                    ("Solar farm cannot be generated, an item in the " 
                    "poly_coords list was not a tuple."
                    ))
            #Check if any tuple is more, or less, than 2 items long.
            if any([len(x) != 2 for x in poly_coords]): 
                raise SolarFarmDataValidationError(
                    ("Solar farm cannot be generated, a coordinate "
                    "point was identified which was not a tuple, or is not a " 
                    "tuple of 2 coordinates. Only 2 dimensions are supported."
                    ))
            #For each tuple, check that each value is numeric
            for tup in poly_coords:
                if any([not isinstance(x,(int, float)) for x  in tup]): 
                    raise SolarFarmDataValidationError(
                        ("Solar farm cannot be generated, a coordinate point "
                        f"in tuple {tup} is not a valid number."
                        ))
            #Create temp polygon and check its bounds
            if len(Polygon(poly_coords).exterior.coords) < 2:
                    raise SolarFarmDataValidationError(
                    ("Solar farm cannot be generated, the polygon bounds form "
                    "a straight line (dimension of poly bounds < 2)."
                    ))
            
            #If we get here validation was passed
            return True
       
        if datatype == 'settings':
            pass
        if datatype == 'cost_data':
            pass

    @staticmethod
    def generate_default_settings():
        #TODO clean up
        with open(Path(__file__).parent / "default_settings.yaml", "r") as stream:
            return yaml.safe_load(stream)


    @staticmethod
    def generate_default_cost_data():
        return {}
#STATIC METHODS OF SolarFarm CLASS END------------------------------------------


#DEBUG AREA FOR TESTING ONLY - run as imported class normally
# coords = [(0,0), (0,2000), (2000,2000), (2000,1500), (1000,750), (1000,500), (2000,250), (2000,0)]
coords = [(0,0), (0,200), (200,200), (200,150), (100,75), (100,50), (200,25), (200,0)]
sftest = SolarFarm(coords)
sftest.generate()
sftest.generate_debug_plot(generate_dxf=True)
