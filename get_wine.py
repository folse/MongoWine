#!/usr/bin/python 
#coding=utf-8
import os
import json
import time
import datetime
import urllib
import urllib2
from pymongo import MongoClient

import sys  
reload(sys)
sys.setdefaultencoding('utf8')   
sys.setrecursionlimit(1000000)

def get_store_wine(wine_category, sys_store_id, page):

	request_data = urllib.urlencode({'subcategory':wine_category_dict[wine_category],'sortdirection':'Ascending','site':sys_store_id,'fullassortment':'0','page':page}) 

	request_url = 'http://www.systembolaget.se/api/productsearch/search?' + request_data.replace('+','%20')

	print wine_category + ', store ' + str(sys_store_id) + ', page ' + str(page)

	try:
		resp = urllib2.urlopen(request_url).read()
	except urllib2.HTTPError, e:
		print e
		time.sleep(2)
	except urllib2.socket.error, e:
		print e
		time.sleep(2)
		resp = urllib2.urlopen(request_url).read()
	  
	resp_json = json.loads(resp)
	meta_data = resp_json['Metadata']
	product_array = resp_json['ProductSearchResults']

	i = 0
	while (i < len(product_array)):
		product = product_array[i]
		save_wine_info(product, sys_store_id, wine_category)
		i = i + 1

	next_page = meta_data['NextPage']
	if next_page > 0:
		get_store_wine(wine_category,sys_store_id,next_page)

def save_wine_info(product, sys_store_id, wine_category):
    
    wine_number = product['ProductNumber']
    wine_inventory = int(product['QuantityText'][:-3])
    wine_name = str(product['ProductNameBold']).encode("utf-8")
    if product['ProductNameThin'] != None:
    	wine_name = wine_name + ' ' + str(product['ProductNameThin']).encode("utf-8")

    inventory_collection = "inventory_" + wine_category

    db[inventory_collection].update({ "wine_number": wine_number, "sys_store_id": sys_store_id },\
	 			   { "$set": { "wine_name": wine_name, update_time_period: wine_inventory }}, True, True)

def get_update_time_period():

	current_day_string = datetime.datetime.now().strftime('%Y-%m-%d')
	current_hour_string = datetime.datetime.now().strftime('%H')

	return current_day_string + " " +  current_hour_string + ':00'

def get_wine_info(wine_number, category):
	url = 'https://api.systembolaget.se/V4/artikel/' + wine_number
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
		parse_wine_info(resp, wine_number, category)
	except urllib2.HTTPError, e:
		print e
		pass
	except urllib2.socket.error, e:
		print e
		time.sleep(2)
		resp = urllib2.urlopen(req).read()
		parse_wine_info(resp, wine_number, category)

def parse_wine_info(resp, wine_number, wine_category):

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
				if wine_detail_number == wine_number:
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

			inventory_collection = "inventory_" + wine_category

			db[inventory_collection].update_many(
				{ "wine_number": wine_number }, 
				{ "$set": { "sales_start": sales_start, \
							"alcohol": alcohol, \
							"color": color, \
							"fragrance": fragrance, \
							"ingredient": ingredient, \
							"sugar": sugar, \
							"producer": producer, \
							"supplier": supplier, \
							}})

			inventory = db[inventory_collection].find_one({ "alcohol": {"$exists": False} })
			if inventory != None:
				print inventory['wine_number']
				get_wine_info(inventory['wine_number'], wine_category)

def get_date_from_timestamp(time_stamp_info):
	
	time_stamp = 0

	if time_stamp_info[6] == '1':
		time_stamp = int(time_stamp_info[6:16])
	else:
		time_stamp = int(time_stamp_info[6:15])

	return time.strftime("%Y-%m-%d", time.gmtime(time_stamp + 7200))

def update_wine():

	for wine_category in wine_category_dict.keys():

		inventory_collection = "inventory_" + wine_category

		inventory = db[inventory_collection].find_one({ "alcohol": {"$exists": False} })
		if inventory != None:
			get_wine_info(inventory['wine_number'], wine_category)


if __name__ == '__main__':

	global db
	global resp
	global update_time_period
	global wine_category_dict

	db = MongoClient().wine
	update_time_period = get_update_time_period()
	wine_category_dict = { "red_wine": u'Rött vin', "white_wine": u'Vitt vin' }

	sys_store_ids = []

	for store in db.store.find():
		sys_store_ids.append(store['sys_store_id'])

	for sys_store_id in sys_store_ids:
		for wine_category in wine_category_dict.keys():
			get_store_wine(wine_category, sys_store_id, 0)

	update_wine()
