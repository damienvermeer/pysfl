#enums in this document
from enum import Enum

class POITypes(Enum):
    ROAD_NODE = 0
    SOURCE_STRING_CABLE = 1 #todo implement
    INVERTER_LOCATION = 2 #todo implement

class SPDataTypes(Enum):
    SOLAR_ROW = 0
    ROAD_NODE = 1