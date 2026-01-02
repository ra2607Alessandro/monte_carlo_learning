import numpy as np

class Vanilla:

    def __init__(self,K,T,option_type):
        self.K = K
        self.T = T
        self.option_type = option_type

    def payoff(self,S,r,sigma,iters):
        Z = np.random.normal(size=iters)
        ST = S*np.exp((r-0.5*(sigma**2)) + sigma*np.sqrt(self.T)*Z)
        payoff = 0
        if self.option_type == "call":
            payoff = np.maximum(ST-self.K,0)
        elif self.option_type == "put":
            payoff = np.maximum(self.K - ST, 0)
        
        return payoff

        