import os 
import json
from glob import glob
import sys
import csv
import ast

import mylib

pathInput = "data/input/"
#inputTsv = pathInput + '09.dois-candidati-2016-ordered.tsv'
inputTsv = pathInput + "_".join(mylib.sectors).replace("/","") + "_withNames.tsv"
outputTsv = pathInput + "_".join(mylib.sectors).replace("/","") + "_withNames_scopusId.tsv"
outputTsvEdited = pathInput + "_".join(mylib.sectors).replace("/","") + "_withNames_scopusId_editedAddedMissingScopusId.tsv"

pathAbstracts = "data/output/abstracts/"+ ("_".join(mylib.sectors)).replace("/", "") + "/"
pathOutput = "data/output/"

fileCitationNetV1 = "citationNet_v1_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
#fileCitationNetV2 = "citationNet_v2_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
fileCitationNetV3 = "citationNet_v3_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
fileDoiEidMap = "doiEidMap_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
fileDoiAuthorsMap = "doiAuthorsMap_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
codePrefix = "2-s2.0-"

def computeCitedNetwork(path):
	documentSet = set()
	contents = glob(path + '*.json')
	contents.sort()
	# get set of eids from the input list of dois
	for filename_withPath in contents:
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			try:
				citing = data['abstracts-retrieval-response']['coredata']['eid']
				documentSet.add(citing)
			except:
				print ('*** EID ERROR: ' + filename_withPath + " ***")	

	# create the dictionary of cited papers (with empty lists of citing papers)
	citedDict = dict()
	for citing in documentSet:
		citedDict[citing] = []

	for filename_withPath in contents:
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			try:
				citing = data['abstracts-retrieval-response']['coredata']['eid']
				biblio = data['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']
				numRefs = int(biblio['@refcount'])
				for ref in biblio['reference']: #range(numRefs):
					temp = ref['ref-info']['refd-itemidlist']['itemid']
					if type(temp) is not list:
						idtype = temp['@idtype']
						code = temp['$']
						cited = codePrefix + code
						if cited in documentSet:
							citedDict[cited].append(citing)
					else:
						for el in temp:
							idtype = el['@idtype'] 
							code = el['$']
							cited = codePrefix + code
							if idtype == 'SGR':
								if cited in documentSet:
									citedDict[cited].append(citing)
			except:
				print ('*** BIBLIOGRAPHY ERROR: ' + filename_withPath + " ***")	
	
	return citedDict

def doiAuthorsMap(tsv):
	res = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in mylib.sectors:
				idCv = row['ID CV']
				dois = ast.literal_eval(row['DOIS ESISTENTI'])
				for doi in dois:
					if doi not in res:
						res[doi] = [idCv]
					else:
						l = res[doi]
						l.append(idCv)
						res[doi] = l
	return res

def computeCitedNetwork_v3(tsv, citedNet, doiEidMap, doiAuthorsMap):
	cvIdScopusIdMap = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in mylib.sectors:
				idCv = row['ID CV']
				scopusId = row['SCOPUS ID']
				cvIdScopusIdMap[idCv] = scopusId
		
	res = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in mylib.sectors:
				idCv = row['ID CV']
				sessione = row['SESSIONE']
				fascia = row['FASCIA']
				settore = row['SETTORE']
				scopusId = row['SCOPUS ID']
				doisCited = ast.literal_eval(row['DOIS ESISTENTI'])
				pubsEid = dict()
				pubsDoi = dict()
				pubs = list()
				for doiCited in doisCited:
					'''
					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						#pubsEid[eid] = citedNet[eid]
						temp = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							temp.append({eidCiting: doiAuthorsMap[doiCiting]})
						pubsEid[eidCited] = temp
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)

					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						doisCiting = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							doisCiting.append({doiCiting: doiAuthorsMap[doiCiting]})
						pubsDoi[doiCited] = doisCiting
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)
					'''
					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						temp = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							
							doiAuthorsScopusIdMap = list()
							for idCvTemp in doiAuthorsMap[doiCiting]:
								scopusIdTemp = cvIdScopusIdMap[idCvTemp]
								doiAuthorsScopusIdMap.append({"idCv": idCvTemp, "authorId": scopusIdTemp})
							#temp.append({'eid': eidCiting, 'doi': doiCiting, 'authors-idCv': doiAuthorsMap[doiCiting]})
							temp.append({'eid': eidCiting, 'doi': doiCiting, 'authors': doiAuthorsScopusIdMap})
						pubs.append({
							"cited": {"doi": doiCited, "eid": eidCited},
							"citing": temp
						})
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)

				#print (pubs)
				res[scopusId] = dict()
				res[scopusId][idCv] = {
					"sessione": sessione,
					"fascia": fascia,
					"settore": settore,
					#"pubsEid": pubsEid,
					#"pubsDoi": pubsDoi,
					"pubs": pubs
				}
	# prendo doi unici
	return res
	
# V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** 
# compute citation network v1 (eid-cited -> list-eids-citing) using abstracts (i.e. json files)
#citedNetV1 = computeCitedNetwork(pathAbstracts)

# save the citation network v1 (eid-cited -> list-eids-citing) to file
#with open(pathOutput + fileCitationNetV1, 'w') as fp:
#	json.dump(citedNetV1, fp, indent=4)

# load the citation network v1 (eid-cited -> list-eids-citing) from file
with open(pathOutput + fileCitationNetV1) as json_file:
	citedNetV1 = json.load(json_file)




# V2 *** V2 *** V2 *** V2 *** V2 *** V2 *** V2 *** V2 *** V2 ***
# compute doiAuthors map (in a dictionary)
#doiAuthors = doiAuthorsMap(inputTsv)

# save doiAuthors map to file
#with open(pathOutput + fileDoiAuthorsMap, 'w') as fp:
#	json.dump(doiAuthors, fp, indent=4)

# load doiAuthors map from file
with open(pathOutput + fileDoiAuthorsMap) as json_file:
	doiAuthors = json.load(json_file)




# compute doiEid map (in a dictionary)
#doiEidMap = mylib.doiEidMap(pathAbstracts)

# save doiEid map to file
#with open(pathOutput + fileDoiEidMap, 'w') as fp:
#	json.dump(doiEidMap, fp, indent=4)

# load doiEid map from file
with open(pathOutput + fileDoiEidMap) as json_file:
	doiEidMap = json.load(json_file)




# trovo scopusId - Input: 09_withNames.tsv (provaNomeCognome.py) - Output: 09_withNamesScopusId_editedAddedMissingScopusId.tsv (mylib.getAuthorsId + manual edit)
mylib.addAuthorsIdScopusToTsv(inputTsv, pathAbstracts, doiEidMap, outputTsv)




#citNetV2 = computeCitedNetwork_v2(inputTsv, citedNetV1, doiEidMap, doiAuthors)
#with open(pathOutput + fileCitationNetV2, 'w') as fp:
#	json.dump(citNetV2, fp, indent=4)
citNetV3 = computeCitedNetwork_v3(outputTsvEdited, citedNetV1, doiEidMap, doiAuthors)
with open(pathOutput + fileCitationNetV3, 'w') as fp:
	json.dump(citNetV3, fp, indent=4)




'''
def computeCitedNetwork_v2(tsv, citedNet, doiEidMap, doiAuthorsMap):
	res = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in mylib.sectors:
				idCv = row['ID CV']
				sessione = row['SESSIONE']
				fascia = row['FASCIA']
				settore = row['SETTORE']
				doisCited = ast.literal_eval(row['DOIS ESISTENTI'])
				pubsEid = dict()
				pubsDoi = dict()
				pubs = list()
				for doiCited in doisCited:
					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						#pubsEid[eid] = citedNet[eid]
						temp = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							temp.append({eidCiting: doiAuthorsMap[doiCiting]})
						pubsEid[eidCited] = temp
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)

					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						doisCiting = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							#doisCiting.append(doiCiting)
							doisCiting.append({doiCiting: doiAuthorsMap[doiCiting]})
						pubsDoi[doiCited] = doisCiting
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)

					try:
						eidCited = doiEidMap["doi-to-eid"][doiCited]
						temp = list()
						for eidCiting in citedNet[eidCited]:
							doiCiting = doiEidMap["eid-to-doi"][eidCiting]
							temp.append({'eid': eidCiting, 'doi': doiCiting, 'authors-idCv': doiAuthorsMap[doiCiting]})
						pubs.append({
							"cited": {"doi": doiCited, "eid": eidCited},
							"citing": temp
						})
					except:
						print ("ERROR - CV: " + idCv + ", EID not found for DOI: " + doiCited)


				res[idCv] = {
					"sessione": sessione,
					"fascia": fascia,
					"settore": settore,
					#"pubsEid": pubsEid,
					#"pubsDoi": pubsDoi,
					"pubs": pubs
				}
	# prendo doi unici
	return res
'''
