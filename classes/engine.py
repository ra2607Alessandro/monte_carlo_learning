import numpy as np

class MonteCarloEngine:

    def __init__(self,option, rng = None):
        self.option = option
        if not rng == None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()
        
    def price(self, r,sigma, n_paths,method ,return_payoffs = False):
        if method == 'plain':
            Z = self.rng
        if method == 'antithetic':
            arr = (self.rng)/2
            arr_simmetric = - arr
            Z = np.concatenate([arr,arr_simmetric])
        else:
            raise ValueError("method is either 'plain' or 'antithetic'")
        
        #pricing equation
        
        