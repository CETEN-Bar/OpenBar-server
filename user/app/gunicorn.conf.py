#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gunicorn conf file
"""

import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
