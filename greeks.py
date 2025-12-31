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
    ST = S*np.exp((r - ((sigma**2)/2))*T + sigma*np.sqrt(T)*z)
    payoffs = np.maximum(ST - K , 0)
    return np.exp(-(r*T))*np.mean(payoffs)

    #look for formulas and theory while you code
def calculate_greeks(S,K,T,sigma,r,iterations ):
     # params: S, K, r, sigma, T, iterations=1000000
     #  Generate random shocks once to use for all perturbations
    Z = np.random.normal(size=iterations)
     # Define a small 'bump' (h)
    h = 0.01 * S 
    vol_h = 0.01 # 1% bump for Vega
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
    d_sigma_plus = montecarlo_pricing(S, T,K,sigma + vol_h,r,Z)
    d_sigma_minus = montecarlo_pricing(S,T,K,sigma - vol_h,r,Z)
    vega = (d_sigma_plus - d_sigma_minus)/(2*vol_h)

    #return the greeks as a dictionary (object)
    return {
        "Price": price_mid,
        "Delta": delta,
        "Gamma": gamma,
        "Vega": vega
    }

results = calculate_greeks(S=100, K=100, r=0.05, sigma=0.2, T=1, iterations= 1000000  )

for greek, value in results.items(): #since the greeks come as dictionaries (objects), items paires the name with the value
    print(f"{greek}: {value:.2f}") # .4f just says to reduce the number to 4 decimals after the point

    # vega is supposed to be bigger because if you bump up sigma it results in a much bigger bump than if you bump up S a bit
