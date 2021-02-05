import urllib.request
from urllib.error import HTTPError
import time
import re
import datetime
import glob
import os

HTTP_HEADERS={
'User-Agent': 'Mozilla/5.0 Firefox/34.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

#BLACKLIST=["http://www.spiegel.de/spiegel/print/d-128476281.html"]

RE_FILENAME=re.compile(r"data/index-([0-9]{4})-([0-9]{1,2}).html")
RE_LINKS=re.compile(r'<div class="epub-article">.*?<a target="_blank" href="(.*?)">',re.DOTALL|re.MULTILINE)
BASE_URL="http://www.spiegel.de/spiegel/print/{}"

SKIPPED_URLS=[]

def fetch(url,year,month):
	filename=url[url.rfind("/")+1:]
	filename="data/{}/{}/{}".format(year,month,filename)
	try:
		fh=open(filename,"rb")
		txt=fh.read()
		fh.close()
		return False
	except:	

		numTries=1
		while True:
			numTries+=1
			try:
				req=urllib.request.Request(url,None,HTTP_HEADERS)
				resp=urllib.request.urlopen(req)
				txt=resp.read()
				resp.close()
				break
			except Exception as e:
				print(str(e))
				if numTries>3:
					print(url,year,month)
					print("Tried three times and failed to connect.")
					if isinstance(e,urllib.error.HTTPError) and e.code==404:
						SKIPPED_URLS.append(url)
						return True
					quit()
				else:
					print(url,year,month)
					print("Connection error, waiting 30 seconds to retry...")
					time.sleep(30)
				
		fh=open(filename,"wb")
		fh.write(txt)
		fh.close()
		return True

for file in glob.glob("data/*.html"):
	tmp=RE_FILENAME.match(file)
	year=tmp.group(1)
	month=tmp.group(2)
	try:
		os.mkdir("data/{}".format(year))
	except:
		pass
	try:
		os.mkdir("data/{}/{}".format(year,month))
	except:
		pass
	print(year,month)
	with open(file,"r") as fh:
		html=fh.read()
		links=RE_LINKS.findall(html)
		for link in links:
			url=BASE_URL.format(link)
			#if url in BLACKLIST:
			#	continue
			if fetch(url,year,month):
				time.sleep(5)

with open("404_urls.txt","w") as f:
	for u in SKIPPED_URLS:
		f.write(u)
		f.write("\n")

