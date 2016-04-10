from __future__ import print_function

import sys
import re
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

def is_verb(node):
    """
    A verb is either a non-terminal VP (verb phrase), a terminal verb (VB, VBZ,
    etc.), or a modal verb (a sort of auxiliary verb).
    """
    return node.label()[0] == 'V' or node.label() == 'MD'

def is_proper_noun(node):
    """
    There are two types of proper nouns: the singular "NNP" and the plural
    "NNPS". This function checks whether a node's tag is either of these.
    """
    return node.label() == 'NNP' or node.label() == 'NNPS'

def is_prp(node):
    """
    There are two types of pronouns nouns: personal pronouns "PRP" and
    personal possessive pronouns "PRP$".
    This function only checks whether a node's tag is "PRP".
    """
    return node.label() == 'PRP'

def is_leaf(node):
    """
    For us "leaf" nodes are the nltk.tree.Tree objects that contain no Tree
    objects in their children.
    """
    return all([not isinstance(child, Tree) for child in node])

def tree_any(tree, f):
    """
    Runs a predicate function f over all the elements of a tree.
    Returns whether the function is true for any element of the tree.
    """
    if isinstance(tree, Tree):
        return f(tree) or any(tree_any(child, f) for child in tree)
    else:
        return False

def as_string(node):
    """
    We can get a simple string from a node by flattening it to give us a Tree
    with all string children, then joining those strings.

    On top of this, we heuristically try to push punctuation back up to the
    previous token using a regex, so things like
        "Is this a question ?"
    becomes
        "Is this ia question?"
    (note the '?' placement).
    """
    joined = ' '.join(node.flatten())
    return re.sub(r'\s+(\W)', r'\1', joined)

def upcase(node):
    """
    Takes a node and upcases the left-most leaf.
    """
    if not isinstance(node, Tree):
        return node.title()
    else:
        if len(node) == 0:
            return node
        else:
            left_child = node[0]
            return Tree(node.label(), [upcase(left_child)] + node[1:])

def downcase(node, pos=None):
    """
    Takes a node and downcases the left-most leaf, according to it's POS tag.
    """
    if not isinstance(node, Tree):
        if pos is None or (pos != 'NNP' and pos != 'NNPS'):
            return node.lower()
        else:
            # Don't change anything if the node is a proper noun
            return node
    else:
        if len(node) == 0:
            return node
        else:
            left_child = node[0]
            return Tree(node.label(),
                    [downcase(left_child, pos=node.label())] + node[1:])

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

