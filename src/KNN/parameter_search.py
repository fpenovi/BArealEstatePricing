#!/usr/bin/python
# -*- coding: utf-8 -*-

# PYTHON imports hack
#################################################################
#import sys, os                                                  #
#file_dir = os.path.dirname(os.path.realpath(__file__))          #
#sys.path.insert(0, os.path.abspath(os.path.dirname(file_dir)))  #
#################################################################
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from matplotlib import pyplot as plt

# http://scikit-learn.org/stable/auto_examples/model_selection/plot_multi_metric_evaluation.html#sphx-glr-auto-examples-model-selection-plot-multi-metric-evaluation-py (BEST)

start = time.time()     # Arranco a contar el tiempo

print "Cargando dataset..."
dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected2/train_corrected2.csv')
train = dfTrain.drop(columns=['price_usd', 'id'], axis=1)
target = dfTrain.price_usd

# PARAMETROS PARA KNN
# Aca estoy definiendo 1 sola grilla
param_grid = [
                {'n_neighbors': [5, 10, 15, 20, 25, 30, 40, 50, 75],
                 'weights': ['uniform', 'distance'],
                 'metric': ['euclidean', 'manhattan', 'chebyshev']}]

# MEDIDA DE SCORE PARA CROSS-VALIDATION
scoring = {'MSE': 'neg_mean_squared_error'}
knn = KNeighborsRegressor(n_jobs=-1)
gs = GridSearchCV(knn, scoring=scoring, param_grid=param_grid, cv=10, refit='MSE', return_train_score=False)

# COMIENZO EL GRID SEARCH
print "Comienzo búsqueda de parámetros mediante Grid Search..."
gs.fit(train, target);
results = gs.cv_results_
print "Graficando..."

dfResults = pd.DataFrame(results).loc[:, ('rank_test_MSE', 'mean_test_MSE',
                                          'param_metric', 'param_n_neighbors', 'param_weights')].infer_objects()

combinatorias = set()

for metric in param_grid[0]['metric'] :
    for weight in param_grid[0]['weights'] :
        tupla = (metric, weight)

        if tupla not in combinatorias and tupla[::-1] not in combinatorias :
            combinatorias.add(tupla)

dfs = []

for opcion in combinatorias :
    dfs.append(dfResults.loc[dfResults.param_metric.str.contains(opcion[0]) & dfResults.param_weights.str.contains(opcion[1])])

# Ploteo los resultados
ax = None
for df in dfs :
    df = df.reset_index()
    new_name = df.param_metric[0] + ' | ' + df.param_weights[0]
    df = df.rename(columns={'mean_test_MSE':new_name })
    ax = df.plot(ax=ax, x='param_n_neighbors', y=new_name,
                 figsize=(12, 12))

ax.grid()
ax.set_title("Grid Search KNN: finding best metric and k value", fontsize=18)
ax.set_xlabel('K neighbors', fontsize=14)
ax.set_ylabel('NegMSE\n(higher is better)', fontsize=14)
ax.legend(fontsize=11)

end = time.time()
m, s = divmod(end - start, 60)
h, m = divmod(m, 60)
print "Finalizó!"
print 'Tiempo:', "%02d:%02d:%02d" % (h, m, s)
print "\nMejores parametros:", gs.best_params_
print "Tuvieron un error de:", repr(-gs.best_score_), "midiendo MSE"

plt.show()
