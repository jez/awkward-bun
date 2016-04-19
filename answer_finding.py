#!/usr/bin/env python

import settings

import nltk
from nltk.parse import stanford
from pattern.en import conjugate
import grammar_util    

import io
import codecs
import math
parser = stanford.StanfordParser(encoding="utf-8")

D = {}

def deconjugate_leaves(T):
    if T.height()==1: return
    if T.height()==2:
        if T.label()[0] == "V":
            T.set_label("VB")
            T[0] = conjugate(T[0], "VB")
    else:
        for i in T:
	    deconjugate_leaves(i)

def deconjugate_leaves_memo(T):
    s = str(T)
    if s in D: return D[s]
    t_c = T.fromstring(s)
    deconjugate_leaves(t_c)
    D[s] = t_c
    return t_c

def tree_edit_distance(t1, t2, p):
    if t1 == t2: return 1
    if t1.label()[0] != t2.label()[0] and not p(t1): return 0 
    t1_c = deconjugate_leaves_memo(t1)
    st1 = set(map(lambda x: str(x), t1_c.subtrees()))
    st2 = set(map(lambda x: str(x), t2.subtrees()))
    base = 0
    if "(VB be)" in st2:
        base = 1 if len(filter(lambda x: x.startswith("(NP|<,-NP"), list(st1))) > 0 else 0
	
    return float(len(st1 & st2)+base)/float(len(st2))

def score(query, p):
    return (lambda t: tree_edit_distance(t,query, p))

def pairmax(L, f):
    max_val, max_index = -float("inf"), None
    max_comma_val, max_comma_index = -float("inf"), None
    for i in L:
        val = f(i)
        if val >= max_val:
            if i.height()>2 and len(i)>1 and i[1].label().startswith("NP|<,-NP"):
	        max_comma_val = val
		max_comma_index = i
	    max_val = val
            max_index = i
    if max_comma_val == max_val:
        return (max_comma_index[0], max_comma_val)
    return (max_index, max_val)

def match_tree(tree, query):
#    tree.pretty_print()
#    query.pretty_print()
    return pairmax(tree.subtrees(), score(query, lambda x: x.label()[0]=='N'))


def select_answer(sentences, query):
#    print sentences
    query,q_type = query
    if q_type == unknown:
        return sentences[0]
    parses = list(map(lambda x: x.next(), parser.raw_parse_sents(sentences)))


    query_tree = parser.raw_parse(query).next()
    query_tree.chomsky_normal_form()
    deconjugate_leaves(query_tree)
    query_tree = query_tree[0]
#    query_tree.pretty_print()


    m = -float("inf")
    val = None
    for i in parses:
#        print i
        i.chomsky_normal_form()
        (p,v) = match_tree(i,query_tree)
	if v > m:
	     val = p
	     m = v
    if val.label()=="NP|<,NP,>": print "commas"
    return val
    
    
