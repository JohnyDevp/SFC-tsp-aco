# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-20
# file: aco_settings.py

from enum import Enum
# set verbose
class ACS2GUIMessage(Enum):
    GLOBAL_PHEROMONE_UPDATE_DONE = 1
    
global VERBOSE
VERBOSE = False