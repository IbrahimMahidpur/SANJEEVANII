"""
Numpy compatibility shim for Python 3.13
Fixes np.float_ deprecation issue
"""

import numpy as np

# Add compatibility for numpy 2.0
if not hasattr(np, 'float_'):
    np.float_ = np.float64
    np.int_ = np.int64
    np.bool_ = np.bool
    np.object_ = np.object
    np.str_ = np.str_
    np.complex_ = np.complex128
