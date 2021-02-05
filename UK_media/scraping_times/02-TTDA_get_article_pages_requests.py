# This file opens a csv file containing
# a link to front page of every article in the Times Digital Archive in a certain date range
# and finds a link to every article on that day.
# It then saves those links to a csv file, one for each day in the original csv file.


import time
import pandas as pd
from datetime import datetime, timedelta, date
import requests
from lxml import html 

def fetch_url_articles(url):

	numTries=1
	while True:
		numTries+=1
		try:
			response = requests.get(url)
			tree = html.fromstring(response.text)
			date_formatted = tree.xpath("//a[@title='Add to My Folder']")[0].attrib['data-pub-date-formatted']
			str_date = datetime.strptime(date_formatted, '%B %d, %Y').strftime('%Y-%m-%d')
			print('%s: fetched front page' % str_date)

			prefix_pages = 'http://gdc.galegroup.com/gdc/artemis/NewspapersDetailsPage/NavigationPortletWindow?action=f&id=loadPageArticles&cacheability=PAGE&p=TTDA&u=oxford&pageId='
			#prefix_articles = 'http://gdc.galegroup.com'
			urls_pages = [ prefix_pages + i.attrib['data-page_id'] for i in tree.xpath("//h3[@class='treeview-head']") ]
			print("%s: found %d pages" % (str_date,len(urls_pages)) )

			urls_articles = []
			page_numbers = []

			url_article_template = 'http://gdc.galegroup.com/gdc/artemis/NewspapersDetailsPage/NewspapersDetailsWindow?disableHighlighting=false&displayGroupName=DVI-Newspapers&docIndex=&source=Article&prodId=&mode=view&limiter=&display-query=&contentModules=&action=e&sortBy=&windowstate=normal&currPage=1&dviSelectedPage=&scanId=&query=&search_within_results=&p=TTDA&catId=&u=oxford&displayGroups=&documentId=GALE%{}&activityType=BrowseByDate&failOverType=&commentary='

			for page_num, url in enumerate(urls_pages):
				response = requests.get(url)
				tree = html.fromstring(response.text)
				for article in tree.xpath("//a[@class='newspaperArticles ellipsis ']"):
					article_code = article.attrib['href'].split('%')[-1]
					urls_articles += [ url_article_template.format(article_code) ]
					#urls_articles += [ prefix_articles + i.attrib['href'] for i in  ]
					page_numbers += [ page_num+1 ]

			break
		except:
			if numTries>3:
				print("Tried three times and failed to connect. Quiting.")
				txt = b''
				break
			else:
				print("Connection error, waiting 30 seconds to retry...")
				time.sleep(1)

	## save urls_articles
	outfile = 'data/unfiltered/%s.csv' % str_date
	with open(outfile,"w") as f:
		out_str = ''.join( '%s,%s,%d\n' % (str_date,url,n) for url,n in zip(urls_articles, page_numbers) )
		f.write(out_str)

	print("%s: saved all %d articles" % (str_date,len(urls_articles)) )

	time.sleep(3)
	return True


def fetch_all():
	infile = 'data/all_front_pages_wednesdays.csv'
	df = pd.read_csv(infile, names=['date','url_front_page'])

	for url in df.url_front_page.values:
		fetch_url_articles(url)

