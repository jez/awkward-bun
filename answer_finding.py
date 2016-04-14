#!/usr/bin/env python

import settings

import nltk
from nltk.parse import stanford
from nltk.stem.porter import PorterStemmer
import grammar_util    

import io
import codecs
import math
parser = stanford.StanfordParser(encoding="utf-8")

def tree_edit_distance(t1, t2, p):

    if t1 == t2: return 1
    if t1.label()[0] != t2.label()[0] and not p(t1): return 0 
    st1 = set(map(lambda x: str(x), t1.subtrees()))
    st2 = set(map(lambda x: str(x), t2.subtrees()))
    return float(len(st1 & st2))/float(len(st2))

def score(query, p):
    return (lambda t: tree_edit_distance(t,query, p))

def pairmax(L, f):
    max_val, max_index = -float("inf"), None
    for i in L:
        val = f(i)
#	print (i, f(i))
        if val >= max_val:
            max_val = val
            max_index = i
    return (max_index, max_val)

def match_tree(tree, query):
#    tree.pretty_print()
#    query.pretty_print()
    return pairmax(tree.subtrees(), score(query, lambda x: x.label()[0]=='N'))


def select_answer(sentences, query):
#    print sentences
    stemmer = PorterStemmer()
    query,q_type = query
#    query.pretty_print()
#    query = grammar_util.as_string(query)
    parses = list(map(lambda x: x.next(), parser.raw_parse_sents(sentences)))
#    query_tree = parser.raw_parse(query).next()
#    query_tree.chomsky_normal_form()
#    query_tree.pretty_print()
    query_tree = query[0]
#    query_tree.pretty_print()
    m = -float("inf")
    val = None
    for i in parses:
        i.chomsky_normal_form()
        (p,v) = match_tree(i,query_tree)
	if v > m:
	     val = p
	     m = v
    return val
    
    
