#!/usr/bin/env python
# coding=utf-8

# import pprint
import sys
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

csv.field_size_limit(sys.maxsize)

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

# Collects Crypto news from Google news
@click.command()
@click.option('--filename', default='prop_content_200227_1421.csv')
@click.option('--secrets', default='secrets.json')
# @click.option('--session_id', default='2171486e6c13b61ad78b34a59f337ab0')
# def collector(secrets, url, session_id):
def readprop(filename, secrets):
  secrets_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), secrets)
  try:
    with open(secrets_file_path) as data_file:    
      secret = (json.load(data_file))['esp']
  except FileNotFoundError:
    print('Error: file not found..')
    return

  property_ids = []

  try:
    # filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
    with open(filename, encoding='utf-8-sig') as csvfile:
      ids = set()
      reader = csv.DictReader(csvfile, delimiter='^')
      for row in reader:
        entry = {}
        entry['property_id'] = row['property_id']
        entry['name'] = row['name']
        entry['phone'] = row['phone']
        property_ids.append(entry)
  except FileNotFoundError:
    print('Error: {} file not found...'.format(filename))
    return

  print('INFO: {} id parsed...'.format(len(property_ids)))

  print(property_ids)

	# time.sleep(100000000) 
  return 

if __name__ == '__main__':
  readprop()