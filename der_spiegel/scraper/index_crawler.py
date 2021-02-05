
YEARS={
	"1947":51, 	"1948":52,	"1949":53,	"1950":52,	"1951":52,
	"1952":52,	"1953":52,	"1954":52,	"1955":53,	"1956":52,
	"1957":52,	"1958":52,	"1959":52,	"1960":52,	"1961":53,
	"1962":52,	"1963":52,	"1964":52,	"1965":53,	"1966":53,
	"1967":53,	"1968":52,	"1969":53,	"1970":53,	"1971":53,
	"1972":53,	"1973":53,	"1974":53,	"1975":53,	"1976":53,
	"1977":53,	"1978":52,	"1979":53,	"1980":53,	"1981":53,
	"1982":52,	"1983":52,	"1984":52,	"1985":52,	"1986":52,
	"1987":53,	"1988":52,	"1989":52,	"1990":52,	"1991":52,
	"1992":53,	"1993":52,	"1994":52,	"1995":52,	"1996":52,
	"1997":52,	"1998":53,	"1999":52,	"2000":52,	"2001":52,
	"2002":52,	"2003":52,	"2004":53,	"2005":52,	"2006":52,
	"2007":52,	"2008":52,	"2009":52,	"2010":52,	"2011":52,
	"2012":52,	"2013":52,	"2014":52,	"2015":53,	"2016":50
}


import urllib.request
from urllib.error import HTTPError
import time
import re
import datetime

HTTP_HEADERS={
'User-Agent': 'Mozilla/5.0 Firefox/34.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

URL="http://www.spiegel.de/spiegel/print/index-{}-{}.html"


def fetch(url,filename):
	try:
		fh=open("data/{0}".format(filename),"rb")
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
			except:
				if numTries>3:
					filename=url[url.rfind("/")+1:]
					print("Tried three times and failed to connect. Quiting file %s." % filename)
					txt = b''
					break
					#quit()
				else:
					print("Connection error, waiting 30 seconds to retry...")
					time.sleep(30)
				
		fh=open("data/{0}".format(filename),"wb")
		fh.write(txt)
		fh.close()
		return True


for year in YEARS:
	print(year)
	month=0
	while month<YEARS[year]:
		month+=1
		url=URL.format(year,month)
		filename=url[url.rfind("/")+1:]
		if fetch(url,filename):
			time.sleep(5)
		print("  ",year,month)
		
		
		
