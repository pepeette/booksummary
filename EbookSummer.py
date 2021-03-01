#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#pip install EbookLib


# In[1]:


import ebooklib
from ebooklib import epub
import bs4
import streamlit as st
import os


# ## coding the app

# In[ ]:


# Add a title
st.title('Ebook summary')
# Add some text
st.text('upload your book in .epub format')


# In[1]:


# allow user input
uploaded_file = st.file_uploader("Upload Files",type=['epub'])
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    st.write(file_details)


# # SUMMARIZING THE WHOLE BOOK

# ## 1- TRansforming the epub into text



# In[ ]:


# Seeing the chapters
# agenda = []
# livre = epub.read_epub(uploaded_file)
# for item in livre.get_items():
#     if item.get_type() == ebooklib.ITEM_NAVIGATION:
#             #print('----------------------------------')
#         agenda.append(item.get_content())
#             #print('==================================')
        


# In[249]:

livre = epub.read_epub(uploaded_file)
def epub2thtml(epub_path):
    livre = epub.read_epub(uploaded_file)
    
    chapters = []

    for item in livre.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            #print('----------------------------------')
            chapters.append(item.get_body_content())
            #print('==================================')
    return chapters

#need to store the below data get_content in a table (chapter as index and text for content to work on)
#then we need to look for each :  h2 class="chn1_chapter_number_" for index // h3 class="ha1_head_var_1o" for text
#maybe with beautifulsoup


# In[250]:


from bs4 import BeautifulSoup as soup
blacklist = ['[document]','noscript','header','html','meta','head', 'input','script',
# there may be more elements you don't want, such as "style", etc.
]

def chap2text(chap):
    output = ''
    souper = soup(chap, 'html.parser')
    text = souper.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output


# In[251]:


def thtml2ttext(thtml):
    Output = []
    for html in thtml:
        text =  chap2text(html)
        Output.append(text)
    return Output


# In[252]:


def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    ttext = thtml2ttext(chapters)
    return ttext


# In[253]:


text = epub2text(livre)


# In[255]:


print(type(text))


# ## Now, we can apply the text PREPROCESSING

# In[256]:

import re

# Removing Square Brackets and Extra Spaces
t = [re.sub(r'\[[0-9]*\]', ' ', i) for i in text]
t = [re.sub(r'\s+', ' ', i) for i in t]


# In[257]:


# Removing special characters and digits
t1 = [re.sub(r'[^a-zA-Z]', ' ', i) for i in t]
t1 = [re.sub(r'\s+', ' ', i) for i in t1]


# In[258]:


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


# In[259]:


# tokenizing 
sentence_list = [sent_tokenize(i) for i in t]
sentence_list[3]


# In[260]:


# find frequecy of occurrence

stopWords = set(stopwords.words("english"))

word_frequencies = {}
for chapter in t1:
    for word in word_tokenize(chapter):
        if word not in stopWords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1


# In[261]:


# second we calculate the weighted frequency

maximum_frequency = max(word_frequencies.values())

for word in word_frequencies.keys():
    word_frequencies[word] = (word_frequencies[word]/maximum_frequency)


# In[262]:


# third we expand this weighted F to the sentences to score them

sentence_scores = {}
for chapter in sentence_list[1:]:
    for sent in chapter:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 100:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]


# ## HERE IS THE SUMMARY

# In[ ]:


# # first choose the length of your summary for the app (streamlit)
# x = st.slider('Select a length')
# st.write(x, 'squared is', x * x)


# In[263]:


# retrieving the TOP 200 sentences 

import heapq
summary_sentences = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)

summary = ' '.join(summary_sentences)
print(summary)


# In[ ]:


# display text on app
st.write(summary)


# In[ ]:





# In[ ]:




