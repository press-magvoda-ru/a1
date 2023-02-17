import multiprocessing as mp,os, pprint, sys
from collections import defaultdict, namedtuple
from datetime import datetime
from functools import lru_cache
from itertools import chain
from os.path import basename, dirname, join
import fitz, rezname, timing
import os
from reparseWxMx import Hn, Pg, bundle, add2Hn, DictFromFile, name2str, prsM, prsW, rname, makeEmptyPg, makeFakeNxtPg
import inspect; __LINE__ = inspect.currentframe()
print(__LINE__.f_lineno);print(__LINE__.f_lineno)
#+1 or unk# +1 for de_ug purpose:
inN, de_ug =os.cpu_count()+1, 0 #+1 
#root=''
def mkmk(fld): # утилита для mainUI
    if not os.path.isdir(fld):
        os.mkdir(fld)
    os.chdir(fld)
    os.system(f'start "" "{fld}"')
def mainUI(in_srcM,in_srcW,in_fld):
    from PyQt5 import QtWidgets, uic
    frm_cls = uic.loadUiType(f"{os.path.dirname(__file__)}\guiForPairing.ui")[0]
    class mn_Window(QtWidgets.QMainWindow, frm_cls):
        def __init__(self, parent=None):
            QtWidgets.QMainWindow.__init__(self, parent)
            self.setupUi(self)
            self.b_srcM.setText(in_srcM) 
            self.b_srcW.setText(in_srcW) 
            self.b_fld.setText(in_fld) 
            self.b_srcM.clicked.connect(self.choose_srcM)
            self.b_srcW.clicked.connect(self.choose_srcW)
            self.b_fld.clicked.connect(self.choose_fld)
            self.b_chekMEK.clicked.connect(self.chekMEK)
            self.b_start_and_done.clicked.connect(self.run_run)
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
            srcM,srcW,fld=self.b_srcM.text(),self.b_srcW.text(),self.b_fld.text()
            mkmk(fld)
            stdout, sys.stdout = sys.stdout, open(f'{(nm:=rezname.rezname()+"_rep.1.txt")}','w')
            print(f'{rezname.rezname()}')
            if not os.path.isdir(fld):
                os.mkdir(fld)
            MMM=M_data_spliting(srcM,fld)
            print(f"общее количество страниц   :{MMM['pages']:^10}\n"
                  f"общее количество квитанций :{MMM['kvits']:^10}")
            sys.stdout.close()
            os.system(f'start "" {nm}')
            sys.stdout=stdout
        def run_run(self):
            srcM,srcW,fld=self.b_srcM.text(),self.b_srcW.text(),self.b_fld.text()
            mkmk(fld)
            print(srcM,srcW,fld)
            #HERE use SAGEread for 
            nm='';
            if not de_ug:
                M_data_spliting(srcM, fld) # если чек т.е есть mTotB был то воспользоваться УЖОЙным M_
                W_data_spliting(srcW, fld)
                pprint.pprint(rname, stream=open(
                    join(fld, name2str(f'{rname=}')), 'w'), width=333)  # nero are
                nm=WM_mergeFromMultiPagePdf(fld, fld, fld)
            else: # de_ug yap
                rootTotS=r'C:\AAA\MWrez_2023-02-17__14-35-06' #r"C:\AAA\MWrez_2023-02-16__08-35-37" 
                nm=WM_mergeFromMultiPagePdf(rootTotS, rootTotS, fld)# de_ug of doubling All
            os.system(nm)
            sys.exit()
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mn_Window()
    myWindow.show()
    app.exec()
    return ['','','']
Nparts = namedtuple('Nparts', 'sum lst index')
Wshort = namedtuple('Wshort', 'weight Hn wm w cs') # -замена семантики
# было(wm-список парных;w-список водных_только)? - стало(w cписок [w,m*];
#  wm-развёрнутый(раскрытый) список  собранный из участков 1 длины [w,0] либо участки из мек файла ([0,m]*,[w,m],[0,m]*)
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
@lru_cache(maxsize=256)
def pagesInPDF(a): return fitz.open(a).page_count
Mpages2time = {n: (0.004+0.005/2000*n)*n for n in range(9999)};""" ... из предположения что удвоение учетверяет ( хотя по факту утраивает)\
    \n словарь/список (пока нет) с аппроксимацией - число_страниц_файла->время_на_файл :"""
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
def lstInWithExtention(src,ext='.pdf'):
    lst=[]
    for r,d,f in os.walk(src):
        for file in f:
            if file.endswith(ext): lst.append(os.path.join(r,file))
    return lst
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
    add2Hn(lfiles := sorted(lstInWithExtention(src), key=pagesInPDF, reverse=True),Tp)
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
    mainUI(join(root,'_mek'),join(root,'_w_t'),join(rout,f'MW{rezname.rezname()}'))
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
        kvt=sum(cs)+cs[-1]; tot=2*sum(cs);  sps=tot-kvt
        return f'{name[2:]} ${str(bundle(*cs,kvt,sps,tot)).replace(" ","")}'
def savepdfW(doc, name):
    if (p := doc.page_count):
        global pdfnum
        doc.save(name, garbage=2, deflate=True)
        pdfnum = pdfnum+1
        print(timing.log(f'№{pdfnum:>03}', name))
def fromTo(src,pN,oname,x,dst):
    if(src):
        dst.insert_pdf(src, from_page=x.pN, to_page=x.pN, links=0, annots=0, final=False)
    else:
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
          f' '.join(f'{f.weight}'for f in prt.lst), end=' ENDWW\n')
    ePg=makeEmptyPg()  
    for e in prt.lst:  # e is namedtuple('Wshort', 'weight Hn wm w cs')
        Hn=e.Hn;    
        onamePdf=f'{join(ofld,Hn[2:])}.pdf'
        onameBnd=f'{join(ofld,bundlename(Hn,e.cs))}.py'
        pagestxt = open(onameBnd, 'w')
        pN,inp =-1,fitz.open(rname[Hn]) #;counters=[0,0,0]
        pagestxt.write('[\n');  out=fitz.open()
        for x,y in e.wm:
            t=[]
            if not x:
                t.append(fromTo(0,pN:=pN+1,onamePdf,ePg,out))#x and inp,pN,onamePdf,x or ePg,out
            else:
                t.append(fromTo(inp,pN:=pN+1,onamePdf,x,out))
            if not y:
                t.append(fromTo(0,pN:=pN+1,onamePdf,ePg,out))
            else:
                try:
                    if y.Hn not in WMdocByHn:
                        WMdocByHn[y.Hn] = fitz.open(rname[y.Hn])
                except Exception as z:
                    raise(z)
                t.append(fromTo(WMdocByHn[y.Hn],pN:=pN+1,onamePdf,y,out))
            #counters[2*int(bool(x))+int(bool(y)-1)]+=1
            pagestxt.write('[')
            print(*t,sep=',',end='],\n',file=pagestxt)#.write(f"{str(t).replace(' ','')},\n") #lol
        savepdfW(out, onamePdf)
        pagestxt.write(']')
    print(timing.log(f'{" ":<7}{pid:>5}', f'{pid:05}'), flush=True)

def buildDSmakingCake(WW, MM, ofld):
    os.chdir(ofld)  # на усях слу
    print(timing.log('3.-2', "buildWowDataStructureTM:"))
    # привет 202№!  тахионы ушли в путь
    class sameELS():
        def __init__(self):
            self.wl,self.ml,self.pairs=list(),list(),list()
    class posOfVinLwhat():
        def __init__(self,pos=0,typeL='_'):
            self.pos,self.t=pos,typeL #'wwm'.find(typeL)
    def Harvest(WW,MM):
        byEls=defaultdict(sameELS)
        for k, v in WW.items():
            byEls[v.els].wl+=[v]
        for k, v in MM.items():
            cur = byEls[v.els]
            if (not v.els): cur.ml += [v]; continue
            for i,e in enumerate(cur.wl): # единичное поэтому без lst =cur.wl.copy()
                if e.u == v.u: # пока инициалов достаточно 
                    cur.pairs += [[cur.wl.pop(i),v]] 
                    break
            else:
                cur.ml += [v]
        for k, cur in byEls.items():
            if not k:
                continue
            while cur.wl and cur.ml:
                cur.pairs +=[[cur.wl.pop(0),cur.ml.pop(0)]] #  не оптимально ибо с головы 
        v2posInl=defaultdict()#posOfVinLwhat)#make v2posInL great again:
        for k,cur in byEls.items(): #потом(очень потом)- слоты и индексы wl 0 wm-pairs 1  ml 2 
            for i,v in enumerate(cur.wl,0):
                v2posInl[v]=posOfVinLwhat(i,'w')
            for i,v in enumerate(cur.ml,0):
                v2posInl[v]=posOfVinLwhat(i,'m')
            for i,v in enumerate(cur.pairs,0):
                v2posInl[v[0]]=posOfVinLwhat(i,'wm')
                v2posInl[v[1]]=posOfVinLwhat(i,'wm')
        return byEls,v2posInl
    bdB,v2posInl, = Harvest(WW,MM)

    print(timing.log('3', "Построение словаря елс'ок с парнованием ежель чё"))
    for Hn, fullpath in rname.items():
        WMdocByHn[Hn] = fitz.open(fullpath)
        if Hn[0] == 'M':
            MbyW[Hn] = {'Sz':WMdocByHn[Hn].page_count,'WMed':set(),'p': set(range(WMdocByHn[Hn].page_count)),'S': defaultdict(int), }
    os.mkdir(unk:= join(ofld, "WMpdfs"))
    os.system(f'start "Квитанции с водой" "{unk}"')
    #словарь[файлов] -> валидных страниц МЭК список их 'all' и их "парных"-зацепленных 'wmz' - из него выставки в выходной:
    def makeMekAmbit(MM):
        AmbitByHn=dict()
        for v in MM.values():
            if not v.Hn in AmbitByHn:
                AmbitByHn[v.Hn]={'all':defaultdict(Pg),'wmz':[-1,pagesInPDF(rname[v.Hn])]}# если слева -1 то с префиксом; полуоткрытый интервал [-1,len)
            AmbitByHn[v.Hn]['all'][v.pN]=v
        return AmbitByHn
    MekAmbit=makeMekAmbit(MM)
    #Wshort = namedtuple('Wshort', 'weight Hn wm w') from Head 
    Wlst, usedWnames = [], set()
    # достройка карты с прициплением непрививязанных МЭК
    for v in WW.values():
        if (vHn := v.Hn) not in usedWnames:
            usedWnames.add(vHn)
            Wlst.append(Wshort([0], vHn, [], [],[0,0,0])) # cs is m,w,P
            z = WbyM[vHn] = {'c': 0, 'b': 0, 'S': defaultdict(int), }
        ou = Wlst[-1]  # ибо квитанции воды идут подряд пофайлово
        (cur := bdB[v.els])
        if (pos:=v2posInl[v]).t=='wm': #in pairs    
            www, mmm = cur.pairs[pos.pos]
            ou.w.append([www, mmm]);ou.cs[2]+=1 
            z['S'][(yHn := mmm.Hn)] += 1
            MbyW[yHn]['S'][www.Hn] += 1
            try:
                MbyW[yHn]['p'].remove(mmm.pN)
            except Exception as e:
                raise(e)
        else:
            ou.w.append([cur.wl.pop(0),0]);ou.cs[1]+=1 
            z['b'] += 1
        z['c'] += 1
    for ou in Wlst:
        ou.w.sort(key=lambda v:v[0].pN) # ну а вдруг водные чехарда
        for el in ou.w:
            if el[1]:
                curMekV=el[1]
                MekAmbit[curMekV.Hn]['wmz'].append(curMekV.pN)
    for Hn,mk in MekAmbit.items():
        mk['wmz'].sort()
    #инвариант незацепленности MekAmbit[Hn(pathМЭКfile)]['wmz'].__len__()==2
    for ou in Wlst:
        for el in ou.w:
            if not el[1]:
                ou.wm.append(el);#ou.cs см выше при ou.w
                continue
            curMekM=MekAmbit[el[1].Hn]
            cur_all,cur_wmz=curMekM['all'],curMekM['wmz']
            PosInWmz=cur_wmz.index(el[1].pN)
            if cur_wmz[PosInWmz-1]<0: #случай первого в файле == PozInWmz==1
                for i in range(el[1].pN):
                    if(mm:=cur_all[i]): # and while mm.pN<el[1].pN
                        ou.wm.append([0,mm]);ou.cs[0]+=1
            ou.wm.append(el)
            RightEdge=cur_wmz[PosInWmz+1]
            i=el[1].pN+1
            while i<RightEdge:
                if(mm:=cur_all[i]): # and while mm.pN<el[1].pN
                    ou.wm.append([0,mm]);ou.cs[0]+=1
                i+=1
        ou.weight[0] =len(ou.wm);#== sum(ou.cs)   # число листов
    #дописываем незацепленные Meк к Wlst
    IslandMek=[Hn for Hn in MekAmbit.keys() if len(MekAmbit[Hn]['wmz'])==2]
    print("Незацпленные  МЭК-файлы:",len(IslandMek))
    pprint.pprint(IslandMek,width=99999999)
    for Hn in IslandMek:
        if (vHn := Hn) not in usedWnames:
            usedWnames.add(vHn)
            Wlst.append(Wshort([0], vHn, [], [],[0,0,0])) # cs is m,w,P
        ou = Wlst[-1]
        for v in MekAmbit[Hn]['all'].values(): # исходим что страницы мек в pN возрастающем 
            ou.wm.append([0,v]);ou.cs[0]+=1
        ou.weight[0] =len(ou.wm)

    procs, chunks = [], [Nparts([0], [], i+1) for i in range(inN)] 
    for e in sorted(Wlst,key=lambda e: e.weight[0], reverse=True):  # e is namedtuple('Wshort', 'weight Hn wm w')
        (fullpath := min(chunks)).sum[0] += e.weight[0]
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
    #pprint.pprint(bdB,width=99999999, stream=open(join(ofld, 'bdB'), 'w'))
    print(timing.log('4_3', ":bdB"))
    def MKadrlist():
        adrlist=[]
        for k,v in bdB.items():
            for e in v['l']:
                adrlist.append(e[-1])
        adrlist.sort(key=lambda a:a.adr)
        pprint.pprint(adrlist, stream=open(join(ofld, 'adrlist'), 'w'))
    
    from  debundle import getS
    getS(unk)

    from generXLS import makeXLS
    rez=makeXLS(unk)
    print(timing.log('4_E', "Отсохронялись"))
    return rez
import obsolete
if __name__ == '__main__':
    mp.freeze_support()
    root = rezname.getArgOr(1, dirname(dirname(__file__)), 'Dir')
    SAGAread=rezname.getArgOr(2, ['doParseMEK','doParseWT','doParing']) #for real """TODO import ast;ast.literal_eval"""
    print(root)
    print(f':\t Начало', timing.log('', f'{timing.pred-timing.base}'))
    main(join(root, ''))
    timing.ender()
#TODO TODO норм логгер это что?
#TODO TODO изолировать∧стянуть∧вынести_в_синглтон_доступа∧абстрагировать имя мек-файлов