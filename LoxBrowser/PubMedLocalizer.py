# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 12:37:38 2017

@author: Martlan Landman
"""

from urllib.error import HTTPError
from Bio import Entrez, Medline
import os, time, nltk, mysql.connector

TERM = '(("1990"[Date - Publication] : "3000"[Date - Publication]) AND lipoxygenase) NOT cancer'

def main():
    # Kijk of er al papers lokaal zijn opgeslagen. Als dit het geval is dan wordt er gekeken of
    # er nieuwe papers zijn. Als er nog geen papers zijn dan worden deze gedownload.
    if checkPubMedFetched():
        updateCount = checkForUpdates()
        if updateCount > 0:
            print("New publications available...")
            fetchPapers(updateCount)
            updateKeywords()
            print("Updated keywords")
            recordParser()
            print("Saved all records in the database")
        else:
            print("There are no new publications available")
    else:
        fetchPapers(getPaperCount())
        updateKeywords()
        print("Updated keywords")
        recordParser()
        print("Saved all records in the database")

# Checkt of het bestand PubMedFetched.txt bestaat
def checkPubMedFetched():
    return os.path.isfile("PubMedFetched\\PubMedFetched.txt")

# Verbindt met de database.
def connectToDB():
    conn = mysql.connector.connect(host = "localhost",
                         user = "Martijn",
                         password = "blaat1234",
                         db="mydb")
    return conn

# Het aantal papers die lokaal zijn opgeslagen wordt geteld  en dit getal wordt
# vergeleken met het aantal beschikbare papers om vast te stellen of er nieuwe
# papers
def checkForUpdates():
    recordCount = 0
    with open("PubMedFetched\\PubMedFetched.txt") as handle:
        for record in Medline.parse(handle):
            recordCount += 1
    print("{0} publications stored locally".format(recordCount))
    paperCount = int(getPaperCount())
    updateCount = paperCount-recordCount
    return updateCount

# Checkt PubMed voor het aantal beschikbare papers.
def getPaperCount():
    Entrez.email = 'A.N.Other@example.com'
    net_handle = Entrez.esearch(db='pubmed', retmax='1', term=TERM)
    result = Entrez.read(net_handle)
    paperCount = result['Count']
    print('Total number of publications containing lipoxygenase: {0}'.format(paperCount))
    net_handle.close
    return paperCount

# Haalt papers op van PubMed n batches van 500 (tenzij er minder dan 500 papers opgehaald
# moeten worden). De papers worden vervolgens in het bestand PubMedFetched.txt weggeschreven.
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

# De keywords uit BioCorpus.txt en de keywords uit de artikelen worden samengevoegd
# in één lijst en vervolgens opgeslagen in BioCorpus.txt. (duplicaten worden verwijderd)
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

# Loopt door de papers heen en geeft iedere paper door aan recordHandler().
# Geeft de verkregen resultaten uit recordHandler() door aan resultsToDB() zodat
# de resultaten worden opgeslagen.
def recordParser():
    try:
        with open("PubMedFetched\\PubMedFetched.txt") as file_handle:
            count = 0
            for record in Medline.parse(file_handle):
                count += 1
                print("Record {0}".format(count))
                results = recordHandler(record)
                if results != False:
                    resultsToDB(results)
    except FileNotFoundError:
        print("Can't find PubMedFetched.txt in the PubMedFetched directory")

# Haalt de relevante informatie uit de paper en zet dit in een dictionary.
# Als er informatie ontbreekt in de paper dan wordt deze overgeslagen.
def recordHandler(record):
    try:
        results = {}
        results['PubMedID'] = record["PMID"]
        results['URL'] = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(results['PubMedID'])
        results['title'] = record["TI"]
        results['author'] = record["AU"]
        results['publicationDate'] = str(record["DP"][0:4])
        results['keywords'] = textMiner(record["AB"], record["TI"])
        print("PMID: {0}\nURL: {1}\nTitle: {2}\nAuthor: {3}\nDP: {4}\nAB: {5}\n".format(results['PubMedID'],results['URL'],results['title'],results['author'],results['publicationDate'],results['keywords']))
        return results
    except KeyError as err:
        print("Received error from server %s" % err)
        print("Disrecarding record for lacking information")
        return False

# Doorzoekt de abstract en de titel op de keywords uit de BioCorpus.
def textMiner(abstract, title):
    keywords = []
    words = nltk.word_tokenize(abstract) + nltk.word_tokenize(title)
    with open("BioCorpus.txt") as file_handle:
        for keyword in file_handle:
            keyword = keyword.strip()
            if keyword in words:
                keywords.append(keyword.lower())
    
    return sorted(list(set(keywords)))

# Slaat de informatie uit de papers op in de database.
def resultsToDB(results):
    conn = connectToDB()
    cursor = conn.cursor()
    
    cursor.execute("""INSERT IGNORE INTO results(pubMed_ID, url, Title) VALUES (%s,%s,%s)""", (results['PubMedID'], results['URL'], results['title']))
    for author in results['author']:
        author_id = hash(author)
        author = author.split(" ")
        if len(author) < 2:
            author.append("-")
        cursor.execute("""INSERT IGNORE INTO author(idAuthor, initials, Last_Name) VALUES (%s,%s,%s)""", (author_id, author[1], author[0]))
        cursor.execute("""INSERT IGNORE INTO results_has_author(results_pubMed_ID,Author_idAuthor) VALUES (%s,%s)""", (results['PubMedID'], author_id))
    
    cursor.execute("""INSERT IGNORE INTO publication_date(date) VALUES ({0})""".format(results['publicationDate']))
    cursor.execute("""INSERT IGNORE INTO results_has_publication_date(results_pubMed_ID,Publication_date_date) VALUES (%s,%s)""", (results['PubMedID'], results['publicationDate']))
    for keyword in results['keywords']:
        keyword_id = hash(keyword)
        cursor.execute("""INSERT IGNORE INTO keywords(keyword_ID, keyword) VALUES (%s,%s)""", (keyword_id, keyword))
        cursor.execute("""INSERT IGNORE INTO results_has_keywords (results_pubMed_ID, keywords_keyword_ID) VALUES (%s, %s)""", (results['PubMedID'], keyword_id))
    
    conn.commit()
    cursor.close()
    conn.close()

main()