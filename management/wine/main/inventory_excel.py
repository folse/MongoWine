#!/usr/bin/python 
# -*- coding: UTF-8 -*-
import os
import datetime
from pymongo import MongoClient
import csv
import codecs

import sys  
reload(sys)
sys.setdefaultencoding('utf8')

inventory_file_name = 'inventory.xlsx'
log_file_name = 'inventory.log'

def remove_file(file_name):
	if os.path.isfile(file_name): 
		os.remove(file_name)

def write_log(self, index):
	self.log_file = file(log_file_name,"w+")
	completion_rate = str((index+1)*100/436) + "%"
	self.log_file.writelines(completion_rate)

def get_day(start_time, fix_day):

	if start_time == None:
		start_time = datetime.datetime.now()

	last_time = start_time + datetime.timedelta(days=-fix_day)
	day_string = last_time.strftime('%Y-%m-%d')

	return day_string

def get_day_titles(self):

	day_titles = []

	hour_period_array = ['10:00', '14:00', '22:00']
	for i in xrange(0,self.days_count+1):
		j = 3
		while (j > 0):
			j-=1
			day_period = get_day(self.end_day,i) + ' ' + hour_period_array[j]
			day_titles.append(day_period)

	return day_titles

def write_store(self, store):

	store_id = str(store['sys_store_id'])
	store_name = str(store['name'])

	store_info = 'Store Id: ' + store_id + ', Store Name: ' + store_name
	
	self.writer.writerow([store_info])
	self.dict_writer.writeheader()

	inventorys = self.db.inventory.find({ "sys_store_id": store_id })
	for inventory in inventorys:
		self.dict_writer.writerow(inventory)

class WineExcel:

	def __init__(self, start_date, end_date):

		self.db = MongoClient().wine

		remove_file(log_file_name)

		self.start_day = datetime.datetime.strptime(start_date,'%Y-%m-%d')
		self.end_day = datetime.datetime.strptime(end_date,'%Y-%m-%d')
		self.days_count = (self.end_day-self.start_day).days

		field_names = ['wine_name', 'wine_number']
		field_names.extend(get_day_titles(self))

		csv_file = file('inventory.csv', 'w')
		csv_file.write(codecs.BOM_UTF8)
		self.writer = csv.writer(csv_file)
		self.dict_writer = csv.DictWriter(csv_file, fieldnames=field_names, extrasaction='ignore')

	def export_inventory(self):

		store_array = self.db.store.find()
		for i in xrange(0,store_array.count()):
			store = store_array[i]
			write_store(self, store)
			write_log(self,i)

		self.log_file.close()


if __name__ == '__main__':

	wineExcel = WineExcel('2016-09-08','2016-09-15')
	wineExcel.export_inventory()

