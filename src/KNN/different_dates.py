#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from matplotlib import pyplot as plt


start = time.time()

print "Cargando dataset..."
dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected2/train_corrected2.csv')
train = dfTrain.drop(['price_usd', 'id'], axis=1)
train.reset_index(drop=True, inplace=True)

print "Generando DataFrame con timestamps..."
datestr_series = train.year_created.astype(np.int64).astype(np.str) + '/' + train.month_created.astype(np.int64).astype(np.str) + '/' + train.day_created.astype(np.int64).astype(np.str)
datetime64_series = pd.to_datetime(datestr_series, format='%Y/%m/%d')
timestamp_series = ((datetime64_series - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))
trainTS = pd.DataFrame(train).drop(['year_created', 'month_created', 'day_created'], axis=1)
trainTS.insert(loc=0, column='timestamp', value=timestamp_series)

train = pd.DataFrame(StandardScaler().fit_transform(train), columns=train.columns)
target = dfTrain.price_usd

dfs = { 'YYYY-MM-DD' : train,
        'YYYY-MM' : train.drop(['day_created'], axis=1),
        'YYYY' : train.drop(['day_created', 'month_created'], axis=1),
        'Undated' : train.drop(['day_created', 'month_created', 'year_created'], axis=1),
        'Timestamp' : pd.DataFrame(StandardScaler().fit_transform(trainTS)) }

param_grid = [ { 'n_neighbors' : [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 125, 150, 175, 200, 300, 400, 500],
                 'weights' : ['distance'],
                 'metric' : ['manhattan'] } ]

scoring = {'MSE': 'neg_mean_squared_error'}
results = {}
all_gs = {}

for date_format, df_train in dfs.items() :
    print "Realizando GridSearch para", date_format
    knn = KNeighborsRegressor(n_jobs=-1)
    gs = GridSearchCV(knn, scoring=scoring, param_grid=param_grid, cv=10, refit='MSE', return_train_score=False)
    gs.fit(df_train, target)
    results_ = gs.cv_results_
    all_gs[date_format] = gs
    results[date_format] = pd.DataFrame(results_).loc[:, ('rank_test_MSE', 'mean_test_MSE',
                                                           'param_n_neighbors', 'param_weights')].infer_objects()

ax = None
for date_format, df_result in results.items() :
    df_result = df_result.rename(columns={ 'mean_test_MSE' : date_format })
    ax = df_result.plot(ax=ax,
                        x='param_n_neighbors', y=date_format,
                        figsize=(12, 12), rot=45)

ax.grid()
ax.set_title('Grid Search KNN: finding best date format', fontsize=18)
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

for date_format, gs in all_gs.items() :
    print "\n\nPara", date_format, "se obtuvo..."
    print "\nMejores parametros:", gs.best_params_
    print "Tuvo un error de:", repr(gs.best_score_), "midiendo Neg MSE"
    bestest.append( (gs.best_score_, date_format) )

bestest = sorted(bestest)[::-1]
print "\nEl mejor fue:", bestest[0][1]

plt.show()
