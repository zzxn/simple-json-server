#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps


def log(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print('%s is invoked' % f.__name__, 'with parameters', args, kwargs)
        return f(*args, **kwargs)

    return decorated