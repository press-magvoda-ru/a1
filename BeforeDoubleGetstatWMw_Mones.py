import os
from os.path import join
import sys

def lst(path):
    return [a.replace('.pdf','') for a in os.listdir(path) if a.split('.')[-1]=='pdf']

def getstatWMw(b):
    r={'m':0,'w':0,}
    for c in b:
        d=c.split()
        r['w']+=int(d[-1])
        r['m']+=int(d[-1]) if d[-2]=='2' else 0
    return r

def getstatMones(b):
    r={'m':0}
    for c in b:
        d=c.split()
        r['m']+=int(d[-1])
    return r

path=sys.argv[-1] if sys.argv[1:] else '.'
print(getstatWMw(lst(join(path,'WMpdfs'))))
print(getstatMones(lst(join(path,'MekOnes'))))


