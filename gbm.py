import os
import random
import string

import click
import numpy as np
import pandas as pd

class GMB:
    
    def __init__(
        self,
        start_date,
        end_date,
        output_dir,
        symbol_length,
        init_price,
        mu,
        sigma,
        pareto_shape):
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = output_dir
        self.symbol_length = symbol_length
        self.init_price = init_price
        self.mu = mu
        self.sigma = sigma
        self.pareto_shape = pareto_shape
    
    def generate_random_symbol(self):
        return " ".join(random.choice(string.ascii_uppercase,k = self.symbol_length))
    
    

    def GMB_simulation():

    def __call__(self, *args, **kwds):
        
          