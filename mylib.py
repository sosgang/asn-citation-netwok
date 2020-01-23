import csv
import ast


#sectors = ['13/D1', '13/D2', '13/D3', '01/B1', '09/H1']
sectors = ['01/B1']

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
