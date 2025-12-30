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

def montecarlo_pricing(S,T,K,sigma,r  ):
    ST = S*np((r - ((sigma**2)/2))*T + sigma*np.sqrt(T)*np.random.normal())
    payoffs = np.maximum(ST - K , 0)
    return np.exp(-(r*T))*np.mean(payoffs)

    #look for formulas and theory while you code
def calculate_greeks():
     # params: S, K, r, sigma, T, iterations=1000000
     #  Generate random shocks once to use for all perturbations
     # Define a small 'bump' (h)
     h = 0.01 * S 
      # --- DELTA & GAMMA ---
    # We need price at S+h, S, and S-h with montecarlo
    # create greeks from the prices
    # --- VEGA ---
    # We need price at sigma + h
    #return the greeks