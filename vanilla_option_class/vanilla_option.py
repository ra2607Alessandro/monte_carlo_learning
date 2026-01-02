import numpy as np

class Vanilla:

    def __init__(self,K,T,option_type):
        if K > 0:
          self.K = K
        if T > 0:
          self.T = T
        if option_type == "call" or option_type == "put" :
          self.option_type = option_type


    def payoff(self,ST):
        ST_arr = np.array(ST)
        payoff = 0
        if self.option_type == "call":
            payoff = np.maximum(ST-self.K,0)
        elif self.option_type == "put":
            payoff = np.maximum(self.K - ST, 0)
        elif ST_arr.ndim == 0:
           ST_terminal = ST_arr.item()
           payoff = np.maximum(ST_terminal-self.K,0)
        elif ST_arr.ndim == 1:
           ST_terminal = ST_arr
           payoff = np.maximum(ST_terminal-self.K,0)
        elif ST_arr.ndim == 2:
           ST_terminal = ST_arr[:,-1]
           payoff = np.maximum(ST_terminal-self.K,0)
        
        return payoff
    
    def simulate_terminal(self,S,r,sigma,iters):
        Z = np.random.normal(size=iters)
        ST = S*np.exp((r-0.5*(sigma**2))*self.T + sigma*np.sqrt(self.T)*Z)
        return ST
    
    def discounted_payoff(self,r,ST):
        return np.exp(-r*self.T)*self.payoff(ST)