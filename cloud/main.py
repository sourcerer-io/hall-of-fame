"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os
import sys
from os.path import abspath, dirname

# Obnoxious. TODO(sergey): Find a better way.
BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.append(BASE_DIR)

import fame.storage

def glorify(data, context):
    print('Glory!')

glorify(None, None)
