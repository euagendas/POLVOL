
# coding: utf-8

# # 02-topic-modelling-spiegel
# 
# Calculate the topic distribution for every article in every week, over a range of years.
# So first I'll put all the documents together, then calculate the words-per-topic matrix, then run a long model, and finally produce the documents-per-topic matrix.

# In[5]:


import os
import string
import nltk
#nltk.download('stopwords')
#nltk.download('punkt')
import time

import pandas as pd
import numpy as np
from functools import reduce
from scipy.stats import entropy
from datetime import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("poster", font_scale=1.5, rc={"lines.linewidth": 2.5})
sns.mpl.rc("figure", figsize=(9,6))

import warnings; warnings.filterwarnings('ignore')


# In[6]:


def tokenize(text):
    stopwords = set(nltk.corpus.stopwords.words('german'))
    with open('data/german_stopwords.txt') as f:
        more_stopwords = [ line[:-1] for line in f ]
    stopwords = stopwords.union(set(more_stopwords))
    
    minlength = 3
    
    invalidChars = { '¡', '§', '©', '\xad', '°', '²', '³', 'µ', '¹', '¿', '×', '\u200b', 
                    '•', '‣', '…', '⁄', '₂', '€', '™', '▇', '■', '▶', '◆', '●', '★', '✽',
                    '❏', '➝', '主', '原', '年', '後', '歸', '物', '舧', '舰'}
    invalidChars = invalidChars.union(set(string.punctuation.replace("-", "–„“")))
    for token in nltk.word_tokenize(text):
        t = token.lower()
        if (len(t)<minlength) or (t in stopwords) or (t.replace('ß','ss') in stopwords)         or (t in string.punctuation) or (t[0] in string.punctuation)         or any(char in invalidChars for char in token):
            continue
        yield t
        
def normalise(vec):
    return vec / np.dot(vec,vec)

def combine_vectors(vectors):
    return normalise(np.sum(vectors, axis=0))

def important_words(vectorizer, vec, n):
    return sorted(zip(vectorizer.get_feature_names(), vec), key=lambda x:x[1], reverse=True)[:n]


# In[7]:


years = range(1947,2017)

infiles = [ 'data/%d.csv' % d for d in years ]

# create DataFrame for all articles
df = pd.DataFrame()

for infile in infiles:

    df_year = pd.read_csv(infile, index_col=0)
    df_year = df_year[pd.notnull(df_year['text'])]

    # uncomment for short run
    #df = df.head(50)
    
    df = df.append(df_year)


# In[8]:


len(df_year), len(df)


# ### Now let's estimate how long it's going to take.
# _________________________________
# 
# 25 topics (time in minutes)
# [
# [100, 0.24],
# [200, 0.42],
# [500, 0.66],
# [1000, 1.14],
# [2000, 2.10],
# [5000, 5.22]
# ]
# 
# Ok, from this I get that the time in minutes is:
# T = 0.1514 + 0.0010*n_documents
# 
# 
# - 10K documents               ->  10.15 minutes
# - 28178 (2009-2016) documents ->  28.32 minutes
# - 100K documents              ->  100.15 minutes (<2 hours)
# - 1M documents                ->  1000.15 minutes (~17 hours)
# _________________________________
# 
# 50 topics (time in minutes)
# [
# [100, 0.45],
# [200, 0.75],
# [500, 1.30],
# [1000, 2.23],
# [2000, 4.14],
# [5000, 9.77]
# ]
# Ok, from this I get that the time in minutes is:
# T = 0.33 + 0.00189*n_documents
# 
# - 10K documents               -> 19.23 minutes
# - 28178 (2009-2016) documents -> 53.59 minutes
# - 100K documents              -> 189.33 minutes (3 hours)
# - 1M documents                -> 1890.33 minutes (31.5 hours)
# _________________________________
# 
# 100 topics (time in minutes)
# [
# [100, 0.80],
# [200, 1.83],
# [500, 2.25],
# [1000, 4.51],
# [2000, 8.09],
# [5000, 18.97]
# ]
# 
# Ok, from this I get that the time in minutes is:
# T = 0.7077 + 0.003659*n_documents
# 
# - 10K documents               ->  37 minutes
# - 28178 (2009-2016) documents ->  103 minutes (< 2 hours)
# - 100K documents              ->  366.61 minutes (6 hours)
# - 1M documents                ->  3659.70 minutes (2.5 days)
# 
# _________________________________
# 
# On the number of tokens:
# 
# 28178 documents:
# - n_topics=50, min_df=0.010, max_df=0.8: 5866 different tokens, total 6847730
# - n_topics=50, min_df=0.005, max_df=0.8: 10757 different tokens, total 8015999
# - n_topics=50, min_df=0.001, max_df=0.8: 37335 different tokens, total 9960130
# 

# In[9]:


from sklearn.feature_extraction.text import CountVectorizer
start = time.time()

# list of text documents
text = df.text.values
doc_ids = df.filename.values

# create the transform
vectorizer = CountVectorizer(tokenizer=tokenize, min_df=0.005, max_df=0.8)

# tokenize and build vocab
vectorizer.fit(text)

# summarize
#print(vectorizer.vocabulary_)

# encode document-term matrix
dtm = vectorizer.transform(text)

# summarize encoded vector
print('Shape of document-term matrix (documents, tokens):', dtm.shape)
print('Total number of tokens:', dtm.sum() )
#print(type(dtm))
#print(dtm.toarray())

end = time.time()
print((end - start)/60.0,'minutes')


# In[10]:


# summarize encoded vector
print('Shape of document-term matrix (documents, tokens):', dtm.shape)
print('Total number of tokens:', dtm.sum() )
#print(type(dtm))
#print(dtm.toarray())

end = time.time()
print(round((end - start)/60.0,2),'minutes')

from scipy.sparse import save_npz
save_npz('data/dtm_matrix.npz', dtm)


# In[11]:


from scipy.sparse import load_npz
dtm = load_npz('data/dtm_matrix.npz')

dtm


# In[12]:


nnz_per_row = dtm.getnnz(axis=1)
non_null_rows = np.where(nnz_per_row > 0)[0]
null_rows     = np.where(nnz_per_row <= 0)[0]

dtm = dtm[dtm.getnnz(1)>0]
dtm


# In[ ]:


import lda

#n_topics = 30
#n_topics = 50
#n_topics = 70

n_topics = 15

topic_model = lda.LDA(n_topics=n_topics, n_iter=1500, random_state=1)


# In[ ]:


start = time.time()

document_topic_distributions = topic_model.fit_transform(dtm)

end = time.time()
print((end - start)/60.0,'minutes')


# In[ ]:


vocab = vectorizer.get_feature_names()
topic_names = ['Topic %d'%k for k in range(1, n_topics + 1)]

topic_word_distributions = pd.DataFrame(topic_model.components_, columns=vocab, index=topic_names)

document_topic_distributions = pd.DataFrame(document_topic_distributions,
                                            columns=topic_names,
                                            index=doc_ids[non_null_rows])


# In[ ]:


document_topic_distributions.to_csv('data/document_topic_distributions_'+str(n_topics)+'topics.csv')
topic_word_distributions.to_csv('data/topic_word_distributions_'+str(n_topics)+'topics.csv')


# In[ ]:


topic_word_distributions.loc['Topic 2'].sort_values(ascending=False).head(15)


# In[ ]:


document_topic_distributions.head()


# In[ ]:


topic_word_distributions.head()

