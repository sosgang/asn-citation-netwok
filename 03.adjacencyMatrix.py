import os 
import sys
import json
from glob import glob
import ast
import csv

import mylib

pathInput = "data/input/"
#inputTsv = pathInput + "citationNet_v3_" + "_".join(mylib.sectors).replace("/","") + ".json"
inputTsv = pathInput + "_".join(mylib.sectors).replace("/","") + "_withNames_scopusId_editedAddedMissingScopusId.tsv"

pathOutput = "data/output/"
pathAbstracts = pathOutput + "abstracts/"+ ("_".join(mylib.sectors)).replace("/", "") + "/"
fileCitingNet = pathOutput + "citingNet_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
codePrefix = "2-s2.0-"
fileDoiEidMap = pathOutput + "doiEidMap_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"
eidToAuthorsFile = pathOutput + "eidToAuthors_" + ("_".join(mylib.sectors)).replace("/", "") + ".json"

outputTsv = pathOutput + "adjacencyMatrix_" + ("_".join(mylib.sectors)).replace("/", "") + ".tsv"


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

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
	citingCitedDict = dict()
	for citing in documentSet:
		citingCitedDict[citing] = []

	for filename_withPath in contents:
		with open(filename_withPath) as json_file:
			data = json.load(json_file)
			try:
				citing = data['abstracts-retrieval-response']['coredata']['eid']
				biblio = data['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']
				numRefs = int(biblio['@refcount'])
				for ref in biblio['reference']: #range(numRefs):
					temp = ref['ref-info']['refd-itemidlist']['itemid']
					#print (filename_withPath)
					if type(temp) is not list:
						idtype = temp['@idtype']
						code = temp['$']
						cited = codePrefix + code
						if cited in documentSet:
							citingCitedDict[citing].append(cited)
					else:
						for el in temp:
							idtype = el['@idtype'] 
							code = el['$']
							cited = codePrefix + code
							if idtype == 'SGR':
								if cited in documentSet:
									citingCitedDict[citing].append(cited)
			except:
				print ('*** BIBLIOGRAPHY ERROR: ' + filename_withPath + " ***")	
	
	return citingCitedDict
	
def getEidToAuthors(tsv, doiEidMap):
	eidToAuthors = dict()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			authorId = row['SCOPUS ID']
			citingDois = ast.literal_eval(row['DOIS ESISTENTI'])
			for citingDoi in citingDois:
				try:
					citingEid = doiEidMap["doi-to-eid"][citingDoi]
					if citingEid in eidToAuthors:
						temp = eidToAuthors[citingEid]
						if authorId not in temp:
							temp.append(authorId)
							eidToAuthors[citingEid] = temp
					else:
						eidToAuthors[citingEid] = [authorId]
				except:
					continue
	return eidToAuthors

def getAuthorIdsList(tsv):
	authorIdsSet = set()
	with open(tsv, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			authorId = row['SCOPUS ID']
			authorIdsSet.add(authorId)		
	authorIdsList = list(authorIdsSet)
	authorIdsList.sort()
	return authorIdsList

def getAdjacencyMatrix(tsv, authorIdsList, doiEidMap, citingCitedDict, eidToAuthors):

	# initialize empty map (dict of dict)
	matrix = AutoVivification()
	for authorId1 in authorIdsList:
		for authorId2 in authorIdsList:
			matrix[authorId1][authorId2] = 0


	with open(tsv, newline='') as csvfile:
		authorsAnalyzed = set()
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			citingAuthor = row['SCOPUS ID']
			if citingAuthor in authorsAnalyzed:
				continue
			authorsAnalyzed.add(citingAuthor)
			citingDois = ast.literal_eval(row['DOIS ESISTENTI'])
			for citingDoi in citingDois:
				try:
					citingEid = doiEidMap["doi-to-eid"][citingDoi]
					for citedEid in citingCitedDict[citingEid]:
						citedAuthors = eidToAuthors[citedEid]
						for citedAuthor in citedAuthors:
							temp = matrix[citingAuthor][citedAuthor]
							#print (temp)
							temp += 1
							matrix[citingAuthor][citedAuthor] = temp
				except:
					continue
	return matrix

#Save Adjacency Matrix to TSV file
def saveMatrixToFile(tsv, matrix, authorList):
	res = "\tCV-" + "\tCV-".join(authorList) + "\n"
	for authorIdCiting in authorList:
		line = list()
		for authorIdCited in authorList:
			line.append(str(matrix[authorIdCiting][authorIdCited]))
		res += "CV-" + authorIdCiting + "\t" + "\t".join(line) + "\n"
	text_file = open(tsv, "w")
	text_file.write(res)
	text_file.close()



# load doiEid map from file
with open(fileDoiEidMap) as json_file:
	doiEidMap = json.load(json_file)

eidToAuthors = getEidToAuthors(inputTsv, doiEidMap)

with open(eidToAuthorsFile, 'w') as fp:
	json.dump(eidToAuthors, fp, indent=4)

# compute citing network (eid-citing -> list-eids-cited) using abstracts (i.e. json files)
citingCitedDict = computeCitedNetwork(pathAbstracts)

# save the citing network (eid-citing -> list-eids-cited) to file
with open(fileCitingNet, 'w') as fp:
	json.dump(citingCitedDict, fp, indent=4)

# load the citing network (eid-citing -> list-eids-cited) from file
#with open(fileCitingNet) as json_file:
#	citingCitedDict = json.load(json_file)

authorIdsList = getAuthorIdsList(inputTsv)

adjacencyMatrix = getAdjacencyMatrix(inputTsv, authorIdsList, doiEidMap, citingCitedDict, eidToAuthors)

saveMatrixToFile(outputTsv, adjacencyMatrix, authorIdsList)



'''
with open(inputTsv) as json_file:
	data = json.load(json_file)
	# get author ids
	authorIds = list()
	for authorId in data:
		authorIds.append("cv-" +authorId)
	
	# initialize empty map (dict of dict)
	matrix = AutoVivification()
	for authorId1 in authorIds:
		for authorId2 in authorIds:
			matrix[authorId1][authorId2] = 0
			print (matrix[authorId1][authorId2])
			
			
	for citing in citingCitedDict:
		for cited in citingCitedDict[citing]:
			temp = matrix[citing][cited]
			print (temp)
			matrix[citing][cited] = temp + 1

	
	res = "\t" + "\t".join(authorIds) + "\n"
	for authorIdCiting in authorIds:
		res += authorIdauthorIdCiting
		for authorIdCited in authorIds:
			res += matrix[authorIdCiting][authorIdCited]
		res += "\n"

	print (res)







	citingMap = dict()
	for authorCited in data:
		for idCv in data[authorCited]:
			for pub in data[authorCited][idCv]["pubs"]:
				cited = pub["cited"]["doi"]
				citing = pub["citing"]["doi"]
				authorsCiting = pub["citing"]["authors"]
				
				for authorCitingDict in authorsCiting:
					authorCiting = authorCitingDict["authorId"]
					temp = dict()
					if authorCiting in citingMap:
						temp = citingMap[authorCited]
'''				
			

'''
		c1	c2	...	cn
	c1
	c2
	...
	cn
'''
