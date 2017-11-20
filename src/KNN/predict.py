#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

start = time.time()

print 'Cargando datasets...'
dfTrain = pd.read_csv('../../data/TRAIN_TEST_corrected2/train_corrected2.csv')
dfTest = pd.read_csv('../../data/TRAIN_TEST_corrected2/test_corrected2.csv')


target = dfTrain.price_usd
testIds = dfTest.id

train = dfTrain.drop(['id', 'price_usd'], axis=True)
testVals = dfTest.drop(['id'], axis=True)

knn = KNeighborsRegressor(n_neighbors=75, weights='distance',
                          algorithm='kd_tree', leaf_size=30,
                          metric='manhattan', n_jobs=-1)

print 'Volcando puntos...'
knn.fit(train, target)
predictions = knn.predict(testVals)

result = pd.DataFrame({'id':testIds, 'price_usd':predictions})
filename = 'knn_' + repr(start).replace('.', '')

end = time.time()
m, s = divmod(end - start, 60)
h, m = divmod(m, 60)
print 'Tiempo:', "%02d:%02d:%02d" % (h, m, s)

print 'Escribiendo archivo de predicciones...'
result.to_csv('../../data/predictions/' + filename + '.csv', index=False)
print 'Finalizó'
