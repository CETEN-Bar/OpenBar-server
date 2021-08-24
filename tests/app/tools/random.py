#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of functions to generate random things
"""

import random, string

def random_string():
    """Return a radom string"""
    return ''.join(random.choices(string.ascii_letters, k=random.randint(0, 50)))

def random_boolean():
    """Return a radom boolean"""
    return random.randint(0, 1) == 1
