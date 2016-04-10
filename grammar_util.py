from __future__ import print_function

import sys
from nltk.tree import Tree

LOG_ERRORS = False

def log_error(tree, message):
    if LOG_ERRORS:
        print("Error:",                   file=sys.stderr)
        print(                            file=sys.stderr)
        print(message,                    file=sys.stderr)
        print(                            file=sys.stderr)
        print("Sentence was:",            file=sys.stderr)
        print(' '.join(tree.flatten()),   file=sys.stderr)
        print(                            file=sys.stderr)
        print("Tree was:",                file=sys.stderr)
        print(tree,                       file=sys.stderr)


def is_complete_sentence(root_node):
    """
    We'll use "complete sentence" to mean we've found a node tagged 'S'
    directly below a node tagged 'ROOT', i.e.:

        (ROOT
          (S ...))
    """
    return root_node.label() == 'ROOT' and \
            len(root_node) == 1 and \
            root_node[0].label() == 'S'

def is_simple_pred(root_node):
    """
    A simple predicate sentence is a complete sentence where the sentence is
    three components: a noun phrase, a verb phrase, and a terminal punctuation.

    In symbols:

        (ROOT
          (S
            (NP ...)
            (VP ...)
            (. .)))
    """
    return is_complete_sentence(root_node) and \
            len(root_node[0]) == 3 and \
            root_node[0][0].label() == 'NP' and \
            root_node[0][1].label() == 'VP' and \
            root_node[0][2].label() == '.'

def get_sentence(root_node):
    """
    Given a complete sentence like (ROOT (S ...)), returns the nested (S ...).

    In symbols:

        (ROOT
          (S             <-- returns this node
            (NP ...)
            (VP ...)
            (. .)))
    """
    return root_node[0]

def get_subject(root_node):
    """
    Given a simple predicate sentence like (ROOT (S (NP VP .)), returns the NP.

    In symbols:

        (ROOT
          (S
            (NP ...)     <-- returns this node
            (VP ...)
            (. .)))
    """
    return get_sentence(root_node)[0]

def get_predicate(root_node):
    """
    Given a simple predicate sentence like (ROOT (S (NP VP .)), returns the VP.

    In symbols:

        (ROOT
          (S
            (NP ...)
            (VP ...)     <-- returns this node
            (. .)))
    """
    return get_sentence(root_node)[1]

def is_verb_node(node):
    """
    A verb is either a non-terminal VP (verb phrase), a terminal verb (VB, VBZ,
    etc.), or a modal verb (a sort of auxiliary verb).
    """
    return node.label()[0] == 'V' or node.label() == 'MD'

def is_leaf(node):
    """
    For us "leaf" nodes are the nltk.tree.Tree objects that contain no Tree
    objects in their children.
    """
    return all([type(child) != Tree for child in node])

def as_string(node):
    """
    We can get a simple string from a node by flattening it to give us a Tree
    with all string children, then joining those strings.
    """
    return ' '.join(node.flatten())

def is_label_in(node, label):
    for i in xrange(len(node)):
        child = node[i]
        if (child.label() == label):
            return True
    return False

def find_label_in(node, label):
    for i in xrange(len(node)):
        child = node[i]
        if (child.label() == label):
            return i
    return -1

def find_verb_in(node):
    for i in xrange(len(node)):
        child = node[i]
        if (is_verb_node(child)):
            return i
    return -1

