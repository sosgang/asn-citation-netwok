# -*- coding: UTF-8 -*-
import requests
import csv
import sys
import datetime
import time
import os 
import json
from glob import glob
import ast

import urllib.parse

sys.path.append('..')
import apikeys

pathInput = "../data/input/"
pathTsv = pathInput + "cercauniversita/"
pathAuthorSearch = pathInput + "authors-search/"

sectors = ['13/D1', '13/D2', '13/D3']

res = "Id	Cognome e Nome	Fascia	Ateneo	Struttura di afferenza	S.S.D.	AUTHOR-ID	#Link	L1	L2	L3	...\n"
for sector in sectors:
	tsvFileName = pathTsv + sector.replace("/", "") + "_2016_id.csv"
	maxRes = 0
	with open(tsvFileName, newline='') as tsvFile:
		spamreader = csv.DictReader(tsvFile, delimiter='\t')
		table = list(spamreader)
		for row in table:
			idCv = row["Id"]
			jsonFilename = pathAuthorSearch + sector.replace("/","") + "/" + idCv + ".json"
			if os.path.exists(jsonFilename):
				with open(jsonFilename) as json_file:
					data = json.load(json_file)
					totalRes = data["search-results"]["opensearch:totalResults"]
					if int(totalRes) > maxRes:
						maxRes = int(totalRes)
		#print (maxRes)
		
		for row in table:
			idCv = row["Id"]
			jsonFilename = pathAuthorSearch + sector.replace("/","") + "/" + idCv + ".json"
			if os.path.exists(jsonFilename):
				with open(jsonFilename) as json_file:
					data = json.load(json_file)
					totalRes = data["search-results"]["opensearch:totalResults"]
					authors = data["search-results"]["entry"]
					hrefs = list()
					for author in authors:
						for link in author["link"]:
							if link["@ref"] == "scopus-author":
								href = link["@href"]
						#dcId = author["dc:identifier"]
						#eid = author["eid"]
						#authorId = dcId.replace("AUTHOR_ID:","")
						#hrefs.append({"href": href, "authorId": authorId})
						hrefs.append(href)
					#print (idCv)
					#print (hrefs)
					#print (row)
					#"Id","Fascia","Cognome e Nome","Genere","Ateneo","Facoltà","S.S.D.","S.C.","Struttura di afferenza"
					res += row["Id"] + "\t" + row["Cognome e Nome"] + "\t" + row["Fascia"] + "\t" + row["Ateneo"].replace("\"","") + "\t" + row["Struttura di afferenza"].replace("\"","") + "\t" + row["S.S.D."] + "\t\t" + totalRes + "\t" + "\t".join(hrefs) + "\n"
			else:
				res += row["Id"] + "\t" + row["Cognome e Nome"] + "\t" + row["Fascia"] + "\t" + row["Ateneo"].replace("\"","") + "\t" + row["Struttura di afferenza"].replace("\"","") + "\t" + row["S.S.D."] + "\t\t0\t\n"

text_file = open(pathTsv + "_".join(sectors).replace("/","") + "_2016_id_2doMANUALCHECK.tsv", "w")
text_file.write(res)
text_file.close()
					
