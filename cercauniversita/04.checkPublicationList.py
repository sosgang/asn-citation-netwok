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
import mylib

anno = "2016"

inputTsvAuto = "../data/input/cercauniversita/" + "_".join(mylib.sectors).replace("/","") + "_" + anno + "_id_MAPPING-AUTO.tsv"
inputTsvManual = "../data/input/cercauniversita/" + "_".join(mylib.sectors).replace("/","") + "_" + anno + "_id_MANUALCHECKED.tsv"
inputTsvCercauniversita = "../data/input/cercauniversita/" + "_".join(mylib.sectors).replace("/","") + "_" + anno + "_id_CERCAUNIVERSITA.tsv"
inputPathAbstracts = "../data/output/abstracts/" + "_".join(mylib.sectors).replace("/","") + "/"

publicationListPath = "../data/output/publicationsList/" + "_".join(mylib.sectors).replace("/","") + "/"
abstractsPath = "../data/output/abstracts/" + "_".join(mylib.sectors).replace("/","") + "/"

# UNUSED
def doChecks():
	for tsvFilename in [inputTsvAuto,inputTsvManual,inputTsvCercauniversita] :
		with open(tsvFilename, newline='') as tsvFile:
			spamreader = csv.DictReader(tsvFile, delimiter='\t')
			table = list(spamreader)

			# TEST 1: multiple authorIds
			multipleList = list()
			multipleList.append(["cercauniId", "AuthorId"])
			authors = list()
			for row in table:
				idCercauni = row["cercauniId"]
				authorId = row["AuthorId"]
				if authorId not in authors:
					authors.append(authorId)
				else:
					multipleList.append([idCercauni, authorId])

			# TEST 2: missing JSON (download problem)
			missingJsonList = list()
			missingJsonList.append(["cercauniId", "AuthorId"])
			for row in table:
				idCercauni = row["cercauniId"]
				authorId = row["AuthorId"]
				if not os.path.exists(os.path.join(publicationListPath, authorId + '.json')):
					print (idCercauni + "\t" + authorId)
					missingJsonList.append([idCercauni, authorId])
			
			print (multipleList)
			print (missingJsonList)





def getEidsToDownload(arrayFiles, pathAbstracts):
	pubsList = set()
	counter = 0
	for tsvFilename in arrayFiles:
		with open(tsvFilename, newline='') as tsvFile:
			spamreader = csv.DictReader(tsvFile, delimiter='\t')
			table = list(spamreader)
			for row in table:
				idCercauni = row["cercauniId"]
				authorId = row["AuthorId"]
				
				# skip authors for whom no scopus authorId has been found
				if authorId == "":
					continue
				
				pubsFile = publicationListPath + authorId + ".json"
				with open(pubsFile) as json_file:
					j = json.load(json_file)
					entries = j["search-results"]["entry"]
					for entry in entries:
						counter += 1
						#doi = entry["prism:doi"]
						eid = entry["eid"]
						pubsList.add(eid)
	#print (counter)
	print (len(pubsList))


	pubsAbstracts = set()
	contents = glob(pathAbstracts + '*.json')
	contents.sort()
	for filename_withPath in contents:
		eid = os.path.basename(filename_withPath).replace(".json","")
		pubsAbstracts.add(eid)
	print (len(pubsAbstracts))

	pubsToDownload = pubsList.difference(pubsAbstracts)
	print (len(pubsToDownload))
	
	return pubsToDownload
	
eidSet = getEidsToDownload([inputTsvAuto,inputTsvManual,inputTsvCercauniversita], abstractsPath)
for eid in eidSet:
	print ('Processing ' + eid)
	jsonAbs = mylib.getAbstract(eid, 'EID', apikeys.keys)
	if jsonAbs is not None:
		mylib.saveJsonAbstract(jsonAbs,abstractsPath)
		print ('\tSaved to file.')
	else:
		print ('\tNone -> not saved.')

#getAbstracts(pubsToDownload)
