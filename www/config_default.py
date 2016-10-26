#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configuration.
'''


__author__ = 'Aiss86'


configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}