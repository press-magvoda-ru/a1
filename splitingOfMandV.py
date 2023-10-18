import multiprocessing as mp,os, pprint, sys
from collections import defaultdict, namedtuple
from datetime import datetime
from functools import lru_cache
from os.path import basename, dirname, join, exists,splitext
import fitz, rezname, timing
#import os
from reparseWxMx import Hn, Pg, bundle, add2Hn, DictFromFile, name2str, prsM, prsW, rname,\
    makeEmptyPg, makeFakeNxtPg, lstInWithExtention
from itertools import chain
from generXLS import makeXLS,typefilesOfdata
import inspect; __LINE__ = inspect.currentframe()
from NormiW import NormiAdr as forCMP
#from exceptlst import Except
print(__LINE__.f_lineno);print(__LINE__.f_lineno)
#+1 or unk# +1 for de_ug purpose:
inN, de_ug =os.cpu_count()+1, 0#+1 #
VRS=rezname.rezname()
VRSbs=basename(splitext(__file__)[0])
def mkmk(fld): # утилита для mainUI
    if not os.path.isdir(fld):        os.mkdir(fld)
    os.chdir(fld);    os.system(f'start "" "{fld}"')
def mainUI(in_srcM,in_srcW,in_fld):
    from PyQt5 import QtWidgets, uic
    try:
        frm_cls = uic.loadUiType(f'{os.path.dirname(__file__)}\\guiForPairing.ui')[0]
    except:
        from guiForPairing import Ui_MainWindow as frm_cls

    class mn_Window(QtWidgets.QMainWindow, frm_cls):
        def __init__(self, parent=None):
            QtWidgets.QMainWindow.__init__(self, parent)
            self.setupUi(self); self.b_srcM.setText(in_srcM);   self.b_srcW.setText(in_srcW) 
            self.b_fld.setText(in_fld); self.b_srcM.clicked.connect(self.choose_srcM)
            self.b_srcW.clicked.connect(self.choose_srcW);  self.b_fld.clicked.connect(self.choose_fld)
            self.b_chekMEK.clicked.connect(self.chekMEK);   self.b_start_and_done.clicked.connect(self.run_run)
        def choose_srcM(self):
            if (t:=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\')):
                self.b_srcM.setText(t)
        def choose_srcW(self):
            if (t:=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\')):
                self.b_srcW.setText(t)
        def choose_fld(self):
            if (t:=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\')):
                self.b_fld.setText(t)
        def chekMEK(self):
            srcM,fld=self.b_srcM.text(),self.b_fld.text()
            mkmk(fld);  stdout, sys.stdout = sys.stdout, open(f'{(nm:=rezname.rezname()+"_rep.1.txt")}','w')
            print(f'{rezname.rezname()}')
            if not os.path.isdir(fld):  os.mkdir(fld)
            MMM=M_data_spliting(srcM,fld)
            print(f"общее количество страниц   :{MMM['pages']:^10}\n"
                  f"общее количество квитанций :{MMM['kvits']:^10}")
            sys.stdout.close(); os.system(f'start "" {nm}');    sys.stdout=stdout
        def run_run(self):
            srcM,srcW,fld=self.b_srcM.text(),self.b_srcW.text(),self.b_fld.text()
            mkmk(fld);  print(srcM,srcW,fld)
            #HERE use SAGEread for 
            nm='';
            if not de_ug:
                M_data_spliting(srcM, fld) # если чек т.е есть mTotB был то воспользоваться УЖОЙным M_
                W_data_spliting(srcW, fld)

                pprint.pprint(rname, stream=open(
                    join(fld, name2str(f'{rname=}')), 'w'), width=333)  # nero are
                nm=WM_mergeFromMultiPagePdf(fld, fld, fld)
            else: # de_ug yap
                rootTotS=r'C:\AAA\MWrez_2023-10-17__15-02-36' #r'C:\AAA\MWrez_2023-05-22__15-19-38' #r'C:\AAA\MWrez_2023-05-19__14-06-31' #r'C:\AAA\MWrez_2023-05-18__11-17-51' #r'C:\AAA\MWrez_2023-05-11__14-28-22' #r'C:\AAA\MWrez_2023-05-10__13-54-07' #r'C:\AAA\MWrez_2023-04-06__18-21-47' #r'C:\AAA\MWrez_2023-04-06__13-10-57' #r'C:\AAA\MWrez_2023-04-06__11-43-38' #r'C:\AAA\MWrez_2023-04-05__16-26-04' #r'C:\AAA\MWrez_2023-04-05__13-59-22' #r'C:\AAA\MWrez_2023-03-29__22-47-56' #r'C:\AAA\MWrez_2023-03-29__19-26-09' #r'c:\aaa\MWrez_2023-03-29__10-11-48' #r'C:\AAA\MWrez_2023-03-20__09-53-55' #r'C:\AAA\MWrez_2023-03-07__15-52-36' #r'C:\AAA\MWrez_2023-03-06__14-40-51' #r'C:\AAA\MWrez_2023-03-06__13-36-47' #r'C:\AAA\MWrez_2023-02-28__15-47-32' #r'C:\AAA\MWrez_2023-02-28__13-53-17' #r'C:\AAA\MWrez_2023-02-17__14-35-06' #r"C:\AAA\MWrez_2023-02-16__08-35-37" 
                nm=WM_mergeFromMultiPagePdf(rootTotS, rootTotS, fld)# de_ug of doubling All
            os.system(f'start "" "{nm[0]}"')
            nm[1] and os.system(f'start "" "{nm[1]}"') #если wf is None 
            sys.exit()
    app = QtWidgets.QApplication(sys.argv); (myWindow:=mn_Window()).show();    app.exec()
    return ['','','']
Nparts = namedtuple('Nparts', 'sum lst index')
Wshort = namedtuple('Wshort', 'Hn ll cs') # -замена семантики 
# было(wm-список парных;w-список водных_только)? - стало(w cписок [w,m*];
#  wm-развёрнутый(раскрытый) список  собранный из участков 1 длины [w,0] либо участки из мек файла ([0,m]*,[w,m],[0,m]*) --- cs is c(m),c(w),c(wm)
WMdocByHn, mainpid = {}, os.getpid()
def dirend(pathofdir): return join(pathofdir, '')
def LinesOfFileName(pathofFile): return open(pathofFile).read().splitlines()
@lru_cache(maxsize=999)
def weightMek(a):
    try:
        if (rl := pagesInPDF(a))==(nm := int(basename(a).split('-')[4])): return nm
    except:
        print(f'!!!Файл:{a} - Не форматное имя  +{rl} к различению общего числа (страниц VS квитанций')
        return 0         #TODO write in table bads of mek-file-pdf with massage
    print(f'!!!Файл:{a} из имени: {nm} по факту: {rl}  имя не != содержимому')
    return rl
@lru_cache(maxsize=999)
def pagesInPDF(a): return fitz.open(a).page_count
Mpages2time = {n: (0.004+0.005/2000*n)*n for n in range(9999)};""" ... из предположения что удвоение учетверяет ( хотя по факту утраивает)\n словарь/список (пока нет) с аппроксимацией - число_страниц_файла->время_на_файл :"""
class entityByindex():  
    def __getitem__(self,n):return n
Wpages2time=entityByindex() #не λ ибо нужно[]; # lambda n:n # (0.004+0.006/2000*n)*n for n in range(9999)}
def SumMap(wf, l): return sum(map(wf, l))
def toNparts(elems:list, nparts:int, pages2weight, pages):
    """Разбивка elems на nparts  почти равных по sum(pages2weight[pages(e)] for e in rez[j].lst) для каждой из частей j"""  
    rez = [Nparts([0], [], i+1) for i in range(nparts)]
    for e in elems:
        (v := min(rez)).sum[0] += pages2weight[pages(e)]
        v.lst.append(e)
    return rez
def inSubProcM(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.index} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'M{prt.index:>03}', 'w')  # {pid:>6}
    if (prt.index == 1):  # само пикленье Рика
        pagestxt.write('{\n')
    print(f'{prt.index=:^3} weght:{prt.sum[0]:^17.3f} {pid=:^7}len={len(prt.lst):>4} ',
          f' '.join(f'{weightMek(f)}'for f in prt.lst), end=' END\n')
    for inp in (fitz.open(f) for f in prt.lst):
        Name = Hn(inp.name,Tp)
        for p in range(szInp := inp.page_count):
            try:
                pagestxt.write(f'{(i := i+1):>6}:{prsM(inp.get_page_text(p), Name, p)},\n')
            except Exception as e:
                print(f'{__LINE__.f_lineno=} :\n {locals()=}')
                raise e
        print(timing.log(szInp, Name))
    if (prt.index == inN):
        pagestxt.write('}')
    print(timing.log(f'{i-base:<7}{pid:>5}', f'{pid:05}'), flush=True)
def M_data_spliting(src, of):
    src, Tp, = dirend(src), 'M',
    stdout, sys.stdout = sys.stdout, open((of := of+f'\\_{Tp}{rezname.rezname()}')+'.txt', 'w')
    print(f">{Tp} start: {datetime.now()}")
    print(timing.log(f'mainpid', f':{mainpid=:05} {inN=:^20}'), flush=True)
    (lfiles := sorted(lstInWithExtention(src), key=weightMek, reverse=True))
    MlFilteredFiles=[e for e in lfiles if basename(e).split('.', 1)[0].split('-')[5:]] #ПYAтыЙ йэлемент мила
    add2Hn(MlFilteredFiles,Tp)
    (base, procs, chunks,) = (0, [], toNparts(MlFilteredFiles, inN, Mpages2time, weightMek))
    for chunk in chunks:  # [:-1]):
        proc = mp.Process(target=inSubProcM, args=(Tp, base, chunk))
        procs.append(proc)
        proc.start()
        base += SumMap(weightMek, chunk.lst)
    for proc in procs:
        proc.join()
    print(timing.log('totalM_data_spliting', of))
    print(f">{Tp}   end: {datetime.now()}")
    os.system('copy /b m??? mTotB')
    os.system('del m???')
    print(timing.log('mTotB', of))
    sys.stdout = stdout
    numOfGoodPages=open('mTotB','r').readlines().__len__() -2 #{} проще из размера(max(keys)) словаря
    def f(lfiles):
        return sum(pagesInPDF(f) for f in lfiles)
    return {'of':of,'kvits':numOfGoodPages,'pages':f(lfiles)} # namedtuple in next season :)
def inSubProcW(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.index} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'W{prt.index:>03}', 'w')  # {pid:>6}
    if (prt.index == 1):
        pagestxt.write('{')
    print(f'{prt.index=:^3} weght:{prt.sum[0]:^17.3f} {pid=:^7}len={len(prt.lst):>4} ',
          f' '.join(f'{pagesInPDF(f)}'for f in prt.lst), end=' END\n')
    for inp in (fitz.open(f) for f in prt.lst):
        Name = Hn(inp.name,Tp)
        for p in range(szInp := inp.page_count):
            pagestxt.write(
                f'{(i := i+1):>6}:{prsW(inp.get_page_text(p),Name, p)},\n')
        print(timing.log(szInp, Name))
    if (prt.index == inN):
        pagestxt.write('}')
    print(timing.log(f'{i-base:<7}{pid:>5}', f'{pid:05}'), flush=True)
def W_data_spliting(src, of):
    src, Tp,  = dirend(src), 'W',
    stdout, sys.stdout = sys.stdout, open(
        (of := of+f'\\_{Tp}{rezname.rezname()}')+'.txt', 'w')
    print(f">{Tp} start:{datetime.now()}")
    print(timing.log(f'mainpid', f':{mainpid=:05} {inN=:^20}'), flush=True)
    add2Hn(lfiles := sorted(lstInWithExtention(src,non='Сопроводитель'), key=pagesInPDF, reverse=True),Tp)
    base, procs, chunks, = 0, [], toNparts(lfiles, inN, Wpages2time, pagesInPDF)
    for chunk in chunks:
        proc = mp.Process(target=inSubProcW, args=(Tp, base, chunk))
        procs.append(proc)
        proc.start()
        base += SumMap(pagesInPDF, chunk.lst)
    for proc in procs:
        proc.join()
    print(timing.log('totalW_data_spliting', of))
    print(f">{Tp}   end:{datetime.now()}")
    os.system('copy /b w??? wTotB')
    os.system('del w???')
    print(timing.log('wTotB', of))
    sys.stdout = stdout
    os.chdir(dirname(src))
    return of
def main(root, rout=None):
    rout = rout or root
    srcM, srcW, = (f'{root}{"_mek__shrt"}',
                   f'{root}{"_w__shrt"}') if de_ug else (f'{root}{"_mek_dec"}', f'{root}{"_w_t_dec"}',)
    mainUI(join(root,'_mek'),join(root,'_w_t'),join(rout,f'MW{VRS}'))
# различные DS(ах если бы - чисто воборьи и пушки) для быстро-быстрого паренья:
W, M, = None, None, 
WbyM, MbyW = {}, {}  #WbyM is  { HnW:{HnM:{номерв(HnM):номерв(HnW)}}} ...
def WM_mergeFromMultiPagePdf(srcW, srcM, outfld):
    #return 
    global W, M  # , rname
    if de_ug:
        global rname
        rname=DictFromFile(join(srcW or srcM,'rname'))#DictFromFile(join(root,'rname'))
    nm=buildDSmakingCake(  W := DictFromFile(join(srcW, 'wTotB')),
                        M := DictFromFile(join(srcM, 'mTotB')), outfld)
    return nm
pdfnum = 0
def bundlename(name,cs):#counters[m,w,wm]
        kvt=cs[0]+cs[1]+2*cs[-1]; #== печатных страниц
        tot=sum(cs)*(1+(1 if cs[-1] else 0))
        sps=tot-kvt
        return f'{name[2:]} ${str(bundle(*cs,kvt,sps,tot)).replace(" ","")}'
def savepdfW(doc, name):
    if (p := doc.page_count):
        global pdfnum
        doc.save(name, garbage=2, deflate=True)
        pdfnum = pdfnum+1
        print(timing.log(f'№{pdfnum:>03}', name))
def fromTo(doEmpty,src,pN,oname,x,dst):
    if(src):
        dst.insert_pdf(src, from_page=x.pN, to_page=x.pN, links=0, annots=0, final=False)
    elif doEmpty:
        dst.new_page()
    return f"Pg{tuple(makeCurPg(pN,oname,x))}"#.replace(' ','')
def makeCurPg(pN,oname,v):
    # as like in makeFakeNxtPg
    t={v._fields[i]:v[i] for i,fld in enumerate(v)}
    t['pN'],t['Hn']=pN,oname,
    return Pg(*t.values())
def inSubmergeW(prt, ofld, rname):
    pid = os.getpid()
    print(f'>>WW from {prt.index} {os.getpid()} {os.getcwd()}')
    WMdocByHn = {}
    print(f'{prt.index=:^3} weght:{prt.sum[0]:^17.3f} {pid=:^7}len={len(prt.lst):>4} ',
          f' '.join(f'{len(f.ll)}'for f in prt.lst), end=' ENDWW\n')
    ePg=makeEmptyPg()  
    for e in prt.lst:  # e is namedtuple('Wshort', 'Hn ll cs')
        Hn=e.Hn;    ewm=e.ll
        kkey=lambda l:l[0] and forCMP(l[0].adr) or forCMP(l[1].adr,'M')
        onamePdf=f'{join(ofld,rnm:=Hn[2:])}.pdf'
        if rnm[0]in ["№","Г","У"]: #"Пач-ин" #!!! ориентир наличие № :) AZAZA
            prf='000-'; onamePdf2=f'{join(ofld,prf+rnm)}.pdf'
            sG=set(forCMP(a[0].adr).blding()for a in ewm if a[0])
            oldEwm=ewm;ewm=[];onlyMEK=[]
            for a in oldEwm:
                if a[0]or(forCMP(a[1].adr,'M').blding() in sG):    ewm.append(a)
                else:                                               onlyMEK.append(a)
            if onlyMEK:
                r2=len(onlyMEK);e.cs[0]-=r2
                onameBnd2=f'{join(ofld,prf+bundlename(Hn,[r2,0,0]))}{typefilesOfdata}'
                pagestxt2 = open(onameBnd2, 'w')
                pN2=-1
                pagestxt2.write('[\n');  out2=fitz.open()
                onlyMEK[:]=sorted(onlyMEK,key=kkey) #lol всёж adr f а не adrNorm
                for x,y2 in onlyMEK:
                    t2=[fromTo(0,0,pN2:=pN2+1,onamePdf2,ePg,out2)]#x and inp,pN,onamePdf,x or ePg,out
                    try:
                        if y2.Hn not in WMdocByHn:
                            WMdocByHn[y2.Hn] = fitz.open(rname[y2.Hn])
                    except Exception as z:
                        raise(z)
                    t2.append(fromTo(r2,WMdocByHn[y2.Hn],pN2:=pN2+1,onamePdf2,y2,out2))
                    pagestxt2.write('[')
                    print(*t2,sep=',',end='],\n',file=pagestxt2)#.write(f"{str(t).replace(' ','')},\n") #lol
                savepdfW(out2, onamePdf2)
                pagestxt2.write(']')
                print(timing.log(f'{" ":<7}{pid:>5}', f'{pid:05}'), flush=True)
        onameBnd=f'{join(ofld,bundlename(Hn,e.cs))}{typefilesOfdata}'
        pagestxt = open(onameBnd, 'w')
        pN,inp =-1,fitz.open(rname[Hn]) #;counters=[0,0,0]
        pagestxt.write('[\n');  out=fitz.open()
        ewm[:]=sorted(ewm,key=kkey) #lol всёж adr f а не adrNorm
        l,r=e.cs[1]+e.cs[2],e.cs[0]+e.cs[2]
        for x,y in ewm:
            t=[]
            def doY():
                nonlocal pN
                if not y:
                    t.append(fromTo(r,0,pN:=pN+1,onamePdf,ePg,out))
                else:
                    try:
                        if y.Hn not in WMdocByHn:   WMdocByHn[y.Hn] = fitz.open(rname[y.Hn])
                    except Exception as z:
                        raise(z)
                    t.append(fromTo(r,WMdocByHn[y.Hn],pN:=pN+1,onamePdf,y,out))
            x and t.append(fromTo(l,inp,pN:=pN+1,onamePdf,x,out))
            doY()
            x or  t.append(fromTo(l,0,pN:=pN+1,onamePdf,ePg,out))#x and inp,pN,onamePdf,x or ePg,out
            x or  (t:=[t[1],t[0]])
            pagestxt.write('[')
            print(*t,sep=',',end='],\n',file=pagestxt)#.write(f"{str(t).replace(' ','')},\n") #lol
        savepdfW(out, onamePdf)
        pagestxt.write(']')
    print(timing.log(f'{" ":<7}{pid:>5}', f'{pid:05}'), flush=True)
def buildDSmakingCake(WW, MM, ofld):
    os.chdir(ofld); print(timing.log('3.-2', "buildWowDataStructureTM:"));  ToBad=[];   toR=[]
    for k,v in MM.items():
        if v.isBad: ToBad.append(v);    toR.append(k)
    for k in toR:del MM[k]
    toR=[]; print('Досохранение except:');    doc=fitz.open();    docName=f'{join(ofld,"except")}.pdf'
    for mmm in ToBad:
        try:
            if mmm.Hn not in WMdocByHn: WMdocByHn[mmm.Hn] = fitz.open(rname[mmm.Hn])
        except Exception as z:  raise(z)
        fromTo(1,WMdocByHn[mmm.Hn],-1,docName,mmm,doc)
    savepdfW(doc,docName)
    class sameBy():
        def __init__(self): self.wl,self.ml=list(),list()
        def __repr__(self):
            def slPg(lPg): return (f'{i:05}:{pg}'for i,pg in enumerate(lPg))
            def tS(lPg):return '\n'.join(slPg(lPg))
            lwl,lml=len(self.wl),len(self.ml)
            h=f'{lwl=},{lml=},{lp=}'
            return f'hhh{h}\nWL({lwl}):\n{tS(self.wl)}\nML({lml}):\n{tS(self.ml)}\n{h}\nhhh'
    Wlst= {} 
    def HarvestByAdr(WW,MM): 
        B2Ouf=defaultdict(set); mw=defaultdict(lambda:defaultdict(int));  Adr=defaultdict(sameBy);  U=set()# квитанция размещена
        pH=join(os.environ['USERPROFILE'],'Desktop','Hints')
        uni=set();edges=defaultdict(set);bad=defaultdict(set)
        old_edges=[];        old_bad=[];        old_uni=[];        new_edges=[]
        def getHints():
            os.makedirs(pH,exist_ok=1)
            if exists(fn:=join(pH,'Hints.txt')):
                for z in open(fn).readlines():
                    if (l:=(z:=z.strip('\n')).split('#')[0].replace(' ','')):
                        if  (   l:=l.partition('+'))[1]=='+':
                            edges[l[2]].add(l[0])
                            old_edges.append(z)
                        elif(l:=l[0].partition('-'))[1]=='-':
                            bad[l[2]].add(l[0])
                            old_bad.append(z)
                        else:
                            uni.add(l[0])
                            old_uni.append(z)
        def toOut(ouF,w,m,i=2):
            if ouF not in Wlst: Wlst[ouF]=Wshort(ouF, [], [0,0,0]) # [m,w,wm]
            F=Wlst[ouF];   
            if w and m: 
                F.ll[w.pN][1]=m;F.cs[1]-=1
                if w.pa not in edges[m.pa]: new_edges.append(f'{w.pa}+{m.pa} #{VRS} {w.Hn}:{w.pN:<4}*{m.pN:>4}:{m.Hn}')
            else:       F.ll.append([w,m])
            U.add(m); U.add(w); F.cs[i]+=1             
            if m:mw[m.Hn][m.pN]=ouF
        getHints()
        WinPos=defaultdict(list)
        for w in WW.values():
            toOut(w.Hn,w,0,1); 
            B2Ouf[forCMP(w.adr).blding()].add(w.Hn)
            if w.pa not in uni:
               Adr[w.adrNorm].wl.append(w)
               WinPos[w.pa].append(w)
        MMost=set()       
        for m in MM.values():
            if m.pa in uni:Adr[m.adrNorm].ml.append(m);continue
            if m.pa in edges and (wpa:=next(iter(edges[m.pa]))) in WinPos:
                fnd,w=0,WinPos[wpa][0]
                for i,v in enumerate((A:= Adr[w.adrNorm]).wl):# Не предполагаем что адресс общий всёж
                    if v==w:fnd=1;WinPos[wpa].pop(0);       toOut(w.Hn,A.wl.pop(i),m);break
                if fnd:continue
            MMost.add(m)
        for m in MMost:
            for i,w in enumerate((A:= Adr[m.adrNorm]).wl):
                if w.u == m.u and (w.pa not in bad[m.pa]):  toOut(w.Hn,A.wl.pop(i),m);break
            else:   A.ml.append(m)
        
        for  A in Adr.values():
            if len(A.wl)*len(A.ml)==1 and((m:=A.ml[0]).pa not in uni)and(w:=A.wl[0]).pa not in bad[m.pa]: 
                                                            toOut(w.Hn,w,m)
            else:set(toOut(next(iter(B2Ouf[B])),0,m,0)for m in  A.ml if(B:=forCMP(m.adr,'M').blding())in B2Ouf)
        for m in MM.values():
            if m.pN==0:     ouF=E[min(E.keys())] if(E:=mw[m.Hn])else m.Hn
            if E[m.pN]:     ouF=E[m.pN]
            if m not in U:                                  toOut(ouF,0,m,0)
        
        with open(join(pH,VRS+'.txt'),'w') as fn:
            for l in old_edges,old_bad,old_uni,new_edges: 
                print(*l,sep='\n',file=fn)
        ff=open('B2ouf','w')    
        for k in B2Ouf:
            if len(zzz:=B2Ouf[k])>1:
                print(f"Разнофайловый дом:{k:^77} файлы:{zzz}",file=ff)
        print(f'{B2Ouf=}')
        ff.close()
    HarvestByAdr(WW,MM)
    print(timing.log('3', "Построение листов"))
    #for Hn, fullpath in rname.items():  WMdocByHn[Hn] = fitz.open(fullpath)
    os.mkdir(unk:= join(ofld, "WMpdfs"))
    os.system(f'start "Квитанции с водой" "{unk}"')
    procs, chunks = [], [Nparts([0], [], i+1) for i in range(inN)] 
    for e in sorted(Wlst.values(),key=lambda e: len(e.ll), reverse=True):  # e is namedtuple('Wshort', 'weight Hn wm w')
        (fullpath := min(chunks)).sum[0] += len(e.ll)
        fullpath.lst.append(e)
    for chunk in chunks:
        proc = mp.Process(target=inSubmergeW, args=(chunk, unk, rname))
        procs.append(proc)
        proc.start()
    for proc in procs:  proc.join() 
    print(timing.log('totalW_data_merging', "ПарамПамПам"))
    print(f">WWW   end:{datetime.now()}")
    pprint.pprint(MbyW, width=99999999, stream=open(join(ofld, 'MbyW'), 'w'))
    print(timing.log('4_1', ":MbyW"))
    pprint.pprint(WbyM, width=99999999, stream=open(join(ofld, 'WbyM'), 'w'))
    print(timing.log('4_2', ":WbyM"))
    from  debundle import getS
    getS(unk);  rez=makeXLS(unk,VRSbs);   unk=join(unk,'');
    os.system(f'del "{unk}*{typefilesOfdata}"')
    print(timing.log('4_E', "Отсохронялись"))
    return rez
if __name__ == '__main__':
    mp.freeze_support()
    root = rezname.getArgOr(1, dirname(dirname(__file__)), 'Dir')
    SAGAread=rezname.getArgOr(2, ['doParseMEK','doParseWT','doParing']) #for real """TODO import ast;ast.literal_eval"""
    print(root);    print(f':\t Начало', timing.log('', f'{timing.pred-timing.base}'))
    main(join(root, ''))
    timing.ender()
