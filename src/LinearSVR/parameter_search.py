#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVR
from matplotlib import pyplot as plt


start = time.time()

dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected3/train_corrected3.csv')

train = dfTrain.drop(['price_usd', 'id'], axis=1)
target = dfTrain.price_usd

# DATA SCALING
scaler = StandardScaler()
train = pd.DataFrame(scaler.fit_transform(train), columns=train.columns)

# PARAMETROS PARA LinearSVR
param_grid = [
                { 'C': [0.01, 0.08, 0.2, 0.3, 0.5, 0.75, 1, 2, 3, 5, 10, 20, 35, 50, 75],
                  'max_iter' : [1000] }
              ]

scoring = {'MSE': 'neg_mean_squared_error'}

# COMIENZO EL GRID SEARCH
print "Comienzo búsqueda de parámetros mediante Grid Search..."
gs = GridSearchCV(LinearSVR(), scoring=scoring, param_grid=param_grid, cv=10, refit='MSE', return_train_score=False)
gs.fit(train, target);
results = gs.cv_results_
print "Graficando..."

dfResults = pd.DataFrame(results).loc[:, ('rank_test_MSE', 'mean_test_MSE',
                                          'param_C')].infer_objects()

ax = dfResults.plot(x='param_C', y='mean_test_MSE',
             figsize=(12, 12), color='darkgreen', lw=4, legend=False)

ax.grid()
ax.set_title("Grid Search LinearSVR: finding best C value", fontsize=18)
ax.set_xlabel('C penalization value', fontsize=14)
ax.set_ylabel('NegMSE\n(higher is better)', fontsize=14)
step = 10
C_param = param_grid[0]['C']
ax.set_xticks(range(int(min(C_param)), int(max(C_param)), step));
# ax.legend(fontsize=11)

end = time.time()
m, s = divmod(end - start, 60)
h, m = divmod(m, 60)
print "Finalizó!"
print 'Tiempo:', "%02d:%02d:%02d" % (h, m, s)
print "\nMejores parametros:", gs.best_params_
print "Tuvieron un error de:", repr(-gs.best_score_), "midiendo MSE"

plt.show()
