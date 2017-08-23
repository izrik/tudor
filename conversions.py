#!/usr/bin/env python

from decimal import Decimal


def bool_from_str(s):
    if isinstance(s, basestring):
        s = s.lower()
    if s in ['true', 't', '1', 'y']:
        return True
    if s in ['false', 'f', '0', 'n']:
        return False
    return bool(s)


def int_from_str(s):
    try:
        return int(s)
    except:
        return None


def str_from_datetime(dt):
    if dt is None:
        return None
    return str(dt)


def money_from_str(s):
    try:
        d = Decimal(s).quantize(Decimal('.01'))
        return d
    except:
        return None
