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

sectors = ['13/D1', '13/D2', '13/D3']
anno = "2016"

pathInput = "../data/input/cercauniversita/"
inputTsvManual = pathInput + "_".join(sectors).replace("/","") + "_" + anno + "_id_MANUALCHECKED_OLDVERSION_GOOGLESPREADSHEET.tsv"
inputTsvAutomatic = pathInput + "_".join(sectors).replace("/","") + "_" + anno + "_id_2doMANUALCHECK.tsv"

outputAutoFile = pathInput + "_".join(sectors).replace("/","") + "_" + anno + "_id_MAPPING-AUTO.tsv"
outputManualFile = pathInput + "_".join(sectors).replace("/","") + "_" + anno + "_id_MANUALCHECKED.tsv"

manualMap = dict()
manualNotFound = list()
with open(inputTsvManual, newline='') as tsvFile:
	spamreader = csv.DictReader(tsvFile, delimiter='\t')
	table = list(spamreader)
	for row in table:
		idCercauni = row["Id"]
		authorId = row["AUTHOR ID SCELTO"]
		if authorId != '':
			manualMap[idCercauni] = authorId
		else:
			manualNotFound.append(idCercauni)

#counter = 0
resAutoMap = dict()
resManualMap = dict()
with open(inputTsvAutomatic, newline='') as tsvFile:
	spamreader = csv.DictReader(tsvFile, delimiter='\t')
	table = list(spamreader)
	for row in table:
		idCercauni = row["Id"]
		numLink = row["#Link"]
		authorId = row["L1"].replace("https://www.scopus.com/authid/detail.uri?partnerID=HzOxMe3b&authorId=","").replace("&origin=inward","")
		'''
		if idCercauni in manualMap:
			#print ("%s" % (numLink))
			if (manualMap[idCercauni] == authorId):
				if numLink == "1":
					#print ("Uguali uguali - NUMLINK = 1")
					pass
				else:
					#print ("Uguali uguali - NUMLINK > 1")
					#print ("NumLink: %s, Auto #1: %s, Manual: %s" % (numLink, authorId, manualMap[idCercauni]))
					pass
			else:
				print (authorId + " - " + manualMap[idCercauni])
		else:
			if numLink != '1' and idCercauni not in manualNotFound:
				counter += 1
print (counter)
		'''
		if idCercauni in manualMap:
			#if (manualMap[idCercauni] == authorId):
			resAutoMap[idCercauni] = manualMap[idCercauni]
		else:
			#if numLink != '1' and idCercauni not in manualNotFound:
			if numLink == '1':
				resAutoMap[idCercauni] = authorId
			elif idCercauni in manualNotFound:
				resAutoMap[idCercauni] = ''
			else:
				#print ("ERROR: manage this case...")
				print (idCercauni + " - " + numLink)
				resManualMap[idCercauni] = ''
				#sys.exit()


# Save result to TSV file 
res = "cercauniId	AuthorId\n"
for idCercauni in resAutoMap:
	res += idCercauni + "\t" + resAutoMap[idCercauni] + "\n"

text_file = open(outputAutoFile, "w")
text_file.write(res)
text_file.close()

# Save result to TSV file 
res = "cercauniId	AuthorId\n"
for idCercauni in resManualMap:
	res += idCercauni + "\t" + resManualMap[idCercauni] + "\n"

text_file = open(outputManualFile, "w")
text_file.write(res)
text_file.close()
