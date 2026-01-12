import numpy as np
from vanilla_option import Vanilla 
import matplotlib.pyplot as plt
from scipy.stats import norm as norm

class MonteCarloEngine:

    def __init__(self,name,option, rng = None):
        self.option = option
        self.name = name
        if not rng == None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()
        
    def price(self,S, r,sigma,K, T,n_sims,method ,return_payoffs = False):
        if method == 'plain':
            Z = np.random.standard_normal(size=n_sims)
        elif method == 'antithetic':
            arr =  np.random.standard_normal(size=int((n_sims)/2))
            arr_simmetric = - arr
            Z = np.concatenate([arr,arr_simmetric])
        else:
            raise ValueError("method is either 'plain' or 'antithetic'")
        
        #pricing equation
        vanilla =Vanilla(K=K,T=T,name=self.name,option_type=self.option)
        ST = vanilla.simulate_terminal(S=S,r=r,sigma=sigma,Z=Z)
        payoff = vanilla.payoff(ST=ST)
        price = np.exp(- r*T)*np.mean(payoff)
        discounted = vanilla.discounted_payoff(ST=ST,r=r)
        SE = self.SE(discounted_payoff=discounted,price=price,n_sims=n_sims)
        if return_payoffs:
            return {
                'name': self.name,
                'price': float(price),
                'Standard Error Deviation': float(SE),
                'payoff': payoff,
                'discounted_payoffs': discounted
            }
        else:
            return {
                'name': self.name,
                'price': float(price),
                'Standard Error Deviation': float(SE)
            }
    
    def SE(self,discounted_payoff, price,n_sims):
        #implement a standard error deviation
        variance = np.sqrt(sum((discounted_payoff-price)**2)/(n_sims-1))
        SE = variance/np.sqrt(n_sims)
        return SE


    def bumps(self,S, r,sigma,Z,K,T):
        vanilla =Vanilla(K=K,T=T,name=self.name,option_type=self.option)
        h = S * 0.01
        vol_h = 0.01
        price_plus = np.mean(vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S + h,r=r,sigma=sigma, Z=Z),r=r))
        price = np.mean(vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S ,r=r,sigma=sigma, Z=Z),r=r))
        price_minus = np.mean(vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S - h,r=r,sigma=sigma, Z=Z),r=r))
        vol_plus = np.mean(vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S ,r=r,sigma=sigma + vol_h, Z=Z),r=r))
        vol_minus = np.mean(vanilla.discounted_payoff(ST=vanilla.simulate_terminal(S=S,r=r,sigma=sigma - vol_h, Z=Z),r=r))
        return {
            'price bump' : h,
            'sigma bump' : vol_h,
            'price + bump' : price_plus,
            'price - bump' : price_minus,
            'price': price,
            'sigma + bump': vol_plus,
            'sigma - bump': vol_minus
        }
    
    def greeks(self,greek,K,S,T,r,sigma,n_sims):
        # Use same random shocks for all bumps (variance reduction) just like you did in antitethic in the price class
        Z = self.rng.standard_normal(size=n_sims) 

        prices = self.bumps(S, r,sigma,Z,K=K,T=T)
        if greek.lower() == 'delta':
            # formula = (V*(S_o + h) - V*(S_o - h))/(2*h)
            delta = (prices['price + bump'] - prices['price - bump'])/(2*prices['price bump'])
            return delta

        elif greek.lower() == 'gamma':
            # formula = (V*(S_o + h) - (2*(V)*(S_o) + V*(S_o - h) ))/ (h**2)
            gamma = (prices['price + bump'] - 2*(prices['price']) + prices['price - bump'])/(prices['price bump']**2)
            return gamma
        
        elif greek.lower() == 'vega':
           # formula = (V*(sigma + h) - V*(sigma - h))/(2*h)
           vega = (prices['sigma + bump'] - prices['sigma - bump'])/(2*prices['sigma bump'])
           return vega
        
        elif greek.lower() == 'rho':
        #formula:  K * t * N(d_2)
            d1 = sigma*np.sqrt(T)
            cumulative_distr = norm.cdf(d1-sigma*np.sqrt(T))
            rho =  K * T * np.exp(-(r*T)) * cumulative_distr 
            return rho

        else:
            raise ValueError('greek can only be delta, gamma, vega, rho')
        
    def plot_Convergence_Plot(self,price):
        # Accept either:
        # - dict returned by `price(..., return_payoffs=True)` containing 'discounted_payoffs'
        # - an array-like of (discounted) payoffs
        discounted = None
        if isinstance(price, dict):
            if 'discounted_payoffs' in price:
                discounted = np.asarray(price['discounted_payoffs'])
            elif 'payoff' in price:
                discounted = np.asarray(price['payoff']) * np.exp(-0)  # not discounted
        else:
            try:
                discounted = np.asarray(price)
            except Exception:
                discounted = None

        if discounted is None or discounted.size == 0:
            print('No payoff array found to plot convergence.')
            return

        running_mean = np.cumsum(discounted) / np.arange(1, discounted.size + 1)

        plt.figure(figsize=(8, 4))
        plt.plot(running_mean, linewidth=1)
        plt.xlabel("Number of Iterations")
        plt.ylabel("Option Price")
        plt.title(f"Convergence Plot: {self.name}")
        plt.grid(alpha=0.3)
        plt.show()

        return running_mean
    
def test_basic_pricing():
  """Test basic call and put pricing."""
  #print("\n" + "="*60)
  #print("TEST 1: Basic Call and Put Pricing")
  #print("="*60)
    
   
    
  params = {
        'S': 100,
        'K': 100,
        'r': 0.05,
        'sigma': 0.2,
        'T': 1.0,
        'n_sims': 100000
    }
  
  vanilla_call = Vanilla(option_type='call',name='FX-swap',K=params['K'],T=params['T'])
  vanilla_put = Vanilla(option_type='put', name='FX-swap',K=params['K'],T=params['T'])

  engine_call= MonteCarloEngine(option=vanilla_call.option_type,name=vanilla_call.name,rng=np.random.default_rng(42))
  engine_put= MonteCarloEngine(option=vanilla_put.option_type,name=vanilla_put.name,rng=np.random.default_rng(42))
    
  call_price = engine_call.price(**params,method='plain',return_payoffs=True)
  put_price = engine_put.price(**params, method='plain',return_payoffs=True)
  
  plot_call= engine_call.plot_Convergence_Plot(call_price)
  plot_put= engine_put.plot_Convergence_Plot(put_price)
    
  #print(f"ATM {vanilla_call.name} Price: ${call_price}")
  #àprint(f"ATM {vanilla_put.name} Price: ${put_price}")
  #print(f"Put-Call Parity Check: C - P = {call_price['price'] - put_price['price']}") 
  #print(f"S - K*exp(-rT) = {params['S'] - params['K']*np.exp(-params['r']*params['T'])}")
  #print("✓ Test passed if values are close")
  #print(plot_put)

ax = test_basic_pricing()
#print(ax)       

def test_greeks():
    """Test Greeks calculation."""
    print("\n" + "="*60)
    print("TEST 2: Greeks Calculation")
    print("="*60)
    
    params = {
        'S': 100,
        'K': 100,
        'r': 0.05,
        'sigma': 0.2,
        'T': 1.0,
        'n_sims': 100000
    }
    
    engine = MonteCarloEngine(
        option='call', 
        name='Test', 
        rng=np.random.default_rng(42)
    )


    
    delta = engine.greeks('delta', **params)
    gamma = engine.greeks('gamma', **params)
    vega = engine.greeks('vega', **params)
    rho = engine.greeks('rho',**params)
    
    print(f"Delta: {delta}")
    print(f"Gamma: {gamma}")
    print(f"Vega: {vega}")
    print(f'Rho: {rho}')

    print("\nBlack-Scholes Theoretical Values (ATM Call):")
    print("  Delta: ~0.6368")
    print("  Gamma: ~0.0198")
    print("  Vega: ~39.74")
    
    if 0.55 <= delta <= 0.70:
        print("✅Delta Passed")
    else: 
        print("❌Delta did not Pass")
    if 0.015 <= gamma <= 0.025 :
        print("✅Gamma Passed") 
    else:
        print("❌Gamma did not Pass")
    if 35 <= vega <= 45:
        print("✅Vega Passed")
    else:
        print("❌Vega did not pass")
    if 4.0 <= rho <= 9.5:
        print("✅Rho Passed")
    else:
        print("❌Rho did not Pass")

    return {'delta': float(delta), 'gamma': float(gamma), 'vega': float(vega),'rho':float(rho)}

#greeks = test_greeks()
#print(greeks)


         