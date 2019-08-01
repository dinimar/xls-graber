# -*- coding: utf-8 -*-
import os
import csv
import time
import logging
import yaml
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# create logger
cli_logger = logging.getLogger('i-otvet-loader')
# set logging level
cli_logger.setLevel(logging.DEBUG)
# create console and file handler
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to handlers
ch.setFormatter(formatter)
# add handlers to logger
cli_logger.addHandler(ch)

# header_x = "//div[contains(@class, 'qam-main-nav-wrapper')]"
toggle_x = "//div[contains(@class, 'qam-account-items-wrapper')]"
sign_in_x = "//input[contains(@name, 'dologin')]"
admin_x = "//li[contains(@class, 'qa-nav-main-admin')]"
cats_x = "//li[contains(@class, 'qa-nav-sub-admin-categories')]"
import_x = "//li[contains(@class, 'qa-nav-sub-admin-import')]"
file_x = "//input[contains(@type, 'file')]"
import_sub_x = "//input[contains(@class, 'qa-form-tall-button-pupi_bcg_button_import')]"
add_cat_x = "//input[contains(@class, 'qa-form-tall-button-add')]"
cat_name_x = "//input[contains(@class, 'qa-form-tall-text')]"
save_cat_x = "//input[contains(@class, 'qa-form-tall-button-save')]"
email_x = "//input[contains(@name, 'emailhandle')]"
pass_x = "//input[contains(@name, 'password')]"

root = "/home/dinir/Documents/git/xls-graber/"
out_dir = "resources/out/"
xlsx_name = "questions.xlsx"
cat_file = "resources/categories.csv"
f_cred_name = "credentials.yaml"

creds = {}
cats = {}

with open(os.path.join(root, f_cred_name), 'r') as stream:
	cli_logger.info("Yaml file's opened")
	try:
		creds = yaml.safe_load(stream)
		cli_logger.info("Credentials're loaded")
	except yaml.YAMLError as exc:
		print(exc)

with open(os.path.join(root, cat_file), newline='') as csvfile:
	cli_logger.info("CSV file's opened")
	cats = dict(csv.reader(csvfile, delimiter=',', quotechar='"'))
	cats = {int(k):v for k, v in cats.items()}	 
	cli_logger.info("Categories're loaded")

options = Options()
# options.headless = True
driver = webdriver.Firefox(options=options)
try:
	driver.get(creds['site-url'])

	# open login dialog
	cli_logger.info("Waiting a toggle button")
	toggle_b = WebDriverWait(driver, 10).until(
    	EC.element_to_be_clickable((By.XPATH, toggle_x)))
	toggle_b.click()
	cli_logger.info("Clicked on toggle button")
	# get sign-in fields
	email_field =	driver.find_element_by_xpath(email_x)
	pwd_field = driver.find_element_by_xpath(pass_x)
	sign_b = driver.find_element_by_xpath(sign_in_x)
	# enter credentials
	email_field.send_keys(creds['email'])
	pwd_field.send_keys(creds['password'])
	cli_logger.info("Email field is filled by: "+creds['email'])
	cli_logger.info("password field is filled by: "+creds['password'])
	# log in
	sign_b.click()
	cli_logger.info("Singed in")
	# open admin dashboard
	cli_logger.info("Waiting an admin button")
	admin_b = WebDriverWait(driver, 10).until(
    	EC.element_to_be_clickable((By.XPATH, admin_x)))
	admin_b.click()
	cli_logger.info("Clicked on admin button")
	# open category dashboard
	cli_logger.info("Waiting a category button")
	cat_b = WebDriverWait(driver, 10).until(
    	EC.element_to_be_clickable((By.XPATH, cats_x)))
	cat_b.click()
	cli_logger.info("Clicked on category button")
	cli_logger.info("Adding categories:")
	for k in sorted(cats.keys()):
		# open 'add category' dashboard
		cli_logger.info("Waiting an 'add category' button")
		add_cat_b = WebDriverWait(driver, 30).until(
	    	EC.presence_of_element_located((By.XPATH, add_cat_x)))
		add_cat_b.click()
		cli_logger.info("Clicked on 'add category' button")
		# fill fieds
		cat_name_f = WebDriverWait(driver, 10).until(
	    	EC.presence_of_element_located((By.XPATH, cat_name_x)))
		cat_name_f.send_keys(cats[k])
		cli_logger.info("Category field is filled by: "+cats[k])
		save_cat_b = WebDriverWait(driver, 10).until(
	    	EC.presence_of_element_located((By.XPATH, save_cat_x)))
		save_cat_b.click()
		cli_logger.info("Clicked on 'save category' button")
	# open import dashboard
	cli_logger.info("Waiting a import button")
	import_b = WebDriverWait(driver, 10).until(
    	EC.element_to_be_clickable((By.XPATH, import_x)))
	import_b.click()
	cli_logger.info("Clicked on import button")
	cli_logger.info("Importing files:")
	for i in range(1000, 10952380, 1000):
		cli_logger.info("Waiting a file field")
		file_f = WebDriverWait(driver, 10).until(
	    	EC.element_to_be_clickable((By.XPATH, file_x)))
		file_f.send_keys(os.path.join(root, (out_dir+str(i)+'-'+xlsx_name)))
		cli_logger.info("Filled file field")

		i_sub = WebDriverWait(driver, 10).until(
	    	EC.element_to_be_clickable((By.XPATH, import_sub_x)))
		i_sub.click()
		cli_logger.info("Clicked 'import'")
		# break

	time.sleep(10)
finally:
	driver.close()