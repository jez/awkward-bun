#!/usr/bin/env python

from __future__ import print_function

import settings

import codecs

import grammar_util as g

import nltk
from nltk.parse import stanford
from nltk.tree import Tree
from pattern.en import conjugate


def q_class(question):
    parser = stanford.StanfordParser()
    parse = parser.raw_parse(question)

    tree = parse.next()
    s_node = tree[0]
    s_tag = s_node.label()

    if s_tag == "SBARQ":
        sq_node = s_node[1]
        filler = Tree('NP', [Tree('NN', ['noun']), Tree('NN', ['phrase'])])
        if not g.is_verb(sq_node[0]):
            print("question not structured properly")
            return (None, "error")
        else:
            if g.is_label_in(sq_node, 'NP'):
                subject_idx = g.find_label_in(sq_node, 'NP')
                subject_node = sq_node[subject_idx]
            else:
                subject_node = filler
            #checking for existance of auxillary verb
            if g.is_verb(sq_node[-1]):
                verb_node = sq_node[-1]
            else:
                verb_node = sq_node[0]

            object_node = filler
            pre_phrase = []
            mid_phrase = []
            post_phrase = []
            v_node = verb_node

            if not g.is_leaf(verb_node):
                object_idx = len(verb_node)
                if subject_node == filler:
                    if g.is_label_in(verb_node,'NP'):
                        object_idx = g.find_label_in(verb_node, 'NP')
                        object_node = verb_node[object_idx]
                    elif g.is_label_in(verb_node, 'PP'):
                        PP_idx = g.find_label_in(verb_node, 'PP')
                        if g.is_label_in(verb_node[PP_idx],'NP'):
                            object_node = verb_node[PP_idx]
                            object_idx = PP_idx

                verb_idx = g.find_verb_in(verb_node)
                print(verb_idx)
                v_node = verb_node[verb_idx]
                pre_phrase = verb_node[:verb_idx]
                mid_phrase = verb_node[verb_idx + 1 :object_idx]
                post_phrase = [] if object_idx == len(verb_node) else verb_node[object_idx + 1:]


            if g.is_verb(sq_node[-1]) and len(sq_node) > 1:
                    aux_node = sq_node[0]
                    verb_label = aux_node.label()
                    new_verb = conjugate(v_node[0], verb_label)
                    v_node = Tree(verb_label, [new_verb])

            vp_node = Tree('VP', pre_phrase + [v_node] + mid_phrase + [object_node] + post_phrase)


            return (Tree('ROOT', [Tree('S',
                        [subject_node] + [vp_node]
                        )]), "SBARQ")
    elif s_tag == "SQ":
        verb_node = s_node[0]
        if not g.is_verb(verb_node):
            print("question not structured properly")
            return (None, "error")
        np_node = s_node[1]
        rest = s_node[2:-1]
        return (Tree('ROOT', [Tree('S',
                    [np_node] + [verb_node] + rest + [Tree('.', ['.'])]), "SQ")
        ])
    else:
        print("question not structured properly")
        return (None, "error")


def print_q(question):
    parser = stanford.StanfordParser()
    parse = parser.raw_parse(question)

    parse.next().draw()


# print_q(q)
# q_class(q)[0].draw()
#print([sent for sent in sentences])

