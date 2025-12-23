import numpy as np
import matplotlib.pyplot as mtp
import pandas as pd

def lcg(seed,a,c,m,size):
    sequence = np.zeros(size)
    sequence[0] = seed

    for i in range (1,size):
        sequence[i] = (a * sequence[i-1] + c) % m
    
    return sequence

seed = 2
a = 1664525
c = 1013904223
m = 2**32
size = 1000
pseudo_random = lcg(seed, a, c, m, size)






