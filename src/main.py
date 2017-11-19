#!/usr/bin/python
# -*- coding: utf-8 -*-

import checkData as chk
import time

def downloadData() :
    print "\nObteniendo links de descarga..."
    urlsToDownload = chk.getDownloadLinks('http://www.properati.com.ar/data/')
    print "A descargar", len(urlsToDownload), "archivos...\n"

    i = 1
    for url in urlsToDownload :
        print "Descargando archivo {} de {}".format(i, len(urlsToDownload))
        chk.downloadFile(url, chk.DATADIR)
        i += 1


def main() :
    downloadData()
    chk.generateBigCsv(chk.DATADIR, 'output_2.csv')

main()
