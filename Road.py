from shapely.geometry import LineString, LinearRing

class Road:

    def __init__(
                self,
                super,
                nodes                                     
                ):
        
        #Create road
        self.super = super
        self.asset_type = 'road' #TODO enum
        self.nodes = nodes

        #expand road from linear into polygon
        if self.nodes[0].code == -1:
            #Perimeter road so use those settings
            roadwidth = self.super.settings['roads']['perimeter']['road-width']
            self.asset_poly = LinearRing([x.asset_poly for x in self.nodes])
        else:
            #Internal road so use those settings
            #TODO no internal road settings yet!
            roadwidth = self.super.settings['roads']['perimeter']['road-width']
            self.asset_poly = LineString([x.asset_poly for x in self.nodes])
        
        #Expand based on road width
        self.asset_poly = self.asset_poly.buffer(
            roadwidth/2,
            resolution=32,
            join_style=2,
        )