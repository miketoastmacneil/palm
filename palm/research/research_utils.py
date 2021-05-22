
import numpy as np

def returns_from_series(prices: np.ndarray):
    """
    Takes a TxN price series and returns the percentage 
    returns 
    """
    return (prices[1:,:] - prices[:-1,:])/prices[:-1,:]

def cumulative_returns(returns: np.ndarray):
    """
    Takes an TxN returns series and returns
    the cumulative returns
    """
    return np.cumprod(returns+1, axis = 0)

def autocovariance(x: np.ndarray, k=0):
    T = x.shape[0]
    x_tilde = x - np.nanmean(x, axis=0)

    if k > 0:
        A_k = 1/(T - k - 1) * np.dot(x_tilde[k:,:].transpose(), x_tilde[:-k])
    else:
        A_k = 1/(T - 1) * np.dot(x_tilde.transpose(), x_tilde)
    return A_k

