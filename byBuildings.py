from collections import defaultdict
from pprint import pprint
from reparseWxMx import DictFromFile, Pg,name2str as nm
import rezname
from os.path import dirname, join
from itertools import chain

from timing import log
__all__=['byBuildings']
def NormalizedAdr(adr):
    #1 - отрезаем __ квартиры и проч
    # возможно в дальнейшем тут дальнейшее приведение в универсальный вид адресов
    rez = adr.split('__',1)[0]
    return rez

def byBuildings(WW:dict,MM:dict,ofld):
    Blds=defaultdict(lambda: defaultdict(int))
    for v in chain(WW.values(), MM.values()):
        Blds[NormalizedAdr(v.adr)][v.Hn]+=1
    outDict('Blds',Blds)

    mulBlds={}
    for k,v in Blds.items():
        if len(v)>1:
            mulBlds[k]=v
    outDict('mulBlds',mulBlds)

    mwBuilds={}
    for k,v in mulBlds.items():
        counts=defaultdict(int)
        for k2,v2 in v.items():
            counts[k2[0]]+=v2
        if len(counts)<2:
            continue
        if counts['M']==1 and counts['W']==1:
            continue
        mwBuilds[k]={'v':v,'counts':counts}
    outDict('mwlBlds',mwBuilds)

    Tria={}
    for k,v in mwBuilds.items():
        if len(v['v'])<3:
            continue
        Tria[k]=v['v']
    outDict('Tria',Tria)
    return Tria



prefix=rezname.rezname()
def outDict(nm,vl):
    ofn=f'{prefix}{nm:^10}.dict.txt'
    pprint(vl,open(ofn,'w'),width=1000)

if __name__=='__main__':
    print(log(0,'start'))
    root = rezname.getArgOr(1, dirname(dirname(__file__)), 'Dir')
    #rname=DictFromFile(join(root,'rname'))
    fld= 'MWrez_2023-06-28__13-23-22'#'MWrez_2023-02-09__16-47-53.striped'
    WW = DictFromFile(join(root+fld, 'wTotB'))
    MM = DictFromFile(join(root+fld, 'mTotB'))
    grp=byBuildings(WW,MM,root)
    print(log(1,'stop'))
    exit()
    ofn=rezname.getArgOr(2,f'Buildings_{rezname.rezname()}.dict.txt')
    pprint(grp,open(ofn,'w'),width=1000)
    
    exit()
    print(len(grp))
    print(grp)




