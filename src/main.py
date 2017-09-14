#!/usr/bin/python
# -*- coding: utf-8 -*-
import checkData as chk

def main() :
    print "\nObteniendo links de descarga..."
    urlsToDownload = chk.getDownloadLinks('http://www.properati.com.ar/data/')
    print "A descargar", len(urlsToDownload), "archivos..."

    i = 1
    for url in urlsToDownload :
        print "Descargando archivo", i, "de", len(urlsToDownload)
        chk.downloadFile(url, chk.DATADIR)
        i += 1

main()
