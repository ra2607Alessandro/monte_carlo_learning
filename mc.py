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
T = ((datetime.date(2025,10,30) -datetime.date(2025,9,5)).days+1)/365
print(T)


# Drift and Diffusion: log(S) + (r - 0.5*vol**2)*dt + vol*np.sqrt(dt)
dt = T/N
nudt = (r - 0.5*vol**2)*dt
volsdt = vol*np.sqrt(dt)
lnS = np.log(S) # the model evolves log prices not prices 

# Standard Error Placeholders
sum_CT = 0
sum_CT2 = 0

# Heart of the Monte Carlo Method
for i in range(M):
    lnSt = lnS
    for j in range(N):
        lnSt = lnSt + nudt + volsdt*np.random.normal() 
# Markov Chain: lnS + nudt*dt + volsdt*Z
# Z is a random number that is meant to create the random shock in the drift and diffusion model


    ST = np.exp(lnSt) #this will convert back to a price
    CT = max(0, ST - K) #option payoff
    sum_CT = sum_CT + CT
    sum_CT2 = sum_CT2 + CT*CT

# Compute Expectation and SE
C0 = np.exp(-r*T)*sum_CT/M #estimation of the option price
sigma = np.sqrt( (sum_CT2 - sum_CT*sum_CT/M)*np.exp(-2*r*T) / (M-1) ) # *np.exp(-2*r*T) is added here because the variance scales,
                                                                      #  and therefore it has to be added to the standard error
SE = sigma/np.sqrt(M)

print("Call value is ${0} with SE +/- {1}".format(np.round(C0,2),np.round(SE,2)))
x1 = np.linspace(C0-3*SE, C0-1*SE, 100)
x2 = np.linspace(C0-1*SE, C0+1*SE, 100)
x3 = np.linspace(C0+1*SE, C0+3*SE, 100)

s1 = stats.norm.pdf(x1, C0, SE)
s2 = stats.norm.pdf(x2, C0, SE)
s3 = stats.norm.pdf(x3, C0, SE)

plt.fill_between(x1, s1, color='tab:blue',label='> StDev')
plt.fill_between(x2, s2, color='cornflowerblue',label='1 StDev')
plt.fill_between(x3, s3, color='tab:blue')

plt.plot([C0,C0],[0, max(s2)*1.1], 'k',
        label='Theoretical Value')
plt.plot([market_value,market_value],[0, max(s2)*1.1], 'r',
        label='Market Value')

plt.ylabel("Probability")
plt.xlabel("Option Price")
plt.legend()
plt.show()
