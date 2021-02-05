# updating index_crawler

import urllib.request
from urllib.error import HTTPError
import time
import re
import datetime

HTTP_HEADERS={
'User-Agent': 'Mozilla/5.0 Firefox/34.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

URL="http://www.spiegel.de/spiegel/print/index-{}.html"

n_volumes = []
for year in range(1947,2009):

	url = URL.format(str(year))
	req=urllib.request.Request(url,None,HTTP_HEADERS)
	resp=urllib.request.urlopen(req)
	txt=str(resp.read())
	resp.close()

	idx = txt.find('index-'+str(year)+'-')
	nvol = txt[idx+11:idx+13]
	n_volumes += [ nvol ]

	#print(resp.status, "on year", year)
	s = '\"'+str(year)+'\":'+nvol
	print(s)

