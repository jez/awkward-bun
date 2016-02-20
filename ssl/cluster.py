import sys
sys.path.insert(0,'../util')
from abutil import Infix

@Infix
def dif(L, R):
    return filter(lambda x: x not in R, L)

def distance(source, target):
    return 0
 
def argmin(L, f):
    min_val = None
    min_cost = float('inf')
    for i in L:
        cost = f(i)
        if cost <= min_cost:
            min_val = i
            min_cost = cost
    return (min_val, min_cost)

# (string list) list -> (string list * string list ) list
# produces mediods, not means
def cluster_mediods(L):
    L = L[:] #this shizz is functional (looking) yo
    candidates = L
    labels = L[:]
    done = False
    while not done:
        done = True
        for (wordlist, position) in zip(L,len(L)):
            (m, cost) = argmin(candidates |dif| wordlist, lambda x: distance(wordlist, x))
            if lone_cost < cost:
                labels = map(lambda s: m if s == wordlist else s, labels)
                candidates = candidates |dif| wordlist
                done = False
    return zip(L, labels)
