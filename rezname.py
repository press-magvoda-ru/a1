import sys,fitz
from  datetime import datetime

import timing

def getArgOr(pos,default,isDir=None):
    rez=sys.argv[pos:]and sys.argv[pos] or default
    return rez+['','\\'][int(bool(isDir and rez[-1]!='\\'))] # os.path.join(path,'')

def rezname():
    return 'rez_'+f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}'
    
def SimpleJoinPdffromListOf(l,path,doc):
    for i,pdf in enumerate(l):
        doc.insert_pdf(fitz.open(f'{path}{pdf}'),links=0,annots=0,show_progress=0)
        print(timing.llgg(i,pdf))
    return doc
    