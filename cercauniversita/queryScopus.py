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

apiURL_search = 'https://api.elsevier.com/content/search/author'
#sectors = ['01/B1','09/H1']
#sectors = ['13/D1', '13/D2', '13/D3']
sector = '01/B1'

pathInput = "../data/input/"
fileCercauniversita = pathInput + "cercauniversita/" + sector.replace("/","") + "_2016.csv"
fileTsv = pathInput + "01B1_09H1_withNames_scopusId_editedAddedMissingScopusId.tsv"

def searchAuthor(name, max_retry=2, retry_delay=1):
	
	retry = 0
	cont = True
	while retry < max_retry and cont:

		#print(apiURL_AbstractDoi + urllib.parse.quote(doi))
		query = 'AUTH(' + name + ')'
		queryEncoded = urllib.parse.quote(query)
		params = {'apikey':apikeys.keys[0], 'httpAccept':'application/json', 'query':queryEncoded} #, 'view':'FULL'}
		r = requests.get(apiURL_search, params=params)
				
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

with open(fileCercauniversita, newline='') as csvfile:
	spamreader = csv.DictReader(csvfile, delimiter='\t')
	for row in spamreader:
		sn = (row['Cognome e Nome']).lower()
		for c in "'-":
			sn = sn.replace(c,"")
		print (sn)
		authorJson = searchAuthor(sn)
		print (authorJson)
		sys.exit()
