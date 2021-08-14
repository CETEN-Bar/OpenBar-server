#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""

from apis import socketio,app



    

if __name__ == '__main__':
    socketio.run(app)
