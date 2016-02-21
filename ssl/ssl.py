import sys
import re
sys.path.insert(0,'../util')
from abutil import Infix
import cluster
from hyperparameters import insert_cost, delete_cost, mediod_cost, new_rule_tolerance


def match_syntax(semantic_rules, text):
    result = {}
    for (rule_type, a, b) in semantic_rules:
        for loc in re.finditer(a, text):
            if text[loc:loc+int(delete_cost)].find(b) >= 0:
                result[(rule_type,a,b)] += text[loc:loc+int(delete_cost)]
    return result

def fixed_points(L):
    return filter(lambda (x,y) : x==y, L)

def gen_mediods(D):
    result = {}
    for (rule,syntax) in D.items:
        (rel, A, B) = rule
        L = fixed_points(cluster.cluster_mediods(map(lambda x: x.split(syntax))))
        result[rule] = map(lambda s: s.replace(A, "(?P<A>\w+").replace(B, "(?P<B>\w+"), L)
    return results

def match(syntatic_rules, text, old_rules):
    result = {}
    for ((rule_type, A, B),syntactic_rules) in syntatic_rules.items():
        for r in syntatic_rules:
            L = findall(r, text)
            for (a,b) in L:
                if (a,b) not in old_rules:
                    if (a,b) in result: result[(a,b)] += 1
                    else: result[(a,b)] = 1
    return result
         

def new_rules(D, text, old_rules):
    new_rules = D.keys()
    for (rule, mediods) in D:
        for ((A,B), occurences) in match(mediods, text, old_rules).items():
            if float(occurrences)/len(mediods)>new_rule_tolerance:
                new_rules += [(rule[0], A, B)]
    return new_rules

def findrules(seed, text, iterations):
    result = {}
    for i in range(iterations):
        print "Starting iteration: \t"+str(i)
        rules = gen_mediods(match_syntax(seed, text))
        result += rules
        seed = new_rules(rules, text, map(lambda (a,b,c): (b,c), result.keys()))
    return result
