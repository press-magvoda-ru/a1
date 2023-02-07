import multiprocessing as mp
import os, pprint, sys
from collections import defaultdict, namedtuple
from datetime import datetime
from functools import lru_cache
from itertools import chain
from os.path import basename, dirname, join
import fitz, rezname, timing
from reparseWxMx import Hn, Pg, add2Hn, name2str, prsM, prsW, rname
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
            M_data_spliting(srcM, fld) # если чек т.е есть mTotB был то воспользоваться УЖОЙным M_
            W_data_spliting(srcW, fld)
            pprint.pprint(rname, stream=open(
                join(fld, name2str(f'{rname=}')), 'w'), width=333)  # nero are
            WM_mergeFromMultiPagePdf(fld, fld, fld)
            sys.exit()
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mn_Window()
    myWindow.show()
    app.exec()
    return ['','','']
inN, de_ug =os.cpu_count()+1, 0 
Nparts = namedtuple('Nparts', 's c i')
Wshort = namedtuple('Wshort', 'weight Hn wm w')
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
# ... из предположения что удвоение учетверяет ( хотя по факту утраивает)
# словарь/список (пока нет) с аппроксимацией - число_страниц_файла->время_на_файл :
Mpages2time = {n: (0.004+0.005/2000*n)*n for n in range(9999)}
# {k: k for k in range(12000)}
# (0.004+0.006/2000*n)*n for n in range(9999)}
Wpages2time = {n: n for n in range(9999)}
def SumMap(wf, l): return sum(map(wf, l))
def toNparts(lfs, n, p2t, wf):
    """Разбивка {lfs} на {n} близковзвешенных по сумме {p2t[wf(i)]} частей"""  # if n < 2: return [lfs]
    rez = [Nparts([0], [], i+1) for i in range(n)]
    for e in lfs:
        (v := min(rez)).s[0] += p2t[wf(e)]
        v.c.append(e)
    return rez
def lstInWithExtention(src,ext='.pdf'):
    lst=[]
    for r,d,f in os.walk(src):
        for file in f:
            if file.endswith(ext): lst.append(os.path.join(r,file))
    return lst
def inSubProcM(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.i} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'M{prt.i:>03}', 'w')  # {pid:>6}
    if (prt.i == 1):  # само пикленье Рика
        pagestxt.write('{\n')
    print(f'{prt.i=:^3} weght:{prt.s[0]:^17.3f} {pid=:^7}len={len(prt.c):>4} ',
          f' '.join(f'{weightMek(f)}'for f in prt.c), end=' END\n')
    for inp in (fitz.open(f) for f in prt.c):
        Name = Hn(inp.name)
        for p in range(szInp := inp.page_count):
            pagestxt.write(
                f'{(i := i+1):>6}:{prsM(inp.get_page_text(p), Name, p)},\n')
        print(timing.log(szInp, Name))
    if (prt.i == inN):
        pagestxt.write('}')
    print(timing.log(f'{i-base:<7}{pid:>5}', f'{pid:05}'), flush=True)
def M_data_spliting(src, of):
    src, Tp, = dirend(src), 'M',
    stdout, sys.stdout = sys.stdout, open((of := of+f'\\_{Tp}{rezname.rezname()}')+'.txt', 'w')
    print(f">{Tp} start: {datetime.now()}")
    print(timing.log(f'mainpid', f':{mainpid=:05} {inN=:^20}'), flush=True)
    add2Hn(lfiles := sorted(lstInWithExtention(src), key=weightMek, reverse=True))
    (base, procs, chunks,) = (0, [], toNparts(lfiles, inN, Mpages2time, weightMek))
    for chunk in chunks:  # [:-1]):
        proc = mp.Process(target=inSubProcM, args=(Tp, base, chunk))
        procs.append(proc)
        proc.start()
        base += SumMap(weightMek, chunk.c)
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
        return sum(fitz.open(f).page_count for f in lfiles)
    return {'of':of,'kvits':numOfGoodPages,'pages':f(lfiles)} # namedtuple in next season :)
def inSubProcW(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.i} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'W{prt.i:>03}', 'w')  # {pid:>6}
    if (prt.i == 1):
        pagestxt.write('{')
    print(f'{prt.i=:^3} weght:{prt.s[0]:^17.3f} {pid=:^7}len={len(prt.c):>4} ',
          f' '.join(f'{weightWT(f)}'for f in prt.c), end=' END\n')
    for inp in (fitz.open(f) for f in prt.c):
        Name = Hn(inp.name)
        for p in range(szInp := inp.page_count):
            pagestxt.write(
                f'{(i := i+1):>6}:{prsW(inp.get_page_text(p),Name, p)},\n')
        print(timing.log(szInp, Name))
    if (prt.i == inN):
        pagestxt.write('}')
    print(timing.log(f'{i-base:<7}{pid:>5}', f'{pid:05}'), flush=True)
def W_data_spliting(src, of):
    src, Tp,  = dirend(src), 'W',
    stdout, sys.stdout = sys.stdout, open(
        (of := of+f'\\_{Tp}{rezname.rezname()}')+'.txt', 'w')
    print(f">{Tp} start:{datetime.now()}")
    print(timing.log(f'mainpid', f':{mainpid=:05} {inN=:^20}'), flush=True)
    add2Hn(lfiles := sorted(lstInWithExtention(src), key=weightWT, reverse=True))
    base, procs, chunks, = 0, [], toNparts(lfiles, inN, Wpages2time, weightWT)
    for chunk in chunks:
        proc = mp.Process(target=inSubProcW, args=(Tp, base, chunk))
        procs.append(proc)
        proc.start()
        base += SumMap(weightWT, chunk.c)
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
W, M, bdB = None, None, defaultdict(list)
WbyM = {}  # { HnW:{HnM:{номерв(HnM):номерв(HnW)}}} ...
MbyW = {}


def WM_mergeFromMultiPagePdf(srcW, srcM, outfld):
    global W, M  # , rname
    def getPgs(path):
        f = open(path)
        txt = f.read()
        rez = eval(txt)  # читаем словарь - куда деваться
        return rez
    buildWowDataStructureTM(W := getPgs(join(srcW, 'wTotB')),
                            M := getPgs(join(srcM, 'mTotB')), outfld)
    # rname = getPgs(join(outfld, name2str(f'{rname=}')))

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
    print(f'>>WW from {prt.i} {os.getpid()} {os.getcwd()}')
    Mfrom = {}

    # pagestxt = open(f'W{prt.i:>03}', 'w')  # {pid:>6}
    print(f'{prt.i=:^3} weght:{prt.s[0]:^17.3f} {pid=:^7}len={len(prt.c):>4} ',
          f' '.join(f'{f.weight}'for f in prt.c), end=' ENDWW\n')

    for e in prt.c:  # e is namedtuple('Wshort', 'weight Hn wm w')
        sz = (inp := fitz.open(rname[e.Hn])).page_count
        out, out1 = fitz.open(), fitz.open()
        for x, y in e.wm:
            fromTo(inp, x.pN, out)
            if y.Hn not in Mfrom:
                Mfrom[y.Hn] = fitz.open(rname[y.Hn])
            fromTo(Mfrom[y.Hn], y.pN, out)
        savepdfW(out, e.Hn, unk, sz)
        for x in e.w:
            fromTo(inp, x.pN, out1)
        savepdfW(out1, e.Hn, unk, sz, 1)
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


def buildWowDataStructureTM(WW, MM, ofld):
    os.chdir(ofld)  # на усях слу
    print(timing.log('3.-2', "buildWowDataStructureTM:"))
    def mkAllByAdrs():
        AllByAdrs = []
        for k, v in chain(WW.items(), MM.items()):
            AllByAdrs.append(v)  # или тут   # собственно здесь нужное отображение втулить из W|M строк адресса в "норм"
        def simpleAdr(v):
            return v.adr.replace('корп.', '%').replace(',кв.', ' ').replace(',д.', ' ')\
                .replace(',д.', ' ').replace('.', ' ').split(' ', 1)[-1].replace(',', ' ').strip()
        AllByAdrs.sort(key=simpleAdr)
        print(timing.log('3.-1builded', ":AllByAdrs:"))
        print('AllByAdrs:')
        pprint.pprint(AllByAdrs, stream=(ou := open('AllByAdrs.dict', 'w')))
        ou.close()
        print(timing.log('3.-1', ":AllByAdrs"))
    # привет 202№!  тахионы ушли в путь
    for k, v in WW.items():
        if v.els not in bdB:
            bdB[v.els] = {'c': 0, 'w': 0, 'm': 0, 'wm': 0, 'l': []}
        cur = bdB[v.els]
        cur['c'] += 1
        cur['w'] += 1
        cur['l'].append([cur['c'], 1, v])
    for k, v in MM.items():
        if v.els not in bdB:
            bdB[v.els] = {'c': 0, 'w': 0, 'm': 0, 'wm': 0, 'l': []}
        cur = bdB[v.els]
        cur['c'] += 1
        if (not v.els):
            cur['m'] += 1
            cur['l'].append([cur['c'], 2, v])
            continue
        for e in cur['l']:
            if e[1] == 1 and e[2].u == v.u:  # логика парности, можно так же  игнорируя u  сличать sq
                #  и вообще глобально игнорируя els сопоставлять по приведённым adr
                #  чудеса сии - ща сборка по парам - добавить сборку в W-файлам для дальнейшего жнивья в 2-3 паралели(2.5 гига на)
                cur['w'] -= 1
                cur['wm'] += 1
                e[1] = 3
                e.append(v)
                break
        else:
            cur['m'] += 1
            cur['l'].append([cur['c'], 2, v])
    # сборка парных в  wm=X w=1 m=1 # таковых вроде всего 293 по ноябрю можно и счётчик тут для
    for k, v in bdB.items():
        if (cur := v)['w'] == 1 and cur['m'] == 1:
            for e in cur['l']:
                if e[1] == 1:   # очевидно непарный M в конце. при пакетном все W затем все M
                    e[1] = 3;e.append(cur['l'].pop()[-1]);cur['w'] -= 1;cur['m'] -= 1;cur['wm']+1;break
    # TODO? here on bdB сопоставление по адресам (по первости только среди безelsных)
    # ---
    print(timing.log('3', "Построение словаря елс'ок с парнованием ежель чё")) # сборка адрессного стола чиста ради прикидки чё как
    for k, v in rname.items():
        if k[0] == 'M':
            Mfrom[k] = fitz.open(v)
            MbyW[k] = {'p': set(range(Mfrom[k].page_count)),
                       'S': defaultdict(int), }
        if k[0] == 'W':
            Wfrom[k] = fitz.open(v)
    os.mkdir(unk := join(ofld, "WMpdfs"))
    os.system(f'start "Квитанции с водой" "{unk}"')
    # перегрупировка пар из bdB в Wlst[]
    Wlst, usedWnames = [], set()
    for k, v in WW.items():
        if (vHn := v.Hn) not in usedWnames:
            usedWnames.add(vHn)
            Wlst.append(Wshort([0], vHn, [], []))
            z = WbyM[vHn] = {'c': 0, 'b': 0, 'S': defaultdict(int), }
        ou = Wlst[-1]
        (cur := bdB[v.els])
        if cur['wm'] and cur['l'][0][1] == 3:
            cur['wm'] -= 1
            x, y = cur['l'].pop(0)[-2:]
            # тут доп  можно передавать причину матчинга из ~~ [0]
            ou.wm.append([x, y])
            z['S'][(yHn := y.Hn)] += 1
            MbyW[yHn]['S'][x.Hn] += 1
            MbyW[yHn]['p'].remove(y.pN)
        else:
            x = (tt := cur['l'].pop(0))[-1]
            ou.w.append(x)
            z['b'] += 1
            cur['l'].append(tt)  # kekeke for [num,1,w]
        z['c'] += 1
    for e in Wlst:
        e.weight[0] = 2*len(e.wm)+len(e.w)  # чисто просто ага  # не факт?!(см .s :)) что поля в порядке имен типа :0
    Wlst.sort(key=lambda e: e.weight[0], reverse=True)
    procs, chunks = [], [Nparts([0], [], i+1)
                         for i in range(inN)]  # ибо память ram?
    for e in Wlst:  # e is namedtuple('Wshort', 'weight Hn wm w')
        (v := min(chunks)).s[0] += e.weight[0]
        v.c.append(e)
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
    def HEREOTHER1():
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
    pprint.pprint(
        {k: {'p': (len(v['p']), v['p']), 'S': dict(v['S'])}for k, v in MbyW.items()}, width=99999999,
        stream=open(join(ofld, 'MbyW'), 'w'))
    print(timing.log('4_1', ":MbyW"))
    pprint.pprint(WbyM, width=99999999, stream=open(join(ofld, 'WbyM'), 'w'))
    print(timing.log('4_2', ":WbyM"))
    print('bdB:')
    pprint.pprint({k: (len(v['l']), v)
                  for k, v in bdB.items() if len(v['l']) > 1}, stream=open(join(ofld, 'bdB'), 'w'))
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
    print(f':\t Начало', timing.log('', f'{timing.pred-timing.base}'))
    main(join(root, ''))
    timing.ender()