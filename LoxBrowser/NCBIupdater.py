# -*- coding: utf-8 -*-
"""
Created on Sat May 27 17:28:54 2017

@author: Martlan Landman
"""

from Bio import Medline

def main():
    try:
        with open("PubMedFetched\\PubMedFetched.txt") as file_handle:
            count = 0
            for record in Medline.parse(file_handle):
                count += 1
                print("Record {0}".format(count))
                recordHandler(record)
    except FileNotFoundError:
        print("Can't find PubMedFetched.txt in the PubMedFetched directory")

def recordHandler(record):
    try:
        record_PubMedID = record["PMID"]
        record_URL = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(record_PubMedID)
        record_title = record["TI"]
        record_author = record["AU"]
        record_publicationDate = record["DP"]
        print("PMID: {0}\nURL: {1}\nTitle: {2}\nAuthor: {3}\nDP: {4}\n".format(record_PubMedID,record_URL,record_title,record_author,record_publicationDate))
    except KeyError as err:
        print("Received error from server %s" % err)
        print("Disrecarding record for lacking information")

main()