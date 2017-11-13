#!/usr/bin/python
# -*- coding: utf-8 -*-

# PYTHON imports hack
#################################################################
import sys, os                                                  #
file_dir = os.path.dirname(os.path.realpath(__file__))          #
sys.path.insert(0, os.path.abspath(os.path.dirname(file_dir)))  #
#################################################################
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from utils import KFold as kf



# dfTest = pd.read_csv('../../data/TRAIN_TEST_corrected/test_corrected.csv')
