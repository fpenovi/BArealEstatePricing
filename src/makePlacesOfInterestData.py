#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import googlemaps as gmaps
from time import sleep
GOOGLE_API = ''

def load_gmaps_API_key() :
    key = ''
    with open('../google_api.key') as gmaps_key :
        key = gmaps_key.readline().strip()

    return key


def doFullQuery(client, query, location, topic) :
    end_result = set()
    result = client.places(query, location=location)

    if result['status'] != 'OK' :
        raise LookupError("No se encontraron resultados para " + query)

    while True :
        results_list = result['results']

        for _result in results_list :
            place_id = _result['place_id']
            lat = _result['geometry']['location']['lat']
            lon = _result['geometry']['location']['lng']
            name = _result['name']
            end_result.add( (place_id, lat, lon, name, topic) )

        if not 'next_page_token' in result :
            break

        next_page_token = result['next_page_token']
        result = _queryNextPage(next_page_token)

    return end_result


def _queryNextPage(token) :
    attempts = 3
    result = None
    sleep(1.5)

    for attempt in xrange(attempts) :
        try:
            result = client.places('', page_token=token)
        except Exception as e:
            sleep(2)

    if result is None :
        raise ValueError('Error buscando pagina siguiente. Intentos: ' + str(attempts))

    return result


GOOGLE_API = load_gmaps_API_key()
client = gmaps.Client(GOOGLE_API)

queries = {
            'SUBTES' : [ 'subte A',
                         'subte B',
                         'subte C',
                         'subte D',
                         'subte E',
                         'subte H',
                         'subte P' ],

             'SHOPPINGS' : [ 'shopping',
                             'centro comercial' ],

             'METROBUS' : [ 'metrobus',
                            'metrobus 9 julio',
                            'metrobus santa fe',
                            'metrobus bajo',
                            'metrobus norte' ],

             'TRENES' : [ 'estaciones tren',
                          'estaciones tren mitre',
                          'estaciones tren belgrano',
                          'estaciones tren sarmiento',
                          'estaciones tren san martin',
                          'estaciones "tren de la costa"' ],

              'PARQUES' : [ 'parks' ] }

CABA_centroid = '-34.596952,-58.454212'
result = set()

for topic, _queries in queries.items() :
    print "Realizando queries de", topic, "..."

    for query in _queries :
        batch_result = doFullQuery(client, query, CABA_centroid, topic)
        result = result.union(batch_result)

print "Cantidad de resultados recuperados:", len(result), "\n"
data = pd.DataFrame(data=[reg for reg in result], columns=['place_id', 'lat', 'lon', 'name', 'topic'])
