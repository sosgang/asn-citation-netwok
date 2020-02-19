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

import apikeys
import mylib

pathInput = "data/input/"
pathOutput = "data/output/abstracts/" + ("_".join(mylib.sectors)).replace("/", "") + "/"
inputTsv = pathInput + '09.dois-candidati-2016-ordered.tsv'
outputTsv = pathInput + "_".join(mylib.sectors).replace("/","") + "_withNames.tsv"
outputTsvWithAsnOutcomes = outputTsv.replace(".tsv","") + "_AsnOutcomes.tsv"
pathAsnDownload = "/var/mobiliti/data/in/2016/candidati/"

apiURL_AbstractDoi = 'https://api.elsevier.com/content/abstract/doi/'


##### TODO ##### TODO ##### TODO ##### TODO ##### TODO #####
# controlla che json dell'abstract ritornato da api sia ok
##### TODO ##### TODO ##### TODO ##### TODO ##### TODO #####
def checkAbsFormat(j):
	return True

# Salvo usando eid come nome
def saveJsonAbstract(j):

	if (checkAbsFormat(j)):
		eid = j['abstracts-retrieval-response']['coredata']['eid']
		
		if not os.path.isdir(pathOutput):
			os.makedirs(pathOutput)
			
		counter = 1
		completepath = os.path.join(pathOutput, eid + '.json')

		with open(completepath, 'w') as outfile:
			json.dump(j, outfile, indent=3)
		
		return True

	else:
		return False

#'https://api.elsevier.com/content/abstract/scopus_id/0032717048?apikey=5953888c807d52ee017df48501d3e598&httpAccept=application/json&view=FULL'
def getAbstract(doi, max_retry=2, retry_delay=1):
	
	retry = 0
	cont = True
	while retry < max_retry and cont:

		params = {'apikey':apikeys.keys[0], 'httpAccept':'application/json'} #, 'view':'FULL'}
		doiEncoded = urllib.parse.quote(doi)
		#print(apiURL_AbstractDoi + urllib.parse.quote(doi))
		r = requests.get(apiURL_AbstractDoi + doiEncoded, params=params)
				
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

# scarica e salva su file (nome=eid.json) json abstract (via scopus API)
# NB: effettua controllo doi con già abstract scaricato, per non ripetere l'operazione
def getAbstracts(dois):
	
	doisToSkip = list()
	
	contents = glob(pathOutput + '*.json')
	contents.sort()
	for filename_withPath in contents:
		#print (filename_withPath)
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			doi = data['abstracts-retrieval-response']['coredata']['prism:doi']
			eid = data['abstracts-retrieval-response']['coredata']['eid']
			doisToSkip.append(doi)
	
	for doi in dois:
		if doi not in doisToSkip:
			print ('Processing ' + doi)
			jsonAbs = getAbstract(doi)
			if jsonAbs is not None:
				saveJsonAbstract(jsonAbs)
				print ('\tSaved to file.')
			else:
				print ('\tNone -> not saved.')
		else:
			print ('Skipping doi ' + doi + ': already downloaded')



# Add authors names and surnames to the TSV ()
#mylib.addAuthorsNamesToTsv(inputTsv, outputTsv, pathInput)

mylib.addAsnOutcomesToTsv(mylib.sectors, outputTsv, outputTsvWithAsnOutcomes, pathAsnDownload)

sys.exit()

#getAbstracts(['10.1016/j.scico.2011.10.006', '10.1016/S0005-2736(99)00198-4', '10.1016/S0014-5793(01)03313-0'])
dois = mylib.getDoisSet(inputTsv)
#print (len(dois))
getAbstracts(dois)

# get delta time
'''
dt1 = datetime.datetime.now()
#print(dt1.year)v

time.sleep(1)
dt2 = datetime.datetime.now()

# FORMAT vedi https://www.w3schools.com/python/python_datetime.asp
#print(dt.strftime("%Y-%m-%d"))

a = {'nome': 'Francesco', 'date1': dt1, 'date2': dt2}
print ( (a['date2'] - a['date1']).total_seconds() )

b = {'nome': 'Francesco', 'date1': datetime.datetime(2020, 1, 23, 12, 26, 1, 625769), 'date2': datetime.datetime(2020, 1, 23, 12, 26, 2, 526150)}
deltaB2 = ( (b['date2'] - b['date1']) )
print (deltaB2.total_seconds())

deltaTest = datetime.timedelta(seconds=1)
print (deltaTest.total_seconds())

print (b)
if deltaB2.total_seconds() > deltaTest.total_seconds():
	print ('maggiore')
else:
	print ('minore')
'''



'''
class ScopusDownloader(object): 

	def __init__(self, url, raw_output=None, limit_results=100, max_retry=2, retry_delay=10):
	
		self.url = url
		self.raw_output = raw_output 
		self.max_retry = max_retry
		self.retry_delay = retry_delay
		self.limit_results = limit_results
		
	def save_raw_response(self, content):

		path = self.raw_output
		
		if not os.path.isdir(path):
			os.mkdir(path)
		
		counter = 1
		now = datetime.datetime.now().strftime("%H%M%S")
		filename = "{:}{:04d}.json".format(now, counter)
		completepath = os.path.join(path, filename)
		while os.path.isfile(completepath):
			counter += 1
			filename = "{:}{:04d}.json".format(now, counter)
			completepath = os.path.join(path, filename)

		f = open(completepath, 'w')
		f.write(content)
		f.close()


	def get(self, params):
		
		retry = 0
		cont = True
		while retry < self.max_retry and cont:

			r = requests.get(self.url, params=params)
			
			if self.raw_output:
				self.save_raw_response(r.text)

			if r.status_code > 200 and r.status_code < 500:
				print(u"{}: errore nella richiesta: {}".format(r.status_code, r.url))
				return None

			if r.status_code != 200:
				retry += 1
				if retry < self.max_retry:
					time.sleep(self.retry_delay)
				continue

			cont = False 
			 
		if retry >= self.max_retry: 
			return None 
 
		return r.json() 
 
 
	def download_results(self, params): 
	 
		ret = [] 
		mypar = params.copy() 
		 
		start = -1 
		items = 0 
		total = 0 
		while start + items < total: 
			part = self.get(mypar) 
			if part and part.get("search-results"): 
 
				start = int(part["search-results"]["opensearch:startIndex"]) 
				items = int(part["search-results"]["opensearch:itemsPerPage"]) 
				if total == 0: 
					if self.limit_results > 0: 
						total = min(int(part["search-results"]["opensearch:totalResults"]), self.limit_results) 
					else: 
						total = int(part["search-results"]["opensearch:totalResults"]) 
				 
				if items > 0: 
					ret.extend(part["search-results"]["entry"]) 
				#print(start, items, total) 
				 
				mypar["start"] = start + items 
			 
			else: 
				break 
 
		return ret

'''
