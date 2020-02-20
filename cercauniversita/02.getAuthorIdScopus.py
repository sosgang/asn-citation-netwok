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
sectors = ['01/B1']
# scopus author search settings, see https://dev.elsevier.com/api_key_settings.html 
authorsPerPage = 200
numItemLimit = 5000

pathInput = "../data/input/authors-search/"
#pathOutput = "../data/input/authors-search/"
anno = "2016"

def testSubjectArea(author, area):
	if "subject-area" in author:
		if type(author["subject-area"]) is list:
			for subjArea in author["subject-area"]:
				#print ("\t\t" + subjArea["@abbrev"])
				#print ("\t\t" + subjArea["$"])
				if subjArea["@abbrev"] == area:
					#print (subjArea["@abbrev"])
					return True
		else:
			#print ("\t\t" + author["subject-area"]["@abbrev"])
			#print ("\t\t" + author["subject-area"]["$"])
			if author["subject-area"]["@abbrev"] == area:
				#print (author["subject-area"]["@abbrev"])
				return True
	else:
		print ("\t\tNO SUBJECT AREAS!!!")
		return False
	return False
	
def testAuthors(authors, area):
	res = dict()
	maxDocs = 0
	for author in authors:
		numDocs = author["document-count"]
		if maxDocs != 0 and numDocs < maxDocs:
			continue
		if maxDocs == 0 or numDocs > maxDocs:
			#print ("\t" + numDocs)
			if testSubjectArea(author, area):
				maxDocs = numDocs
				res = author
	return res
	
for sector in sectors:
	contents = glob(pathInput + sector.replace("/","") + "/*.json")
	contents.sort()
	for filename_withPath in contents:
		# check if data in multiple files
		idCercauniFilename = os.path.basename(filename_withPath).replace(sector.replace("/","")+"-"+anno+"-", "").replace(".json","")
		if "_" in idCercauniFilename:
			print ("Multiple files.")
			sys.exit()
		
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			totalRes = data["search-results"]["opensearch:totalResults"]
			#print (idCercauniFilename + ": " + totalRes)
			authors = data["search-results"]["entry"]
			bestMatch = testAuthors(authors, "COMP")
			if "eid" not in bestMatch:
				print (idCercauniFilename)
			#else:
			#	print (bestMatch["eid"])	
