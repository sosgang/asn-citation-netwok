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
#sector = '09/H1'
sectors = ['13/D1', '13/D2']
# scopus author search settings, see https://dev.elsevier.com/api_key_settings.html 
authorsPerPage = 200
numItemLimit = 5000

pathInput = "../data/input/cercauniversita/"
#fileTsv = pathInput + "01B1_09H1_withNames_scopusId_editedAddedMissingScopusId.tsv"
pathOutput = "../data/input/authors-search/"
anno = "2016"


def searchAuthor(firstnames, lastnames, idCercauni, sector, max_retry=2, retry_delay=1):
	start = 0
	filepath = os.path.join(pathOutput + sector.replace("/","") + "/", idCercauni + '.json')
	data = searchAuthorScopus(firstnames, lastnames, start)
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
			data = searchAuthorScopus(curr['fn'], curr['sn']) #, start)
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
						data = searchAuthorScopus(curr['fn'], curr['sn'], numStart+numPerPage)
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
			data = searchAuthorScopus(firstnames, lastnames, numStart+numPerPage)
			res.append(data)
			numRes = int(data['search-results']['opensearch:totalResults'])
			numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
			numStart = int(data['search-results']['opensearch:startIndex'])
			print ("numRes: %d, numStart: %d, numPerPage: %d" % (numRes, numStart, numPerPage))
		return res
	return None
	'''
	if os.path.isfile(filepath):
		with open(filepath) as json_file:
			data = json.load(json_file)
			numRes = int(data['search-results']['opensearch:totalResults'])
			#res.append(data)
			numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
			numStart = int(data['search-results']['opensearch:startIndex'])
			if numRes == 0:
				return None
			while (numStart + numPerPage) < numRes and start < numItemLimit:
				print (' '.join(lastname) + ': ' + str(start))
				data = searchAuthorScopus(firstname, lastname, start)
				res.append(data)
				numRes = int(data['search-results']['opensearch:totalResults'])
				numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
				numStart = int(data['search-results']['opensearch:startIndex'])
				print ("numRes: %d, numStart: %d, numPerPage: %d" % (numRes, numStart, numPerPage))
				start += authorsPerPage
			return res
			#return True #data
	else:
		return None
	'''
	
	'''
	if os.path.isfile(filepath):
		with open(filepath) as json_file:
			data = json.load(json_file)
			numRes = int(data['search-results']['opensearch:totalResults'])
			#res.append(data)
			numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
			numStart = int(data['search-results']['opensearch:startIndex'])
			if numRes == 0:
				return None
			while (numStart + numPerPage) < numRes and start < numItemLimit:
				print (' '.join(lastname) + ': ' + str(start))
				data = searchAuthorScopus(firstname, lastname, start)
				res.append(data)
				numRes = int(data['search-results']['opensearch:totalResults'])
				numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
				numStart = int(data['search-results']['opensearch:startIndex'])
				print ("numRes: %d, numStart: %d, numPerPage: %d" % (numRes, numStart, numPerPage))
				start += authorsPerPage
			return res
			#return True #data
	else:
		return None
	'''

def searchAuthorScopus(firstname, lastname, start=0, max_retry=2, retry_delay=1):
	
	retry = 0
	cont = True
	query = 'AUTHFIRST(' + " ".join(firstname) + ') and AUTHLAST(' + " ".join(lastname) + ')'
	while retry < max_retry and cont:

		#query = 'AUTH(' + name + ')'
		#queryEncoded = urllib.parse.quote(query)
		params = {
			'apikey':apikeys.keys[0],
			'httpAccept':'application/json',
			'query':query,
			'count': str(authorsPerPage),
			'start': str(start)
		} #, 'view':'FULL'}
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
	#numPerPage = int(data['search-results']['opensearch:itemsPerPage'])
	#if numPerPage < numRes:
	#	pass
	#if numRes != 1:
	print(str(numRes) + ": " + query)
	#json = r.text
	#json['request-time'] = str(datetime.datetime.now().utcnow())
	# TO DECODE:
	#oDate = datetime.datetime.strptime(json['request-time'], '%Y-%m-%d %H:%M:%S.%f')
	return json
	

for sector in sectors:
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

