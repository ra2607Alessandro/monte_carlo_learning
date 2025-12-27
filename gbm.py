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
    
    def create_empty_frame(self):
        date_range = pd.date_range(
        self.start_date,
        self.end_date,
        freq='B')
        zeros = pd.Series(np.zeros(len(date_range)))#create a zero for every single data
        return pd.DataFrame(
            {
                'data': date_range,
                'open':zeros,
                'high': zeros,
                'low': zeros,
                'volume': zeros

            }
        )[['data','open','high','low','volume']]
        

    def GMB_simulation(self, data):
        n = len(data)
        T = 242 #business days in a year
        dt = T/(4*n) # we need 4 prices x day

        asset_price = np.exp((self.mu - (self.sigma**2)/2)*dt + self.sigma*random.normal(0,np.sqrt(dt),size = 4 * n))
        return self.init_price * asset_price.cumprod() 
    
    def append_data_to_csv(self,data,path):
    



    def __call__(self, *args, **kwds):
        
          