import numpy as np
from vanilla_option import Vanilla
class MonteCarloEngine:

    def __init__(self,option, rng = None):
        self.option = option
        if not rng == None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()
        
    def price(self,S, r,sigma,K, T,method ,return_payoffs = False):
        if method == 'plain':
            Z = self.rng
        if method == 'antithetic':
            arr = (self.rng)/2
            arr_simmetric = - arr
            Z = np.concatenate([arr,arr_simmetric])
        else:
            raise ValueError("method is either 'plain' or 'antithetic'")
        
        #pricing equation
        Vanilla.__init__(K=K,T=T,option_type=self.option)
        price = Vanilla.simulate_terminal(S=S,r=r,sigma=sigma,Z=Z)
        return_payoffs = Vanilla.payoff(ST=price)
        return return_payoffs
        
        