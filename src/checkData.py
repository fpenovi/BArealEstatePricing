#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests as reqs
import re
from pyquery import PyQuery as pq
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
    return set( [ f for f in os.listdir(directory) if f.endswith('.csv')] )


''' Devuelve los links que deben ser descargados.
    - INPUT: Un string representando una URL.
    - OUTPUT: Una lista de strings URL's. '''
def getDownloadLinks(URL) :
    handleDirCreation(DATADIR)
    alreadyDownloaded = loadPersistance(DATADIR)
    d = pq(url=URL)
    m = re.compile('.*-[2][0][1][3-7]-[0-1][0-9]-[0][1]-properties-sell.csv$')

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
