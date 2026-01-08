import numpy as np
from vanilla_option import Vanilla 
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
        
        if return_payoffs:
            return {
                'name': self.name,
                'price':price,
                'payoff':payoff
                }
        else:
            return {
                'name':self.name,
                'price':price
                }

    def bumps(self,S, r,sigma,Z,K,T):
        vanilla =Vanilla(K=K,T=T,name=self.name,option_type=self.option)
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
    
    def greeks(self,greek,K,S,r,sigma,n_sims):
        # Use same random shocks for all bumps (variance reduction) just like you did in antitethic in the price class
        Z = self.rng.standard_normal(size=n_sims) 

        prices = self.bumps(S, r,sigma,Z,K=K)
        if greek.lower() == 'delta':
            # formula = (V*(S_o + h) - V*(S_o - h))/(2*h)
            delta = (prices['price + bump'] - prices['price - bump'])/2*prices['price bump']
            return delta

        elif greek.lower() == 'gamma':
            # formula = (V*(S_o + h) - (2*(V)*(S_o) + V*(S_o - h) ))/ (h**2)
            gamma = (prices['price + bump'] - 2*(prices['price']) + prices['price - bump'])/prices['price bump']**2
            return gamma
        
        elif greek.lower() == 'vega':
           # formula = (V*(sigma + h) - V*(sigma - h))/(2*h)
           vega = (prices['sigma + bump'] - prices['sigma - bump'])/2*prices['sigma bump']
           return vega

        else:
            raise ValueError('greek can only be delta, gamma, vega')
       
    
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
  
  vanilla_call = Vanilla(option_type='call',name='FX-swap',K=params['K'],T=params['T'],)
  vanilla_put = Vanilla(option_type='put', name='FX-swap',K=params['K'],T=params['T'])

  engine_call= MonteCarloEngine(option=vanilla_call.option_type,name=vanilla_call.name,rng=np.random.default_rng(42))
  engine_put= MonteCarloEngine(option=vanilla_put.option_type,name=vanilla_put.name,rng=np.random.default_rng(42))
    
  call_price = engine_call.price(**params,method='plain')
  put_price = engine_put.price(**params, method='plain')
    
  #print(f"ATM {vanilla_call.name} Price: ${call_price}")
  #print(f"ATM {vanilla_put.name} Price: ${put_price}")
  #print(f"Put-Call Parity Check: C - P = {call_price['price'] - put_price['price']}") 
  #print(f"S - K*exp(-rT) = {params['S'] - params['K']*np.exp(-params['r']*params['T'])}")
  #print("✓ Test passed if values are close")

#ax = test_basic_pricing()
       

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
    
    print(f"Delta: {delta:.4f}")
    print(f"Gamma: {gamma:.6f}")
    print(f"Vega: {vega:.4f}")
    
    print("\nBlack-Scholes Theoretical Values (ATM Call):")
    print("  Delta: ~0.6368")
    print("  Gamma: ~0.0198")
    print("  Vega: ~39.74")
    
    # Check if values are in reasonable range
    checks = []
    checks.append(("Delta", 0.55 <= delta <= 0.70, delta))
    checks.append(("Gamma", 0.015 <= gamma <= 0.025, gamma))
    checks.append(("Vega", 35 <= vega <= 45, vega))
    
    print("\nValidation:")
    all_passed = True
    for name, passed, value in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {value:.4f}")
        all_passed = all_passed and passed
    
    if all_passed:
        print("\n✅ All Greeks PASSED")
    else:
        print("\n❌ Some Greeks out of expected range")
    
    return {'delta': delta, 'gamma': gamma, 'vega': vega}

greeks = test_greeks()
print(greeks)


         