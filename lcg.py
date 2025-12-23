import numpy as np 
import matplotlib.pyplot as mtp

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

random_sequence = lcg(seed,a,c,m, size)

mtp.hist(random_sequence, bins=50, edgecolor='black', alpha=0.7)
mtp.title("Pseudo-Random Numbers")
mtp.xlabel("Values")
mtp.ylabel("Frequency")
mtp.show()


