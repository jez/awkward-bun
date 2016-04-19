from __future__ import print_function

import sys
import re
import settings as s
from nltk.tree import Tree

LOG_ERRORS = s.DEBUG

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


# ----- Simple predicate sentence helpers ------------------------------------

def is_complete_sentence(root_node):
    """
    We'll use "complete sentence" to mean we've found a node tagged 'S'
    directly below a node tagged 'ROOT', i.e.: (ROOT (S ...))
    """
    return root_node.label() == 'ROOT' and \
            len(root_node) == 1 and \
            root_node[0].label() == 'S'

def is_binary_question(root_node):
    """
    Binary questions use SQ: (ROOT (SQ ...))
    """
    return root_node.label() == 'ROOT' and \
            len(root_node) == 1 and \
            root_node[0].label() == 'SQ'

def is_factoid_question(root_node):
    """
    Factoid questions use SBARQ: (ROOT (SBARQ ...))
    """
    return root_node.label() == 'ROOT' and \
            len(root_node) == 1 and \
            root_node[0].label() == 'SBARQ'

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
    Given a complete sentence like (ROOT (S ...)) or (ROOT (SQ ...)), returns
    the nested (S ...) or (SQ ...).
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

def partition_sq(sq):
    """
    Takes an SQ node (i.e., the first thing under ROOT of something for which
    is_binary_question returns true.

    Returns a tuple (subject, verbs, tail), where:
        - subject is the first NP under the SQ
        - verbs is all nodes for which is_verb returns true
        - tail is everything else
    """
    found_first_np = False
    subject = None
    verbs = []
    tail = []

    for node in sq:
        # Treat the first NP as the subject
        if not found_first_np and node.label() == 'NP':
            found_first_np = True
            subject = node

        # Collect all the verb nodes
        elif is_verb(node):
            verbs.append(node)

        # Dump all the rest of the stuff into a bucket
        else:
            tail.append(node)

    return (subject, verbs, tail)


# ----- Node label helpers ---------------------------------------------------

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

def is_sq(node):
    """
    Is this an SQ node?
    """
    return node.label() == 'SQ'

def is_wh_phrase(node):
    """
    There are a number of phrase types that start SBARQ (i.e. WH-question)
    phrases, like WHNP, WHADJP, WHAVP, and WHPP
    """
    return node.label()[:2] == 'WH'

def is_heshehishers(node):
    """
    Searches for pronouns "he", "she", "his", and "hers",
    returning True if found.
    """
    if len(node) != 1:
        return False

    target = node[0].lower()
    pos = node.label()

    return ((pos == 'PRP')  and (target == 'he'  or target == 'she')) or \
           ((pos == 'PRP$') and (target == 'his' or target == 'hers'))

def is_itits(node):
    """
    Searches for pronouns "it", and "its", returning True if found.
    """
    if len(node) != 1:
        return False

    target = node[0].lower()
    pos = node.label()

    return ((pos == 'PRP')  and (target == 'it')) or \
           ((pos == 'PRP$') and (target == 'its'))

def is_definite_article(node):
    """
    Searches for definite articles, like 'the', 'this', 'that', etc.
    """
    return node.label() == 'DT' and len(node) == 1 and node[0].lower()[:2] == 'th'

# ----- Tree traversal helpers -----------------------------------------------

def is_leaf(node):
    """
    For us "leaf" nodes are the nltk.tree.Tree objects that contain no Tree
    objects in their children.
    """
    return isinstance(node, Tree) and \
            all([not isinstance(child, Tree) for child in node])

def tree_any(tree, f):
    """
    Runs a predicate function f over all the elements of a tree.
    Returns whether the function is true for any element of the tree.
    """
    if not isinstance(tree, Tree):
        return False
    else:
        return f(tree) or any(tree_any(child, f) for child in tree)

def filter_tree(node, f):
    """
    Runs a predicate function f over all the elements of a tree.
    Removes any nodes for which the predicate is False.

    @returns None if f returns False on the root, o.w. returns a Tree with the
        appropriate children filtered.
    """
    if not isinstance(node, Tree):
        return node
    else:
        if f(node):
            filtered_children = []
            for child in node:
                result = filter_tree(child, f)
                if result is not None:
                    filtered_children.append(result)
            return Tree(node.label(), filtered_children)
        else:
            return None

def leaves(node):
    """
    Retur a list where the elements are all the leaves of the input node
    according to is_leaf
    """
    if is_leaf(node):
        return [node]
    else:
        children = []
        for child in node:
            children += leaves(child)
        return children

def replace_leftmost(node, f, replacer):
    """
    Iterate over all nodes of the tree, running f on the node to determine if
    it's a leaf, and running replacer on the node if f returns True.

    @param f Is given a leaf node (as determined by is_leaf), and should return
        a boolean of whether to run `replacer` on this node
    @param replacer Is given a node and should return a list of Trees
        corresponding to what the replacer should be

    @return WARNING: This will return a list of Trees instead of a Tree if the
        top-most call is on a leaf node. Otherwise, returns a Tree.
    """
    if is_leaf(node):
        if f(node):
            replaced = True
            return (replacer(node), replaced)
        else:
            replaced = False
            return (node, replaced)

    else:
        new_children = []

        for cursor in xrange(len(node)):
            (child, replaced) = replace_leftmost(node[cursor], f, replacer)
            if type(child) == list:
                new_children += child
            else:
                new_children.append(child)

            # stop after leftmost replacement is made
            if replaced:
                break

        # copy over the rest of the children unchanged
        new_children += node[cursor+1:]

        return (Tree(node.label(), new_children), replaced)

def unwrap_until_np(node):
    """
    Unwraps things like 'ROOT' and 'FRAG' until we get down to an NP by
    traversing the left spine.
    """
    if node.label() == 'NP':
        return list(node)
    else:
        if len(node) == 0:
            return []
        else:
            return unwrap_until_np(node[0])

def replace_wh_phrase(whp):
    """
    Replace the various POS tags that start with W or WH with a filler word of
    their non-WH counterpart types. For example: Who -> Richard Fan
    """
    pos_mapping = {
        'WHNP': 'NP',
        'WHADJP': 'ADJP',
        'WHAVP': 'WHAVP',
        'WHPP': 'PP',
        'WDT': 'DT',
        'WP': 'PRP',
        'WP$': 'PRP$',
        'WRB': 'RB',
    }
    try:
        label = pos_mapping[whp.label()]
    except:
        label = whp.label()

    # Get new list of children (terminal or non-terminal)
    if is_leaf(whp):
        word_mapping = {
            'who':    'he',
            'whose':  'his',
            'what':   'it',
            'which':  'that',
            'where':  'here',
            'when':   'now',
            'why':    'because',
            'how':    'quite',
        }
        try:
            children = [word_mapping[whp[0].lower()]]
        except KeyError:
            children = [whp[0].lower()]
    else:
        children = [replace_wh_phrase(child) for child in whp]

    return Tree(label, children)

def is_label_in(node, label):
    """
    Searches the immediate children of a node for a certain label, returning
    True when such a label exists, and False when it doesn't
    """
    return any([child.label() == label for child in node])

def find_label_in(node, label):
    """
    Searches the immediate children of a node for a certain label, returning
    the index of the first match if it exists, or None when it doesn't.
    """
    for i in xrange(len(node)):
        child = node[i]
        if (child.label() == label):
            return i
    return None

def find_verb_in(node):
    """
    Searches the immediate children of a node for any verb label, returning
    the index of the first match if it exists, or None when it doesn't.
    """
    for i in xrange(len(node)):
        child = node[i]
        if (is_verb(child)):
            return i
    return None


# ----- Tree to string helpers -----------------------------------------------

def as_string(node):
    """
    We can get a simple string from a node by flattening it to give us a Tree
    with all string children, then joining those strings.

    On top of this, we heuristically try to push punctuation back up to the
    previous token using a regex, so things like
        "Is this a question ?"
    become
        "Is this a question?"
    (note the '?' placement).
    """
    joined = ' '.join(node.flatten())
    joined = re.sub(r'``\s+', '"', joined)
    joined = re.sub(r"\s+''", '"', joined)
    joined = re.sub(r'\s+-LRB-\s+\s+-RRB-', '()', joined)
    joined = re.sub(r'-LRB-\s+', '(', joined)
    joined = re.sub(r'-RRB-', ')', joined)
    joined = re.sub(r'-LSB-\s+', '[', joined)
    joined = re.sub(r'-RSB-', ']', joined)
    return re.sub(r"\s+([-?.,';)])", r'\1', joined)

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

def as_sentence(node):
    """
    Takes a node, calls as_string on it, and converts '?' to '.'
    """
    return re.sub(r'\?', '.', as_string(node))
