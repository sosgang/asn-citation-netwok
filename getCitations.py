import requests
import csv
import sys
import ast
import datetime
import time
import apikeys

import urllib.parse

inputTsv = '09.dois-candidati-2016-ordered.tsv'
#settori = ['13/D1', '13/D2', '13/D3', '01/B1', '09/H1']
settori = ['01/B1']

apiURL_AbstractDoi = 'https://api.elsevier.com/content/abstract/doi/'

def getDoisSet(f):
	doisList = list()
	with open(f, newline='') as csvfile:
		spamreader = csv.DictReader(csvfile, delimiter='\t')
		for row in spamreader:
			#print (row['SETTORE'].replace('-','/'))
			if row['SETTORE'].replace('-','/') in settori:
				doiTemp = ast.literal_eval(row['DOIS ESISTENTI'])
				doisList.extend(doiTemp)

	# prendo doi unici
	return set(doisList)
	

#'https://api.elsevier.com/content/abstract/scopus_id/0032717048?apikey=5953888c807d52ee017df48501d3e598&httpAccept=application/json&view=FULL'
def getAbstract(doi, max_retry=2, retry_delay=1):
	
	retry = 0
	cont = True
	while retry < max_retry and cont:

		params = {'apikey':apikeys.keys[0], 'httpAccept':'application/json'} #, 'view':'FULL'}
		doiEncoded = urllib.parse.quote(doi)
		print(apiURL_AbstractDoi + urllib.parse.quote(doi))
		r = requests.get(apiURL_AbstractDoi + doiEncoded, params=params)
				
		#if self.raw_output:
		#	self.save_raw_response(r.text)

		if r.status_code > 200 and r.status_code < 500:
			print(u"{}: errore nella richiesta: {}".format(r.status_code, r.url))
			return None

		if r.status_code != 200:
			retry += 1
			if retry < max_retry:
				time.sleep(retry_delay)
			continue

		cont = False 
			 
	if retry >= max_retry: 
		return None 
 
	json = r.json() 
	json['request-time'] = datetime.datetime.now()
	return json



'''
dt1 = datetime.datetime.now()
#print(dt1.year)v

time.sleep(1)
dt2 = datetime.datetime.now()

# FORMAT vedi https://www.w3schools.com/python/python_datetime.asp
#print(dt.strftime("%Y-%m-%d"))

a = {'nome': 'Francesco', 'date1': dt1, 'date2': dt2}
print ( (a['date2'] - a['date1']).total_seconds() )

b = {'nome': 'Francesco', 'date1': datetime.datetime(2020, 1, 23, 12, 26, 1, 625769), 'date2': datetime.datetime(2020, 1, 23, 12, 26, 2, 526150)}
deltaB2 = ( (b['date2'] - b['date1']) )
print (deltaB2.total_seconds())

deltaTest = datetime.timedelta(seconds=1)
print (deltaTest.total_seconds())

print (b)
if deltaB2.total_seconds() > deltaTest.total_seconds():
	print ('maggiore')
else:
	print ('minore')
'''



#doisSet = len(getDoisSet(inputTsv))
#sys.exit()

doi = '10.1016/j.scico.2011.10.006'
jsonAbs = getAbstract(doi)
print (jsonAbs)

'''
class ScopusDownloader(object): 

	def __init__(self, url, raw_output=None, limit_results=100, max_retry=2, retry_delay=10):
	
		self.url = url
		self.raw_output = raw_output 
		self.max_retry = max_retry
		self.retry_delay = retry_delay
		self.limit_results = limit_results
		
	def save_raw_response(self, content):

		path = self.raw_output
		
		if not os.path.isdir(path):
			os.mkdir(path)
		
		counter = 1
		now = datetime.datetime.now().strftime("%H%M%S")
		filename = "{:}{:04d}.json".format(now, counter)
		completepath = os.path.join(path, filename)
		while os.path.isfile(completepath):
			counter += 1
			filename = "{:}{:04d}.json".format(now, counter)
			completepath = os.path.join(path, filename)

		f = open(completepath, 'w')
		f.write(content)
		f.close()


	def get(self, params):
		
		retry = 0
		cont = True
		while retry < self.max_retry and cont:

			r = requests.get(self.url, params=params)
			
			if self.raw_output:
				self.save_raw_response(r.text)

			if r.status_code > 200 and r.status_code < 500:
				print(u"{}: errore nella richiesta: {}".format(r.status_code, r.url))
				return None

			if r.status_code != 200:
				retry += 1
				if retry < self.max_retry:
					time.sleep(self.retry_delay)
				continue

			cont = False 
			 
		if retry >= self.max_retry: 
			return None 
 
		return r.json() 
 
 
	def download_results(self, params): 
	 
		ret = [] 
		mypar = params.copy() 
		 
		start = -1 
		items = 0 
		total = 0 
		while start + items < total: 
			part = self.get(mypar) 
			if part and part.get("search-results"): 
 
				start = int(part["search-results"]["opensearch:startIndex"]) 
				items = int(part["search-results"]["opensearch:itemsPerPage"]) 
				if total == 0: 
					if self.limit_results > 0: 
						total = min(int(part["search-results"]["opensearch:totalResults"]), self.limit_results) 
					else: 
						total = int(part["search-results"]["opensearch:totalResults"]) 
				 
				if items > 0: 
					ret.extend(part["search-results"]["entry"]) 
				#print(start, items, total) 
				 
				mypar["start"] = start + items 
			 
			else: 
				break 
 
		return ret

'''
