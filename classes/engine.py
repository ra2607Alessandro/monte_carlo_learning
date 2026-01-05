import numpy as np

class MonteCarloEngine:

    def __init__(self,option, rng = None):
        self.option = option
        if not rng == None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()
        
    def price(self, r,sigma, n_paths,method = 'plain',Z = None,return_payoffs = False):
        