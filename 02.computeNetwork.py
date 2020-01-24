import os 
import json
from glob import glob
import sys

import mylib

pathAbstracts = "data/output/abstracts/"
pathOutput = "data/output/"
fileCitationNet = 'citationNet.json'
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

# compute citation network using abstracts (i.e. json files)
citedNet = computeCitedNetwork(pathAbstracts)

# save the citation network to file
with open(pathOutput + fileCitationNet, 'w') as fp:
	json.dump(citedNet, fp, indent=4)

# load the citation network from file
#with open(pathOutput + fileCitationNet) as json_file:
#	citedNet = json.load(json_file)


i=0
for c in citedNet:
	if len(citedNet[c]) > 0:
		i += 1
print (i)

