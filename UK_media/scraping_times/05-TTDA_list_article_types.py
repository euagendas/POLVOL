import os
import glob
import pandas as pd
import datetime

outfile = 'data/all_article_types.csv'
with open(outfile,'w') as f:
	f.write('filename,type_article\n')

	for infile in sorted(glob.glob('data/filtered/*csv')):
		pairs = ''

		str_date = infile.split('/')[2][:-4]
		download_dir = os.getcwd()+'/data/OCRtext/'+str_date+'/'
		print('Finding article labels from %s' % str_date)

		df = pd.read_csv(infile, names=['date','url_article','page','type_article'])

		for index, row in df.iterrows():
			type_article = row.type_article

			downloaded_files = glob.glob(download_dir+ str(index).zfill(3) + '*')
			if downloaded_files:
				filename = downloaded_files[0].split('OCRtext')[-1][1:]
				pairs += filename+','+type_article+'\n'

		f.write(pairs)
