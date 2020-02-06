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

sectors = ['01/B1','09/H1']
#sectors = ['13/D1', '13/D2', '13/D3']

pathInput = "../data/input/"
fileCercauniversita = pathInput + "cercauniversita/" + sectors.replace() + ".csv"
fileTsv = pathInput + "01B1_09H1_withNames_scopusId_editedAddedMissingScopusId.tsv"

tsv = dict()
with open(fileTsv, newline='') as csvfile:
	spamreader = csv.DictReader(csvfile, delimiter='\t')
	for row in spamreader:
		surname = row['COGNOME']
		name = row['NOME']
		authorId = row['SCOPUS ID']
		idCv = row['ID CV']
		sn = (surname + name).lower()
		for c in " '-":
			sn = sn.replace(c,"")
		tsv[sn] = {"name": name, "surname": surname, "authorId": authorId, "idCv": idCv}

print (len(tsv))

cercauni = dict()
matchCounter = 0
with open(fileCercauniversita, newline='') as csvfile:
	spamreader = csv.DictReader(csvfile, delimiter='\t')
	for row in spamreader:
		sn = (row['Cognome e Nome']).lower()
		for c in " '-":
			sn = sn.replace(c,"")
		cercauni[sn] = {"name": name, "surname": surname, "authorId": authorId, "idCv": idCv}
		if sn in tsv:
			matchCounter += 1

print (len(cercauni))

print (matchCounter)
