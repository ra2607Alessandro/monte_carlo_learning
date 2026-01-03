import numpy as np


class Vanilla:
    """Simple vanilla European option container.

    Stores strike `K`, time-to-maturity `T` and `option_type` ('call' or 'put').
    `payoff` accepts scalar, 1-D arrays of terminal prices or 2-D path arrays
    (shape (n_paths, n_steps)) and returns the elementwise payoff.
    """

    def __init__(self, K, T, option_type):
        if K <= 0:
            raise ValueError("K must be > 0")
        if T < 0:
            raise ValueError("T must be >= 0")

        self.K = float(K)
        self.T = float(T)
        opt = option_type.strip().lower()
        if opt in ("c", "call"):
            self.option_type = "call"
        elif opt in ("p", "put"):
            self.option_type = "put"
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def payoff(self, ST):
        """Return payoff(s) given terminal price(s) ST.

        ST may be:
        - scalar (Python number or 0-D numpy) -> returns Python float
        - 1-D numpy array of terminal prices -> returns 1-D numpy array
        - 2-D numpy array of paths (n_paths, n_steps) -> uses last column as terminal prices
        """
        ST_arr = np.asarray(ST)

        # extract terminal prices depending on the shape
        if ST_arr.ndim == 0:
            terminal = ST_arr.item()
        elif ST_arr.ndim == 1:
            terminal = ST_arr
        elif ST_arr.ndim == 2:
            terminal = ST_arr[:, -1]
        else:
            raise ValueError("ST must be scalar, 1-D or 2-D array")

        if self.option_type == "call":
            result = np.maximum(terminal - self.K, 0)
        else:
            result = np.maximum(self.K - terminal, 0)
        
        if np.isscalar(terminal):
            return float(result)
        else:
            return result
    
    def simulate_terminal(self,S,r,sigma,iters):
        Z = np.random.normal(size=iters)
        ST = S*np.exp((r-0.5*(sigma**2))*self.T + sigma*np.sqrt(self.T)*Z)
        return ST

    def discounted_payoff(self, ST, r):
        """Return discounted payoff(s) given terminal price(s) ST and rate r."""
        return np.exp(-r * self.T) * self.payoff(ST)