#!/usr/bin/env python

from __future__ import print_function

import settings

import codecs

import grammar_util as g

import nltk
from nltk.parse import stanford
from nltk.tree import Tree
from pattern.en import conjugate

#given a question as a single string, outputs the question transformed
#into a statement, with "noun phrase" substituted for what is being asked for.
#Also classifies question as either SBARQ(WH), or SQ(Binary)

def q_class(question):
    parser = stanford.StanfordParser()
    parse = parser.raw_parse(question)

    tree = parse.next()
    s_node = tree[0]
    s_tag = s_node.label()

    if s_tag == "SBARQ":
        sq_node = s_node[1]
        filler = Tree('NP', [Tree('NN', ['Richard']), Tree('NN', ['Fan'])])
        if not g.is_verb(sq_node[0]):
            s_node.set_label("S")
            tree = Tree("Root", [s_node])
            tree.chomsky_normal_form()
            print("Case for non-initial verb_node in SBARQ not accounted for")
            return (tree, "error")
        else:
            #Checking if querying for subject
            if g.is_label_in(sq_node, 'NP'):
                subject_idx = g.find_label_in(sq_node, 'NP')
                subject_node = sq_node[subject_idx]
            else:
                subject_node = filler
                subject_idx = len(sq_node)
            #checking for existance of auxillary verb
            if g.is_verb(sq_node[-1]):
                verb_node = sq_node[-1]
                remaining_phrase = []
            else:
                verb_node = sq_node[0]
                remaining_phrase = sq_node[subject_idx + 1:]

            object_node = [filler]
            pre_phrase = []
            mid_phrase = []
            post_phrase = []
            v_node = verb_node

            #case where not a simple verb
            if not g.is_leaf(verb_node):
                verb_idx = g.find_verb_in(verb_node)
                #querying for object within verb phrase
                if subject_node == filler:
                    if g.is_label_in(verb_node,'NP'):
                        object_idx = g.find_label_in(verb_node, 'NP')
                        object_node = verb_node[object_idx]
                    elif g.is_label_in(verb_node, 'PP'):
                        PP_idx = g.find_label_in(verb_node, 'PP')
                        if g.is_label_in(verb_node[PP_idx],'NP'):
                            object_node = [verb_node[PP_idx]]
                            object_idx = PP_idx
                    else:
                        object_node = []
                        object_idx = verb_idx + 1
                    mid_phrase = verb_node[verb_idx + 1:object_idx]
                    post_phrase = verb_node[object_idx:]
                else:
                    object_idx = verb_idx + 1
                    post_phrase = verb_node[object_idx:]
                v_node = verb_node[verb_idx]
                pre_phrase = verb_node[:verb_idx]

            #conjugate the main verb if an auxiliary verb exists
            if g.is_verb(sq_node[-1]) and len(sq_node) > 1:
                    aux_node = sq_node[0]
                    verb_label = aux_node.label()
                    new_verb = conjugate(v_node[0], verb_label)
                    v_node = Tree(verb_label, [new_verb])

            vp_node = Tree('VP', pre_phrase + [v_node] + mid_phrase + object_node + post_phrase)

            tree = Tree('ROOT', [Tree('S',
                        [subject_node] + [vp_node] + remaining_phrase
                        )])
            tree.chomsky_normal_form()
            return (tree, "SBARQ")
    elif s_tag == "SQ":
        verb_node = s_node[0]
        if not g.is_verb(verb_node):
            s_node.set_label("S")
            tree = Tree("Root", [s_node])
            tree.chomsky_normal_form()
            print("Case for non-initial verb_node in SQ not accounted for")
            return (tree, "error")
        else:
            np_node = s_node[1]
            rest = s_node[2:-1]
            tree = Tree('ROOT', [Tree('S',
                        [np_node] + [verb_node] + rest + [Tree('.', ['.'])])])
            tree.chomsky_normal_form()
            return (tree,"SQ")
    else:
        s_node.set_label("S")
        tree = Tree("Root", [s_node])
        tree.chomsky_normal_form()
        print("question structure not accounted for")
        return (tree, "error")


def print_q(question):
    parser = stanford.StanfordParser()
    parse = parser.raw_parse(question)

    parse.next().draw()


q = "I ate the elephant, correct?"
print_q(q)
q_class(q)[0].draw()
#print([sent for sent in sentences])

