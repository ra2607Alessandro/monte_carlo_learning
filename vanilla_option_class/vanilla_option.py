import numpy as np

class Vanilla:

    def __init__(self,K,T,option_type):
        self.K = K
        self.T = T
        self.option_type = option_type

    def payoff(self,ST):
        
        payoff = 0
        if self.option_type == "call":
            payoff = np.maximum(ST-self.K,0)
        elif self.option_type == "put":
            payoff = np.maximum(self.K - ST, 0)
        elif len(ST)> 1:
            ST_terminal = ST[:,-1]
            arr = np.array(ST_terminal)
            return arr
        
        return payoff
    
    def simulate_terminal(self,S,r,sigma,iters):
        Z = np.random.normal(size=iters)
        ST = S*np.exp((r-0.5*(sigma**2))*self.T + sigma*np.sqrt(self.T)*Z)
        return ST
    
    def discounted_payoff(self,r,ST):
        return np.exp(-r*self.T)*self.payoff(ST)