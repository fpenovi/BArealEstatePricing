#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests as reqs
import re
from pyquery import PyQuery as pq


''' Crea un directorio si este no existe.
    - INPUT: Un string representando un directorio (relativo o absoluto).
    - OUTPUT: None. '''
def handleDirCreation(directory) :
    if not os.path.exists(directory):
        os.makedirs(directory)

''' Carga en memoria los archivos que ya han sido descargados.
    - INPUT: None.
    - OUTPUT: None. '''
def loadPersistance() :
    pass

''' Devuelve los links que deben ser descargados.
    - INPUT: Un string representando una URL.
    - OUTPUT: Una lista de strings URL's. '''
def getDownloadLinks(URL) :
    CSVs = {}
    DATADIR = '../data'

    #loadPersistance(CSVs)
    handleDirCreation(DATADIR)
    d = pq(url=URL)
    m = re.compile('.*-[2][0][1][3-7]-[0-1][0-9]-[0][1]-properties-sell.csv$')

    urlsToDownload = filter(lambda a_tag: m.match(a_tag.attrib['href']),
                            d('.download li a'))

    print "Files to download: " + str(len(urlsToDownload))

    #html = downloadFile(URL)
    print "Finished"

''' Descarga el contenido de la URL y lo guarda en disco.
    - INPUT: Un string representando una URL.
             Un string representando el directorio y nombre del archivo a guardar.
    - OUTPUT: None. '''
def downloadFile(URL, saveDir) :
    # with open(DATADIR + "/web.html", "wb") as code:
        # code.write(html)
    return reqs.get(URL).content




getDownloadLinks('http://www.properati.com.ar/data/')
