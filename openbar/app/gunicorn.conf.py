#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gunicorn conf file
"""

import os
import multiprocessing
import signal


def worker_int(worker):
    """
    Ask gunicorn to kill workers when reloading
    see https://github.com/benoitc/gunicorn/issues/2339#issuecomment-852025685
    """
    os.kill(worker.pid, signal.SIGINT)

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count()
reload = (os.environ.get('ENV', default=None) == 'development')
forwarded_allow_ips = "127.0.0.1"
if os.environ.get('IN_DOCKER', default=None) == 1:
    forwarded_allow_ips = "nginx"
accesslog = "-"
worker_class = "uvicorn.workers.UvicornWorker"

loglevel = 'info'
if os.environ.get('ENV', default=None) in ('development', 'test'):
    loglevel = 'debug'
