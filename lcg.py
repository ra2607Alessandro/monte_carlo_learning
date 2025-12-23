import numpy as np 
import matplotlib.pyplot as mtp
import pandas as pd

def lcg(seed,a,c,m,size):
    #seed : int
    #a : int 
    #c : int relative prime
    #m : int relative prime

    sequence = np.zeros(size)
    sequence[0] = seed
    

    for i in range(1,size):
         sequence[i] = (a*sequence[i - 1] + c ) % m

    return sequence 



seed = 2
a = 1664525
c = 1013904223
m = 2**32
size = 1000

random_sequence = lcg(seed,a,c,m,size)

# HISTOGRAM WITH MATPLOTLIB.PYPLOT

#mtp.hist(random_sequence, bins=50, edgecolor='black', alpha=0.7)
#mtp.title("Pseudo-Random Numbers")
#mtp.xlabel("Values")
#mtp.ylabel("Frequency")
#mtp.show()

# Scattered Plot Diagram
#mtp.scatter(random_sequence[:-1], random_sequence[1:], alpha = 0.5)
#mtp.title("Pseudo-Random Numbers with Scattered Diagram")
#mtp.xlabel("X_n")
#mtp.ylabel("X_n+1")
##mtp.show()

# AUTO-CORRELATION

#series = pd.Series(random_sequence)

#pd.plotting.autocorrelation_plot(series)
#mtp.title("AUTO-CORRELATION")
#mtp.show()




