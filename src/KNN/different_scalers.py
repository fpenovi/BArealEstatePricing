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
dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected3/train_corrected3.csv').sample(frac=0.30)
dfTrain.reset_index(drop=True, inplace=True)
train = dfTrain.drop(['price_usd', 'id', 'day_created', 'month_created', 'year_created'], axis=1)
target = dfTrain.price_usd

dfs = { 'No Scaling' : train }
scalers = { 'MinMaxScaler' : MinMaxScaler(feature_range=(0, 100)).fit(train),
            'Normalizer' : Normalizer().fit(train),
            'StandardScaler' : StandardScaler().fit(train) }

for scaler_name, scaler_obj in scalers.items() :
    dfs[scaler_name] = pd.DataFrame(scaler_obj.transform(train), columns=train.columns)


param_grid = [ { 'n_neighbors' : [10, 20, 40, 80, 160, 200],
                 'weights' : ['distance'],
                 'metric' : ['manhattan'] } ]

scoring = {'MSE': 'neg_mean_squared_error'}

results = {}
all_gs = {}

for scaling_name, df_train in dfs.items() :
    print "Realizando GridSearch para", scaling_name
    knn = KNeighborsRegressor(n_jobs=-1)
    gs = GridSearchCV(knn, scoring=scoring, param_grid=param_grid, cv=5, refit='MSE', return_train_score=False)
    gs.fit(df_train, target)
    results_ = gs.cv_results_
    all_gs[scaling_name] = gs
    results[scaling_name] = pd.DataFrame(results_).loc[:, ('rank_test_MSE', 'mean_test_MSE',
                                                           'param_n_neighbors', 'param_weights')].infer_objects()

ax = None
for scaler_name, df_result in results.items() :
    df_result = df_result.rename(columns={ 'mean_test_MSE' : scaler_name })
    ax = df_result.plot(ax=ax,
                        x='param_n_neighbors', y=scaler_name,
                        figsize=(12, 12), rot=45)

ax.grid()
ax.set_title('Grid Search KNN: finding best data scaling', fontsize=18)
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

for scaling_name, gs in all_gs.items() :
    print "\n\nPara", scaling_name, "se obtuvo..."
    print "\nMejores parametros:", gs.best_params_
    print "Tuvo un error de:", repr(gs.best_score_), "midiendo Neg MSE"
    bestest.append( (gs.best_score_, scaling_name) )

bestest = sorted(bestest)[::-1]
print "\nEl mejor fue:", bestest[0][1]

plt.show()
