import csv
import ast
from glob import glob
import json

#sectors = ['13/D1', '13/D2', '13/D3', '01/B1', '09/H1']
#sectors = ['01/B1','09/H1']
sectors = ['13/D1', '13/D2', '13/D3']

def getAuthorsId(tsv, folderAbstracts, doiEidMap):
	counterAll = 0
	counterGreaterOne = 0
	counterZero = 0
	authorsAll = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in sectors:
				counterAll += 1
				authorsIntersection = set()
				dois = ast.literal_eval(row['DOIS ESISTENTI'])
				idCv = row['ID CV']
				print ("############################################################")
				print (idCv + " - " + str(len(dois)))
				for doi in dois:
					try:
						eid = doiEidMap["doi-to-eid"][doi]
						#print (eid)
						authorsPublication = set()
						with open(folderAbstracts + eid + ".json") as json_file:
							data = json.load(json_file)
							affiliationData = data["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["author-group"]
							#print ("Affiliation")
							#print (affiliationData)
							if type(affiliationData) is not list:
								affiliationList = [affiliationData]
							for affiliation in affiliationList:
								for author in affiliation["author"]:
									name = author["ce:given-name"]
									surname = author["ce:surname"]
									auid = author["@auid"]
									if auid not in authorsAll:
										authorsAll[auid] = {"name": name, "surname": surname}
									authorsPublication.add(auid)
									#print (auid)
							#print (authorsPublication)
							if len(authorsIntersection) is 0:
								#print ("intersection len 0:")
								authorsIntersection = authorsPublication
								#print (authorsIntersection)
							else:
								#print ("intersection len != 0:")
								temp = authorsIntersection.intersection(authorsPublication)
								authorsIntersection = temp
								#print (authorsIntersection)
							#print ()
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doi)
				if len(authorsIntersection) > 1:
					print (authorsIntersection)
					counterGreaterOne += 1
					print ()
				elif len(authorsIntersection) is 0:
					counterZero += 1
	print ("All: " + str(counterAll))
	print ("Zero: " + str(counterZero))
	print ("GreaterOne: " + str(counterGreaterOne))
	
def getDoisSet(f):
	doisList = list()
	with open(f, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in sectors:
				doiTemp = ast.literal_eval(row['DOIS ESISTENTI'])
				doisList.extend(doiTemp)

	# prendo doi unici
	return set(doisList)

def doiEidMap(folder):
	res = { "doi-to-eid": {}, "eid-to-doi": {} }
	contents = glob(folder + '*.json')
	contents.sort()
	# get ...
	for filename_withPath in contents:
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			try:
				eid = data['abstracts-retrieval-response']['coredata']['eid']
				doi = data['abstracts-retrieval-response']['coredata']['prism:doi']
				res["doi-to-eid"][doi] = eid
				res["eid-to-doi"][eid] = doi
			except:
				print ('*** EID/DOI ERROR: ' + filename_withPath + " ***")	
	return res
