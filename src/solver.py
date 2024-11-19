# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18

from aco import ACOWorld

class ACOSolver:
    def __init__(self, n, m, q, alpha, beta, rho):
        self.world = ACOWorld(n, m, q, alpha, beta, rho)
    
    def solve(self):
        pass