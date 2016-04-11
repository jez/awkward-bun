#!/usr/bin/env python

from __future__ import print_function

import sys
import codecs

import settings as s

import grammar_util as g
import util
import string
import math

import nltk
from nltk.corpus import stopwords
from nltk.tree import Tree
from nltk.stem.porter import *
from nltk.parse import stanford


# will stem and tokenize all words in sentence
def tokenize(sentence, stemmer):

    # all lowercase
    lowered_tokens = sentence.lower()

    # remove punctuation
    no_punc = lowered_tokens.encode('utf-8').translate(None, string.punctuation)
    tokenized = nltk.word_tokenize(no_punc)

    # remove stopwords
    no_stops = [t for t in tokenized if t not in stopwords.words('english')]

    # stem words
    stemmed = []
    for t in no_stops:
        stemmed.append(stemmer.stem(t))

    return stemmed

# gives number of documents that contain a given token
def no_appear(token, tokenized_docs):  
    no = 0
    for d in tokenized_docs:
        if token in d:
            no += 1
    return no + 1 # smoothing to avoid division by 0


# Returns a dictionary d.
# For sentence s in article and token t in sentence,
# d[s]['tf'][t] = tf score
# d[s]['idf'][t] = idf score
# d[s]['tf-idf'][t] = tf-idf score
def tfidf(article_name):
    stemmer = PorterStemmer()

    with codecs.open(article_name, encoding='utf-8') as f:
        sentences = nltk.sent_tokenize(f.read())

    tokenized_sentences = []

    scores = {}

    for sentence in sentences:
        tokens = tokenize(sentence, stemmer)
        no_tokens = len(tokens)

        scores[sentence] = {'tf': {}, 'idf': {}, 'tf-idf': {}}
         
        #tf
        for t in tokens:
            freq = tokens.count(t)
            scores[sentence]['tf'][t] = freq / float(no_tokens)
        
        tokenized_sentences.append(tokens)

    no_sentences = len(sentences)

    for sentence in sentences:
        for token in scores[sentence]['tf']:
            tf_val = scores[sentence]['tf'][token]

            # idf
            idf_val = math.log(float(no_sentences) / 
                      no_appear(token, tokenized_sentences))
            scores[sentence]['idf'][token] = idf_val

            #tf-idf
            scores[sentence]['tf-idf'][token] = tf_val * idf_val
            
    # print :D
    #for sentence in scores:
    #    print("\ntf-idf for sentence: " + sentence)
    #    for token in scores[sentence]['tf-idf']:
    #        print(token + ": " + str(scores[sentence]['tf-idf'][token]))
    #    print

    return scores

        
        
#if __name__ == '__main__':
#    if len(sys.argv) != 2:
#        print('usage: %s <article>' % sys.argv[0])
#        sys.exit(1)
#
#    article_name = sys.argv[1]
#
#    tfidf(article_name)
