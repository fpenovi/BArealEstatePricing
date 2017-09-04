#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests as reqs


def handleDirCreation(directory) :
    if not os.path.exists(directory):
        os.makedirs(directory)

def loadPersistance() :
    

def main() :

    CSVs = {}
    DATADIR = '../data'

    handleDirCreation(DATADIR)
    loadPersistance(CSVs)


    i = 0
    #url = CSVs[i]
    url = "https://www.google.com.ar/"
    r = reqs.get(url)
    print "downloading with requests"

    with open(DATADIR + "/csv" + str(i) + ".csv", "wb") as code:
        code.write(r.content)

    print "finished"

main()
