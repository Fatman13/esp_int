#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request

import datetime as datetime
import hashlib
import time
import requests
from urllib.parse import urljoin
import os
import json
import csv
import sys
import re

csv.field_size_limit(sys.maxsize)

secrets_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')
try:
  with open(secrets_file_path) as data_file:    
    secret = (json.load(data_file))['esp']
except FileNotFoundError:
  print('Error: file not found..')

properties={}
properties_r={}
properties_r['New York']=[]
properties_r['Paris']=[]
properties_r['London']=[]
properties_r['Sydney']=[]
properties_r['Singapore']=[]

try:
  # filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
  with open('prop_content_200227_1421.csv', encoding='utf-8-sig') as csvfile:
    ids = set()
    reader = csv.DictReader(csvfile, delimiter='^')
    for row in reader:
      entry = {}
      entry['property_id'] = row['property_id']
      entry['region_id'] = row['region_id']
      entry['region'] = row['region']

      entry['name'] = row['name']
      entry['address'] = json.loads(row['address'])
      entry['ratings'] = json.loads(row['ratings'])
      entry['ratings_n'] = float(entry['ratings']['property']['rating'])
      entry['phone'] = row['phone']
      entry['checkin'] = json.loads(row['checkin'])
      entry['checkout'] = json.loads(row['checkout'])
      entry['amenities'] = json.loads(row['amenities'])
      entry['amenities_list'] = set()
      for key in entry['amenities'].keys():
        # print(key)
        # print(entry['amenities'][key]['name'])
        entry['amenities_list'].add(entry['amenities'][key]['name'])
      # entry['amenities_list'] = amenities_list

      entry['image1'] = json.loads(row['image1'])
      entry['image2'] = json.loads(row['image2'])
      entry['image3'] = json.loads(row['image3'])

      entry['rooms'] = json.loads(re.sub(re.compile('<.*?>'), '', row['rooms']))
      if entry['region_id'] == '2621':
        properties_r['New York'].append(entry)
      if entry['region_id'] == '2734':
        properties_r['Paris'].append(entry)
      if entry['region_id'] == '2114':
        properties_r['London'].append(entry)
      if entry['region_id'] == '178312':
        properties_r['Sydney'].append(entry)
      if entry['region_id'] == '3168':
        properties_r['Singapore'].append(entry)
      properties[entry['property_id']] = entry
except FileNotFoundError:
  print('Error: {} file not found...'.format(filename))

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/eps')
def eps():
  data = {}
  now = datetime.datetime.now() + datetime.timedelta(days=1)
  now1 = datetime.datetime.now() + datetime.timedelta(days=2)
  data['now'] = now
  data['now1'] = now1
  data['New York'] = 1
  return render_template('list.html', data=data)

@app.route('/eps/<property_id>')
def eps_details(property_id):
  data = {}
  now = datetime.datetime.now() + datetime.timedelta(days=1)
  now1 = datetime.datetime.now() + datetime.timedelta(days=2)
  data['now'] = now
  data['now1'] = now1

  data['hotel'] = properties[property_id]

  data['New York'] = 1
  # print(data['hotel'])

  return render_template('list.html', data=data)

@app.route('/eps', methods=['POST'])
def eps_form():
  print(request.form)
  data = {}
  now = datetime.datetime.strptime(request.form['checkin_date'], '%Y-%m-%d')
  now1 = datetime.datetime.strptime(request.form['checkout_date'], '%Y-%m-%d')
  data['now'] = now
  data['now1'] = now1

  data[request.form['region']] = 1

  url = urljoin(secret['base_url'], 'properties/availability')

  timestamp = str(int(time.time()));
  api_key = secret['api_key']
  shared_secret = secret['shared_secret']
  # api_key.encode('utf-8')+shared_secret.encode('utf-8')+timestamp.encode('utf-8')
  signature = '{}'.format(hashlib.sha512(api_key.encode('utf-8')+shared_secret.encode('utf-8')+timestamp.encode('utf-8')).hexdigest())
  auth_header = "EAN APIKey="+api_key + ",Signature="+signature + ",timestamp="+timestamp
  print('INFO: auth_header: {}'.format(auth_header))

  data['auth_header'] = auth_header

  property_ids = []
  for prop in properties_r[request.form['region']]:
    property_ids.append(prop['property_id'])
    # if request.form['ratings'] == 'Choose...' and 'amenities' not in request.form.keys():
    #   property_ids.append(hotel['property_id'])
    #   continue
    # if 

  for hotel in properties_r[request.form['region']]:
    if request.form['ratings'] != 'Choose...':
      if float(request.form['ratings']) > hotel['ratings_n']:
        property_ids.remove(hotel['property_id']) 
        continue
    if 'amenities' in request.form.keys():
      # amenities_request = set(request.form['amenities'])
      amenities_request = set(request.form.getlist('amenities'))
      # print(amenities_request)
      # print(hotel['amenities_list'])
      if not amenities_request.issubset(hotel['amenities_list']):
        property_ids.remove(hotel['property_id'])

  data['ratings'] = request.form['ratings']

  # property_ids = [28540]

  headers = {
      'Accept': 'application/json',
      'Accept-Encoding': 'json',
      'Authorization': auth_header,
      'User-Agent': 'test user agent'
  }
  payload = {
      'language': 'en-US',
      'property_id': property_ids,
      'checkin': request.form['checkin_date'],
      'checkout': request.form['checkout_date'],
      'currency': 'USD',
      'country_code': 'US',
      'occupancy': request.form['occupancy'],
      'sales_channel': 'website',
      'sales_environment': 'hotel_only',
      'rate_plan_count': '1'
  }
  data['api_key'] = secret['api_key']
  data['shared_secret'] = secret['shared_secret']

  r = requests.get(url, headers=headers, params=payload)

  data['request'] = r.url

  rr = r.json()

  # print(rr)
  if len(property_ids) != 0:
    print('+++ {} hotels found +++'.format(len(rr)))
    data['hotels'] = []
    for i, hotel in enumerate(rr):
      # print('+++ {} out of {} hotels +++'.format(i+1, len(rr)))
      # print(hotel)
      ent = {}
      ent['price'] = hotel['rooms'][0]['rates'][0]['occupancy_pricing'][request.form['occupancy']]['totals']['inclusive']['request_currency']['value']
      ent['property_id'] = hotel['property_id']
      ent['name'] = properties[hotel['property_id']]['name']
      ent['address'] = properties[hotel['property_id']]['address']
      ent['region'] = properties[hotel['property_id']]['region']
      ent['region_id'] = properties[hotel['property_id']]['region_id']
      ent['ratings'] = properties[hotel['property_id']]['ratings']
      ent['phone'] = properties[hotel['property_id']]['phone']
      ent['checkin'] = properties[hotel['property_id']]['checkin']
      ent['checkout'] = properties[hotel['property_id']]['checkout']
      ent['amenities'] = properties[hotel['property_id']]['amenities']
      ent['image1'] = properties[hotel['property_id']]['image1']
      ent['image2'] = properties[hotel['property_id']]['image2']
      ent['image3'] = properties[hotel['property_id']]['image3']
      ent['rooms'] = properties[hotel['property_id']]['rooms']
      data['hotels'].append(ent)
  else:
    data['no_result'] = {}

  return render_template('list.html', data=data)













