import os 
import json
#from glob import glob
import sys
import csv
import ast

import mylib

pathInput = "data/input/"
inputTsv = pathInput + '09.dois-candidati-2016-ordered.tsv'

pathAbstracts = "data/output/abstracts/"
pathOutput = "data/output/"
fileCitationNetV1 = "citationNet_v1_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
fileCitationNetV2 = "citationNet_v2_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
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

					'''
		{
			"2-s2.0-80052140865": [
                {
                    "2-s2.0-84858286512": [
                        "46618",
                        "46607",
                        "43964"
                    ]
                },
                {
                    "2-s2.0-84897890150": [
                        "46618",
                        "46607",
                        "43964"
                    ]
                }
            ],
         }
         [
			{
				"cited": {"doi": DOI, "eid": EID},
				"citing": [{"doi": DOI, "eid": EID, "authors": [IIDCV1, ..., IDCVN]}]
			}
         ]   
					'''
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
					"pubsEid": pubsEid,
					"pubsDoi": pubsDoi,
					"pubs": pubs
				}
	# prendo doi unici
	return res

'''
{
	"IDCV-CITATO": {
		"sessione": "...",
		"fascia": "...",
		"settore": "...",
		"pubsEid": {
			"eidCitato1": ["eidCitante1", ..., "eidCitanteN"]
			...
		}
		"pubsDoi": {
			"doiCitato1": ["doiCitante1", ..., "doiCitanteN"]
			...
		}
	}
}
'''

# V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** V1 *** 
# compute citation network v1 (eid-cited -> list-eids-citing) using abstracts (i.e. json files)
#citedNet = computeCitedNetwork(pathAbstracts)

# save the citation network v1 (eid-cited -> list-eids-citing) to file
#with open(pathOutput + fileCitationNetV1, 'w') as fp:
#	json.dump(citedNet, fp, indent=4)



# load the citation network v1 (eid-cited -> list-eids-citing) from file
with open(pathOutput + fileCitationNetV1) as json_file:
	citedNetV1 = json.load(json_file)

'''
i=0
for c in citedNet:
	if len(citedNet[c]) > 0:
		i += 1
print (i)
'''


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

'''
citNetV2 = computeCitedNetwork_v2(inputTsv, citedNetV1, doiEidMap, doiAuthors)
with open(pathOutput + fileCitationNetV2, 'w') as fp:
	json.dump(citNetV2, fp, indent=4)
'''
mylib.getAuthorsId(inputTsv, pathAbstracts, doiEidMap)
