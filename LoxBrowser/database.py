from flask import Flask
import mysql.connector
from mod_python import apache

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()


def index(req):
  req.content_type = "text/html"
  req.write ("Hello World")
  zoek(req)

def form():
  return """<form action=http://cytosine.nl/~owe4_bi1a_1/demodb.py/fillDatabase>
            <input type=text name=woord><input type=submit></form>"""

def fillDatabase(req,woord="zinc finger"):
  req.content_type = "text/html"
  req.write(form())
  req.write ("Zoeken in ensembldb")
  
  #make the connection to the database on the server
  conn = mysql.connector.connect(host = "127.0.0.1",
                         user = "owe8_1617_gr3",
                         password = "blaat1234",
                         db="owe8_1617_gr3")

  cursor = conn.cursor ()
  #replace the values inside the []'s (including the brackets) with the values or variables that need to be inserted
  # by using a transaction you can insert into multiple tables

  conn.start_transaction(consistent_snapshot=bool,
                        isolation_level=level,
                        readonly=access_mode)

#to do, put ever statement in a seperate execute

  cursor.execute ("INSERT INTO results(`pubMed ID`,url,Title) VALUES (%i,%s,%s)", (pubMed_id, URL, Title));
  cursor.execute ("INSERT INTO Author(idAuthor,initials,`Last name`) VALUES (%s,%s,%s)", (Author_ID, Initials, Last_name));
  cursor.execute ("INSERT INTO results_has_Author(`results_pubMed ID`,Author_idAuthor) VALUES (%s,%s)", (pubMed_id, Author_ID));
                     
  cursor.execute ("INSERT INTO Lox(`lox`,`NCBI prot_ID`,`fullname`) VALUES (%s,%s,%s)", (Lox, NCBI_lox, Lox_full));
  cursor.execute ("INSERT INTO results_has_Lox(`results_pubMed ID`,Lox_lox) VALUES (%s,%s)", (pubMed_id, Lox));
                     
  cursor.execute ("INSERT INTO Organism(`Name`,`Kingdom`) VALUES (%s, %s)", (Organism_Name, Kingdom));
  cursor.execute ("INSERT INTO results_has_Organism(`results_pubmed ID`,`Organism_Name`) VALUES (%s,%s)", (pubMed_id, Organism_name));
                     
  cursor.execute ("INSERT INTO `publication_date`(`date`) VALUES (%s)", (Publication_date));
  cursor.execute ("INSERT INTO `results_has_publication_date`(`results_pubMed ID`,`publication_date_date`) VALUES (%s,%s)", (pubMed_id, Publication_date));
                     
  cursor.execute ("INSERT INTO `keywords`(`keyword_ID`,`keyword`) VALUES (%d,%s)", (keyword_ID, keyword));
                      
  cursor.execute ("INSERT INTO `Toepassing`(`Toepassing`) VALUES (%s)", (Toepassing));
  cursor.execute ("INSERT INTO `results_has_Toepassing`(`results_pubMed ID`,`Toepassing_Toepassing`) VALUES (%s,%s))", (pubMed_id,Toepassing));
                     
  conn.commit()

  rows = cursor.fetchall ()




  for row in rows:
    req.write ("<hr>")
