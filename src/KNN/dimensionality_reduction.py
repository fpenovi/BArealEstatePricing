#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt

start = time.time()

print "Cargando dataset..."
dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected3/train_corrected3.csv')\
            .drop(['id', 'day_created', 'month_created', 'year_created'], axis=1)

dfTrain.reset_index(drop=True, inplace=True)

train = dfTrain.drop(['price_usd'], axis=1)
# train = pd.DataFrame(StandardScaler().fit_transform(train), columns=train.columns)

target = dfTrain.price_usd

reductors = { '1-D' : TruncatedSVD(n_components=1),
              '2-D' : TruncatedSVD(n_components=2),
              '3-D' : TruncatedSVD(n_components=3),
              '4-D' : TruncatedSVD(n_components=4),
              '5-D' : TruncatedSVD(n_components=5) }

param_grid = [ { 'n_neighbors' : [10, 20, 40, 80, 160, 200],
                 'weights' : ['distance'],
                 'metric' : ['manhattan'],
                 'n_jobs' : [-1] } ]

scoring = {'MSE': 'neg_mean_squared_error'}
results = {}
all_gs = {}
dfs = {}

for dimensions_str, reductor in reductors.items() :
    dfs[dimensions_str] = pd.DataFrame(reductor.fit_transform(train))

for dimensions_str, df_train in dfs.items() :
    print "Realizando GridSearch para", dimensions_str
    gs = GridSearchCV(KNeighborsRegressor(), scoring=scoring, param_grid=param_grid, cv=10, refit='MSE', return_train_score=False)
    gs.fit(df_train, target)
    results_ = gs.cv_results_
    all_gs[dimensions_str] = gs
    results[dimensions_str] = pd.DataFrame(results_).loc[:, ('rank_test_MSE', 'mean_test_MSE',
                                                             'param_n_neighbors', 'param_weights')].infer_objects()

ax = None
for dimensions_str, df_result in results.items() :
    df_result = df_result.rename(columns={ 'mean_test_MSE' : dimensions_str })
    ax = df_result.plot(ax=ax,
                        x='param_n_neighbors', y=dimensions_str,
                        figsize=(12, 12), rot=45)

ax.grid()
ax.set_title('Grid Search KNN: finding best dimension representation', fontsize=18)
ax.set_xlabel('K neighbors', fontsize=14)
ax.set_ylabel('NegMSE\n(higher is better)', fontsize=14)
ax.legend(fontsize=11)

neighbors = param_grid[0]['n_neighbors']
step = 15
ax.set_xticks(np.arange(min(neighbors), max(neighbors) + step, step));
ax.tick_params(axis = 'x', labelsize = 9)

end = time.time()
m, s = divmod(end - start, 60)
h, m = divmod(m, 60)
print "Finalizó!"
print 'Tiempo:', "%02d:%02d:%02d" % (h, m, s)




bestest = []

for dimensions_str, gs in all_gs.items() :
    print "\n\nPara", dimensions_str, "se obtuvo..."
    print "\nMejores parametros:", gs.best_params_
    print "Tuvo un error de:", repr(gs.best_score_), "midiendo Neg MSE"
    bestest.append( (gs.best_score_, dimensions_str) )

bestest = sorted(bestest)[::-1]
print "\nEl mejor fue:", bestest[0][1]

plt.show()
