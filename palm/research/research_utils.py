
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


def predictable_matrix(X: np.ndarray):
    """
    Gets the predictability matrix defined in d'aspremont and cuturi.
    Reference: https://arxiv.org/pdf/1509.05954.pdf, section 2.2.3.
    """

    A_0 = autocovariance(X)
    A_1 = autocovariance(X, 1)

    U, D, V_t = np.linalg.svd(A_0)
    U_T = np.transpose(U)
    V = np.transpose(V_t)
    D_inv = np.diag(1/np.maximum(D,1.0e-8))
    A_0_inv = np.dot(V, np.dot(D_inv, U_T))
    sqrt_A_0_inv = np.dot(V, np.dot(np.sqrt(D_inv), U_T))

    pred = sqrt_A_0_inv
    pred = np.dot(np.transpose(A_1),pred)
    pred = np.dot(A_0_inv, pred)
    pred = np.dot(A_1, pred)
    pred = np.dot(sqrt_A_0_inv, pred)
    return pred

