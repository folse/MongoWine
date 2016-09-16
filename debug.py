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

if __name__ == '__main__':

        global db
        db = MongoClient().wine

        wine_category_dict = { "red_wine": u'Rött vin', "white_wine": u'Vitt vin' }

        for wine_category in wine_category_dict.keys():

                inventory_collection = "inventory_" + wine_category


                #批量更新 -----

                result = db[inventory_collection].update_many(
                    {"2016-09-17 01:00": {"$exists": True}},
                    {
                        "$unset": {"2016-09-17 01:00": True}
                    }
                )

                print result.matched_count
                print result.modified_count

                # -------

