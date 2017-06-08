# -*- coding: utf-8 -*-
"""
Created on Sat May 27 17:28:54 2017

@author: Martlan Landman
"""

import mysql.connector
from Bio import Medline
import nltk, re, mysql.connector

def main():
    updateKeywords()
    print("Done updating keywords")
    recordParser()

def updateKeywords():
    try:
        keywords = []
        with open("PubMedFetched\\PubMedFetched.txt") as input_handle, open("BioCorpus.txt", "r+") as output_handle:
            for record in Medline.parse(input_handle):
                try:
                    record_OT = record["OT"]
                    for ot in record_OT:
                        keywords.append(ot.strip().strip("*"))
                except KeyError:
                    pass
            for keyword in output_handle:
                keywords.append(keyword.strip().strip("*"))
            keywords = sorted(set(keywords))
            output_handle.seek(0)
            output_handle.truncate()
            for keyword in keywords:
                output_handle.write(keyword+"\n")
    except FileNotFoundError:
        print("Can't find PubMedFetched.txt in the PubMedFetched directory")

def recordParser():
    try:
        with open("PubMedFetched\\PubMedFetched.txt") as file_handle:
            count = 0
            for record in Medline.parse(file_handle):
                count += 1
                print("Record {0}".format(count))
                results = recordHandler(record)
                if count == 10:
                    break
    except FileNotFoundError:
        print("Can't find PubMedFetched.txt in the PubMedFetched directory")

def recordHandler(record):
    try:
        results = {}
        results['PubMedID'] = record["PMID"]
        results['URL'] = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(results['PubMedID'])
        results['title'] = record["TI"]
        results['author'] = record["AU"]
        results['publicationDate'] = record["DP"][0:4]
        results['abstract'] = textMiner(record["AB"], record["TI"])
        print("PMID: {0}\nURL: {1}\nTitle: {2}\nAuthor: {3}\nDP: {4}\nAB: {5}\n".format(results['PubMedID'],results['URL'],results['title'],results['author'],results['publicationDate'],results['abstract']))
        return results
    except KeyError as err:
        print("Received error from server %s" % err)
        print("Disrecarding record for lacking information")

def textMiner(abstract, title):
#    sentences = nltk.sent_tokenize(abstract)
    keywords = []
    words = nltk.word_tokenize(abstract)
    print("words: {0}".format(words))
    with open("BioCorpus.txt") as file_handle:
        for keyword in file_handle:
            keyword = keyword.strip()
            if keyword in words:
                keywords.append(keyword)
#    sentences = [nltk.pos_tag(sent) for sent in sentences]
#    NN_tags = []
#    for sentence in sentences:
#        for word in sentence:
#            match = re.match(r'(NN(.*))|(JJ.?)', word[1])
#            if match and word not in NN_tags:
#                NN_tags.append(word)
    return keywords

#def saveResults(results):
#    conn = mysql.connector.connect(host = "127.0.0.1",
#                         user = "owe8_1617_gr3",
#                         password = "blaat1234",
#                         db="owe8_1617_gr3")
#    cursor = conn.cursor ()
#
#    cursor.execute ("INSERT INTO results(`pubMed ID`,url,Title) VALUES (%i,%s,%s)", (results['PubMedId'], results['URL'], results['title']));
#    cursor.execute ("INSERT INTO Author(idAuthor,initials,`Last name`) VALUES (%s,%s,%s)", (Author_ID, Initials, Last_name));
#    cursor.execute ("INSERT INTO results_has_Author(`results_pubMed ID`,Author_idAuthor) VALUES (%s,%s)", (results['PubMedId'], Author_ID));
#    
#    cursor.execute ("INSERT INTO Lox(`lox`,`NCBI prot_ID`,`fullname`) VALUES (%s,%s,%s)", (Lox, NCBI_lox, Lox_full));
#    cursor.execute ("INSERT INTO results_has_Lox(`results_pubMed ID`,Lox_lox) VALUES (%s,%s)", (results['PubMedId'], Lox));
#     
#    cursor.execute ("INSERT INTO Organism(`Name`,`Kingdom`) VALUES (%s, %s)", (Organism_Name, Kingdom));
#    cursor.execute ("INSERT INTO results_has_Organism(`results_pubmed ID`,`Organism_Name`) VALUES (%s,%s)", (results['PubMedId'], Organism_name));
#     
#    cursor.execute ("INSERT INTO `publication_date`(`date`) VALUES (%s)", (results['publicationDate']));
#    cursor.execute ("INSERT INTO `results_has_publication_date`(`results_pubMed ID`,`publication_date_date`) VALUES (%s,%s)", (results['PubMedId'], results['publicationDate']));
#     
#    cursor.execute ("INSERT INTO `keywords`(`keyword_ID`,`keyword`) VALUES (%d,%s)", (keyword_ID, keyword));
#      
#    cursor.execute ("INSERT INTO `Toepassing`(`Toepassing`) VALUES (%s)", (Toepassing));
#    cursor.execute ("INSERT INTO `results_has_Toepassing`(`results_pubMed ID`,`Toepassing_Toepassing`) VALUES (%s,%s))", (results['PubMedId'],Toepassing));
# 
#    conn.commit()
#
#    rows = cursor.fetchall ()

main()