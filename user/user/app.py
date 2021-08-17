#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""

from apis import create_app, socketio
app = create_app()
if __name__ == '__main__':

    socketio.run(app)
