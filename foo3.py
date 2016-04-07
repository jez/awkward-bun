#!/usr/bin/env python3

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

import settings

import nltk
from nltk.parse import stanford


with open('./data/set1/a1.txt') as f:
    sentences = nltk.sent_tokenize(f.read())

#print('\n'.join(sentences[:10]))
# TODO: restrict length of sentences and number of sentences to meet time bounds

parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
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

for tree in trees:
    for subtree in tree.subtrees(filter = simple_pred):
        print(subtree)

#print([sent for sent in sentences])

