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

inputProva = "../data/input/cercauniversita/" + "_".join(mylib.sectors) + "_" + anno "_PROVA.tsv"
inputTsvAuto = "../data/input/cercauniversita/" + "_".join(mylib.sectors) + "_" + anno + "_id_MAPPING-AUTO.tsv"
inputTsvManual = "../data/input/cercauniversita/" + "_".join(mylib.sectors) + "_" + anno + "_id_MANUALCHECKED.tsv"
inputPathAbstracts = "../data/output/abstracts/" + "_".join(mylib.sectors) + "/"

outputPath = "../data/output/publicationsList/"

apiURL_Search = "https://api.elsevier.com/content/search/scopus"

#https://api.elsevier.com/content/search/scopus?apikey=f5f5306cfd6042a38e90dc053d410c56&httpAccept=application/json&query=AU-ID(55303032000)&view=COMPLETE&start=25&count=26
def getPublicationPage(authorId, start, max_retry=2, retry_delay=1):
#def getAbstract(doi, max_retry=2, retry_delay=1):
	
	retry = 0
	cont = True
	while retry < max_retry and cont:

		query = "AU-ID(" + authorId + ")"
		params = {"apikey":apikeys.keys[0], "httpAccept":"application/json", "query": query, "view": "COMPLETE", "start": start}
		r = requests.get(apiURL_Search, params=params)
				
		#if self.raw_output:
		#	self.save_raw_response(r.text)

		# quota exceeded -> http 429 (see https://dev.elsevier.com/api_key_settings.html)
		if r.status_code == 429:
			print ("Quota exceeded for key " + apikeys.keys[0] + " - EXIT.")
			apikeys.keys.pop(0)
		
		elif r.status_code > 200 and r.status_code < 500:
			print(u"{}: errore nella richiesta: {}".format(r.status_code, r.url))
			return None

		if r.status_code != 200:
			retry += 1
			if retry < max_retry:
				time.sleep(retry_delay)
			continue

		cont = False 
			 
	if retry >= max_retry: 
		return None 
 
	json = r.json() 
	json['request-time'] = str(datetime.datetime.now().utcnow())
	# TO DECODE:
	#oDate = datetime.datetime.strptime(json['request-time'], '%Y-%m-%d %H:%M:%S.%f')
	return json	

def mergeJson(json1, json2):
	try:
		#numRes1 = int(json1["search-results"]["opensearch:totalResults"])
		#numRes2 = int(json2["search-results"]["opensearch:totalResults"])
		#json1["search-results"]["opensearch:totalResults"] = str(numRes1 + numRes2)
		pubs1 = json1["search-results"]["entry"]
		pubs2 = json2["search-results"]["entry"]
		pubs12 = pubs1 + pubs2
		pubs1["search-results"]["entry"] = pubs12
	except:
		...
	return pubs12
	
def getPublicationList(authorId):
	json = getPublicationPage(authorId, 0)
	try:
		numResults = int(json["search-results"]["opensearch:totalResults"])
		numDownloaded = 25
		while numDownloaded < numResults:
			jsonPart = getPublicationPage(authorId, numDownloaded)
			json = mergeJson(json, jsonPart)
			numDownloaded += 25
	except:
		...
	return json

##### TODO ##### TODO ##### TODO ##### TODO ##### TODO #####
# controlla che json dell'abstract ritornato da api sia ok
##### TODO ##### TODO ##### TODO ##### TODO ##### TODO #####
def checkAbsFormat(j):
	numRes = int(j["search-results"]["opensearch:totalResults"])
	pubs = json["search-results"]["entry"]
	if numRes == len(pubs):
		return True
	else:
		print (j["search-results"]["opensearch:Query"]["@searchTerms"] + " - ERROR: numRes=" + str(numRes) + ", numPubs in Json=" + str(len(pubs)))
		return False
	
def saveJsonPubs(j, authorId, pathOutput):

	if (checkAbsFormat(j)):
		if not os.path.isdir(pathOutput):
			os.makedirs(pathOutput)
			
		completepath = os.path.join(pathOutput, authorId + '.json')

		with open(completepath, 'w') as outfile:
			json.dump(j, outfile, indent=3)
		
		return True
	else:
		return False
		
for tsvFilename in [inputProva] #[inputTsvAuto,inputTsvManual]
	with open(tsvFilename, newline='') as tsvFile:
		spamreader = csv.DictReader(tsvFile, delimiter='\t')
		table = list(spamreader)
		for row in table:
			idCercauni = row["cercauniId"]
			authorId = row["AuthorId"]
			print (authorId)
			json = getPublicationList(authorId)
			if json is not None and saveJsonPubs(json, authorId, outputPath):
				print ('\tSaved to file.')
			else:
				print ('\tNone -> not saved.')
