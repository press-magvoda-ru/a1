import sys
import fitz
from datetime import datetime
from os.path import join
from reparseWxMx import DictFromFile,Pg,makeFakeNxtPg
import timing


def getArgOr(pos, default, isDir=None):
    rez = sys.argv[pos:] and sys.argv[pos] or default
    return rez if not isDir else join(rez, '')


def rezname():
    return 'rez_'+f'{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}'
# чисто обвязка:

def SimpleJoinPdffromListOf(l, path, doc):
    for i, pdf in enumerate(l):
        doc.insert_pdf(fitz.open(f'{path}{pdf}'),
                       links=0, annots=0, show_progress=0)
        print(timing.log(i, pdf))
    return doc

def genDoublesDict(frm,to,fl='wTotB'):
    w=DictFromFile(join(frm,fl))
   
    v=Pg(*range(7))
    # with open(to,'w') as file:
    #     print('{',file=file)
    #     for k,v1 in w.items():
    #         if v==v1:
    #             print(f'{k-1}:{v}',file=file)
    #             print(f'{k}:{v}',file=file)
    #         v=v1
    #     print('}',file=file)
    oldout=sys.stdout #Q?:свой контекстный менеджер который замещает(стеково) stdout и  востанавливает по выходу из with
    #e=Pg(*["N/A"]*7)
    with open(to,'w') as sys.stdout:
        print('{')
        for k,v1 in w.items():
            if v==v1:
                print(f'{k-1}:{v},')
                print(f'{k}:{makeFakeNxtPg(v)},')
            v=v1
        print('}')
    sys.stdout=oldout
    print('where IT')

#c=0;
def fromTo(src, p, dst):
    #global c
    #c+=1
    #print(f'{c=}\n\t{src=}\t\t\n ')
    dst.insert_pdf(src, from_page=p, to_page=p, links=0, annots=0, final=False)
def mkPdffromDictOfPg(DictOfPg,Hn2FulPath,outFullpath=None):
    import fitz
    outFullpath=outFullpath or f'{rezname()}.pdf'
    doc=fitz.open()
    for v in DictOfPg.values():
        fromTo(fitz.open(Hn2FulPath[v.Hn]),v.pN,doc)
    doc.save(outFullpath, garbage=2, deflate=True)
if __name__=='__main__':
    frm=getArgOr(2,'../MWrez_2023-02-16__09-19-12')
    to=getArgOr(1,'doubles')
    if to[0]=='_':
        to=to[1:]
        def full(a):return join(frm,a)
        import os
        mkPdffromDictOfPg(DictFromFile(join(os.path.abspath('.'),to)),DictFromFile(full('rname')))
        exit()
    genDoublesDict(frm,to)