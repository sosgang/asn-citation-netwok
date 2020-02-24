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

apiURL_search = 'https://api.elsevier.com/content/search/author'
# scopus author search settings, see https://dev.elsevier.com/api_key_settings.html 
authorsPerPage = 200
numItemLimit = 5000

pathInput = "../data/input/cercauniversita/"
pathOutput = "../data/input/authors-search-v2/"
anno = "2016"

inputTsvAtenei = pathInput + "ListaAteneiSorted.tsv"

def searchAuthor(firstnames, lastnames, idCercauni, sector, ateneo='', area='', max_retry=2, retry_delay=1):
	start = 0
	filepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '.json')
	data = searchAuthorScopus(firstnames, lastnames, ateneo, area, start)
	numRes = int(data['search-results']['opensearch:totalResults'])
	numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
	numStart = int(data['search-results']['opensearch:startIndex'])
	if numRes == 1:
		return [data]
	elif numRes == 0:
		temp = list()
		for firstname in firstnames:
			if len(firstnames) > 1:
				temp.append({'fn': [firstname], 'sn': lastnames})
		#for firstname in firstnames:	
			if len(lastnames) > 1:
				for lastname in lastnames:
					temp.append({'fn': [firstname], 'sn': [lastname]})
		for curr in temp:
			data = searchAuthorScopus(curr['fn'], curr['sn'], ateneo, area, 0) #, start)
			numRes = int(data['search-results']['opensearch:totalResults'])
			numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
			numStart = int(data['search-results']['opensearch:startIndex'])
			if numRes == 1:
				return [data]
			elif numRes == 0:
				continue
			else:
				if numRes < numPerPage:
					return [data]
				else:
					res = [data]
					while (numStart + numPerPage) < numRes: # and start < numItemLimit:
						data = searchAuthorScopus(curr['fn'], curr['sn'], ateneo, area, numStart+numPerPage)
						res.append(data)
						numRes = int(data['search-results']['opensearch:totalResults'])
						numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
						numStart = int(data['search-results']['opensearch:startIndex'])
						print ("numRes: %d, numStart: %d, numPerPage: %d" % (numRes, numStart, numPerPage))
					# TODO JOIN RES
					return res
	else:
		res = [data]
		while (numStart + numPerPage) < numRes: #and start < numItemLimit:
			data = searchAuthorScopus(firstnames, lastnames, ateneo, area, numStart+numPerPage)
			res.append(data)
			numRes = int(data['search-results']['opensearch:totalResults'])
			numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
			numStart = int(data['search-results']['opensearch:startIndex'])
			print ("numRes: %d, numStart: %d, numPerPage: %d" % (numRes, numStart, numPerPage))
		return res
	return None

def searchAuthorScopus(firstname, lastname, ateneo, area, start=0, max_retry=3, retry_delay=1):
	
	retry = 0
	cont = True
	#SUBJAREA(XX)
	#AFFIL()
	query = 'AUTHFIRST(' + " ".join(firstname) + ') and AUTHLAST(' + " ".join(lastname) + ')'
	if ateneo != '':
		query += " AND AFFIL(" + ateneo + ")"
	if area != '':
		query += " AND SUBJAREA(" + area + ")"
	
	while retry < max_retry and cont:
		#queryEncoded = urllib.parse.quote(query)
		params = {
			'apikey':apikeys.keys[0],
			'httpAccept':'application/json',
			'query': query,
			'count': str(authorsPerPage),
			'start': str(start)
		}
		
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
	numRes = int(json['search-results']['opensearch:totalResults'])
	print(str(numRes) + ": " + query)
	return json
	
# Use the Scopus Author Search API to search for Author Ids of the people in cercauniversita.
# output: 
#   - 1 JSON file (in data/input/authors-search/) for each search/person (if numResults > 0)
#   - 1 TSV (one for each sector) with the list of people not found in Scopus (numResults = 0)
'''
for sector in mylib.sectors:
	#fileCercauniversita = pathInput + "cercauniversita/" + sector.replace("/","") + "_2016_id_short.csv"
	fileCercauniversita = pathInput + sector.replace("/","") + "_" + anno + "_id.csv"
	print (fileCercauniversita)	

	missing = list()
	with open(fileCercauniversita, newline='') as csvfile:
		if not os.path.isdir(pathOutput + sector.replace("/","") + "/"):
			os.makedirs(pathOutput + sector.replace("/","") + "/")
		counter = 0
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		table = list(spamreader)
		for row in table:
			sn = (row['Cognome e Nome']).split()
			idCercauni = row['Id']
		
			lastname = list()
			firstname = list()
			for part in sn:
				if part.isupper():
					lastname.append(part)
				else:
					firstname.append(part)
			data = searchAuthor(firstname, lastname, idCercauni, sector)
			if data is not None:
				if type(data) is list and len(data) > 1:
					for i in range(0,len(data)):
						completepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '_' + str(i+1) + '.json')
						with open(completepath, 'w') as outfile:
							json.dump(data[i], outfile, indent=3)
				else:
					completepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '.json')
					with open(completepath, 'w') as outfile:
						json.dump(data[0], outfile, indent=3)
			else:
				missing.append(idCercauni)
	
	if len(missing) > 0:
		res = "Id	Fascia	Cognome e Nome	Genere	Ateneo	Facoltà	S.S.D.	S.C.	Struttura di afferenza\n"
		for row in table:
			currId = row["Id"]
			if currId in missing:
				#print (missing)
				res += row["Id"] + "\t" + row["Fascia"] + "\t" + row["Cognome e Nome"] + "\t" + row["Genere"] + "\t" + row["Ateneo"] + "\t" + row["Facoltà"] + "\t" + row["S.S.D."] + "\t" + row["S.C."] + "\t" + row["Struttura di afferenza"] + "\n"   
		text_file = open(pathInput + "notFoundCercauniversita_" + sector.replace("/","")  + ".csv", "w")
		text_file.write(res)
		text_file.close()
'''

# LOAD THE ATENEI MAP
ateneoMap = dict()
with open(inputTsvAtenei, newline='') as csvfile:
	spamreader = csv.DictReader(csvfile, delimiter='\t')
	for row in spamreader:
		ateneoCercauni = row["Ateneo Cercauniversita"]
		ateneoToSearch = row["Ateneo Search Scopus"]
		ateneoMap[ateneoCercauni] = ateneoToSearch


for sector in mylib.sectors:
	#fileCercauniversita = pathInput + "cercauniversita/" + sector.replace("/","") + "_2016_id_short.csv"
	fileCercauniversita = pathInput + sector.replace("/","") + "_" + anno + "_id.csv"
	print (fileCercauniversita)	

	missing = list()
	with open(fileCercauniversita, newline='') as csvfile:
		if not os.path.isdir(pathOutput + sector.replace("/","") + "/"):
			os.makedirs(pathOutput + sector.replace("/","") + "/")
		counter = 0
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		table = list(spamreader)
		for row in table:
			sn = (row['Cognome e Nome']).split()
			idCercauni = row['Id']
			ateneo = row['Ateneo']
			if ateneo not in ateneoMap:
				print ("ERROR - missing ateneo in ateneoMap: " + ateneo)
				sis.exit()
			#elif ateneoMap[ateneo] == '':
			#	print (ateneo)
			lastname = list()
			firstname = list()
			for part in sn:
				if part.isupper():
					lastname.append(part)
				else:
					firstname.append(part)
			# cerco ateneo e area CS
			data = searchAuthor(firstname, lastname, idCercauni, sector, ateneoMap[ateneo], "COMP")
			if data is None:
				print ("%s, %s: searching area" % (idCercauni, sn))
				data = searchAuthor(firstname, lastname, idCercauni, sector, "COMP")
			if data is None:
				print ("%s, %s: simple search" % (idCercauni, sn))
				data = searchAuthor(firstname, lastname, idCercauni, sector)
			if data is not None:
				if type(data) is list and len(data) > 1:
					for i in range(0,len(data)):
						completepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '_' + str(i+1) + '.json')
						with open(completepath, 'w') as outfile:
							json.dump(data[i], outfile, indent=3)
				else:
					completepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '.json')
					with open(completepath, 'w') as outfile:
						json.dump(data[0], outfile, indent=3)
			else:
				print ("%s, %s: not found" % (idCercauni, sn))
				missing.append(idCercauni)

print ("Missing (i.e. no match found):")
for el in missing:
	print (el)

