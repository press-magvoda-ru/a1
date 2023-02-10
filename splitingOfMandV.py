import multiprocessing as mp,os, pprint, sys
from collections import defaultdict, namedtuple
from datetime import datetime
from functools import lru_cache
from itertools import chain
from os.path import basename, dirname, join
import fitz, rezname, timing
from reparseWxMx import Hn, Pg, add2Hn, DictFromFile, name2str, prsM, prsW, rname
import inspect; __LINE__ = inspect.currentframe()
print(__LINE__.f_lineno);print(__LINE__.f_lineno)
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
            if not de_ug:
                M_data_spliting(srcM, fld) # если чек т.е есть mTotB был то воспользоваться УЖОЙным M_
                W_data_spliting(srcW, fld)
                pprint.pprint(rname, stream=open(
                    join(fld, name2str(f'{rname=}')), 'w'), width=333)  # nero are
                WM_mergeFromMultiPagePdf(fld, fld, fld)
            else: # de_ug yap
                WM_mergeFromMultiPagePdf(root, root, fld)# de_ug of doubling All
            sys.exit()
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mn_Window()
    myWindow.show()
    app.exec()
    return ['','','']
#+1 or unk# +1 for de_ug purpose:
inN, de_ug =os.cpu_count()+1, 0  +1 
Nparts = namedtuple('Nparts', 'sum lst index')
Wshort = namedtuple('Wshort', 'weight Hn wm w') # -замена семантики
# было(wm-список парных;w-список водных_только)? - стало(w cписок [w,m*];
#  wm-развёрнутый(раскрытый) список  собранный из участков 1 длины [w,0] либо участки из мек файла ([0,m]*,[w,m],[0,m]*)
Mfrom, Wfrom, mainpid = {}, {}, os.getpid()
def dirend(pathofdir): return join(pathofdir, '')
def LinesOfFileName(pathofFile): return open(pathofFile).read().splitlines()
@lru_cache(maxsize=999)
def weightMek(a):
    try:
        if ((rl := fitz.open(a).page_count))==(nm := int(basename(a).split('-')[4])): return nm
    except:
        print(f'!!!Файл:{a} - Не форматное имя  +{rl} к различению общего числа (страниц VS квитанций')
        return 0         #TODO write in table bads of mek-file-pdf with massage
    print(f'!!!Файл:{a} из имени: {nm} по факту: {rl}  имя не != содержимому')
    return rl
@lru_cache(maxsize=256)
def weightWT(a): return fitz.open(a).page_count
Mpages2time = {n: (0.004+0.005/2000*n)*n for n in range(9999)}# ... из предположения что удвоение учетверяет ( хотя по факту утраивает)\n# словарь/список (пока нет) с аппроксимацией - число_страниц_файла->время_на_файл :
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
        return sum(weightWT(f) for f in lfiles)
    return {'of':of,'kvits':numOfGoodPages,'pages':f(lfiles)} # namedtuple in next season :)
def inSubProcW(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.index} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'W{prt.index:>03}', 'w')  # {pid:>6}
    if (prt.index == 1):
        pagestxt.write('{')
    print(f'{prt.index=:^3} weght:{prt.sum[0]:^17.3f} {pid=:^7}len={len(prt.lst):>4} ',
          f' '.join(f'{weightWT(f)}'for f in prt.lst), end=' END\n')
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
    add2Hn(lfiles := sorted(lstInWithExtention(src), key=weightWT, reverse=True),Tp)
    base, procs, chunks, = 0, [], toNparts(lfiles, inN, Wpages2time, weightWT)
    for chunk in chunks:
        proc = mp.Process(target=inSubProcW, args=(Tp, base, chunk))
        procs.append(proc)
        proc.start()
        base += SumMap(weightWT, chunk.lst)
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
        rname=DictFromFile(join(root,'rname'))
    buildDSmakingCake(  W := DictFromFile(join(srcW, 'wTotB')),
                        M := DictFromFile(join(srcM, 'mTotB')), outfld)
pdfnum = 0
def savepdf2(doc, name):
    global pdfnum
    doc.save(name, garbage=2, deflate=True)
    pdfnum = pdfnum+1
    print(timing.log(f'№{pdfnum:>03}', name))
def savepdfW(doc, name, fld, sz, sbj=2):
    if (p := doc.page_count):
        p //= sbj
        savepdf2(
            doc, join(fld, z := f'{name[2:]:<15}({sz:05}){sbj:^3}{p:05}.pdf'))
def savepdfM(doc, name, fld, sbj=''):
    if (p := doc.page_count):
        savepdf2(doc, join(fld, z := f'{name:0}{sbj:^3}{p:05}.pdf'))
 
def fromTo(src, p, dst):
    dst.insert_pdf(src, from_page=p, to_page=p, links=0, annots=0, final=False)
def inSubmergeW(prt, unk, rname):
    pid = os.getpid()
    print(f'>>WW from {prt.index} {os.getpid()} {os.getcwd()}')
    Mfrom = {}
    # pagestxt = open(f'W{prt.index:>03}', 'w')  # {pid:>6}
    print(f'{prt.index=:^3} weght:{prt.sum[0]:^17.3f} {pid=:^7}len={len(prt.lst):>4} ',
          f' '.join(f'{f.weight}'for f in prt.lst), end=' ENDWW\n')
    for e in prt.lst:  # e is namedtuple('Wshort', 'weight Hn wm w')
        sz = (inp := fitz.open(rname[e.Hn])).page_count
        out= fitz.open()
        for x,y in e.wm:
            if not x:
                out.new_page()
            else:
                fromTo(inp, x.pN, out)
            if not y:
                out.new_page()
            else:
                if y.Hn not in Mfrom:
                    Mfrom[y.Hn] = fitz.open(rname[y.Hn])
                fromTo(Mfrom[y.Hn], y.pN, out)
        savepdfW(out, e.Hn, unk, sz)
    print(timing.log(f'{" ":<7}{pid:>5}', f'{pid:05}'), flush=True)
def inSubMekOnes(unk, kMv, i):
    t = 0
    for k,(v,l) in kMv.items():
        if t % inN == i:
            z = fitz.open(v)
            z.select(l)  # lol set is not seq for pymupdf
            print(f'MekOnes prt:{i},counter {t}')
            savepdfM(z, f"{i:02}_{basename(v).split('.')[0]}", unk, 1)
        t += 1
def buildDSmakingCake(WW, MM, ofld):
    os.chdir(ofld)  # на усях слу
    print(timing.log('3.-2', "buildWowDataStructureTM:"))
    # привет 202№!  тахионы ушли в путь
    class sameELS():
        def __init__(self):
            self.wl=list()
            self.ml=list()
            self.pairs=list()
            #w,m,wm -разбивка по видам в количествах; 
    class posOfVinLwhat():
        def __init__(self,pos=0,typeL='_'):
            self.pos=pos
            self.t=typeL #'wwm'.find(typeL)
    def Harvest(WW,MM):
        byEls=defaultdict(sameELS)
        for k, v in WW.items():
            cur = byEls[v.els]
            cur.wl += [v]
        for k, v in MM.items():
            #if v.els not in byEls: byEls[v.els] = {'c': 0, 'w': 0, 'm': 0, 'wm': 0, 'l': []}
            cur = byEls[v.els]
            if (not v.els):
                cur.ml += [v]
                continue
            for i,e in enumerate(cur.wl): # единичное поэтому без lst =cur.wl.copy()
                if e.u == v.u: # пока инициалов достаточно 
                    cur.pairs += [[cur.wl.pop(i),v]] 
                    break
            else:
                cur.ml += [v]
        for k, v in byEls.items():
            if not k:
                continue
            cur=v
            while cur.wl and cur.ml:
                #в тупую:
                cur.pairs +=[[cur.wl.pop(0),cur.ml.pop(0)]] #  не оптимально ибо с головы - надежда на реализацию "вирт динамического " массива которые в питоне списком зовётся
        #make v2posInL great again:
        v2posInl=defaultdict()#posOfVinLwhat)
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

    print(timing.log('3', "Построение словаря елс'ок с парнованием ежель чё")) # сборка адрессного стола чиста ради прикидки чё как
    for k, v in rname.items():
        if k[0] == 'M':
            Mfrom[k] = fitz.open(v)
            MbyW[k] = {'Sz':Mfrom[k].page_count,'WMed':set(),'p': set(range(Mfrom[k].page_count)),'S': defaultdict(int), }
        #if k[0] == 'W':            Wfrom[k] = fitz.open(v)
    os.mkdir(unk := join(ofld, "WMpdfs"))
    os.system(f'start "Квитанции с водой" "{unk}"')
    # перегрупировка пар из bdB в Wlst[]
    #словарь[файлов] -> валидных страниц МЭК список их 'all' и их "парных"-зацепленных 'wmz' - из него выставки в выходной:
    def makeMekAmbit(MM):
        AmbitByHn=dict()
        for v in MM.values():
            if not v.Hn in AmbitByHn:
                length=weightWT(rname[v.Hn])
                AmbitByHn[v.Hn]={'all':defaultdict(int),'wmz':[-1,length]}# если слева -1 то с префиксом; полуоткрытый интервал [-1,len)
            AmbitByHn[v.Hn]['all'][v.pN]=v
        #for k in AmbitByHn: AmbitByHn[k]['all'].sort(key=lambda x:x.pN)
        return AmbitByHn
    MekAmbit=makeMekAmbit(MM)
    #Wshort = namedtuple('Wshort', 'weight Hn wm w') from Head 
    Wlst, usedWnames = [], set()
    # достройка карты с прициплением непрививязанных МЭК
    for k, v in WW.items():
        if (vHn := v.Hn) not in usedWnames:
            usedWnames.add(vHn)
            Wlst.append(Wshort([0], vHn, [], []))
            z = WbyM[vHn] = {'c': 0, 'b': 0, 'S': defaultdict(int), }
        ou = Wlst[-1]  # ибо квитанции воды идут подряд пофайлово
        (cur := bdB[v.els])
        if (pos:=v2posInl[v]).t=='wm': #in pairs    
            www, mmm = cur.pairs[pos.pos]
            ou.w.append([www, mmm]) 
            z['S'][(yHn := mmm.Hn)] += 1
            MbyW[yHn]['S'][www.Hn] += 1
            MbyW[yHn]['p'].remove(mmm.pN)
        else:
            try:
                
                www = cur.wl.pop(0)
            except Exception as e:
                print(f'{pos=}')
                raise e

            ou.w.append([www,0]) 
            z['b'] += 1
        z['c'] += 1
    #второй проход с составлением окончательных карт-описей выходных файлов двухсторон:
    #WTAmbit=dict()
    for ou in Wlst:
        ou.w.sort(key=lambda v:v[0].pN) # ну а вдруг водные чехарда
        #достройка wmz
        for el in ou.w:
            if el[1]:
                curMekV=el[1]
                MekAmbit[curMekV.Hn]['wmz'].append(curMekV.pN)
    for k,mk in MekAmbit.items():
        mk['wmz'].sort()
    #инвариант незацепленности MekAmbit[Hn(pathМЭКfile)]['wmz'].__len__()==2
    for ou in Wlst:
        for el in ou.w:
            if not el[1]:
                ou.wm.append(el)
                continue
            curMek=MekAmbit[el[1].Hn]
            cur_all,cur_wmz=curMek['all'],curMek['wmz']
            PosInWmz=cur_wmz.index(el[1].pN)
            if cur_wmz[PosInWmz-1]<0: #случай первого в файле == PozInWmz==1
                for i in range(el[1].pN):
                    if(v:=cur_all[i]):
                        ou.wm.append([0,v])
            ou.wm.append(el)
            RightEdge=cur_wmz[PosInWmz+1]
            i=el[1].pN+1
            while i<RightEdge:
                if(v:=cur_all[i]):
                    ou.wm.append([0,v])
                i+=1
    for e in Wlst:
        e.weight[0] =len(e.wm)  
    procs, chunks = [], [Nparts([0], [], i+1) for i in range(inN)] 
    for e in sorted(Wlst,key=lambda e: e.weight[0], reverse=True):  # e is namedtuple('Wshort', 'weight Hn wm w')
        (v := min(chunks)).sum[0] += e.weight[0]
        v.lst.append(e)
    for chunk in chunks:
        proc = mp.Process(target=inSubmergeW, args=(chunk, unk, rname))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join() 
    
    print(timing.log('totalW_data_merging', "ПарамПамПам"))
    print(f">WWW   end:{datetime.now()}")
   #TODO случай чисто нечётных мэк файлов - вставка 0-чётных страниц вместо 
   #росписи несопоставленных(часть размажется по зацепленным пачкам воды - логика ХЗ1) 
    def makingMekOnes():
        os.mkdir(unk := join(ofld, 'MekOnes'))
        procs, = [],
        rnr = {k: (v, list(MbyW[k]['p']))
            for k, v in rname.items() if k[0] == 'M' and MbyW[k]['p']}
        for i in range(inN):
            proc = mp.Process(target=inSubMekOnes, args=(unk, rnr, i))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
    #makingMekOnes()
    #pprint.pprint({k: {'p': (len(v['p']), v['p']), 'S': dict(v['S'])}for k, v in MbyW.items()}, width=99999999,stream=open(join(ofld, 'MbyW'), 'w'))
    print(timing.log('4_1', ":MbyW"))
    #pprint.pprint(WbyM, width=99999999, stream=open(join(ofld, 'WbyM'), 'w'))
    print(timing.log('4_2', ":WbyM"))
    print('bdB:')
    #pprint.pprint({k: (len(v['l']), v) for k, v in bdB.items() if len(v['l']) > 1}, stream=open(join(ofld, 'bdB'), 'w'))
    print(timing.log('4_3', ":bdB"))
    def MKadrlist():
        adrlist=[]
        for k,v in bdB.items():
            for e in v['l']:
                adrlist.append(e[-1])
        adrlist.sort(key=lambda a:a.adr)
        pprint.pprint(adrlist, stream=open(join(ofld, 'adrlist'), 'w'))
    print(timing.log('4_E', "Отсохронялись"))
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