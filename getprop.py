#!/usr/bin/env python
# coding=utf-8

# import pprint
import csv
import click 
import requests
import datetime as datetime
# from bs4 import BeautifulSoup
# from splinter import Browser
import hashlib
import time
# import re
# import copy
import os
import json
# import pickle
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException   
# from selenium.common.exceptions import ElementNotVisibleException   
# from selenium.common.exceptions import StaleElementReferenceException   
# from selenium.common.exceptions import WebDriverException
# from selenium.common.exceptions import TimeoutException
# from requests.exceptions import ConnectionError
# from requests.exceptions import ChunkedEncodingError
# from requests.exceptions import ReadTimeout
# # from selenium.webdriver import ChromeOptions
# from newsapi import NewsApiClient
from urllib.parse import urljoin

DAYS = 1

# hc_secret = None
def load_secrets(secrets):
	secrets_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')
	try:
		with open(secrets_file_path) as data_file:    
			secret = (json.load(data_file))['esp']
	except FileNotFoundError:
		print('Error: file not found..')
		return None
	except KeyError:
		return None
	return secret

def login_Google(driver, secret):
	try: 
		sign_in_btn = driver.find_element_by_css_selector('a.gb_3.gb_4.gb_ae.gb_pb')
		sign_in_btn.click()
		email_input = driver.find_element_by_id('identifierId')
		email_input.send_keys(secret['account'])
		next_btn = driver.find_element_by_id('identifierNext')
		next_btn.click()
		# password_input = driver.find_element_by_css_selector("input[type='password']")
		# password_input.click()
		# password_input.send_keys(secret['password'])

		var = input('Please entre your password and verification text and press enter to continue...')
		# next_btn = driver.find_element_by_id('passwordNext')
		# next_btn.click()Lyulyu
	except NoSuchElementException:
		print('Error: NoSuchElementException during login...')
		return None
	except KeyError:
		print('Error: KeyError for secret...')
		return None
	except Exception as e:
		print('Error: {}'.format(repr(e)))
		return None

	return 'Successful login'

REMOTE = 'remote'
NEW = 'new'

def get_date(time_text):
	if 'Yesterday' in time_text:
		return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%b %d, %y')
	if '2 days ago' in time_text:
		return (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%b %d, %y')
	if '3 days ago' in time_text:
		return (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%b %d, %y')
	return datetime.datetime.now().strftime('%b %d, %y')

region_names = {
  '2621': 'New York',
  '2734': 'Paris',
  '2114': 'London',
  '178312': 'Sydney',
  '3168': 'Singapore'
}

# Collects Crypto news from Google news
@click.command()
@click.option('--filename1', default='3168.csv')
@click.option('--filename2', default='2621.csv')
@click.option('--filename3', default='2734.csv')
@click.option('--filename4', default='2114.csv')
@click.option('--filename5', default='178312.csv')
@click.option('--secrets', default='secrets.json')
# @click.option('--session_id', default='2171486e6c13b61ad78b34a59f337ab0')
# def collector(secrets, url, session_id):
def getprop(filename1, filename2, filename3, filename4, filename5, secrets):
  secrets_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), secrets)
  try:
    with open(secrets_file_path) as data_file:    
      secret = (json.load(data_file))['esp']
  except FileNotFoundError:
    print('Error: file not found..')
    return

  property_ids = []

  for filename in [filename1, filename2, filename3, filename4, filename5]:
    try:
      # filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
      with open(filename, encoding='utf-8-sig') as csvfile:
        ids = set()
        reader = csv.DictReader(csvfile)
        for row in reader:
          entry = {}
          entry['property_id'] = row['property_id']
          entry['region_id'] = filename.split('.')[0]
          entry['region'] = region_names[entry['region_id']]
          property_ids.append(entry)
    except FileNotFoundError:
      print('Error: {} file not found...'.format(filename))
      continue

  print('INFO: {} id parsed...'.format(len(property_ids)))

  res=[]
  url = urljoin(secret['base_url'], 'properties/content')

  for i, property_id in enumerate(property_ids):
    print('+++ {} out of {} property_ids +++'.format(i+1, len(property_ids)))
    timestamp = str(int(time.time()));
    api_key = secret['api_key']
    shared_secret = secret['shared_secret']
    # api_key.encode('utf-8')+shared_secret.encode('utf-8')+timestamp.encode('utf-8')
    signature = '{}'.format(hashlib.sha512(api_key.encode('utf-8')+shared_secret.encode('utf-8')+timestamp.encode('utf-8')).hexdigest())
    auth_header = "EAN APIKey="+api_key + ",Signature="+signature + ",timestamp="+timestamp
    print('INFO: auth_header: {}'.format(auth_header))

    payload = {
      'language': 'en-US',
      'property_id': property_id['property_id']
    }
    headers = {
      'Accept': 'application/json',
      'Accept-Encoding': 'json',
      'Authorization': auth_header,
      'User-Agent': 'test user agent',
      'Customer-Session-Id': 'test'
    }

    r = requests.get(url, headers=headers, params=payload)

    if r.status_code != requests.codes.ok:
      print('Error: status_code {} skipping {}...'.format(r.status_code, property_id['property_id']))
      continue
    rr = r.json()

    entry = {}
    entry['property_id'] = property_id['property_id']
    entry['region_id'] = property_id['region_id']
    entry['region'] = property_id['region']

    try:
      entry['name'] = rr[property_id['property_id']]['name']
      entry['address'] = json.dumps(rr[property_id['property_id']]['address'])
      entry['ratings'] = json.dumps(rr[property_id['property_id']]['ratings'])
      entry['phone'] = rr[property_id['property_id']]['phone']
      entry['checkin'] = json.dumps(rr[property_id['property_id']]['checkin'])
      entry['checkout'] = json.dumps(rr[property_id['property_id']]['checkout'])
      entry['amenities'] = json.dumps(rr[property_id['property_id']]['amenities'])

      image1 = rr[property_id['property_id']]['images'][0]
      image2 = rr[property_id['property_id']]['images'][1]
      image3 = rr[property_id['property_id']]['images'][2]
      entry['image1'] = json.dumps(image1)
      entry['image2'] = json.dumps(image2)
      entry['image3'] = json.dumps(image3)

      i = 0
      rooms = {}
      for key in rr[property_id['property_id']]['rooms'].keys():
        if i > 9:
          break
        rooms[key] = rr[property_id['property_id']]['rooms'][key]
      entry['rooms'] = json.dumps(rooms).replace('\n', '')

      # entry['images'] = json.dumps(rr[property_id['property_id']]['images'])
      # entry['rooms'] = json.dumps(rr[property_id['property_id']]['rooms']).replace('\n', '')
    except KeyError:
      print('Error: some key not found...')
      continue

    # image1 = rr[property_id['property_id']]['images'][0]
    # image2 = rr[property_id['property_id']]['images'][1]
    # image3 = rr[property_id['property_id']]['images'][2]
    # entry['image1'] = json.dumps(image1)
    # entry['image2'] = json.dumps(image2)
    # entry['image3'] = json.dumps(image3)

    # i = 0
    # rooms = {}
    # for key in rr[property_id['property_id']]['rooms'].keys():
    #   if i > 9:
    #     break
    #   rooms[key] = rr[property_id['property_id']]['rooms'][key]
    # entry['rooms'] = json.dumps(rooms).replace('\n', '')
    print('--- Property {}: {} {}'.format(entry['property_id'], entry['name'], entry['phone']))
    res.append(entry)

  keys = res[0].keys()
  output_filename = '_'.join(['prop_content',
                                datetime.datetime.now().strftime('%y%m%d'),
                                datetime.datetime.now().strftime('%H%M')]) + '.csv'
  with open(output_filename, 'w', newline='', encoding='utf-8-sig') as output_file:
    dict_writer = csv.DictWriter(output_file, keys, delimiter='^')
    # dict_writer = csv.DictWriter(output_file, field_names)
    dict_writer.writeheader()
    dict_writer.writerows(res)

	# time.sleep(100000000) 
  return 

if __name__ == '__main__':
  getprop()