from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from scipy.optimize import newton


def xirr_function(cashflows:list[float], dates:list[datetime], guess:float=0.1)->float:    
    days = np.array([(date - dates[0]).days for date in dates])
    try:
        rs=newton(lambda r: np.sum(cashflows / (1 + r) ** (days / 365)), guess)
    except Exception as e:
        rs = np.nan
    return rs
    
