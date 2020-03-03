import sqlite3
from sqlite3 import Error
from glob import glob
import json
import csv
import sys
import os

import conf

pathAuthorsSearch = "../data/input/authors-search-v2/"
cercauniPath = "../data/input/cercauniversita/"
tsvCercauniAuto = "../data/input/cercauniversita/" + "_".join(conf.sectors).replace("/","") + "_" + conf.anno + "_id_MAPPING-AUTO.tsv"
tsvCercauniManual = "../data/input/cercauniversita/" + "_".join(conf.sectors).replace("/","") + "_" + conf.anno + "_id_MANUALCHECKED.tsv"
tsvCv = "../data/input/" + "_".join(conf.sectors).replace("/","") +"_withNames_AsnOutcomes_scopusId_editedAddedMissingScopusId.tsv"
pathAbstracts = "../data/output/abstracts/" + "_".join(conf.sectors).replace("/","") + "/"

def create_connection(db_file):
	""" create a database connection to the SQLite database
		specified by db_file
	:param db_file: database file
	:return: Connection object or None
	"""
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
 
	return conn


def create_author(conn, author):
	"""
	Create a new author into the authorScopus table
	:param conn:
	:param author:
	:return: author id
	"""
	sql = ''' INSERT INTO authorScopus(id,givenname,surname,initials,orcid)
			  VALUES(?,?,?,?,?) '''
	cur = conn.cursor()
	cur.execute(sql, author)
	return cur.lastrowid
	
def create_cercauniversita(conn, cercauni):
	"""
	Create a new person into the cercauniversita table
	:param conn:
	:param cercauni:
	:return: cercauni id
	"""
	sql = ''' INSERT INTO cercauniversita(id,authorId,anno,settore,ssd,fascia,orcid,cognome,nome,genere,ateneo,facolta,strutturaAfferenza)
			  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''

	cur = conn.cursor()
	cur.execute(sql, cercauni)
	return cur.lastrowid

def create_curriculum(conn, curriculum):
	"""
	Create a new cv into the curriculum table
	:param conn:
	:param curriculum:
	:return: curriculum id
	"""
	sql = ''' INSERT INTO curriculum(id,authorId,annoAsn,settore,ssd,quadrimestre,fascia,orcid,cognome,nome,bibl,I1,I2,I3,idSoglia,esito)
			  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
	sql_create_curriculum_table = """ CREATE TABLE IF NOT EXISTS curriculum (
										id integer PRIMARY KEY,
										authorId integer,
										annoAsn text NOT NULL,
										settore text NOT NULL,
										ssd text,
										quadrimestre integer NOT NULL,
										fascia integer NOT NULL,
										orcid text,
										cognome text,
										nome text,
										bibl integer,
										I1 integer NOT NULL,
										I2 integer NOT NULL,
										I3 integer NOT NULL,
										idSoglia integer NOT NULL,
										esito text NOT NULL,
										FOREIGN KEY (idSoglia) REFERENCES sogliaAsn(id)
										FOREIGN KEY (authorId) REFERENCES authorScopus(id)
									); """

	cur = conn.cursor()
	cur.execute(sql, curriculum)
	return cur.lastrowid


def create_sogliaAsn(conn, sogliaAsn):
	"""
	Create a new soglia into the sogliaAsn table
	:param conn:
	:param sogliaAsn:
	:return: sogliaAsn id
	"""
	sql = ''' INSERT INTO sogliaAsn(annoAsn,settore,descrSettore,ssd,fascia,S1,S2,S3,descrS1,descrS2,descrS3,bibl)
			  VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
	cur = conn.cursor()
	cur.execute(sql, sogliaAsn)
	return cur.lastrowid

def create_wroteRelation(conn, wroteRelation):
	"""
	Create a new wroteRelation into the wroteRelation table
	:param conn:
	:param wroteRelation:
	:return: wroteRelation id
	"""
	sql = ''' INSERT INTO wroteRelation(authorId,eid)
			  VALUES(?,?) '''
	cur = conn.cursor()
	cur.execute(sql, wroteRelation)
	return cur.lastrowid

def create_publication(conn, publication):
	"""
	Create a new publication into the publication table
	:param conn:
	:param publication:
	:return: publication id
	"""
	sql = ''' INSERT INTO publication(eid, doi, publicationDate,publicationYear,title,venueName)
			  VALUES(?,?,?,?,?,?) '''
	cur = conn.cursor()
	cur.execute(sql, publication)
	return cur.lastrowid

def create_citesRelation(conn, citesRelation):
	"""
	Create a new citesRelation into the citesRelation table
	:param conn:
	:param citesRelation:
	:return: citesRelation id
	"""
	sql = ''' INSERT INTO citesRelation(eidCiting,eidCited,citationDate,citationYear)
			  VALUES(?,?,?,?) '''
	cur = conn.cursor()
	cur.execute(sql, citesRelation)
	return cur.lastrowid


def getEidsInNetwork(pathAbstracts):
	# TODO:	andrebbe fatto prendendo dati nelle publicationList (../data/output/publicationList/[sectors]/*.json)
	# 		Non lo faccio perché non ho quelle dei candidati.
	#		Quindi per adesso considero solo gli abstracts che ho scaricato.
	eids = set()
	contents = glob(pathAbstracts + "*.json")
	contents.sort()
	for filename in contents:
		eid  = os.path.basename(filename).replace(".json","")
		'''
		with open(filename) as json_file:
			j = json.load(json_file)
			
			# POPULATE PUBLICATION TABLE
			eid = j["abstracts-retrieval-response"]["coredata"]["eid"]
			print (eid)
			sys.exit()
			eids.add(eid)
		'''
		eids.add(eid)
	return eids

def main():
	# create a database connection
	conn = create_connection(conf.dbFilename)
	with conn:
		
		authorIds = set()
		for sector in conf.sectors:
			# compute idCercauni/authorId map
			cercauniAuthorMap = dict()
			for tsvFN in [tsvCercauniAuto,tsvCercauniManual]:
				with open(tsvFN, newline='') as tsvFile:
					spamreader = csv.DictReader(tsvFile, delimiter='\t')
					table = list(spamreader)
					for row in table:
						cercauniId = row["cercauniId"]
						authorId = row["AuthorId"]
						cercauniAuthorMap[cercauniId] = authorId

			contents = glob(pathAuthorsSearch + sector.replace("/","") + "/*.json")
			contents.sort()
			# POPULATE TABLE authorScopus
			for filename in contents:
				with open(filename) as json_file:
					j = json.load(json_file)
					entries = j["search-results"]["entry"]
					if len(entries) == 0:
						print ("No results.")
						sys.exit()
					for entry in entries:
						authorId = entry["dc:identifier"].replace("AUTHOR_ID:","")
						authorIds.add(authorId)
						eid = entry["eid"]
						if "orcid" in entry:
							orcid = entry["orcid"]
						else:
							orcid = ""
						surname = entry["preferred-name"]["surname"]
						givenname = entry["preferred-name"]["given-name"]
						initials = entry["preferred-name"]["initials"]
						
						# create a new author
						author = (int(authorId),givenname,surname,initials,orcid)
						author_id = create_author(conn, author)

			# POPULATE TABLE cercauniversita
			cercauniFile = cercauniPath + sector.replace("/","") + "_" + conf.anno + "_id.csv"
			with open(cercauniFile, newline='') as tsvFile:
				spamreader = csv.DictReader(tsvFile, delimiter='\t')
				table = list(spamreader)
				for row in table:
					sn = (row['Cognome e Nome']).split()
					lastname = list()
					firstname = list()
					for part in sn:
						if part.isupper():
							lastname.append(part)
						else:
							firstname.append(part)
					cognome = (" ".join(lastname)).title()
					nome = (" ".join(firstname)).title()
					
					cercauni = (row["Id"], cercauniAuthorMap[row["Id"]], conf.anno, row["S.C."], row["S.S.D."], row["Fascia"], "", cognome, nome, row["Genere"], row["Ateneo"], row["Facoltà"], row["Struttura di afferenza"])
					cercauni_id = create_cercauniversita(conn, cercauni)
		
		# POPULATE TABLE curriculum
		with open(tsvCv, newline='') as tsvFile:
			spamreader = csv.DictReader(tsvFile, delimiter='\t')
			table = list(spamreader)
			for row in table:
				if row["BIBL?"] == "B":
					bibl = 1
				elif row["BIBL?"] == "NB":
					bibl = 0
				else:
					print ("ERROR in bibliometric/non-bibliometic data in cercauniversita (TSV).")
					sys.exit()
				curriculum = (row["ID CV"], row["SCOPUS ID"], conf.anno, row["SETTORE"].replace("-","/"), row["SSD"], row["SESSIONE"], row["FASCIA"], "", row["COGNOME"].title(), row["NOME"].title(), bibl, row["I1"], row["I2"], row["I3"],	"", row["ESITO"])
				curriculum_id = create_curriculum(conn, curriculum)
			
		# POPULATE TABLE soglia
		tsvSoglieBilbio = "../data/input/soglie_2016_bibliometrici.tsv"
		#for tsvFN in [tsvSoglieBilbio,tsvSoglieNonBilbio]:
		with open(tsvSoglieBilbio, newline='') as tsvFile:
			spamreader = csv.DictReader(tsvFile, delimiter='\t')
			table = list(spamreader)
			for row in table:
				temp = row["SC/SSD"]
				if len(temp) == 5:
					settore = temp
					ssd = ""
				else:
					settore = temp[:5]
					ssd = temp[6:]

				descrSettore = row["SETTORE CONCORSUALE"]
				s1_l1 = row["Numero articoli 10 anni"]
				s2_l1 = row["Numero citazioni 15 anni"]
				s3_l1 = row["Indice H 15 anni"]
				soglia = ("2016",settore,descrSettore,ssd,"1",s1_l1,s2_l1,s3_l1,"Numero articoli 10 anni","Numero citazioni 15 anni","Indice H 15 anni",1)
				create_sogliaAsn(conn,soglia)

				s1_l2 = row["Numero articoli 5 anni"]
				s2_l2 = row["Numero citazioni 10 anni"]
				s3_l2 = row["Indice H 10 anni"]
				soglia = ("2016",settore,descrSettore,ssd,"2",s1_l2,s2_l2,s3_l2,"Numero articoli 5 anni","Numero citazioni 10 anni","Indice H 10 anni",1)
				create_sogliaAsn(conn,soglia)

		tsvSoglieNonBiblio = "../data/input/soglie_2016_non-bibliometrici.tsv"
		with open(tsvSoglieNonBiblio, newline='') as tsvFile:
			spamreader = csv.DictReader(tsvFile, delimiter='\t')
			table = list(spamreader)
			for row in table:
				temp = row["SC/SSD"]
				if len(temp) == 5:
					settore = temp
					ssd = ""
				else:
					settore = temp[:5]
					ssd = temp[6:]

				descrSettore = row["SETTORE CONCORSUALE"]
				s1_l1 = row["Numero articoli e contributi 10 anni"]
				s2_l1 = row["Numero articoli classe A 15 anni"]
				s3_l1 = row["Numero Libri 15 anni"]
				soglia = ("2016",settore,descrSettore,ssd,"1",s1_l1,s2_l1,s3_l1,"Numero articoli e contributi 10 anni","Numero articoli classe A 15 anni","Numero Libri 15 anni",0)
				create_sogliaAsn(conn,soglia)

				s1_l2 = row["Numero articoli e contributi 5 anni"]
				s2_l2 = row["Numero articoli classe A 10 anni"]
				s3_l2 = row["Numero Libri 10 anni"]
				soglia = ("2016",settore,descrSettore,ssd,"2",s1_l2,s2_l2,s3_l2,"Numero articoli e contributi 5 anni","Numero articoli classe A 10 anni","Numero Libri 10 anni",0)
				create_sogliaAsn(conn,soglia)
		
		
		#recupero insieme eid da considerare (i.e. non tengo citazioni a paper che siano fuori dalla network)
		eids = getEidsInNetwork(pathAbstracts)
		#print (len(eids))
		
		counter = 1
		contents = glob(pathAbstracts + "*.json")
		contents.sort()
		for filename in contents:
			with open(filename) as json_file:
				j = json.load(json_file)
				
				# POPULATE PUBLICATION TABLE
				eid = j["abstracts-retrieval-response"]["coredata"]["eid"]
				try:
					doi = j["abstracts-retrieval-response"]["coredata"]["prism:doi"]
				except:
					#print ("Missing doi: " + eid)
					doi = ""
				try:
					publicationDate = j["abstracts-retrieval-response"]["coredata"]["prism:coverDate"]
				except:
					#print ("Missing publicationDate: " +eid)
					publicationDate = ""
				try:
					publicationYear = j["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["source"]["publicationyear"]["@first"]
				except:
					#print ("Missing publication year: " + eid)
					publicationYear = ""
				#title = j["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["citation-title"]
				try:
					title = j["abstracts-retrieval-response"]["coredata"]["dc:title"]
				except:
					title = ""
				#venueName = j["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["source"]["sourcetitle"]
				try:
					venueName = j["abstracts-retrieval-response"]["coredata"]["prism:publicationName"]
				except:
					venueName = ""
				publication = (eid,doi,publicationDate,publicationYear,title,venueName)
				try:
					create_publication(conn, publication)
				except:
					print ("%s, %s, %s, %s, %s, %s" % (eid,doi,publicationDate,publicationYear,title,venueName))
					sys.exit()
				#print (str(counter) + ") insert done!")
				counter += 1
				
				# POPULATE WROTERELATION TABLE
				try:
					authors = j["abstracts-retrieval-response"]["authors"]["author"]
					for author in authors:
						authorId = author["@auid"]

						# OCCHIO # OCCHIO # OCCHIO # 
						# keep only authors in cercauniversita or curriculum
						if authorId in authorIds:
							wroteRelation = (authorId,eid)
							create_wroteRelation(conn,wroteRelation)
						# OCCHIO # OCCHIO # OCCHIO # 

				except:
					print (eid + ": wroteRelation()")
				
				# POPULATE CITESRELATION TABLE
				"""
				if j["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"] is not None and "bibliography" in j["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"] and "reference" in j["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"]["bibliography"]:
					references = j["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"]["bibliography"]["reference"]
				"""
				try:
					references = j["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"]["bibliography"]["reference"]
					if type(references) is not list:
						references = [references]
					for reference in references:
						try:
							#if "$" in reference["ref-info"]["refd-itemidlist"]["itemid"]:
							eidCited = "2-s2.0-" + reference["ref-info"]["refd-itemidlist"]["itemid"]["$"]
						except:
							eidCited = ""
						# Skip 1. papers without citations; 2. papers with no authors in the network
						if eidCited == "" or eidCited not in eids:
							continue
						else:
							citesRelation = (eid,eidCited,publicationDate,publicationYear)
							create_citesRelation(conn,citesRelation)
					#else:
					#	print (filename)
				except:
					#print ("No reference for " + eid + ": skipping.")
					pass

if __name__ == '__main__':
	main()
