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

def get_store_wine(wine_subcategory,sys_store_id,page):

	request_data = urllib.urlencode({'subcategory':wine_subcategory,'sortdirection':'Ascending','site':sys_store_id,'fullassortment':'0','page':page}) 

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
		save_wine_info(product, sys_store_id)
		i = i + 1

	next_page = meta_data['NextPage']
	if next_page > 0:
		get_store_wine(wine_subcategory,sys_store_id,next_page)

def save_wine_info(product, sys_store_id):
    sys_wine_id = product['ProductId']
    wine_name = str(product['ProductNameBold']).encode("utf-8")

    if product['ProductNameThin'] != None:
    	wine_name = wine_name + ' ' + str(product['ProductNameThin']).encode("utf-8")

    wine_number = product['ProductNumber']
    wine_inventory = product['QuantityText'][:-3]
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
					 "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
    	wine_id = db.wine.insert(new_wine)
        print 'Inserted a new wine: ' + str(wine_id)
    else:
        wine_id = result['_id']

    # inventory_collection = 'inventory_' + str(sys_store_id)

    # new_inventory = { "wine_id": wine_id, "wine_name": wine_name, "wine_number": wine_number, "sys_store_id": sys_store_id, "inventory": wine_inventory, "day_period": update_time_period, "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    # db.inventory.insert(new_inventory)

    # new_inventory.pop('sys_store_id', None)
    # db[inventory_collection].insert(new_inventory)

    db.inventory.update({ "wine_id": wine_id, "sys_store_id": sys_store_id },\
	 			   { "$set": { "wine_name": wine_name, \
	 						   "wine_number": wine_number, \
	 						   update_time_period: wine_inventory, \
	 						   "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
	 						  }}, True, True)

def get_update_time_period():

	current_day_string = datetime.datetime.now().strftime('%Y-%m-%d')
	current_hour_string = datetime.datetime.now().strftime('%H:%M')

	return current_day_string + " " +  current_hour_string

if __name__ == '__main__':
	#  785 1288
	wine_subcategory = u'Rött vin'
	# wine_subcategory = u'Vitt vin'

	global db
	global update_time_period

	db = MongoClient().wine
	update_time_period = get_update_time_period()

	for store in db.store.find():
		get_store_wine(wine_subcategory, store['sys_store_id'], 0)
