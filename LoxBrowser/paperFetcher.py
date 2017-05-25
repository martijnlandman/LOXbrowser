# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:26:02 2017

@author: Martijn Landman
"""

from Bio import Entrez
from Bio import Medline

TERM = '(("1990"[Date - Publication] : "3000"[Date - Publication]) AND (LOX OR lipoxygenase)) NOT cancer'

Entrez.email = 'A.N.Other@example.com'
h = Entrez.esearch(db='pubmed', retmax='1', term=TERM)
result = Entrez.read(h)
resultCount = result['Count']
print('Total number of publications containing lipoxygenase: {0}'.format(resultCount))

print('Getting {0} publications containing lipoxygenase...'.format(resultCount))
h = Entrez.esearch(db='pubmed', retmax=resultCount, term=TERM)
result = Entrez.read(h)
ids = result['IdList']
h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
records = Medline.parse(h)
records = list(records)

#authors = []
for record in records:
    print("title:", record.get("TI", "?"))
    print("authors:", record.get("AU", "?"))
    print("source:", record.get("SO", "?"))
    print("")
#    au = record.get('AU', '?')
#    for a in au:
#        if a not in authors:
#            authors.append(a)
#    authors.sort()
#print('Authors: {0}'.format(', '.join(authors)))