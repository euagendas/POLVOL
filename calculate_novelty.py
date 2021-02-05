#!/usr/bin/env python

import numpy as np
import pandas as pd
from itertools import *

import os
import time
import sys

# Novelty measures

from numpy.linalg import norm
from scipy.stats import entropy
from scipy.spatial.distance import hamming
from scipy.spatial.distance import euclidean
from sklearn.metrics import mutual_info_score
from scipy.stats import entropy
entropy_fix = np.log2(np.e)


def rel_entr(P, Q):                
    return entropy(P,Q)*entropy_fix

def novelty(p,q, metric='KL'):
    if metric=='KL':
        return rel_entr(p,q)
    else:
        return 0

# Read topics
def read_topics(n_topics, data_folder='spiegel/data/'):

    infile1 = data_folder+'topic_word_distributions_'+str(n_topics)+'topics.csv'
    infile2 = data_folder+'document_topic_distributions_'+str(n_topics)+'topics.csv'
    readingfile = data_folder+'reading_topics.tmp'

    while os.path.isfile(readingfile):
        print('Waiting for '+readingfile)
        time.sleep(2)

    # once it disappears, create it and start reading
    os.mknod(readingfile)
    print('Reading topics now')
    words_per_topic     = pd.read_csv(infile1, index_col=0)
    topics_per_document = pd.read_csv(infile2, index_col=0)
    os.remove(readingfile)
    print('Finished reading topics')

    return words_per_topic, topics_per_document


def read_df_alldocs(data_folder='spiegel/data/'):
    years = range(1947,2017)

    infiles = [ data_folder+'%d.csv' % d for d in years ]
    readingfile = data_folder+'reading_years.tmp'

    # create DataFrame for all articles
    df_alldocs = pd.DataFrame()

    while os.path.isfile(readingfile):
        print('Waiting for '+readingfile)
        time.sleep(2)

    # once it disappears, create it and start reading
    os.mknod(readingfile)
    print('Reading years now')

    for infile in infiles:
        print(infile)
        df_year = pd.read_csv(infile, index_col=0)
        df_year = df_year[pd.notnull(df_year['text'])]
        del df_year['text']
        
        # uncomment for short run
        #df = df.head(50)
        
        df_alldocs = df_alldocs.append(df_year)

    os.remove(readingfile)
    print('Finished reading years')

    return df_alldocs

def measure_KL(df_alldocs, novelty_years, week_range, words_per_topic, topics_per_document, n_topics, data_folder='spiegel/data/'):
# Compare all weeks from all years to the 10 weeks before that.

    df = df_alldocs
    week_gap=4

    for week_idx in week_range:
        print(week_idx)
        for year in novelty_years:

            filenames_this_week  = df[ (df.year==year) & (df.week==week_idx) ].filename.values
            filenames_past       = df[ (df.year==year) & (df.week<week_idx) & (df.week>=(week_idx-week_gap)) ].filename.values
            novelty_weeks = []

            print("Measuring KL for year %d, week %d, week gap %d" % (year, week_idx, week_gap) )
            print('len(filenames_this_week)*len(filenames_past) = %d' % (len(filenames_this_week)*len(filenames_past)) )
            for fi,fj in product(filenames_this_week,filenames_past):
                try:
                    dfi = topics_per_document.loc[fi]
                    if type(dfi) == pd.core.frame.DataFrame:
                        #print('Document ID clash:')
                        #print(df[df.filename==fi])
                        dfi = dfi.iloc[0]

                    dfj = topics_per_document.loc[fj]
                    if type(dfj) == pd.core.frame.DataFrame:
                        #print('Document ID clash:')
                        #print(df[df.filename==fj])
                        dfj = dfj.iloc[0]

                    KL     = novelty(dfi, dfj)
                    #jensen = novelty(dfi, dfj, metric='JSD')
                    #bhatta = novelty(dfi, dfj, metric='BCD')
                    #mutual = novelty(dfi, dfj, metric='MI')/novelty(dfj, dfj, metric='MI')

                    #novelty_weeks += [(week, year, fi, fj, KL, jensen, bhatta, mutual)]
                    novelty_weeks += [(week_idx, year, fi, fj, KL)]
                    if len(novelty_weeks) % 1000 == 0:
                        print(len(novelty_weeks))

                except TypeError:
                    #crashed += [ (fi, fj) ]
                    print('Crashed:',fi,fj)

                except KeyError:
                    print("Document %s or %s has invalid text" % (fi, fj))
                    pass

            df_novelty_weeks = pd.DataFrame(novelty_weeks, columns=['week', 'year', 'filename1', 'filename0', 'KL'])
                                                                        #'jensen', 'bhatta', 'mutual'])

            outfile = data_folder+'df_novelty_%d_week%d_%d.csv' % (n_topics,week_idx, year)
            df_novelty_weeks.to_csv(outfile)
            print('Saving',outfile)



def main():

    if len(sys.argv) == 6:
        year0 = int(sys.argv[1])
        year1 = int(sys.argv[2])
        week0 = int(sys.argv[3])
        week1 = int(sys.argv[4])
        n_topics = int(sys.argv[5])

        novelty_years = range(year0, year1)
        week_range    = range(week0, week1)

        # see if I can start reading
        from itertools import product

        all_weeks  = [ (year, week) for week,year in product(range(5,50), range(1947,2017)) ]

        prev_weeks = all_weeks[ :all_weeks.index( (year0,week0) ) ]

        reading_files = [ 'novG.py_%d_%d_hasnt_read2' % yearweek for yearweek in prev_weeks ]

        while True:
            can_read = True
            for reading_file in reading_files:
                if os.path.isfile(reading_file):
                    can_read = False
                    print('Stopping because %s' % reading_file)
                    break

            if can_read:
                print("I can now read")
                break
            else:
                time.sleep(10)

        words_per_topic, topics_per_document = read_topics(n_topics)
        df_alldocs = read_df_alldocs()

        my_reading_file = 'novG.py_%d_%d_hasnt_read2' % (year0, week0)
        if os.path.isfile(my_reading_file):
            os.remove(my_reading_file)
        print('Finished reading, now removing %s' % my_reading_file)

        measure_KL(df_alldocs, novelty_years, week_range,
                   words_per_topic, topics_per_document, n_topics)


if __name__ == "__main__":
    main()



