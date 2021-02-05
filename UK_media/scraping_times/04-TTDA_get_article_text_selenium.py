# This file opens a list of csv files containing
# links to articles in the Times Digital Archive .
# It downloads the OCR text from those articles,
# saving them to one folder for each date.

import os
import glob
import time
import pandas as pd
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException

# Meedan's fix
def wait_for_selector(browser, element_id=None, xpath=None):
	attempts = 0
	max_attempts = 10
	element = None
	while (element==None) and (attempts < max_attempts):
		attempts += 1
		try:
			if element_id is not None:
				element = browser.find_element_by_id(element_id)
				#if not element.is_displayed():
				if not element.is_enabled():
					raise ElementNotVisibleException("Element not visible! Trying again...")

			elif xpath is not None:
				element = browser.find_element_by_xpath(xpath)
				#if not element.is_displayed():
				if not element.is_enabled():
					raise ElementNotVisibleException("Path not visible! Trying again...")

			else:
				raise ValueError('Both element_id and xpath are None')

		except (ElementNotVisibleException, BrokenPipeError) as e:
			print(e)
			element = None

		time.sleep(1)
	return element


def fetch_articles(infile):
	str_date = infile.split('/')[2][:-4]
	#infile = 'data/%s.csv' % str_date

	tmp_dir = os.getcwd()+'/data/OCRtext/tmp'
	download_dir = os.getcwd()+'/data/OCRtext/'+str_date
	if not os.path.exists(download_dir):
		os.makedirs(download_dir)

	# See if the whole date has been downloaded
	file_done  = download_dir + '/' + 'done.txt'
	if os.path.exists(file_done):
		print('Nothing left to download from %s' % str_date)
		return

	print('Downloading OCR text from %s' % str_date)
	df = pd.read_csv(infile, names=['date','url_article','page','type_article'])

	fox_profile = webdriver.FirefoxProfile()
	fox_profile.set_preference('browser.download.folderList', 2)
	fox_profile.set_preference('browser.download.manager.showWhenStarting', False)
	fox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
	fox_profile.set_preference("browser.download.dir", tmp_dir)
	fox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
	fox_profile.set_preference('permissions.default.image', 2) # 1 for show, 2 for not show


	"""
	# Other profile preferences I might want to use   

    fox_profile.set_preference("plugin.state.flash", 0)
    fox_profile.set_preference("plugin.state.java", 0)

    fox_profile.set_preference("dom.max_chrome_script_run_time", 0)
    fox_profile.set_preference("dom.max_script_run_time", 0)
    fox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')

    # this disables javascript (don't use it)
    fox_profile.set_preference("javascript.enabled", False)

    fox_profile.set_preference('app.update.auto', False)
    fox_profile.set_preference('app.update.enabled', False)
    fox_profile.set_preference('app.update.silent', False)

    fox_profile = FirefoxProfile()
    fox_profile.set_preference("focusmanager.testmode", False)
    fox_profile.set_preference('plugins.testmode', False)
    fox_profile.set_preference('webdriver_enable_native_events', True)
    fox_profile.set_preference('webdriver.enable.native.events', True)
    fox_profile.set_preference('enable.native.events', True)
    fox_profile.native_events_enabled = True

	fox_profile.set_preference("browser.cache.disk.enable", False)
	fox_profile.set_preference("browser.cache.memory.enable", False)
	fox_profile.set_preference("browser.cache.offline.enable", False)
	fox_profile.set_preference("network.http.use-cache", False)
	"""

	executable_path = '/usr/local/bin/geckodriver'

	fox_opt = webdriver.FirefoxOptions()
	#fox_opt.add_argument('--headless') # Keep it not headless for now, for some reason that makes the OCR work

	to_filter_out = ['Advertising','Arts and Sports','People',
					 'Preliminary and Supplementary Material']

	# Before opening the browser, see if there's any article left to fetch
	indices_to_fetch = []
	for index, row in df.iterrows():
		type_article = row.type_article
		url 		 = row.url_article
		print('Article %d: ' % index, end='')

		# See if file has already been downloaded
		fetched_article = glob.glob(download_dir + '/' + str(index).zfill(3) + '*')

		if type_article in to_filter_out:
			print('Filtering %s out' % type_article)
			if len(fetched_article) > 0:
				str_fetched_article = '/'.join(fetched_article[0].split('/')[-2:])
				if os.path.exists(fetched_article[0]):
					os.remove(fetched_article[0])
					print("Removing", str_fetched_article)


		elif len(fetched_article) > 0:
			str_fetched_article = '/'.join(fetched_article[0].split('/')[-2:])
			print(str_fetched_article,"already fetched")

		else:
			indices_to_fetch += [index]
			print("to fetch")

	if len(indices_to_fetch) > 0:
		print( len(indices_to_fetch), "articles to fetch for", str_date)
		df_to_fetch = df.loc[indices_to_fetch]

		with webdriver.Firefox(firefox_options=fox_opt, firefox_profile=fox_profile, executable_path=executable_path) as browser:
			browser.set_page_load_timeout(120) # timeout = 120 seconds
			browser.implicitly_wait(10)

			for index, row in df_to_fetch.iterrows():
				type_article = row.type_article
				url 		 = row.url_article
				print('Article %d: ' % index, end='')

				numTries=0
				while numTries<3: 
					try:
						browser.get(url)
						numTries=3 # lazy writing. Rewrite this later
					except:
						numTries += 1
						print("\nTrying to load the page again...")
						time.sleep(1)

				if numTries > 3:
					with open('articles_to_scrape_again.txt','a') as f:
						f.write(str_date+','+url+','+str(index)+'\n')
					print("Error for article %d from %s:" % (index, str_date))
					break

				numTries=0
				while True:
					numTries+=1
					try:
						# browser.find_element_by_id('download_link').click()
						#
						# Find Download button
						#
						# Try Meedan's fix						#
						print("\nFinding download button on menu")
						element = wait_for_selector(browser, element_id='download_link')
						
						# Click on Download
						element.click()
						time.sleep(1)

						# This doesn't work
						#wait = WebDriverWait(browser, 10)
						#element = wait.until(EC.element_to_be_clickable((By.ID, 'dvi_page_range_ocr')))

						# Find OCR button

						#browser.find_element_by_id('dvi_page_range_ocr').click()
						#time.sleep(1)

						# Try Meedan's fix
						print("Finding OCR button")
						element = wait_for_selector(browser, element_id='dvi_page_range_ocr')

						# Click on OCR
						element.click()

						# Find Download button

						#xpath = "//div[@class='ui-dialog-buttonset']/button"
						#browser.find_elements_by_xpath(xpath)[-2].click()
						#time.sleep(1)

						# Try Meedan's fix
						xpath = "/html/body/div[10]/div[3]/div/button[1]"
						# I found this xpath by going on Ctrl-Shift-C, hovering over download, right-clicking its code and doing Copy > Xpath

						print("Finding Download OK button")
						element = wait_for_selector(browser, xpath=xpath)

						# Click on Download button
						element.click()

						# Save article
						file_oldaddress = glob.glob(tmp_dir+'/*')[0]
						file_name = file_oldaddress.split('/')[-1]
						file_newaddress = download_dir + '/' + str(index).zfill(3) + '_' + file_name
						os.rename(file_oldaddress, file_newaddress)
						print("Saved article %d from %s" % (index, str_date))

						break

					except Exception as e:
						print('Exception: %s' % str(e))

						message = 'Unable to locate element'
						if message in str(e):
							print(str_date, 'article', index, 'does not contain OCR')
							# Save dummy article
							file_name = 'dummy.txt' 
							file_newaddress = download_dir + '/' + str(index).zfill(3) + '_' + file_name
							open(file_newaddress,'a').close()
							print("Saved dummy article %d from %s" % (index, str_date))
							break
						else:
							if numTries>3:
								with open('articles_to_scrape_again.txt','a') as f:
									f.write(str_date+','+url+','+str(index)+'\n')
								print("Error for article %d from %s:" % (index, str_date))
								break

							else:
								print(str_date, 'article', index)
								print(url)
								print("Error, waiting 5 seconds to retry...")
								time.sleep(5)		

	else:
		print('Nothing left to download from %s' % str_date)
		file_newaddress = download_dir + '/' + 'done.txt'
		open(file_newaddress,'a').close()

def fetch_year_range(y0,y1):
	for year in range(y1, y0-1, -1):
		print("Fetching year %d" % year)
		for infile in sorted(glob.glob('data/filtered/%s*' % year), reverse=True):
			#str_date = d.strftime("%Y-%m-%d")
			#print(infile, infile.split('/')[1][:-4])
			fetch_articles(infile)


def fetch_with_time(y0,y1):
	import time
	t0 = time.time()
	fetch_year_range(y0,y1)
	t1 = time.time()
	print("time it took in seconds:", t1-t0)
