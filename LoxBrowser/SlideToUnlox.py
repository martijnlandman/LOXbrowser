# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 12:37:38 2017

@author: Martlan Landman, Roel Koper
"""

from flask import Flask, request , render_template
import mysql.connector

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("input.html")

@app.route('/output', methods=['POST'])
def output():
    zoekterm = request.form.get("woord")
    papers = searchTheDB(zoekterm)
    return render_template("output.html", papers=papers)

# Verbindt met de database.
def connectToDB():
    conn = mysql.connector.connect(host = "localhost",
                         user = "Martijn",
                         db="mydb",
                         passwd = "blaat1234")
    return conn

# Doorzoekt de database naar de papers die de zoekterm bevatten en haalt vervolgens
# alle informatie op die aan de gevonden papers is gekoppeld.
def searchTheDB(zoekterm):
    conn = connectToDB()
    cursor = conn.cursor()
    papers = []
    cursor.execute("""SELECT pubMed_ID
                      FROM mydb.results AS R
                      JOIN mydb.results_has_keywords AS RK ON RK.results_pubMed_ID = R.pubMed_ID
                      JOIN mydb.keywords AS K on RK.keywords_keyword_ID = K.keyword_ID
                      WHERE K.keyword = '{0}'
                      """.format(zoekterm))
    pubMed_ids = set(cursor.fetchall())
    for pubMed_ID in pubMed_ids:
        paper_info = []
        pubMed_ID = str(pubMed_ID).strip(",)").strip("(")
        cursor.execute("""SELECT R.pubMed_ID, R.title, R.url
                          FROM mydb.results AS R
                          WHERE R.pubMed_ID = '{0}'
                          """.format(pubMed_ID))
        results_handler = cursor.fetchall()[0]
        paper_info.append(results_handler[0])
        paper_info.append(results_handler[1])
        paper_info.append(results_handler[2])
        cursor.execute("""SELECT K.keyword
                          FROM mydb.results AS R
                          INNER JOIN mydb.results_has_keywords AS RK ON RK.results_pubMed_ID = R.pubMed_ID
                          INNER JOIN mydb.keywords AS K on RK.keywords_keyword_ID = K.keyword_ID
                          WHERE R.pubMed_ID = '{0}'
                          """.format(pubMed_ID))
        keyword_handler = cursor.fetchall()
        keywords = [a[0] for a in keyword_handler]
        paper_info.append(sorted(list(set(keywords))))
        cursor.execute("""SELECT D.`date`
                          FROM mydb.results AS R
                          INNER JOIN mydb.results_has_publication_date as RD ON RD.results_pubMed_ID = R.pubMed_ID
                          INNER JOIN mydb.publication_date as D ON RD.Publication_date_date = D.`date`
                          WHERE R.pubMed_ID = '{0}'
                          """.format(pubMed_ID))
        date_handler = cursor.fetchall()[0][0]
        paper_info.append(date_handler)
        cursor.execute("""SELECT A.initials, A.Last_Name
                          FROM mydb.results AS R
                          INNER JOIN mydb.results_has_author as RA ON RA.results_pubMed_ID = R.pubMed_ID
                          INNER JOIN mydb.author AS A ON RA.Author_idAuthor = A.idAuthor
                          WHERE R.pubMed_ID = '{0}'
                          """.format(pubMed_ID))
        author_handler = cursor.fetchall()
        authors = []
        for author in author_handler:
            author = " ".join(author)
            authors.append(author.strip("-"))
        paper_info.append(list(set(authors)))
        
        papers.append(paper_info)
    cursor.close()
    conn.close()
    return papers

if __name__ == '__main__':
    app.run(debug=False)