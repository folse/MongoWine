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

def get_store_wine(wine_subcategory, sys_store_id, page):

	request_data = urllib.urlencode({'subcategory':wine_subcategory_dict[wine_subcategory],'sortdirection':'Ascending','site':sys_store_id,'fullassortment':'0','page':page}) 

	request_url = 'http://www.systembolaget.se/api/productsearch/search?' + request_data.replace('+','%20')

	print 'store: ' + str(sys_store_id) + ', page:' + str(page)

	try:
		resp = urllib2.urlopen(request_url).read()
	except Exception, e:
		print e
		time.sleep(60)
		resp = urllib2.urlopen(request_url).read()
	  
	resp_json = json.loads(resp)
	meta_data = resp_json['Metadata']
	product_array = resp_json['ProductSearchResults']

	i = 0
	while (i < len(product_array)):
		product = product_array[i]
		save_wine_info(product, sys_store_id, wine_subcategory)
		i = i + 1

	next_page = meta_data['NextPage']
	if next_page > 0:
		get_store_wine(wine_subcategory,sys_store_id,next_page)

def save_wine_info(product, sys_store_id, wine_subcategory):
    sys_wine_id = product['ProductId']
    wine_name = str(product['ProductNameBold']).encode("utf-8")

    if product['ProductNameThin'] != None:
    	wine_name = wine_name + ' ' + str(product['ProductNameThin']).encode("utf-8")

    wine_number = product['ProductNumber']
    wine_inventory = int(product['QuantityText'][:-3])
    wine_url = product['ProductUrl']
    wine_id = 0

    result = db.wine.find_one({"sys_wine_id": sys_wine_id})
    if result == None:
    	new_wine = { "sys_wine_id": sys_wine_id, \
    				 "name": wine_name, \
    				 "number": wine_number, \
    				 "url": wine_url, \
    				 "sales_start": "", \
	        		 "alcohol": "", \
					 "color": "", \
					 "fragrance": "", \
					 "ingredient": "", \
					 "sugar": "", \
					 "producer": "", \
					 "supplier": "", \
					 "category": wine_subcategory, \
					 "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
    	wine_id = db.wine.insert(new_wine)
        print 'Inserted a new wine: ' + str(wine_id)
    else:
        wine_id = result['_id']

    inventory_collection = "inventory_" + wine_subcategory

    db[inventory_collection].update({ "wine_id": wine_id, "sys_store_id": sys_store_id },\
	 			   { "$set": { "wine_name": wine_name, \
	 						   "wine_number": wine_number, \
	 						   update_time_period: wine_inventory, \
	 						   "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
	 						  }}, True, True)

def get_update_time_period():

	current_day_string = datetime.datetime.now().strftime('%Y-%m-%d')
	current_hour_string = datetime.datetime.now().strftime('%H')

	return current_day_string + " " +  current_hour_string + ':00'

if __name__ == '__main__':

	global db
	global update_time_period
	global wine_subcategory_dict

	db = MongoClient().wine
	update_time_period = get_update_time_period()
	wine_subcategory_dict = { "red_wine": u'Rött vin', "white_wine": u'Vitt vin' }

	sys_store_ids = []

	for store in db.store.find():
		sys_store_ids.append(store['sys_store_id'])

	for sys_store_id in sys_store_ids:
		for wine_subcategory in wine_subcategory_dict.keys():
			get_store_wine(wine_subcategory, sys_store_id, 0)
