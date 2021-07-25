#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to check authorization before accessing the API.
"""

from functools import wraps

def check_authorization(f):
    """Place holder to show how to wrap a function to check auth"""
    @wraps(f)
    def decorated_function(*args,**kwargs):
        """Place holder to show how to decorate a function to check auth"""
        return f(*args, **kwargs)
    return decorated_function
