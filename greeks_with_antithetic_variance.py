# The Math: Finite Difference Greeks
#Since Monte Carlo gives us a "price," we calculate Greeks by bumping the input slightly and seeing how the price changes.
#Delta :
# formula = (V*(S_o + h) - V*(S_o - h))/(2*h)
 ##(Central Difference)
#Gamma :
# formula = (V*(S_o + h) - (2*(V)*(S_o) + V*(S_o - h) ))/ (h**2)
 
#Vega: 
# formula = (V*(sigma + h) - V*(sigma - h))/(2*h)
import numpy as np
import pandas as pd

def mc_pricing(S,T,K,sigma,r ,z ):
    price = S*np.exp((r - (sigma**2)/2) + sigma*np.sqrt(T)*z )
    payoff = np.maximum(price - K, 0)
    return  np.exp(- (r * T))*np.mean(payoff)

def calc_greeks(S,T,K,sigma,r ,iterations):

    Z = np.random.normal(size=(0.5*iterations))
    Z_simmetry = -1*Z

    arr = np.concatenate(Z,Z_simmetry) # with np.concatenate you merge two lists together

    h = S * 0.01
    vol_h = 0.01

    price_minus = mc_pricing(S - h,T,K,sigma, r, arr)
    price_plus = mc_pricing(S + h, T, K, sigma , r, arr)
    price_mid = mc_pricing(S,T,K,sigma,r,arr)

    delta = (price_plus - price_minus)/(2*h)
    gamma = (price_plus -2*(price_mid) + price_minus)/(h**2)

    price_vol_min_h = mc_pricing(S,T,K,sigma - vol_h,r,arr)
    price_vol_plus_h = mc_pricing(S,T,K,sigma + vol_h,r,arr)

    vega = (price_vol_plus_h - price_vol_min_h)/(2*vol_h)

    return {
        "Price" : price_mid,
        "Delta" : delta,
        "Gamma" : gamma,
        "Vega" : vega
    }

result = calc_greeks(S=100, K=100, r=0.05, sigma=0.2, T=1, iterations= 1000000  )

for greek,value in result.items():
    print(f"{greek} : {value: .2f}")



    