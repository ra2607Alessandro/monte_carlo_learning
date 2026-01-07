import numpy as np
from vanilla_option import Vanilla 
class MonteCarloEngine:

    def __init__(self,option, rng = None):
        self.option = option
        if not rng == None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()
        
    def price(self,name,S, r,sigma,K, T,n_sims,method ,return_payoffs = False):
        if method == 'plain':
            Z = self.rng
        elif method == 'antithetic':
            arr = np.random.standard_normal((n_sims)/2)
            arr_simmetric = - arr
            Z = np.concatenate([arr,arr_simmetric])
        else:
            raise ValueError("method is either 'plain' or 'antithetic'")
        
        #pricing equation
        vanilla =Vanilla(K=K,T=T,name=name,option_type=self.option)
        ST = vanilla.simulate_terminal(S=S,r=r,sigma=sigma,Z=Z)
        payoff = vanilla.payoff(ST=ST)
        price = np.exp(- r*T)*np.mean(payoff)
        
        if return_payoffs:
            return {
                'name': vanilla.name,
                'price':price,
                'payoff':payoff
                }
        else:
            return {
                'name':vanilla.name,
                'price':price
                }

    def bumps(self,name,S, r,sigma,Z,K,T):
        vanilla =Vanilla(K=K,T=T,name=name,option_type=self.option)
        h = S * 0.01
        vol_h = 0.01
        price_plus = vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S + h,r=r,sigma=sigma, Z=Z),r=r)
        price = vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S ,r=r,sigma=sigma, Z=Z),r=r)
        price_minus = vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S - h,r=r,sigma=sigma, Z=Z),r=r)
        vol_plus = vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S ,r=r,sigma=sigma + vol_h, Z=Z),r=r)
        vol_minus = vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S,r=r,sigma=sigma - vol_h, Z=Z),r=r)
        return {
            'price bump' : h,
            'sigma bump' : vol_h,
            'price + bump' : price_plus,
            'price - bump' : price_minus,
            'price': price,
            'sigma + bump': vol_plus,
            'sigma - bump': vol_minus
        }
    
    def greeks(self,greek,S,r,sigma,n_sims):
        # Use same random shocks for all bumps (variance reduction) just like you did in antitethic in the price class
        Z = np.random.standard_normal(n_sims) 

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
       
    
def test_basic_pricing():
  """Test basic call and put pricing."""
  print("\n" + "="*60)
  print("TEST 1: Basic Call and Put Pricing")
  print("="*60)
    
   
    
  params = {
        'S': 100,
        'K': 100,
        'r': 0.05,
        'sigma': 0.2,
        'T': 1.0,
        'n_sims': 100000
    }
  
  vanilla_call = Vanilla(option_type='call',name='FX-swap',K=params['K'],T=params['T'],)
  vanilla_put = Vanilla(option_type='put', name='FX-swap',K=params['K'],T=params['T'])

  engine_call= MonteCarloEngine(option=vanilla_call.option_type,rng=np.random.default_rng(42))
  engine_put= MonteCarloEngine(option=vanilla_put,rng=np.random.default_rng(42))
    
  call_price = engine_call.price(**params, name=vanilla_call.name,method='plain')
  put_price = engine_put.price(**params,name=vanilla_put.name, method='plain')
    
  print(f"ATM {vanilla_call.name} Price: ${call_price:.4f}")
  print(f"ATM {vanilla_put.name} Price: ${put_price:.4f}")
  print(f"Put-Call Parity Check: C - P = {call_price - put_price:.4f}") 
  print(f"S - K*exp(-rT) = {params['S'] - params['K']*np.exp(-params['r']*params['T']):.4f}")
  print("✓ Test passed if values are close")

ax = test_basic_pricing()
print(ax)
         