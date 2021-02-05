# This file runs over a range of dates, running backwards from the last date,
# jumping in gaps of a year, a month, a week or a day,
# and saves the link to the front page of every article in the Times Digital Archive
# to a csv file.

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import timedelta, datetime, date

def daterange_forward(start_date, end_date, gap='day'):

	if gap == 'year':
		for year in range(start_date.year,end_date.year+1):
			nextdate = date(year, start_date.month, start_date.day)
			if nextdate.weekday() is 6: # if it's a Sunday
				yield nextdate + timedelta(1)
			else:
				yield nextdate

	elif gap == 'month':
		for n in range(int ((end_date - start_date).days+1)):
			nextdate = start_date + timedelta(n)
			if nextdate.day == start_date.day:
				if nextdate.weekday() is 6: # if it's a Sunday
					yield nextdate + timedelta(1)
				else:
					yield nextdate

	elif gap == 'week':
		for n in range(int ((end_date - start_date).days+1)):
			nextdate = start_date + timedelta(n)
			if nextdate.weekday() == 2: # if it's a Wednesday
				yield nextdate

	else: # gap == 'day':
		for n in range(int ((end_date - start_date).days)):
			yield start_date + timedelta(n)


# This one goes backwards
def daterange(start_date, end_date, gap='day'):

	if gap == 'year':		
		#for year in range(start_date.year,end_date.year+1):
		for year in range(end_date.year, start_date.year-1, -1):
			nextdate = date(year, start_date.month, start_date.day)
			if nextdate.weekday() is 6: # if it's a Sunday
				yield nextdate + timedelta(1)
			else:
				yield nextdate

	elif gap == 'month':
		for n in range(int ((end_date - start_date).days+1)):
#			nextdate = start_date + timedelta(n)
			nextdate = end_date - timedelta(n)
			if nextdate.day == start_date.day:
				if nextdate.weekday() is 6: # if it's a Sunday
					yield nextdate + timedelta(1)
				else:
					yield nextdate

	elif gap == 'week':
		for n in range(int ((end_date - start_date).days+1)):
#			nextdate = start_date + timedelta(n)
			nextdate = end_date - timedelta(n)
			if nextdate.weekday() == 2: # if it's a Wednesday
				yield nextdate

	else: # gap == 'day':
		for n in range(int ((end_date - start_date).days)):
			#yield start_date + timedelta(n)
			yield end_date - timedelta(n)


def fetch_all():

	start_date = date(1947, 1, 1)   # to match Der Spiegel
	end_date   = date(2012, 12, 31)
	gap = 'week'

	URL_prefix  = 'http://gdc.galegroup.com/gdc/artemis/BrowseByDatePage/BrowseByDateWindow?displayGroupName=DVI-Newspapers&p=TTDA&mode=view&u=oxford&action=e&windowstate=normal#'

	fox_opt = webdriver.FirefoxOptions()
	fox_opt.add_argument('--headless')

	with webdriver.Firefox(firefox_options=fox_opt) as browser:
		browser.set_page_load_timeout(120) # timeout = 120 seconds
		browser.get(URL_prefix) # This line is necessary for the next browser.get() to work
		
		for d in daterange(start_date, end_date, gap=gap):

			str_date = d.strftime("%Y-%m-%d")
			print("Fetching %s" % str_date)

			URL_date_format = 'http://gdc.galegroup.com/gdc/artemis/BrowseByDatePage/BrowseByDateWindow?action=f&id=issueDocument&cacheability=PAGE&p=TTDA&u=oxford&month={}&day={}&year={}&mCodes=0FFO&al=true'
			URL_date = URL_date_format.format(str(d.month).zfill(2), str(d.day).zfill(2), d.year )

			try:
				browser.get(URL_date)
			except BrokenPipeError:
				browser.get(URL_date)

			try:
				a_elements = browser.find_elements_by_xpath("//div[@id='thumb_image']/a[@href]")
			except BrokenPipeError:
				a_elements = browser.find_elements_by_xpath("//div[@id='thumb_image']/a[@href]")

			try:
				URL_front_page = a_elements[0].get_attribute('href')
			except BrokenPipeError:
				URL_front_page = a_elements[0].get_attribute('href')
			except IndexError:
				pass

			time.sleep(2)
			#print( '%s,%s\n' % (str_date, URL_front_page) )

			# save url_front_page
			outfile  = 'data/all_front_pages_wednesdays.csv'
			with open(outfile,"a") as f:
				f.write('%s,%s\n' % (str_date, URL_front_page))

