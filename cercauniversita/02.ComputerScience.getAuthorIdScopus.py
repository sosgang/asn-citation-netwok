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

#pathInput = "../data/input/authors-search/"
pathInput = "../data/input/"
pathInputCsv = pathInput + "cercauniversita/"
pathInputJson = pathInput + "authors-search-v2/"

sectors = ["01/B1", "09/H1"]
anno = "2016"
areaToSearch = "COMP"


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
			if testSubjectArea(author, area):
				maxDocs = numDocs
				res = author
	return res


manualSearchList = list()
automaticMatchList = dict()
for sector in sectors:
	tsvFilename = pathInputCsv + sector.replace("/","") + "_" + anno + "_id.csv"

	with open(tsvFilename, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		table = list(spamreader)
		for row in table:
			idCercauni = row["Id"]
			jsonFilename = pathInputJson + sector.replace("/","") + "/" + idCercauni + ".json"
			if not os.path.exists(jsonFilename):
				manualSearchList.append(idCercauni)
			else:
					if "_" in jsonFilename:
						print ("Multiple files.")
						#sys.exit()
						
					with open(jsonFilename) as json_file:
						data = json.load(json_file)
						totalRes = data["search-results"]["opensearch:totalResults"]
						authors = data["search-results"]["entry"]
						bestMatch = testAuthors(authors, areaToSearch)
						if "eid" not in bestMatch:
							#print (idCercauni)
							manualSearchList.append(idCercauni)
						else:
							#	print (bestMatch["eid"])
							automaticMatchList[idCercauni] = bestMatch["eid"].replace("9-s2.0-","")
#print (manualSearchList)
#print (automaticMatchList)

resAuto = "cercauniId	AuthorId\n"
for idCercauni in automaticMatchList: #sorted(automaticMatchList.keys()) :
	resAuto += idCercauni + "\t" + automaticMatchList[idCercauni] + "\n"
#print (resAuto)
text_file = open(pathInputCsv + "_".join(sectors).replace("/","") + "_2016_id_MAPPING-AUTO.tsv", "w")
text_file.write(resAuto)
text_file.close()

resManual = "cercauniId	AuthorId\n"
for idCercauni in manualSearchList:
	resManual += idCercauni + "\t\n"
#print (resManual)
text_file = open(pathInputCsv + "_".join(sectors).replace("/","") + "_2016_id_2doMANUALCHECK.tsv", "w")
text_file.write(resManual)
text_file.close()
	

'''
manualSearchList = list()
for sector in mylib.sectors:
	contents = glob(pathInput + sector.replace("/","") + "/*.json")
	contents.sort()
	for filename_withPath in contents:
		# check if data in multiple files
		idCercauniFilename = os.path.basename(filename_withPath).replace(sector.replace("/","")+"-"+anno+"-", "").replace(".json","")
		if "_" in idCercauniFilename:
			print ("Multiple files.")
			#sys.exit()
		
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			totalRes = data["search-results"]["opensearch:totalResults"]
			#print (idCercauniFilename + ": " + totalRes)
			authors = data["search-results"]["entry"]
			bestMatch = testAuthors(authors, areaToSearch)
			if "eid" not in bestMatch:
				print (idCercauniFilename)
				#print (bestMatch)
				manualSearchList.append(idCercauniFilename)
			#else:
			#	print (bestMatch["eid"])	
	print (manualSearchList)
'''
