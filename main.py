"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os

import fame.storage

def glorify(data, context):
    print('Glory!')
