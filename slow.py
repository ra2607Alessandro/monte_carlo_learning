import math
import numpy as np
import pandas as pd
import datetime
import scipy.stats as stats
import matplotlib.pyplot as plt
from revised_lcg import  a, seed, size, m, c, lcg

S = 101.45
K = 98.01
vol = 0.0991
r = 0.01
N = 10
M = 1000

market_value = 3.86

T = ((datetime.date(2025,4,26) - datetime.date(2024,11,30)).days + 1)/365

# Drift and Diffusion: log(S) + (r - 0.5*vol**2)*dt + vol*np.sqrt(dt)
dt = T/N
log_price = np.log(S)
mem_II = (r - 0.5*vol**2)*dt
mem_III = vol*np.sqrt(dt)
MC = 0




# Standard Error Placeholders
Sum_CT = 0
Sum_CT_2 = 0



# Heart of the Monte Carlo Method
for i in range(M):
   MC = log_price
   for j in range (N):
      MC = MC + mem_II + mem_III*np.random.normal() 
# Markov Chain: lnS + nudt*dt + volsdt*Z
      real_price = np.exp(MC)
      payoff = max(0,real_price - K )
      Sum_CT = Sum_CT + payoff
      Sum_CT_2 = Sum_CT_2 + payoff**2


# Compute Expectation and SE with reference to variance
C_0 = np.exp(-r*T)*Sum_CT/M
sigma = np.sqrt((Sum_CT_2 - Sum_CT*Sum_CT/M)*np.exp(-r*T)/(M-1)) 
SE = sigma/np.sqrt(M)