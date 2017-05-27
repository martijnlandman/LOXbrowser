# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:26:02 2017

@author: Martijn Landman
"""

from urllib.error import HTTPError
from Bio import Entrez, Medline
import time
import os

TERM = '(("1990"[Date - Publication] : "3000"[Date - Publication]) AND (LOX OR lipoxygenase)) NOT cancer'

def main():
    if checkPubMedFetched():
        updateCount = checkForUpdates()
        if updateCount > 0:
            print("New publications available...")
            fetchPapers(updateCount)
        else:
            print("There are no new publications available")
    else:
        fetchPapers(getPaperCount())

def checkPubMedFetched():
    return os.path.isfile("PubMedFetched\\PubMedFetched.txt")

def checkForUpdates():
    recordCount = 0
    with open("PubMedFetched\\PubMedFetched.txt") as handle:
        for record in Medline.parse(handle):
            recordCount += 1
    print("{0} publications stored locally".format(recordCount))
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

def fetchPapers(paperCount):
    search_handle = Entrez.esearch(db='pubmed', retmax=paperCount, idtype="acc", term=TERM, usehistory="y")
    result = Entrez.read(search_handle)
    search_handle.close
    count = int(paperCount)
    webenv = result["WebEnv"]
    query_key = result["QueryKey"]
    
    print('Getting {0} publications containing lipoxygenase...'.format(count))
    batch_size = 500
    if count < batch_size:
        batch_size = count
    os.makedirs("PubMedFetched", exist_ok=True)
    out_handle = open("PubMedFetched\\PubMedFetched.txt", "a")
    for start in range(0, count, batch_size):
        end = min(count, start+batch_size)
        print("Going to download record %i to %i" % (start+1, end))
        attempt = 0
        while attempt < 3:
            attempt += 1
            try:
                fetch_handle = Entrez.efetch(db="pubmed",
                                             rettype="medline", retmode="text",
                                             retstart=start, retmax=batch_size,
                                             webenv=webenv, query_key=query_key,
                                             idtype="acc")
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("Received error from server %s" % err)
                    print("Attempt %i of 3" % attempt)
                    time.sleep(15)
                else:
                    raise
            except TimeoutError as err:
                print("Received error from server %s" % err)
                print("Attempt %i of 3" % attempt)
                time.sleep(15)
        data = fetch_handle.read()
        fetch_handle.close()
        out_handle.write(data)
    out_handle.close()
    print("Downloaded and saved all {0} records".format(count))

main()