import sys
sys.path.insert(0,'../util')
from abutil import Infix

#hyperparameters (to be tuned)
delete_cost = 1.0
insert_cost = 6.0
mediod_cost = 20.0

@Infix
def sub(L, r):
    return filter(lambda x: x != r, L)


def distance(source, target):
    def distance_dp(source, target, D):
        (s,t) = (len(source),len(target))
        if (s,t) in D:
            return D[(s, t)]
        if (s,t) == (0,0): 
            D[(s,t)] = 0.0
            return 0.0
        if s == 0: 
            D[(s,t)] = insert_cost * t
            return insert_cost * t
        if t == 0: 
            D[(s,t)] = delete_cost * s
            return delete_cost * s
        if source[0] == target[0]:
            return distance_dp(source[1:], target[1:], D)
        rs = distance_dp(source[1:], target, D) + delete_cost
        rt = distance_dp(source, target[1:], D) + insert_cost
        v = min(rs,rt)
        D[(s,t)] = v
        return v
    return distance_dp(source, target, {})

def argmin(L, f):
    min_val = L[0]
    min_cost = f(L[0]) 
    for i in L[1:]:
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
        (wordlist, (cost, m)) = argmin(candidates, lambda wl: (lambda (x,y):(y,x))(argmin(candidates |sub| wl, lambda x: distance(wl, x))))
        if cost<mediod_cost:
            labels = map(lambda s: m if s == wordlist else s, labels)
            candidates = candidates |sub| wordlist
            done = len(candidates)<=1
    return zip(L, labels)

