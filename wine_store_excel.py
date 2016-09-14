#!/usr/bin/python 
#coding=utf-8
import os
import json
import time
import datetime

import csv
import codecs
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys  
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':

	start_date = '2016-08-28'
	end_date = '2016-09-01'

	sql_start_time = datetime.datetime.strptime(start_date,'%Y-%m-%d') + datetime.timedelta(days=-1)
	sql_end_time = datetime.datetime.strptime(end_date,'%Y-%m-%d') + datetime.timedelta(days=1)
	sql_start_date = sql_start_time.strftime('%Y-%m-%d')
	sql_end_date = sql_end_time.strftime('%Y-%m-%d')

	csv_file = file('product_list.csv', 'w')
	csv_file.write(codecs.BOM_UTF8)
	writer = csv.writer(csv_file)

	field_names = ['Product Name', 'Product Id', 'Säljstart', 'Alkoholhalt', 'Färg', 'Doft', 'Råvaror', 'Sockerhalt', 'Producent', 'Leverantör']
	dict_writer = csv.DictWriter(csv_file, fieldnames=field_names)

	global db
	db = MongoClient().wine

	for store in db.store.find():

		if store != None:

			store_id = store['sys_store_id']
			store_name = store['name']

			store_info = 'Store Id: ' + store_id + ', Store Name: ' + store_name

			print store_id

			writer.writerow([store_info])
			dict_writer.writeheader()

			inventories = db.inventory.find({ "sys_store_id": store_id })
			for inventory in inventories:
				
				wine_id = inventory['wine_id']
				wine = db.wine.find_one({ "_id": ObjectId(str(wine_id)) })
				dict_writer.writerow({'Product Name': wine['name'], 'Product Id': wine['sys_wine_id'], 'Säljstart': wine['sales_start'], 'Alkoholhalt': wine['alcohol'], 'Färg': wine['color'], 'Doft': wine['fragrance'], 'Råvaror': wine['ingredient'], 'Sockerhalt': wine['sugar'], 'Producent': wine['producer'], 'Leverantör': wine['supplier']})

			writer.writerow([' '])
			writer.writerow([' '])


