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
    
    def bumps(self,S, r,sigma,Z):
        h = S * 0.01
        vol_h = 0.01
        price_plus = Vanilla.discounted_payoff(ST=Vanilla.simulate_terminal(S=S + h,r=r,sigma=sigma, Z=Z),r=r)
        price = Vanilla.discounted_payoff(ST=Vanilla.simulate_terminal(S=S ,r=r,sigma=sigma, Z=Z),r=r)
        price_minus = Vanilla.discounted_payoff(ST=Vanilla.simulate_terminal(S=S - h,r=r,sigma=sigma, Z=Z),r=r)
        vol_plus = Vanilla.discounted_payoff(ST=Vanilla.simulate_terminal(S=S ,r=r,sigma=sigma + vol_h, Z=Z),r=r)
        vol_minus = Vanilla.discounted_payoff(ST=Vanilla.simulate_terminal(S=S,r=r,sigma=sigma - vol_h, Z=Z),r=r)
        return {
            'price bump' : h,
            'sigma bump' : vol_h,
            'price + bump' : price_plus,
            'price - bump' : price_minus,
            'price': price,
            'sigma + bump': vol_plus,
            'sigma - bump': vol_minus
        }
    
    def greeks(self,greek,S,r,sigma,Z):
        prices = self.bumps(S, r,sigma,Z)
        if greek.lower() == 'delta':
            # formula = (V*(S_o + h) - V*(S_o - h))/(2*h)
            delta = (prices['price + bump'] - prices['price - bump'])/2*prices['price bump']
            return delta

        if greek.lower() == 'gamma':
            # formula = (V*(S_o + h) - (2*(V)*(S_o) + V*(S_o - h) ))/ (h**2)
            gamma = (prices['price + bump'] - 2*(prices['price']) + prices['price - bump'])/prices['price bump']**2
            return gamma
        
        if greek.lower() == 'vega':
           # formula = (V*(sigma + h) - V*(sigma - h))/(2*h)
           vega = (prices['sigma + bump'] - prices['sigma - bump'])/2*prices['sigma bump']
           return vega

        else:
            raise ValueError('greek can only be delta, gamma, vega')
       
    

         