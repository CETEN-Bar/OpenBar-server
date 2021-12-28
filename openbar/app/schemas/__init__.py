#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains pydantic models
"""
from typing import Optional

import pydantic


class AllOptional(pydantic.main.ModelMetaclass):
    """
    This class is to transform any model in a model where everything is optional.
    Made for partial updates
    # https://stackoverflow.com/a/67733889
    """
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
