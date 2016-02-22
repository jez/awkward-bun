import sys
import re
sys.path.insert(0,'../util')
from abutil import Infix
import cluster
from hyperparameters import insert_cost, delete_cost, mediod_cost, new_rule_tolerance

#to be done:
#   hyperparameter tuning
#   integration of PoS tagging

def match_syntax(semantic_rules, text):
    result = {}
    for (rule_type, a, b) in semantic_rules:
        if (rule_type,a,b) not in result: result[(rule_type,a,b)] = []
        for match in re.finditer(a, text):
            loc = match.start()
            loc_b = text[loc:loc+10*int(mediod_cost/delete_cost)].find(b)
            loc_p = text[loc:loc+10*int(mediod_cost/delete_cost)].find('.')
            if loc_b>= 0 and (loc_p < 0 or loc_b < loc_p) :
                result[(rule_type,a,b)] += [text[loc: loc+text[loc:loc+10*int(mediod_cost/delete_cost)].find(b)+len(b)]]
    return result

def fixed_points(L):
    return map(lambda (x,y):x, filter(lambda (x,y) : x==y, L))

def gen_mediods(D):
    result = {}
    for (rule,syntax) in D.items():
        (rel, A, B) = rule
        syntax = list(set(syntax))
        L = fixed_points(cluster.cluster_mediods(map(lambda x: x.split(),syntax)))
        result[rule] = map(lambda s: (' '.join(s)).replace(A, "(?P<A>\w+)").replace(B, "(?P<B>\w+)"), L)
    return result

def match(syntatic_rules, text, old_rules):
    result = {}
    print syntatic_rules
    for r in syntatic_rules:
        L = re.findall(r, text)
        for (a,b) in L:
            if (a,b) not in old_rules:
                if (a,b) in result: result[(a,b)] += 1
                else: result[(a,b)] = 1
    return result
         

def new_rules(D, text, old_rules):
    new_rules = D.keys()
    for (rule, mediods) in D.items():
        (rel, A, B) = rule
        for ((A,B), occurrences) in match(mediods, text, old_rules).items():
            if float(occurrences)/len(mediods)>new_rule_tolerance:
                print A + "\t" + B +"\t" + str(float(occurrences)/len(mediods))
                new_rules += [(rule[0], A, B)]
    return new_rules

def findrules(seed, text, iterations):
    result = {}
    for i in range(iterations):
        print "Starting iteration: \t"+str(i)
        rules = gen_mediods(match_syntax(seed, text))
        result.update(rules)
        seed = new_rules(rules, text, map(lambda (a,b,c): (b,c), result.keys()))
        print "new seed:\t" + str(seed)
        print "new result:\t" + str(result)
    return result

seed = [("is", "obama", "president")]
text = "obama is president . california is state . obama , despite popular belief , is president . the president is obama . despite popular belief , california , as great as it is , is state. state is california . despite popular belief , the president , the leader , is obama . obama , president . california , state"
print findrules(seed, text, 3)
