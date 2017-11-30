#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from matplotlib import pyplot as plt


start = time.time()

dfTrain = pd.read_csv('../data/TRAIN_TEST_corrected3/train_corrected3.csv')
dfTest = pd.read_csv('../data/TRAIN_TEST_corrected3/test_corrected3.csv')

train = dfTrain.drop(['id', 'price_usd', 'day_created', 'month_created', 'year_created'], axis=1)
scaler = StandardScaler()
train = scaler.fit_transform(train)
target = dfTrain.price_usd

test = dfTest.drop(['id', 'day_created', 'month_created', 'year_created'], axis=1)
test = scaler.transform(test)
test_ids = dfTest.id

param_grid = [
                { 'alpha_1'  : [1/float(1000000), 1/float(100000), 1/float(10000), 1/float(1000), 1/float(100), 1/float(10), 1],
                  'alpha_2'  : [1/float(1000000), 1/float(100000), 1/float(10000), 1/float(1000), 1/float(100), 1/float(10), 1],
                  'lambda_1' : [1/float(1000000), 1/float(100000), 1/float(10000), 1/float(1000), 1/float(100), 1/float(10), 1],
                  'lambda_2' : [1/float(1000000), 1/float(100000), 1/float(10000), 1/float(1000), 1/float(100), 1/float(10), 1] }
              ]

scoring = {'MSE': 'neg_mean_squared_error'}

# COMIENZO EL GRID SEARCH
print "Comienzo búsqueda de parámetros mediante Grid Search..."
gs = GridSearchCV(GradientBoostingRegressor(), scoring=scoring, param_grid=param_grid, cv=5, refit='MSE', return_train_score=False)
gs.fit(train, target);
results = gs.cv_results_
print "Graficando..."
