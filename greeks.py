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
    ST = S*np.exp((r - (0.5*((sigma**2)/2)))*T + sigma*(np.sqrt(T)*np.random.normal()))
    payoff = np.maximum(ST - K, 0)
    return np.exp(-1*(r*T)) * np.mean(payoff)