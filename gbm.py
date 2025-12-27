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
                'date': date_range,
                'open':zeros,
                'high': zeros,
                'low': zeros,
                'volume': zeros

            }
        )[['date','open','high','low','volume']]
        

    def GMB_simulation(self, data):
        n = len(data)
        T = 242 #business days in a year
        dt = T/(4*n) # we need 4 prices x day

        asset_price = np.exp((self.mu - (self.sigma**2)/2)*dt + self.sigma*random.normal(0,np.sqrt(dt),size = 4 * n))
        return self.init_price * asset_price.cumprod() 
    
    def append_data_to_csv(self,data,path):
        data['open'] = path[0::4]
        data['close'] = path[3::4]

        data['high'] = np.maximum(
                 np.maximum(path[0::4],path[1::4]),
                 np.maximum(path[2::4],path[3::4])
        )
        data['low'] = np.minimum(
            np.minimum(path[0::4],path[1::4]),
            np.minimum(path[2::4],path[3::4])
        )
    
    def append_volume_to_data(self,data):
        data = np.array(
            map(
                int,
                np.random.pareto(
                    self.pareto_shape,
                    size=len(data)
                )*1000000
            )
        )
    
    def output_frame_to_dir(self,symbol,data):
        output_file = os.path.join(self.output_dir, '%s.csv' % symbol)
        data.to_csv(output_file, index=False, float_format='%.2f')


    def __call__(self):
        symbol = self.generate_random_symbol()
        frame = self.create_empty_frame()
        GMB = self.GMB_simulation(frame)
        csv = self.append_data_to_csv(frame, GMB)
        volume = self.append_volume_to_data(frame)
        output = self.output_frame_to_dir(symbol,frame)



@click.command()
@click.option('--num-assets', 'num_assets', default='1', help='Number of separate assets to generate files for')
@click.option('--random-seed', 'random_seed', default='42', help='Random seed to set for both Python and NumPy for reproducibility')
@click.option('--start-date', 'start_date', default=None, help='The starting date for generating the synthetic data in YYYY-MM-DD format')
@click.option('--end-date', 'end_date', default=None, help='The starting date for generating the synthetic data in YYYY-MM-DD format')
@click.option('--output-dir', 'output_dir', default=None, help='The location to output the synthetic data CSV file to')
@click.option('--symbol-length', 'symbol_length', default='5', help='The length of the asset symbol using uppercase ASCII characters')
@click.option('--init-price', 'init_price', default='100.0', help='The initial stock price to use')
@click.option('--mu', 'mu', default='0.1', help='The drift parameter, \mu for the GBM SDE')
@click.option('--sigma', 'sigma', default='0.3', help='The volatility parameter, \sigma for the GBM SDE')
@click.option('--pareto-shape', 'pareto_shape', default='1.5', help='The shape of the Pareto distribution simulating the trading volume')
def cli(num_assets, random_seed, start_date, end_date, output_dir, symbol_length, init_price, mu, sigma, pareto_shape):
    num_assets = int(num_assets)
    random_seed = int(random_seed)
    symbol_length = int(symbol_length)
    init_price = float(init_price)
    mu = float(mu)
    sigma = float(sigma)
    pareto_shape = float(pareto_shape)

    # Need to seed both Python and NumPy separately
    random.seed(random_seed)
    np.random.seed(seed=random_seed)

    gbmas = GMB(
        start_date,
        end_date,
        output_dir,
        symbol_length,
        init_price,
        mu,
        sigma,
        pareto_shape
    )

    # Create num_assets files by repeatedly calling
    # the instantiated class
    for i in range(num_assets):
        print('Generating asset path %d of %d...' % (i+1, num_assets))
        gbmas()

        
          