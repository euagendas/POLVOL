import glob
import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import json

#RE_ART=re.compile(r'<div class="dig-artikel"
#<span class="dig-oberzeile dig-h">
#<span class="dig-ueberschrift dig-h">
#<div class="dig-text" data-field="text"> 
#dig-vorspann lead
#dig-oberzeile section
#dig-ueberschrift headline


RE_FILENAME=re.compile("data/([0-9]{4})/([0-9]{1,2})/(.*?)\.html")

with open("dictionary.json","r") as f:
	DICT=json.load(f)

DICT_RE={}
for cat in DICT:
	DICT_RE[cat]=[]
	for word in DICT[cat]:
		DICT_RE[cat].append(re.compile(r"\b{}\b".format(word)))

CATS=list(DICT.keys())
policy_counts=[]
for y_entry in os.scandir("data/"):
	if not y_entry.is_dir():
		continue
	year=y_entry.name
	print(year)
	#if year!="2016":
	#	continue
	articles=[]
	for w_entry in os.scandir("data/{}/".format(year)):
		if not w_entry.is_dir():
			continue
		week=w_entry.name
		
		week_article_count=0
		counts=[0]*len(CATS)
		for file in glob.glob("data/{}/{}/*.html".format(year,week)):
			tmp=RE_FILENAME.match(file)
			#year=tmp.group(1)
			#week=tmp.group(2)
			filename=tmp.group(3)
	
			with open(file,"r") as fh:
				soup = BeautifulSoup(fh, 'html.parser')
		
			#print(file)
			#print(soup)
			article=soup.find("div",{"class":"dig-artikel"})
			if article==None:
				print("No article in {}".format(file))
				continue

			#print(article)
			text=article.find("div",{"data-field":"text"}).get_text().strip()
		
			#Policy counts
			week_article_count+=1
			for i in range(0,len(CATS)):
				cat=CATS[i]
				for word in DICT_RE[cat]:
					if word.search(text)!=None:
						counts[i]+=1
						break #Go to next
			
			lead=article.find("div",{"class":"dig-vorspann"})
			if lead!=None:
				lead=lead.get_text().strip()
			section=article.find("span",{"class":"dig-oberzeile"}).get_text().strip()
			headline=article.find("span",{"class":"dig-ueberschrift"}).get_text().strip()

			script = soup.find('script', text=re.compile('dateCreated'))
			jsondata = json.loads(script.get_text().strip())
			datecreated = jsondata['dateCreated']
		
			articles.append([year,week,datecreated,section,headline,lead,text,filename])
			
		#Completed the week. Store counts in policy_counts array
		policy_counts.append([year,week,week_article_count]+counts)
		print("Finished",year,"week",week)
        #Completed the year, make a data.frame of all articles in the year and save to a csv
	df=pd.DataFrame(articles, columns=["year","week","datecreated","section","headline","lead","text","filename"])
	df.to_csv("data/{}.csv".format(year))

#Completed all years. Write policy counts data.frame to CSV
df=pd.DataFrame(policy_counts, columns=["year","week","article_count"]+CATS)
df.to_csv("data/policy_counts.csv")
		

