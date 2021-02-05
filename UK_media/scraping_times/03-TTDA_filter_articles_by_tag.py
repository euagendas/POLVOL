import os 
import sys
import glob
import pandas as pd
import requests
import re
import time

RE_SECTION=re.compile("<div class=\"category\">Publication Section: (.*?)</div>")

def get_section(url):

	#t0 = time.time()

	session = requests.Session()
	session.headers.update({
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
			})

	numTries = 0
	while True:
		try:
			req = requests.Request('GET', url)
			prepped = req.prepare()
			resp=session.send(prepped)
			payload=resp.text
			#time.sleep(1)
			#t1 = time.time()
			#print( str(t1-t0)+',' )
	
			tags = RE_SECTION.findall(payload)
			return tags[0]

		except:
			numTries += 1
			if numTries>3:
				print("Tried three times and failed to connect. Quiting.")
				return 'None'
			else:
				print("Connection error, waiting 30 seconds to retry...")
				time.sleep(30)
	return 'None'
	

def fetch_year_range(y0,y1):
	for year in range(y1, y0-1, -1):
		for infile in sorted(glob.glob('data/unfiltered/%s*' % year), reverse=True):
			filename = infile.split('/')[2][:-4]
			outfile  = 'data/filtered/%s.csv' % filename

			if os.path.isfile(outfile):
				print('%s already exists' % outfile)
			else:
				print('Running %s.csv' % filename)
				df = pd.read_csv(infile, names=['date','url_article','page'])
				df['section'] = df.url_article.apply(get_section)
				df.to_csv(outfile, index=False, header=False )


if len(sys.argv) == 3:
	y0 = int(sys.argv[1])
	y1 = int(sys.argv[2])
	fetch_year_range(y0,y1)
