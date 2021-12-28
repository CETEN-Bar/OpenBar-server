#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for OpenBar API
"""

import os

API_ROOT = "http://127.0.0.1:8080/api/v0/"
if os.environ.get('IN_DOCKER', default=None) == "1":
    API_ROOT = "http://nginx:8080/api/v0/"
