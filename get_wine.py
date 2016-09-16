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

	print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
