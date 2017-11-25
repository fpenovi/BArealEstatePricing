#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from haversine import haversine
import sys
import os.path

def _entornoScore(puntaje, d, dmax) :

    if (d > dmax) :
        return 0

    exp = 3/float(2)
    return puntaje * (1 - (d/float(dmax))**exp )


def entornoScore(lat, lon, matrix, puntajes) :

    LAT, LON, TOPIC = (1, 2, 4)
    score = 1   # Los scores comienzan en 1

    for row in matrix :
        topic = row[TOPIC]
        lat_ = row[LAT]
        lon_ = row[LON]

        pje = puntajes[topic]['puntaje']
        dist_max = puntajes[topic]['dist_max_mts']

        dist_a_pto_interes = haversine( (lat_,lon_), (lat, lon) ) * 1000.0
        score += _entornoScore(pje, dist_a_pto_interes, dist_max)

    return score


def informCompletition(current, to_finish, old_percentage) :
    current += 1
    new_percentage = (current*100.0) / to_finish

    if (abs(old_percentage - new_percentage) >= 1) :
        old_percentage = new_percentage
        print '{}%\t'.format(int(new_percentage)),
        sys.stdout.flush()

    if (current == to_finish) :
        print '100%'

    return current, to_finish, old_percentage


def makeScoresForIds(df, dfPlaces) :

    # PUNTAJES:
    puntajes = { 'SUBTES'    : { 'puntaje':80,  'dist_max_mts':500 },
                 'SHOPPINGS' : { 'puntaje':100, 'dist_max_mts':900 },
                 'METROBUS'  : { 'puntaje':40,  'dist_max_mts':300 },
                 'TRENES'    : { 'puntaje':65,  'dist_max_mts':500 },
                 'PARQUES'   : { 'puntaje':30,  'dist_max_mts':300 },
                 'TURISMO'   : { 'puntaje':20,  'dist_max_mts':400 },
                 'SEGURIDAD' : { 'puntaje':45,  'dist_max_mts':250 }
               }

    # Inicializo todos los scores en NaN
    id_scores = dict([ (row, np.nan) for row in df.id ])
    ID, lat, lon = (df.columns.get_loc('id'),
                    df.columns.get_loc('lat'),
                    df.columns.get_loc('lon'))

    big_array = df.as_matrix()
    small_array = dfPlaces.as_matrix()

    # Itero el dataframe grande
    size = len(big_array)
    i = 0
    percentage = 0

    for row in big_array :
        id_scores[ row[ID] ] = entornoScore(row[lat], row[lon], small_array, puntajes)
        i, _, percentage = informCompletition(i, size, percentage)

    return pd.DataFrame(id_scores.items(), columns=['id', 'entorno_score'])


# Si existen no los pisa porque son pesados de calcular
PATH_TRAIN = '../data/externalData/scoresOfInterest_train.csv'
PATH_TEST = '../data/externalData/scoresOfInterest_test.csv'
dfPlaces = pd.read_csv('../data/externalData/placesOfInterest.csv', encoding='utf-8')

if not os.path.isfile(PATH_TEST) :
    print "Calculando scores para Test..."
    dfTest = pd.read_csv('../data/TRAIN_TEST_corrected2/test_corrected2.csv')
    dfScores_test = makeScoresForIds(dfTest, dfPlaces)
    dfScores_test.to_csv('../data/externalData/scoresOfInterest_test.csv', index=False)
    dfTest.loc[:, ('order')] = pd.Series(xrange(len(dfTest)))
    test = dfTest.merge(dfScores_test, on=['id'], how='inner').sort_values(by='order').drop('order', axis=1)
    test.to_csv('../data/TRAIN_TEST_corrected3/test_corrected3.csv')
else :
    print 'El archivo', PATH_TEST.split('/')[-1], 'ya existe. Borrarlo para recalcular.'


if not os.path.isfile(PATH_TRAIN) :
    print "Calculando scores para Train..."
    dfTrain = pd.read_csv('../data/TRAIN_TEST_corrected2/train_corrected2.csv')
    dfScores_train = makeScoresForIds(dfTrain, dfPlaces)
    dfScores_train.to_csv('../data/externalData/scoresOfInterest_train.csv', index=False)
    dfTrain.loc[:, ('order')] = pd.Series(xrange(len(dfTrain)))
    train = dfTrain.merge(dfScores_train, on=['id'], how='inner').sort_values(by='order').drop('order', axis=1)
    train.to_csv('../data/TRAIN_TEST_corrected3/train_corrected3.csv')
else :
    print 'El archivo', PATH_TRAIN.split('/')[-1], 'ya existe. Borrarlo para recalcular.'
