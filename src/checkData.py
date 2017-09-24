#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests as reqs
from pyquery import PyQuery as pq
import pandas as pd
import numpy as np
import re, os, hashlib, random, string
DATADIR = '../data'


''' Crea un directorio si este no existe.
    - INPUT: Un string representando un directorio (relativo o absoluto).
    - OUTPUT: None. '''
def handleDirCreation(directory) :
    if not os.path.exists(directory):
        os.makedirs(directory)


''' Devuelve los nombres de los archivos que ya han sido descargados.
    - INPUT: Directorio.
    - OUTPUT: Lista de nombres de archivos csv descargados. '''
def loadPersistance(directory) :
    return set( [ f for f in os.listdir(directory) if isCsvFile(directory + '/' + f)] )


''' Evalua si un directorio es un archivo con extension .csv.
    - INPUT: Directorio.
    - OUTPUT: True | False '''
def isCsvFile(filename) :
    return os.path.isfile(filename) and filename.endswith('.csv')


''' Devuelve los links que deben ser descargados.
    - INPUT: Un string representando una URL.
    - OUTPUT: Una lista de strings URL's. '''
def getDownloadLinks(URL) :
    handleDirCreation(DATADIR)
    alreadyDownloaded = loadPersistance(DATADIR)
    d = pq(url=URL)
    m = re.compile('.*-[2][0][1][3-7]-[0-1][0-9]-[0-3][0-9]-properties-sell.csv$')

    urlsToDownload = filter(lambda a_tag: m.match(a_tag.attrib['href']),
                            d('.download li a'))
    urlsToDownload = map(lambda a_tag: URL + a_tag.attrib['href'],
                            urlsToDownload)
    urlsToDownload = filter(lambda url: url.split('/')[-1] not in alreadyDownloaded,
                            urlsToDownload)

    return urlsToDownload


''' Descarga el contenido de la URL y lo guarda en disco.
    - INPUT: Un string representando una URL.
             Un string representando el directorio y nombre del archivo a guardar.
    - OUTPUT: None. '''
def downloadFile(URL, saveDir) :
    contenido = reqs.get(URL).content

    with open(saveDir + '/' + URL.split('/')[-1], "wb") as code:
        code.write(contenido)


''' Carga todo el DataSet de los csv's y guarda el resultado
    en dentro de una carpeta con el nombre 'out_fname'.
    - INPUT: Directorio de csv's.
    - OUTPUT: None. '''
def generateBigCsv(directory, out_fname='output.csv') :

    fold_name = out_fname.split('.')[0]
    out_dir = directory + '/' + fold_name
    if fold_name in os.listdir(directory) and out_fname in os.listdir(out_dir) :
        print "Archivo ya existente, no se realizará procesamiento."
        return

    print "Concatenando y unificando todos los CSV's..."

    csv_files = sorted(loadPersistance(DATADIR))
    df = pd.read_csv(directory + '/' + csv_files[-1])   # Cargo un df para copiar su formato
    df.drop(['country_name', 'lat-lon', 'properati_url', 'description', 'title', 'image_thumbnail'],
            axis=1, inplace=True)
    dfOutput = pd.DataFrame(columns=df.columns)
    last_date_done = None

    for f_name in csv_files :
        print "Procesando archivo:", f_name
        last_date_done, df = loadDataFrame(directory + '/' + f_name, last_date_done)
        dfOutput = dfOutput.append(df)

    print "Removiendo duplicados idénticos..."
    dfOutput.drop_duplicates(inplace=True)                  # Remuevo los duplicados exactos (en todas las columnas iguales)
    print "Generando ID's únicos..."
    generateMissingUniqueID(dfOutput)                       # Genero id's en HEXA para los registros que no tienen
    print "Removiendo ID's duplicados..."
    dfOutput.drop_duplicates(subset='id', inplace=True)     # Remuevo las filas con id's repetidos (que quedaron de la primera pasada)
    print "Realizando formateado final..."
    dfOutput = doFinalFormatting(dfOutput)
    print "Procesamiento finalizado OK"
    print "Guardando", out_fname + "..."
    file_out = out_dir + '/' + out_fname

    handleDirCreation(out_dir)
    dfOutput.to_csv(file_out, index=False)

    print "Archivo guardado en:", os.path.abspath(file_out)


''' Carga DataFrame de manera unificada, especialmente
    para el set de datos de Properati.
    - INPUT: Directorio donde se encuentra el CSV.
             Fecha para elegir solo los registros posteriores a ella.
    - OUTPUT: La fecha del ultimo registro del csv. '''
def loadDataFrame(directory, start_date) :
    dfCurrent = pd.read_csv(directory,
                            parse_dates=['created_on'],
                            infer_datetime_format=True)
    try:
        # CASO FORMATO NUEVO
        if len(dfCurrent.columns) == 27 :
            dfCurrent.drop(['country_name', 'description', 'title'],
                            axis=1, inplace=True)
        # CASO VARIANT 1
        elif len(dfCurrent.columns) == 25 :
            dfCurrent.drop(['description', 'title', 'extra'],
                            axis=1, inplace=True)
            dfCurrent.loc[:,'state_name'] = dfCurrent.apply(lambda row: row.place_with_parent_names.strip('|').split('|')[1],
                                                            axis=1)
        # CASO VARIANT 2
        elif len(dfCurrent.columns) == 23 :
            dfCurrent.rename(columns={'surface_in_m2':'surface_total_in_m2'}, inplace=True)
            dfCurrent.drop(['description', 'title', 'extra'], axis=1, inplace=True)
            dfCurrent.loc[:,'state_name'] = dfCurrent.apply(lambda row: row.place_with_parent_names.strip('|').split('|')[1],
                                                            axis=1)
        # CASO FORMATO VIEJO
        elif len(dfCurrent.columns) == 20 :
            dfCurrent.rename(columns={'surface_in_m2':'surface_total_in_m2'}, inplace=True)
            dfCurrent.loc[:,'state_name'] = dfCurrent.apply(lambda row: row.place_with_parent_names.strip('|').split('|')[1],
                                                            axis=1)
        else :
            raise TypeError("ERROR: Archivo " + directory.split('/')[-1] + "no cumple con ninguno de los dos formatos.")

        dfCurrent.drop(['lat-lon', 'properati_url', 'image_thumbnail'],
                        axis=1, inplace=True)

        # CASO DF VACIO
        if len(dfCurrent) < 1 :
            return (start_date, dfCurrent)

        isFirstTimer = False

        # Caso primer DataFrame necesito ordenar para obtener la primera fecha
        if start_date is None :
            dfCurrent.sort_values(by='created_on', ascending=False, inplace=True)
            start_date = dfCurrent.created_on.iloc[len(dfCurrent) - 1] - pd.DateOffset(1)
            isFirstTimer = True

        # DEJO SOLAMENTE LOS REGISTROS QUE SON ESTRICTAMENTE POSTERIORES A START_DATE
        dfCurrent = dfCurrent[dfCurrent.created_on > start_date]

        # DEJO SOLAMENTE LOS REGISTROS QUE SON DE CAPITAL FEDERAL Y GBA
        dfCurrent = dfCurrent[dfCurrent.state_name.str.contains('Capital Federal') | dfCurrent.state_name.str.contains('G.B.A.')]

        if not isFirstTimer :
            dfCurrent.sort_values(by='created_on', ascending=False, inplace=True)

        return (dfCurrent.created_on.iloc[len(dfCurrent) - 1], dfCurrent)

    except Exception as e:
        raise TypeError("ERROR: En archivo " + directory.split('/')[-1], e)


''' Corrige campos y los devuelve en un orden conveniente.'''
def doFinalFormatting(df) :
    df.dropna(subset=['price_aprox_usd'], inplace=True)
    df = fillPlaceNames(df)
    df = fixDoubles(df)
    df.expenses = df.apply(_makeExpenses, axis=1)
    return df[['id', 'created_on', 'property_type',
               'place_name', 'state_name', 'lat', 'lon',
               'price', 'currency', 'price_aprox_local_currency',
               'price_aprox_usd', 'surface_total_in_m2',
               'surface_covered_in_m2', 'price_usd_per_m2',
               'price_per_m2', 'floor', 'rooms', 'expenses']]


''' Genera un ID en hexadecimal de 40 digitos para los registros del
    DataFrame que no tengan uno.
    - INPUT: DataFrame con columna 'id'.
    - OUTPUT: None. '''
def generateMissingUniqueID(dataframe) :
    usableIDs = makeUsableIDs(dataframe)
    dataframe.loc[:, 'id'] = dataframe.apply(_makeID, args=(usableIDs,), axis=1)


''' Genera ID's hexadecimales de longitud 40 que no se encuentran
    utilizados en el DataFrame.
    - INPUT: DataFrame con ids.
    - OUTPUT: Set de ids utilizables. '''
def makeUsableIDs(dataframe) :
    toMake = len(dataframe.id)
    usedIDs = set(dataframe.id.dropna())
    keys = set()

    while len(keys) < toMake :
        hexhash = os.urandom(40 / 2).encode('hex')

        if hexhash not in usedIDs :
            keys.add(hexhash)

    return keys


''' Asigna un ID unico para una fila.
    - INPUT: Fila y Set de ID's.
    - OUTPUT: ID de fila. '''
def _makeID(row, usableIDs) :
    if not pd.isnull(row.id) :
        return row.id

    return usableIDs.pop()


''' Relleno los campos de place_name.
    INPUT: DataFrame con esa columna.
    OUTPUT: DataFrame modificado. '''
def fillPlaceNames(df) :
    if df.place_name.isnull().sum() == 0 :
        return df

    df = df.reset_index(drop='index')
    dfapply = df.loc[df.place_name.isnull()].loc[:,('place_name', 'place_with_parent_names')]
    dfapply.loc[:,'place_name'] = dfapply.apply(lambda row: row.place_name if not pd.isnull(row.place_name) else row.place_with_parent_names.strip('|').split('|')[-1], axis=1)
    df.update(dfapply.loc[:,('place_name')], overwrite=True)
    return df


''' Arregla los valores de las expensas.'''
def fixDoubles(df) :
    df = df.reset_index(drop='index')
    dfapply = df.loc[~df.expenses.isnull(), ('id', 'expenses')]
    dfapply.expenses = dfapply.apply(_fixDoubles, axis=1)
    dfapply = dfapply.loc[(pd.to_numeric(dfapply.expenses) >= 100) & (pd.to_numeric(dfapply.expenses) <= 15000)]
    dfapply.expenses = pd.to_numeric(dfapply.expenses)
    df.expenses = pd.Series([np.NaN for i in xrange(len(df))])
    df.update(dfapply.loc[:,('expenses')], overwrite=True)
    return df


def _fixDoubles(row) :
    str_ = str(row.expenses)
    str_ = filter( lambda c: c.isdigit() or c == '.', str_.replace(",", ".") )
    points = str_.count('.')
    return str_.replace('.', '', points - 1) if points > 1 else str_


def _makeExpenses(row) :
    if (row.property_type in ('house', 'store', 'PH') and pd.isnull(row.expenses)) :
        return 0
    return row.expenses
