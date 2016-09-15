#!/usr/bin/python 
#coding=utf-8
import os
import json
import time
import datetime
import urllib2
from pymongo import MongoClient

import sys 
reload(sys)
sys.setdefaultencoding('utf8')   
sys.setrecursionlimit(1000000)

def get_wine_info(wine):
	url = 'https://api.systembolaget.se/V4/artikel/' + wine['number']
	username = 'DMZ1\SybApi'
	password = 'zc3R21Q8nJ4y8Pj1A6uB'
	send_headers = {
	 'Host':'api.systembolaget.se',
	 'User-Agent':'Systembolaget/2.1 (iPhone; iOS 10.0; Scale/2.00)',
	 'Authorization':'Basic RE1aMVxTeWJBcGk6emMzUjIxUThuSjR5OFBqMUE2dUI=',
	 'Connection':'keep-alive'
	}
	  
	passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passman.add_password(None, url, username, password)
	urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

	req = urllib2.Request(url,headers=send_headers)

	try:
		resp = urllib2.urlopen(req).read()
		parse_wine_info(resp,wine)
	except HTTPError, e:
		print e
		if e.getcode() == 500:
			pass
		else:
			time.sleep(10)
			resp = urllib2.urlopen(req).read()
			parse_wine_info(resp,wine)

def parse_wine_info(resp,wine):

	data = json.loads(resp)

	if data.has_key('Artikeldetaljer'):

		wine_detail = data['Artikeldetaljer']

		wine_info = ''
    	sales_start = ''
    	alcohol = ''
    	color = ''
    	fragrance = ''
    	ingredient = ''
    	sugar = ''
    	producer = ''
    	supplier = ''

    	if data.has_key('Artiklar'):
			for i in range(len(data['Artiklar'])):
				wine_detail_number = data['Artiklar'][i]['ArtikelNr']
				if wine_detail_number == wine['number']:
					wine_info = data['Artiklar'][i]

			if wine_info.has_key('Saljstartsdatum'):
				sales_start = get_date_from_timestamp(wine_info['Saljstartsdatum'])

			if wine_info.has_key('Alkoholhalt'):
				alcohol = str(wine_info['Alkoholhalt']) + ' %'

			if wine_detail.has_key('Farg'):
				color = wine_detail['Farg']

			if wine_detail.has_key('Doft'):
				fragrance = wine_detail['Doft']

			if wine_detail.has_key('Ravara'):
				ingredient = wine_detail['Ravara']

			if wine_detail.has_key('Sockerhalt'):
				sugar = wine_detail['Sockerhalt'] + ' g/l'

			if wine_info.has_key('Producent'):
				producer = wine_info['Producent']

			if wine_info.has_key('Leverantor'):
				supplier = wine_info['Leverantor']

			db.wine.update({ "_id": wine['_id'] },\
			 			   { "$set": { "sales_start": sales_start, \
			 	            		   "alcohol": alcohol, \
			 						   "color": color, \
			 						   "fragrance": fragrance, \
			 						   "ingredient": ingredient, \
			 						   "sugar": sugar, \
			 						   "producer": producer, \
			 						   "supplier": supplier, \
			 						   "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
			 						  }}, False, False)

def get_date_from_timestamp(time_stamp_info):
	
	time_stamp = 0

	if time_stamp_info[6] == '1':
		time_stamp = int(time_stamp_info[6:16])
	else:
		time_stamp = int(time_stamp_info[6:15])

	return time.strftime("%Y-%m-%d", time.gmtime(time_stamp + 7200))

if __name__ == '__main__':

	global db
	db = MongoClient().wine

	wines = db.wine.find({ "alcohol": "" })
	for wine in wines:
		print wine['number']
		get_wine_info(wine)
