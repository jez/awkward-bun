#!/usr/bin/env python

#
# This file is just a playground for some code that uses the Stanford Parser
# and NLTK. It's not finished.
#
# If you've run through the setup correctly, you should be able to run
#
#     ./foo.py
#
# and see some simple predicate sentence trees.
#

from __future__ import print_function

import settings

import nltk
from nltk.parse import stanford

import io
import codecs


# pattern.en y u no python3 :<
#with open('./data/set1/a1.txt') as f:
#    sentences = nltk.sent_tokenize(f.read())
with codecs.open('./data/set1/a1.txt', encoding='utf-8') as f:
    sentences = nltk.sent_tokenize(f.read())

#print('\n'.join(sentences[:10]))
# TODO: restrict length of sentences and number of sentences to meet time bounds

parser = stanford.StanfordParser()
parses = parser.raw_parse_sents(sentences[:10])
trees = [next(tree) for tree in parses]

def simple_pred(node):
    return node.label() == 'ROOT' and \
            len(node) == 1 and \
            node[0].label() == 'S' and \
            len(node[0]) == 3 and \
            node[0][0].label() == 'NP' and \
            node[0][1].label() == 'VP' and \
            node[0][2].label() == '.'

# TODO this is not finished
def has_auxiliary_verb(node):
    return node.label() == 'VP' and \
            False

for tree in trees:
    for subtree in tree.subtrees(filter = simple_pred):
        print(subtree)

#print([sent for sent in sentences])

