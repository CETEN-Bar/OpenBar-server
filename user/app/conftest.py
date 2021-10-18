#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration file for pytest-flask
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Return the app flask object for tests"""
    return create_app()
