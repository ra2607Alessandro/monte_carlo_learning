import pandas as pd
import numpy as np
# The Math: Finite Difference Greeks
#Since Monte Carlo gives us a "price," we calculate Greeks by bumping the input slightly and seeing how the price changes.
#Delta :
# formula = (V*(S_o + h) - V*(S_o - h))/(2*h)
 ##(Central Difference)
#Gamma :
# formula = (V*(S_o + h) - (2*(V)*(S_o) + V*(S_o - h) ))/ (h**2)
 
#Vega: 
# formula = (V*(sigma + h) - V*(sigma - h))/(2*h)

def montecarlo_pricing(S,T,K,sigma,r ,z ):
    ST = S*np((r - ((sigma**2)/2))*T + sigma*np.sqrt(T)*z)
    payoffs = np.maximum(ST - K , 0)
    return np.exp(-(r*T))*np.mean(payoffs)

    #look for formulas and theory while you code
def calculate_greeks(S,K,T,sigma,r,iters:1000000 ):
     # params: S, K, r, sigma, T, iterations=1000000
     #  Generate random shocks once to use for all perturbations
    Z = np.random.normal(size=iters)
     # Define a small 'bump' (h)
    h = 0.01 * S 
      # --- DELTA & GAMMA ---
    # We need price at S+h, S, and S-h with montecarlo
    price_plus = montecarlo_pricing(S + h,T,K,sigma,r,Z)
    price_mid = montecarlo_pricing(S,T,K,sigma,r,Z)
    price_minus = montecarlo_pricing(S - h, T,K,sigma,r,Z) 

    # create greeks from the prices
    delta = (price_plus - price_minus)/2*h
    gamma = (price_plus - 2*(price_mid) + price_minus)/(h**2)
    # --- VEGA ---
    # We need price at sigma + h
    
    #return the greeks