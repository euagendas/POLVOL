# Scraping Der Spiegel archive data

All past editions of Der Spiegel are available from [their website](https://www.spiegel.de/spiegel/print/index-2021.html).

To aquire the data, 
1. First run `index_crawler.py` in order to get the list of articles in each week's edition. This will generate one file per edition on your harddisk. 
2. Then run `article_crawler.py` to get the full HTML pages of each article and save these on your harddisk
3. Finally, run `article_extract.py` to extract the text from the HTML pages and create CSV files for each year (e.g., 1984.csv). 

These CSV files produced in step 3 are the input data for the anlaysis code in the parent directory. 
