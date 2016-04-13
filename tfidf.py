#!/usr/bin/env python

from __future__ import print_function

import sys
import codecs
from Queue import PriorityQueue

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
    no_punc = (lowered_tokens.encode('utf-8')
                             .translate(None, string.punctuation)
                             .decode('utf-8'))
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
# d['idf'][t] = idf score for token
# d['scores'][s]['tf'][t] = tf score
# d['scores'][s]['tf-idf'][t] = tf-idf score
def get_scores(article_name):
    stemmer = PorterStemmer()

    with codecs.open(article_name, encoding='utf-8') as f:
        sentences = nltk.sent_tokenize(f.read())

    tokenized_sentences = []    # article sentences
    info = {}
    info['scores'] = {}
    info['idf'] = {}

    scores = info['scores']
    idf = info['idf']

    for sentence in sentences:
        tokens = tokenize(sentence, stemmer)
        no_tokens = len(tokens)

        scores[sentence] = {'tf': {}, 'tf-idf': {}}

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
            if token not in idf:
                idf_val = math.log(float(no_sentences) /
                          no_appear(token, tokenized_sentences))
                idf[token] = idf_val
            else:
                idf_val = idf[token]

            #tf-idf
            scores[sentence]['tf-idf'][token] = tf_val * idf_val

    return info

def cosine_sim(v1, v2):
    dotproduct = sum(v1[t] * v2[t] for t in v1 if t in v2)
    v1_sqsum = sum(v1[t]**2 for t in v1)
    v2_sqsum = sum(v2[t]**2 for t in v2)
    mag = math.sqrt(v1_sqsum) * math.sqrt(v2_sqsum)
    if mag == 0:
        return 0
    return dotproduct / mag

# tfidf returns best_matches function, which returns sentence list
# article_name -> (string query, int nquestions) -> sentence list
def tfidf(article_name):
    stemmer = PorterStemmer()

    info = get_scores(article_name)

    # scores[sentence]['tf'/'tf-idf'][token] = tf/tf-idf score
    scores = info['scores']
    # idf[token] = tf-idf score
    idf = info['idf']

    # returns list of best matched sentences in article
    def best_matches(query, nquestions):
        bests = PriorityQueue()
        matches = []
        query_tfidf = {}

        # weird case where query is exactly a sentence in the article
        if query in scores:
            util.output("query '%s' is a sentence in the article" % query)
            return [query]

        query_tokens = tokenize(query, stemmer)

        for t in query_tokens:
            freq = query_tokens.count(t)
            q_tf = freq / float(len(query_tokens))
            if t in idf:
                query_tfidf[t] = q_tf * idf[t]

        for sentence in scores:
            s_tfidf = scores[sentence]['tf-idf']
            bests.put((cosine_sim(query_tfidf, s_tfidf), sentence))

            if bests.qsize() > nquestions:
                _ = bests.get()

        while bests.qsize() > 0:
            matches.append(bests.get()[1])

        return matches[::-1] 

    return best_matches

        
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: %s <article> <query> <number of best matches requested>' % sys.argv[0])
        sys.exit(1)

    article_name = sys.argv[1]
    query = sys.argv[2]
    nquestions = int(sys.argv[3])

    best_matches = tfidf(article_name)
    sentence_list = best_matches(query, nquestions)

    # print :D
    print("closest sentences to query: " + query)
    for sentence in sentence_list:
        print(sentence)
