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

		field_names = ['wine_name', 'wine_number', 'Säljstart', 'Alkoholhalt', 'Färg', 'Doft', 'Råvaror', 'Sockerhalt', 'Producent', 'Leverantör']
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

			sales_start = ''
			alcohol = ''
			color = ''
			fragrance = ''
			ingredient = ''
			sugar = ''
			producer = ''
			supplier = ''

			inventory_collection = "inventory_" + category
			
			for inventory in db[inventory_collection].find({ "sys_store_id": store_id }):

				if inventory.has_key('sales_start'):
					sales_start = inventory['sales_start']

				if inventory.has_key('alcohol'):
					alcohol = inventory['alcohol']

				if inventory.has_key('color'):
					color = inventory['color']

				if inventory.has_key('fragrance'):
					fragrance = inventory['fragrance']

				if inventory.has_key('ingredient'):
					ingredient = inventory['ingredient']

				if inventory.has_key('sugar'):
					sugar = inventory['sugar']

				if inventory.has_key('producer'):
					producer = inventory['producer']

				if inventory.has_key('supplier'):
					supplier = inventory['supplier']

				dict_writer.writerow({ 'wine_name': inventory['wine_name'], \
									'wine_number': inventory['wine_number'], \
									'Säljstart': sales_start, \
									'Alkoholhalt': alcohol, \
									'Färg': color, \
									'Doft': fragrance, \
									'Råvaror': ingredient, \
									'Sockerhalt': sugar, \
									'Producent': producer, \
									'Leverantör': supplier })

			writer.writerow([' '])

			write_log(self,i)

		self.log_file.close()

if __name__ == '__main__':

	WineExcel('red_wine')
