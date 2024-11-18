# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18

class Ant:
    pass

class World:
    def __init__(self, n, m, q, alpha, beta, rho):
        self.n = n
        self.m = m
        self.q = q
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.tau = [[1.0 for i in range(n)] for j in range(n)]
        self.eta = [[1.0 / (1 + abs(i - j)) for i in range(n)] for j in range(n)]
        self.delta_tau = [[0.0 for i in range(n)] for j in range(n)]
        self.ant = [Ant(self) for i in range(m)]
        self.best_ant = Ant(self)
        self.best_ant.path = [0 for i in range(n)]
        self.best_ant.path[0] = 0
        self.best_ant.path[n - 1]
    