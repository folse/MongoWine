# -*- coding:utf-8 -*-
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, g, make_response, send_file
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Wine
from wine_excel import WineExcel
from inventory_excel import InventoryExcel

import threading

import os, time, datetime, calendar
import simplejson

def register_request(app):
    @app.before_request
    def register_g():
        # g.status_to_title=['A', 'B', 'C', 'D', 'E']
        # g.status_to_title_dict={None: '', 0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'}
        pass

def export_inventory_excel(start_date, end_date, category):
    inventoryExcel = InventoryExcel(start_date, end_date, category)

def export_wine_excel():
    wineExcel = WineExcel()

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('main.html')

@main.route('/export_inventory', methods=['POST'])
@login_required
def export_inventory():
    if request.method == 'POST':
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        category = request.args.get('category', '')

        start_day = datetime.datetime.strptime(start_date,'%Y-%m-%d')
        end_day = datetime.datetime.strptime(end_date,'%Y-%m-%d')
        days_count = (end_day-start_day).days

        if days_count > 31:
            data = { "msg":"Please don't select more than 31 days", "code":"0001" }
        else:
            threads = []
            thread = threading.Thread(target=export_inventory_excel,args=(start_date, end_date, category))
            threads.append(thread)
            for t in threads:
                t.setDaemon(True)
                t.start()

            data = { "msg":"Executed", "code":"0000" }
        
        return simplejson.dumps(data)

@main.route('/export_wine', methods=['POST'])
@login_required
def export_wine():
    if request.method == 'POST':

        month = request.args.get('month', '')

        threads = []
        thread = threading.Thread(target=export_wine_excel,args=())
        threads.append(thread)
        for t in threads:
            t.setDaemon(True)
            t.start()

        data = { "msg":"Executed", "code":"0000" }
        
        return simplejson.dumps(data)

@main.route('/get_excel_progress', methods=['GET'])
@login_required
def get_excel_progress():
    type = request.args.get('type', '')

    if type == 'inventory':
        file_name = 'inventory.log'
    elif type == 'wine':
        file_name = 'wine.log'

    if os.path.exists(file_name):
        log_file = open(file_name)
        log_msg = log_file.readline()
        data = { "msg":log_msg, "code":"0000" }
    else:
        data = { "msg":'Generating...', "code":"0000" }
    
    return simplejson.dumps(data)

@main.route('/download_excel')
@login_required
def download_excel():

    type = request.args.get('type', '')
    category = request.args.get('category', '')

    if type == 'wine':
        file_name = 'wine.csv'
    else:
        file_name = 'inventory_' + category + '.csv'

    file_path = os.getcwd() + '/' + file_name
    print os.getcwd()
    response = make_response(send_file(file_path))
    response.headers["Content-Disposition"] = "attachment; filename=%s;" % file_name
    return response
