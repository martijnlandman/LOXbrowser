# -*- coding: utf-8 -*-
"""
Created on Sat May 27 17:28:54 2017

@author: Martlan Landman
"""

from Bio import Medline
import nltk, mysql.connector

def main():
    updateKeywords()
    print("Done updating keywords")
    recordParser()
    print("Done saving records")

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
#                resultsToDB(results)
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
        results['keywords'] = textMiner(record["AB"], record["TI"])
        print("PMID: {0}\nURL: {1}\nTitle: {2}\nAuthor: {3}\nDP: {4}\nAB: {5}\n".format(results['PubMedID'],results['URL'],results['title'],results['author'],results['publicationDate'],results['keywords']))
        return results
    except KeyError as err:
        print("Received error from server %s" % err)
        print("Disrecarding record for lacking information")

def textMiner(abstract, title):
#    sentences = nltk.sent_tokenize(abstract)
    keywords = []
    words = nltk.word_tokenize(abstract) + nltk.word_tokenize(title)
    with open("BioCorpus.txt") as file_handle:
        for keyword in file_handle:
            keyword = keyword.strip()
            if keyword in words:
                keywords.append(keyword.lower())
#    sentences = [nltk.pos_tag(sent) for sent in sentences]
#    NN_tags = []
#    for sentence in sentences:
#        for word in sentence:
#            match = re.match(r'(NN(.*))|(JJ.?)', word[1])
#            if match and word not in NN_tags:
#                NN_tags.append(word)
    return sorted(list(set(keywords)))

def connectToDB():
    conn = mysql.connector.connect(host = "127.0.0.1",
                         user = "owe8_1617_gr3",
                         password = "blaat1234",
                         db="owe8_1617_gr3")
    return conn

def resultsToDB(results):
    conn = connectToDB()
    cursor = conn.cursor()
    
    cursor.execute ("INSERT IGNORE INTO results(`pubMed ID`,url,Title) VALUES (%i,%s,%s)", (results['PubMedID'], results['URL'], results['title']))
    for author in results['author']:
        author_id = hash(author)
        author = author.split(" ")
        cursor.execute ("INSERT IGNORE INTO Author(idAuthor,initials,`Last name`) VALUES (%s,%s,%s)", (author_id, author[1], author[0]))
        cursor.execute ("INSERT IGNORE INTO results_has_Author(`results_pubMed ID`,Author_idAuthor) VALUES (%i,%s)", (results['PubMedID'], author_id))
    
    cursor.execute ("INSERT IGNORE INTO publication_date(`date`) VALUES (%s)", (results['publicationDate']))
    cursor.execute ("INSERT IGNORE INTO results_has_publication_date(`results_pubMed ID`,publication_date_date) VALUES (%s,%s)", (results['PubMedID'], results['publicationDate']))
    for keyword in results['keywords']:
        
        cursor.execute ("INSERT IGNORE INTO keywords(keyword) VALUES (%s)", (keyword))
        keyword_ID = cursor.insert_id()
        cursor.execute ("INSERT IGNORE INTO results_has_keywords (results_pubMed_ID, keywords_keyword_ID) VALUES (%i, %s )", (results['PubMedID'], keyword_ID))
    
    conn.commit()
    cursor.close()
    conn.close()

main()