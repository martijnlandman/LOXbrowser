# -*- coding: utf-8 -*-
"""
Created on Sat May 27 17:28:54 2017

@author: Martlan Landman
"""

from Bio import Medline
import nltk

def main():
    try:
        with open("PubMedFetched\\PubMedFetched.txt") as file_handle:
            count = 0
            for record in Medline.parse(file_handle):
                count += 1
                print("Record {0}".format(count))
                recordHandler(record)
                if count == 1:
                    break
    except FileNotFoundError:
        print("Can't find PubMedFetched.txt in the PubMedFetched directory")

def recordHandler(record):
    try:
        record_PubMedID = record["PMID"]
        record_URL = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(record_PubMedID)
        record_title = record["TI"]
        record_author = record["AU"]
        record_publicationDate = record["DP"]
        record_abstract = textMiner(record["AB"])
        print("PMID: {0}\nURL: {1}\nTitle: {2}\nAuthor: {3}\nDP: {4}\nAB: {5}\n".format(record_PubMedID,record_URL,record_title,record_author,record_publicationDate,record_abstract))
    except KeyError as err:
        print("Received error from server %s" % err)
        print("Disrecarding record for lacking information")

def textMiner(abstract):
    sentences = ie_preprocess(abstract)
    return sentences

def ie_preprocess(abstract):
    sentences = nltk.sent_tokenize(abstract)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

main()