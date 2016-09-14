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

log_file_name = 'wine.log'

def remove_file(file_name):
	if os.path.isfile(file_name): 
		os.remove(file_name)

def write_log(self, index):
	self.log_file = file(log_file_name,"w+")
	completion_rate = str((index+1)*100/436) + "%"
	self.log_file.writelines(completion_rate)

class WineExcel:

	def __init__(self, category):

		remove_file(log_file_name)
		self.log_file = file(log_file_name,"w")

		file_name = 'product_' + category	+ '.csv'
		print file_name
		csv_file = file(file_name, 'w')
		csv_file.write(codecs.BOM_UTF8)
		writer = csv.writer(csv_file)

		field_names = ['Product Name', 'Product Id', 'Säljstart', 'Alkoholhalt', 'Färg', 'Doft', 'Råvaror', 'Sockerhalt', 'Producent', 'Leverantör']
		dict_writer = csv.DictWriter(csv_file, fieldnames=field_names)

		db = MongoClient().wine

		store_array = db.store.find()
		for i in xrange(0,store_array.count()):

			store = store_array[i]

			store_id = store['sys_store_id']
			store_name = store['name']

			store_info = 'Store Id: ' + store_id + ', Store Name: ' + store_name

			print store_id

			writer.writerow([store_info])
			dict_writer.writeheader()

			inventory_collection = "inventory_" + category
			inventories = db[inventory_collection].find({ "sys_store_id": store_id })
			for inventory in inventories:
				
				wine_id = inventory['wine_id']
				wine = db.wine.find_one({ "_id": ObjectId(str(wine_id)) })
				dict_writer.writerow({'Product Name': wine['name'], 'Product Id': wine['sys_wine_id'], 'Säljstart': wine['sales_start'], 'Alkoholhalt': wine['alcohol'], 'Färg': wine['color'], 'Doft': wine['fragrance'], 'Råvaror': wine['ingredient'], 'Sockerhalt': wine['sugar'], 'Producent': wine['producer'], 'Leverantör': wine['supplier']})

			writer.writerow([' '])
			writer.writerow([' '])

			write_log(self,i)

		self.log_file.close()

if __name__ == '__main__':

	WineExcel('red_wine')
