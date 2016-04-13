#!/usr/bin/env python

import settings

import nltk
from nltk.parse import stanford

import io
import codecs
import math
parser = stanford.StanfordParser()

def tree_edit_distance(t1, t2, p):

    if t1 == t2: return 1
    if t1.label()[0] != t2.label()[0] and not p(t1): return 0 
    st1 = set(map(lambda x: str(x), t1.subtrees()))
    st2 = set(map(lambda x: str(x), t2.subtrees()))
#   st1 = set(map(lambda x: str(x.label())+str(x.leaves()) if len(x.leaves())==1 else str(x.label())+str(x.height()), t1.subtrees()))
#    st2 = set(map(lambda x: str(x.label())+str(x.leaves()) if len(x.leaves())==1 else str(x.label())+str(x.height()), t2.subtrees()))
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
    return pairmax(tree.subtrees(), score(query, lambda x: x.label()[0]=='N'))


def select_answer(sentences, query):
    parses = list(map(lambda x: x.next(), parser.raw_parse_sents(sentences)))
    query_tree = parser.raw_parse(query).next()
    query_tree.chomsky_normal_form()
    query_tree = query_tree[0]
    m = -float("inf")
    val = None
    for i in parses:
        i.chomsky_normal_form()
        (p,v) = match_tree(i,query_tree)
	if v > m:
	     val = p
	     m = v
    return val
    
    
