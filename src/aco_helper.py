# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-20
# file: aco_helper.py

import numpy as np

def euclidean_distance(node_first, node_second):
    return np.round(np.sqrt((node_first.x - node_second.x)**2 + (node_first.y - node_second.y)**2), 3)
