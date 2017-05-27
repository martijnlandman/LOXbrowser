# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:26:02 2017

@author: Martijn Landman
"""

from Bio import Entrez, Medline
import os

TERM = '(("1990"[Date - Publication] : "3000"[Date - Publication]) AND (LOX OR lipoxygenase)) NOT cancer'

def main():
    if checkPubMedFetched():
        updateCount = checkForUpdates()
        if updateCount!=0:
            print("New publications available...")
            fetchPapers(updateCount,"a")
        else:
            print("There are no new publications available")
    else:
        fetchPapers(getPaperCount(),"w")

def checkPubMedFetched():
    return os.path.isfile("PubMedFetched\\PubMedFetched.txt")

def checkForUpdates():
    recordCount = 0
    with open("PubMedFetched\\PubMedFetched.txt") as handle:
        for record in Medline.parse(handle):
            recordCount += 1
    paperCount = int(getPaperCount())
    updateCount = paperCount-recordCount
    return updateCount

def getPaperCount():
    Entrez.email = 'A.N.Other@example.com'
    net_handle = Entrez.esearch(db='pubmed', retmax='1', term=TERM)
    result = Entrez.read(net_handle)
    paperCount = result['Count']
    print('Total number of publications containing lipoxygenase: {0}'.format(paperCount))
    net_handle.close
    return paperCount

def fetchPapers(paperCount, writeMode):
    h = Entrez.esearch(db='pubmed', retmax=paperCount, term=TERM)
    result = Entrez.read(h)
    ids = result['IdList']
    h.close
    print('Getting {0} publications containing lipoxygenase...'.format(paperCount))
    os.makedirs("PubMedFetched", exist_ok=True)
    net_handle = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
    output_handle = open("PubMedFetched\\PubMedFetched.txt", writeMode)
    output_handle.write(net_handle.read())
    output_handle.close()
    net_handle.close()
    print("Saved all {0} publications".format(paperCount))

main()