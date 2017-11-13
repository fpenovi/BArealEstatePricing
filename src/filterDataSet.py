#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def _translate(row) :

    english = ['apartment', 'PH', 'house', 'store']
    spanish = ['departamento', 'ph', 'casa', 'local']

    if row.property_type in spanish :
        return english[spanish.index(row.property_type)]

    return row.property_type


def correctTestSet(testSet) :
    testSet['order'] = pd.Series(xrange(len(dfTest)))
    testSet.property_type = testSet.apply(_translate, axis=1)
    testSet.iat()[1, 4] = 'Palermo'
    testSet.iat()[1, 7] = 'Capital Federal'
    testSet.iat()[1, 14] = 2
    testSet['year_created'] = pd.Series(testSet.created_on.dt.year)
    testSet['month_created'] = pd.Series(testSet.created_on.dt.month)
    testSet['day_created'] = pd.Series(testSet.created_on.dt.day)
    return testSet.sort_values(by='order').loc[:, ('id', 'year_created', 'month_created', 'day_created',
                                                   'property_type', 'place_name', 'state_name', 'lat', 'lon',
                                                   'surface_total_in_m2', 'rooms') ]


def _pointInsideBsAs(lat, lon) :
    NO, NE, SE, SO = (-34.2560, -60.1354), (-34.2560, -57.0902), (-36.0219, -57.0902), (-36.0219, -60.1354)
    return not ( (lat > NO[0]) or (lon < NO[1]) or (lon > NE[1]) or (lat < SE[0]) )

def pointInsideBsAs(latSeries, lonSeries) :
    result = []

    for lat, lon in zip(latSeries, lonSeries) :
        result.append(_pointInsideBsAs(lat, lon))

    return np.array(result, dtype='bool')

def correctTrainSet(trainSet):
    trainSet = trainSet.loc[ pointInsideBsAs(trainSet.lat, trainSet.lon) ]
    trainSet = trainSet.loc[ (trainSet.price_aprox_usd > 11) & (trainSet.price_aprox_usd < 20000000) ]
    trainSet = trainSet.loc[ (trainSet.surface_total_in_m2 > 11) & (trainSet.surface_total_in_m2 < 15000) ]
    trainSet = trainSet.loc[ ~trainSet.place_name.str.contains('coord') ]
    #trainSet = trainSet.loc[ (trainSet.surface_covered_in_m2 > 11) & (trainSet.surface_covered_in_m2 < 15000) ]
    #trainSet = trainSet.loc[ trainSet.rooms < 11 ]
    #trainSet = trainSet.loc[ trainSet.expenses < 3500 ]
    trainSet['year_created'] = pd.Series(trainSet.created_on.dt.year)
    trainSet['month_created'] = pd.Series(trainSet.created_on.dt.month)
    trainSet['day_created'] = pd.Series(trainSet.created_on.dt.day)
    return trainSet.loc[:, ('id', 'year_created', 'month_created', 'day_created',
                            'property_type', 'place_name', 'state_name', 'lat', 'lon',
                            'surface_total_in_m2',
                            'rooms', 'price_aprox_usd') ]


dfTest = pd.read_csv('../data/TEST_SET/properati_dataset_testing_noprice.csv', parse_dates=['created_on'], infer_datetime_format=True)
dfTrain = pd.read_csv('../data/output_2/output_2.csv', parse_dates=['created_on'], infer_datetime_format=True)

dfTest = correctTestSet(dfTest)
dfTrain = correctTrainSet(dfTrain)

dfTest.to_csv('../data/TRAIN_TEST_corrected/test_corrected.csv', index=False)
dfTrain.to_csv('../data/TRAIN_TEST_corrected/train_corrected.csv', index=False)
