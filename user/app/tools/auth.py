#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to check authorization before accessing the API.
"""

from functools import wraps
from flask_login import login_required, current_user

def is_manager(api):
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if current_user.role.id != 1:
                    return api.abort(404, f"Wrong creditencial")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
