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
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor

# INFO: https://www.quantstart.com/articles/Using-Cross-Validation-to-Optimise-a-Machine-Learning-Method-The-Regression-Setting
# -> este va piola INFO: https://stackoverflow.com/questions/45115964/separate-pandas-dataframe-using-sklearns-kfold
# http://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_digits.html#sphx-glr-auto-examples-model-selection-plot-grid-search-digits-py
# http://maciejjaskowski.github.io/2016/01/22/pandas-scikit-workflow.html -> (muy lindo, empezar por aca)
# http://scikit-learn.org/stable/auto_examples/model_selection/plot_multi_metric_evaluation.html#sphx-glr-auto-examples-model-selection-plot-multi-metric-evaluation-py (BEST)

dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected/train_corrected.csv')
train = dfTrain.drop(columns=['price_usd'], axis=1)
target = dfTrain.price_usd

# PARAMETROS PARA KNN
# Aca estoy definiendo 2 grillas
# (esto me sirve para hacer una que incluya distancia hamming con ball-tree y las demas con kd-tree)
param_grid = [
                {'n_neighbors': [5, 30, 100, 200],
                 'weights': ['uniform', 'distance'],
                 'metric': ['euclidean', 'manhattan', 'chebyshev']},

                { 'n_neighbors': [5, 30, 100, 200],
                  'weights': ['uniform', 'distance'],
                  'metric': ['hamming', 'canberra']}]

# MEDIDA DE SCORE PARA CROSS-VALIDATION
scoring = {'MSE': 'neg_mean_squared_error'}

knn = KNeighborsRegressor(n_jobs=-1)
gs = GridSearchCV(knn, scoring=scoring, param_grid=param_grid, cv=3, refit=True)

gs.fit(train, target)
results = gs.cv_results_


##### PLOTTING RESULTS #####
# plt.figure(figsize=(13, 13))
# plt.title("GridSearchCV evaluating using multiple scorers simultaneously",
#           fontsize=16)
#
# plt.xlabel("min_samples_split")
# plt.ylabel("Score")
# plt.grid()
#
# ax = plt.axes()
# ax.set_xlim(0, 402)
# ax.set_ylim(0.73, 1)
#
# # Get the regular numpy array from the MaskedArray
# X_axis = np.array(results['param_min_samples_split'].data, dtype=float)
#
# for scorer, color in zip(sorted(scoring), ['g', 'k']):
#     for sample, style in (('train', '--'), ('test', '-')):
#         sample_score_mean = results['mean_%s_%s' % (sample, scorer)]
#         sample_score_std = results['std_%s_%s' % (sample, scorer)]
#         ax.fill_between(X_axis, sample_score_mean - sample_score_std,
#                         sample_score_mean + sample_score_std,
#                         alpha=0.1 if sample == 'test' else 0, color=color)
#         ax.plot(X_axis, sample_score_mean, style, color=color,
#                 alpha=1 if sample == 'test' else 0.7,
#                 label="%s (%s)" % (scorer, sample))
#
#     best_index = np.nonzero(results['rank_test_%s' % scorer] == 1)[0][0]
#     best_score = results['mean_test_%s' % scorer][best_index]
#
#     # Plot a dotted vertical line at the best score for that scorer marked by x
#     ax.plot([X_axis[best_index], ] * 2, [0, best_score],
#             linestyle='-.', color=color, marker='x', markeredgewidth=3, ms=8)
#
#     # Annotate the best score for that scorer
#     ax.annotate("%0.2f" % best_score,
#                 (X_axis[best_index], best_score + 0.005))
#
# plt.legend(loc="best")
# plt.grid('off')
# plt.show()
