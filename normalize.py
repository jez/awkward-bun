#!/usr/bin/env python

#
# Normalize a question into a sentence to make it easier
# to answer questions about.
#

from __future__ import print_function

# this module should be imported before using any NLTK or Stanford Parser code,
# as it initializes these with their support folders.
import settings as s

import grammar_util as g
import util

import nltk
from nltk.tree import Tree
from pattern.en import conjugate

# Return status types: possible values returned from normalize
BINARY = 's-BINARY'
FACTOID = 's-FACTOID'
SENTENCE = 's-SENTENCE'
NOSUBJECT = 'f-NOSUBJECT'
UNKNOWN = 'f-UNKNOWN'

def is_success_type(qtype):
    """
    Interprets a qtype (BINARY, UNKNOWN, etc.) as a "success" or "failure"
    """
    return qtype[0] == 's'

def flatten(l):
    return [item for sublist in l for item in sublist]

def normalize_binary(root, extras=[]):
    sq = g.get_sentence(root)
    (subject, verb_nodes, tail) = g.partition_sq(sq)

    # Sometimes the root we get is from a factoid SQ, which means the subject
    # is outside in a WH-phrase. Let's let them know, so they can handle it.
    if subject is None:
        return (NOSUBJECT, [g.as_sentence(root)])

    # Treat non-verb nodes as leaves
    def leaf_fn(node):
        return g.is_leaf(node) or not g.is_verb(node)

    # list of Trees (which are lists). To access the string contents of the
    # i'th element, use verb_leaves[i][0]
    leaf_nodes = flatten([g.leaves(verb_node, leaf_fn=leaf_fn) \
            for verb_node in verb_nodes])

    verb_leaves = [leaf for leaf in leaf_nodes if g.is_verb(leaf)]
    non_verb_leaves = [leaf for leaf in leaf_nodes if not g.is_verb(leaf)]

    (positive_vp, negative_vp) = g.negate_verb_leaves(verb_leaves)

    # Check to see if we have to collapse things like 'does eat' to 'eats'
    if len(positive_vp) > 1 and conjugate(positive_vp[0][0], 'VB') == 'do':
        # Grab the second verb and conjugate it according
        # to the POS of the 'do' verb
        pos = positive_vp[0].label()
        positive_vp = [Tree(pos, [conjugate(positive_vp[1][0], pos)])] + positive_vp[2:]

    sentences = []
    sentences.append(Tree('S',
            [g.upcase(subject), g.downcase(Tree('VP', positive_vp))] +
            extras + non_verb_leaves + tail))
    sentences.append(Tree('S',
            [g.upcase(subject), g.downcase(Tree('VP', negative_vp))] +
            extras + non_verb_leaves + tail))

    # TODO(jez): handle the WHNP/NP + 'be' case
    if len(positive_vp) == 1 and conjugate(positive_vp[0][0], 'VB') == 'is':
        # positive reverse
        sentences.append(Tree('S', extras + non_verb_leaves + tail +
            [g.downcase(Tree('VP', positive_vp)), g.upcase(subject)]))
        # negative reverse
        sentences.append(Tree('S', extras + non_verb_leaves + tail +
            [g.downcase(Tree('VP', negative_vp)), g.upcase(subject)]))

    return (BINARY, [g.as_sentence(sent) for sent in sentences])


def normalize_factoid(root):
    sbarq = g.get_sentence(root)
    # blindly take the first SQ; if we get an exception,
    # it will be caught higher up
    sq = next(child for child in sbarq if g.is_sq(child))
    sq_root = Tree('ROOT', [sq])

    try:
        whp = next(child for child in sbarq if g.is_wh_phrase(child))
        non_whp = [g.replace_wh_phrase(whp)]
    except StopIteration:
        non_whp = []

    (qtype, sentences) = normalize_binary(sq_root, extras=non_whp)
    if qtype == NOSUBJECT:
        # The subject must be in the wh-phrase, because it definitely
        # wasn't in the nested SQ, so we can just replace and move on
        return (FACTOID, [g.as_sentence(g.replace_wh_phrase(root))])
    else:
        # The '?' gets truncated when we dive into the nested SQ,
        # so let's add it back manually
        return (FACTOID, [sent + '.' for sent in sentences])

def normalize_sentence(root):
    non_whp = g.replace_wh_phrase(root)
    return (SENTENCE, [g.as_sentence(non_whp)])

def normalize(root):
    """
    Tries as best we can to convert the parsed sentence into a question.

    If something fails (either we didn't get an expected sentence type or an
    exception was raised outside of DEBUG mode), we return the original
    string.

    Otherwise, returns a pair (qtype, sentences), where:
        - qtype is one of BINARY, FACTOID, or UNKNOWN, describing the type of
          question which was asked
        - sentences is a list of strings representing our guesses at how to
          convert the question into a sentence
    """
    try:
        if g.is_binary_question(root):
            return normalize_binary(root)
        elif g.is_factoid_question(root):
            return normalize_factoid(root)
        elif g.is_complete_sentence(root):
            return normalize_sentence(root)
        else:
            g.log_error(root, 'Malformed question')
    except:
        g.log_error(root, 'Exception raised while parsing')
        if s.DEBUG:
            # only re-raise errors in DEBUG mode
            raise

    # Fall back to the original question if something failed
    return (UNKNOWN, [g.as_sentence(root)])


def use_line(line):
    return len(line.strip()) > 0 and line.strip()[0] != '#'

if __name__ == '__main__':
    # Only import these if we've been invoked from the command line
    import sys
    import codecs
    from nltk.parse import stanford as stanford_parse

    if len(sys.argv) != 2:
        print('usage: %s <questions.txt>' % sys.argv[0])
        sys.exit(1)

    questions_file = sys.argv[1]

    sp = stanford_parse.StanfordParser()

    with codecs.open(questions_file) as f:
        questions = [line.strip() for line in f.readlines() if use_line(line)]

    for question in questions:
        parse = next(sp.raw_parse(question))
        (qtype, normalizeds) = normalize(parse)

        print(question)
        print('  ' + qtype)
        for normalized in normalizeds:
            print('  ' + normalized)
        print()
