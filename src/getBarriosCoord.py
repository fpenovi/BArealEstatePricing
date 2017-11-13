#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import googlemaps as gmaps
import geopy.distance
GOOGLE_API = ''


def load_gmaps_API_key() :
    key = ''
    with open('../google_api.key') as gmaps_key :
        key = gmaps_key.readline().strip()

    return key



GOOGLE_API = load_gmaps_API_key()
client = gmaps.Client(GOOGLE_API)

dfTrain = pd.read_csv('../data/TRAIN_TEST_corrected/train_corrected.csv')
dfTest = pd.read_csv('../data/TRAIN_TEST_corrected/test_corrected.csv')

# Busco las localidades sin coordenadas
dfTrain = dfTrain.loc[pd.isnull(dfTrain.lat) | pd.isnull(dfTrain.lon)]
dfTest = dfTest.loc[pd.isnull(dfTest.lat) | pd.isnull(dfTest.lon)]

placesToQuery = set(list(dfTrain.place_name) + list(dfTest.place_name))
print len(placesToQuery), 'places to query...'

obelisco = client.geocode('Obelisco, Avenida 9 de Julio, Buenos Aires')[0]
obelisco = (obelisco['geometry']['location']['lat'], obelisco['geometry']['location']['lng'])

columns = {'place':[], 'lat':[], 'lon':[], 'distance_to_obelisco_mtrs':[]}
errores = []

i = 1
for place_name in placesToQuery :
    print 'Querying', place_name, str(i), 'of', len(placesToQuery)
    try:
        result = client.geocode(place_name)[0]
    except Exception as e:
        print 'Error en', place_name
        print e
        columns['place'].append(place_name)
        columns['lat'].append(np.nan)
        columns['lon'].append(np.nan)
        columns['distance_to_obelisco_mtrs'].append(np.nan)
        errores.append( (place_name, e) )
        i += 1
        continue

    lat = result['geometry']['location']['lat']
    lon = result['geometry']['location']['lng']
    distance = geopy.distance.vincenty(obelisco, (lat, lon)).m
    columns['place'].append(place_name)
    columns['lat'].append(lat)
    columns['lon'].append(lon)
    columns['distance_to_obelisco_mtrs'].append(distance)
    i += 1


dfCoords = pd.DataFrame(columns)[['place', 'lat', 'lon', 'distance_to_obelisco_mtrs']]
dfCoords.to_csv('../data/externalData/coordenadas_barrios.csv', index=False)

print "ERRORES:"
for err in errores :
    print err
