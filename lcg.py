import numpy as np 
import matplotlib as mtp

def lcg(seed,a,c,m,size):
     #seed : int
    #a : int 
    #c : int relative prime
    #m : int relative prime

    sequence = np.zeros(seed)
    sequence[0] = seed
    

    for i in range(1,size):
         sequence[i] = (a*sequence[i - 1] + c ) % m

    return sequence 




