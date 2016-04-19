#!/usr/bin/env python
import time

import settings

import nltk
from nltk.parse import stanford
from pattern.en import conjugate
import grammar_util    

import normalize
import io
import codecs
import math
parser = stanford.StanfordParser(encoding="utf-8")
BINARY = normalize.BINARY
FACTOID = normalize.FACTOID
#NOSUBJECT = 'f-NOSUBJECT'
UNKNOWN = normalize.UNKNOWN
total_time = 300.00
D = {}
D_parse = {}

def deep_copy(tree):
    return tree.fromstring(str(tree))

def raw_parse_sents(sentences):
    result = []
    for s in sentences:
        if s in D_parse: 
	    result += [nltk.tree.Tree.fromstring(D_parse[s])]
        else:
	    query_tree = parser.raw_parse(s).next()
	    D_parse[s] = str(query_tree)
	    result += [query_tree]
    return result
    

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
    if (t1.label()[0] != t2.label()[0] and not p(t1)) or t1.label().startswith("S|<VP-"): return 0 
    t1_c = deconjugate_leaves_memo(t1)
    st1 = set(map(lambda x: str.lower(str(x)) if not x.label().startswith(".") else "", t1_c.subtrees()))
    st2 = set(map(lambda x: str.lower(str(x)), t2.subtrees()))
    base = 0
    if "(VB be)" in st2:
        base = 1 if len(filter(lambda x: x.startswith("(NP|<,-NP"), list(st1))) > 0 else 0
#    print (t1, st1 & st2)
    return float(len(st1 & st2)+base)/float(len(st2)+float(len(st1-st2))/10)

def score(query, p):
    return (lambda t: tree_edit_distance(t,query, p))

def pairmax(L, f):
    max_val, max_index = -float("inf"), None
    max_comma_val, max_comma_index = -float("inf"), None
    for i in L:
        val = f(i)
#        if val > 0.0: print (i, val)
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


def generate_query(text):
    query_tree = parser.raw_parse(text).next()
    query_tree.chomsky_normal_form()
    deconjugate_leaves(query_tree)
    query_tree = query_tree[0]
    #query_tree.pretty_print()
    return query_tree


def filter_sbar_one(tree):
#    print tree
    if tree.height()<3: return [tree]
    if "SBAR" in tree.label():
        result = [None]
    else: result = []
    if len(tree)>1:
        LL = filter_sbar_one(tree[0])
        LR = filter_sbar_one(tree[1])
        for (nodeL, nodeR) in [(x,y) for x in LL for y in LR]:
	    T = deep_copy(tree)
	    if nodeL and nodeR: 
	        T[0]=nodeL
	        T[1]=nodeR
	        result += [T]
	    elif nodeL:
	        T[0]=nodeL
	        T.pop()
	        result += [T]
	    elif nodeR:
	        T[0]=nodeR
		T.pop()
	        result += [T]
	return result
    else:
        L = filter_sbar_one(tree[0])
        for node in L:
	    T = deep_copy(tree)
	    if node: 
	        T[0]=node
	    else:
	        T.pop()
	    result += [T]
	return result
        

    
def filter_sbar(trees):
    result = []
    for t in trees:
        result += filter_sbar_one(t)
    return result

def select_answer(sentences, query, start_time):
#    print sentences
    time_left = total_time - (time.time()-start_time)
    if time_left < 10.0:
        return sentences[0] 
    parses = list(map(lambda x: x, raw_parse_sents(sentences)))

    (q_type, queries) = query
    if not normalize.is_success_type(q_type):
        return sentences[0]
#    if q_type == boolean:
#        (pos, neg) = query
    for i in parses:
        i.chomsky_normal_form()
    parses = filter_sbar(parses)       
    query_trees = map(generate_query, queries)
    
    m = -float("inf")
    val = None
    for q in query_trees:
#        q.pretty_print()
        for i in parses:
            time_left = total_time - (time.time()-start_time)
            if time_left < 5.0:
	        return sentences[0] 
            i.chomsky_normal_form()
#            i.pretty_print()
            (p,v) = match_tree(i,q)
#            print v 
            if v > m:
	        val = p
	        m = v
    return grammar_util.as_string(val)
    
    
