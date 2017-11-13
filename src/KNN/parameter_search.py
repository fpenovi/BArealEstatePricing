#!/usr/bin/python
# -*- coding: utf-8 -*-

# PYTHON imports hack
#################################################################
#import sys, os                                                  #
#file_dir = os.path.dirname(os.path.realpath(__file__))          #
#sys.path.insert(0, os.path.abspath(os.path.dirname(file_dir)))  #
#################################################################
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# INFO: https://www.quantstart.com/articles/Using-Cross-Validation-to-Optimise-a-Machine-Learning-Method-The-Regression-Setting
# -> este va piola INFO: https://stackoverflow.com/questions/45115964/separate-pandas-dataframe-using-sklearns-kfold
# http://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_digits.html#sphx-glr-auto-examples-model-selection-plot-grid-search-digits-py

# http://maciejjaskowski.github.io/2016/01/22/pandas-scikit-workflow.html -> (muy lindo, empezar por aca)



# dfTest = pd.read_csv('../../data/TRAIN_TEST_corrected/test_corrected.csv')
