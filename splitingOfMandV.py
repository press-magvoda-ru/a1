from reparseWxMx import prsM, prsW, Pg, Hn, rname, name2str, add2Hn
from collections import namedtuple
from os.path import dirname, join, basename
import timing
import pprint
import rezname
import fitz
import os
import sys
import multiprocessing as mp
from datetime import datetime
from functools import lru_cache
from itertools import chain
from collections import defaultdict


def mainUI(in_srcM,in_srcW,in_fld):
    from PyQt5 import QtWidgets, uic
    def baseof(path):
        return  os.path.dirname(path)
    frm_cls = uic.loadUiType(f"{baseof(__file__)}\guiForPairing.ui")[0]
    class mn_Window(QtWidgets.QMainWindow, frm_cls):
        def __init__(self, parent=None):
            QtWidgets.QMainWindow.__init__(self, parent)
            self.setupUi(self)
            self.lb_srcM.text=self.srcM=in_srcM.replace('/','\\')
            self.lb_srcW.text=self.srcW=in_srcW.replace('/','\\')
            self.lb_fld.text=self.fld=in_fld.replace('/','\\')
            self.pButt_srcM.clicked.connect(self.choose_srcM)
            self.pButt_srcW.clicked.connect(self.choose_srcW)
            self.pButt_fld.clicked.connect(self.choose_fld)
            self.pButt_start_and_done.clicked.connect(self.run_run)
        def choose_srcM(self):
            #self.lb_srcM.text=
            self.srcM=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\') or self.srcM
            self.pButt_srcM.setText(self.srcM)
        def choose_srcW(self):
            self.srcW = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\') or self.srcW
            self.pButt_srcW.setText(self.srcW)
        def choose_fld(self):
            self.fld = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).replace('/','\\') or self.fld
            self.pButt_fld.setText(self.fld)
        def run_run(self):
            if not os.path.isdir(self.fld):
                os.mkdir(self.fld)
            os.chdir(self.fld)
            os.system(f'start "" "{self.fld}"')
            print(self.srcM,self.srcW,self.fld)
            M_data_spliting(self.srcM, self.fld)
            W_data_spliting(self.srcW, self.fld)
            pprint.pprint(rname, stream=open(
                join(self.fld, name2str(f'{rname=}')), 'w'), width=333)  # nero are
            WM_mergeFromMultiPagePdf(self.fld, self.fld, self.fld)
            exit()







    app = QtWidgets.QApplication(sys.argv)
    myWindow = mn_Window()
    myWindow.show()
    app.exec()
    # exit()
    return ['','','']

inN, = 9,
de_ug = None
#de_ug = 1

Nparts = namedtuple('Nparts', 's c i')
Wshort = namedtuple('Wshort', 'weight Hn wm w')
Mfrom, Wfrom = {}, {}

(mainpid,) = (os.getpid(),)
def dirend(pathofdir): return join(pathofdir, '')
def LinesOfFileName(pathofFile): return open(pathofFile).read().splitlines()


@lru_cache(maxsize=999)
def weightMek(a):
    if (nm := int(basename(a).split('-')[4])) == (rl := fitz.open(a).page_count):
        return nm
    print(
        f'!!!Файл:{a} из имени: {nm} по факту: {rl}  оно(кол-во) !=')
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


def inSubProcM(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.i} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'M{prt.i:>03}', 'w')  # {pid:>6}
    if (prt.i == 1):  # само пикленье Рика
        pagestxt.write('{')
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

    stdout, sys.stdout = sys.stdout, open(
        (of := of+f'\\_{Tp}{rezname.rezname()}')+'.txt', 'w')
    print(f">{Tp} start: {datetime.now()}")
    print(timing.log(f'mainpid', f':{mainpid=:05} {inN=:^20}'), flush=True)
    add2Hn(lfiles := sorted(
        os.popen(f'dir {src}/s/b|wsl grep pdf').read().splitlines(), key=weightMek, reverse=True))
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
    return of


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
    add2Hn(lfiles := sorted(os.popen(
        f'dir {src}/s/b|wsl grep -v Сопро|wsl grep pdf').read().splitlines(), key=weightWT, reverse=True))
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
    # тЭсто сливание сразу из pdf
    srcM, srcW, = (f'{root}{"_mek_nov_shrt"}',
                   f'{root}{"_w_nov_shrt"}') if de_ug else (f'{root}{"_mek_dec"}', f'{root}{"_w_t_dec"}',)
                   #_mek_dec
                   #_mek_dec_1ZYX
    print(root, rout, srcM, srcW, sep="\t")
    mainUI(srcM,srcW,join(rout,f'MW{rezname.rezname()}'))
    



# различные DS(ах если бы - чисто воборьи и пушки) для быстро-быстрого паренья:
W, M, bdB = None, None, defaultdict(list)
bdByAdr = defaultdict(list)
Wpa, Mpa = defaultdict(list), defaultdict(list)
emptyEls = []
# outFileName = 'bdB.defaultdict.txt'
Wfa, Mfa = defaultdict(list), defaultdict(list)

# WfaMfa - таблица пересечений - список общих(парных) в возрастающем по Wfa номерам - пора бы и pandas подсобить сюдыть
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
    None


pdfnum = 0


def savepdf2(doc, name):
    global pdfnum
    doc.save(name, garbage=2, deflate=True)
    pdfnum = pdfnum+1
    print(timing.log(f'№{pdfnum:>03}', name))


def savepdfW(doc, name, fld, sz, sbj=2):
    #sz=sz or WbyM[name]["c"]
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
    AllByAdrs = []
    for k, v in chain(WW.items(), MM.items()):
        AllByAdrs.append(v)  # или тут
    # собственно здесь нужное отображение втулить из W|M строк адресса в "норм"

    def simpleAdr(v):
        return v.adr.replace('корп.', '%').replace(',кв.', ' ').replace(',д.', ' ')\
            .replace(',д.', ' ').replace('.', ' ').split(' ', 1)[-1].replace(',', ' ').strip()

    AllByAdrs.sort(key=simpleAdr)
    print(timing.log('3.-1builded', ":AllByAdrs:"))
    print('AllByAdrs:')
    pprint.pprint(AllByAdrs, stream=(ou := open('AllByAdrs.dict', 'w')))
    ou.close()
    print(timing.log('3.-1', ":AllByAdrs"))

    # привет 202№!

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
                if e[1] == 1:
                    e[1] = 3
                    # очевидно непарный M в конце. при пакетном все W затем все M
                    e.append(cur['l'].pop()[-1])
                    cur['w'] -= 1
                    cur['m'] -= 1
                    cur['wm']+1
                    break

    # here on bdB сопоставление по адресам (по первости только среди безelsных)
    # ---

    print(timing.log('3', "Построение словаря елс'ок с парнованием ежель чё"))
    # сборка адрессного стола чиста ради прикидки чё как

    for k, v in rname.items():
        if k[0] == 'M':
            Mfrom[k] = fitz.open(v)
            MbyW[k] = {'p': set(range(Mfrom[k].page_count)),
                       'S': defaultdict(int), }
        if k[0] == 'W':
            Wfrom[k] = fitz.open(v)

    out, out1 = fitz.open(), fitz.open()
    tf = 'imposible'
    os.mkdir(unk := join(ofld, "WMpdfs"))

    # перегрупировка пар из bdB в Wlst[]
    Wlst = []
    usedWnames = set()

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
        e.weight[0] = 2*len(e.wm)+len(e.w)  # чисто просто ага
    # не факт?!(см .s :)) что поля в порядке имен типа :0
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

    adrlist=[]
    for k,v in bdB.items():
        for e in v['l']:
            adrlist.append(e[-1])
   
    adrlist.sort(key=lambda a:a.adr)
    pprint.pprint(adrlist, stream=open(join(ofld, 'adrlist'), 'w'))





    # saving rest from BdB (m then w cose kekeke :
    if False:# пока без bdBEls
        os.mkdir(unk := join(ofld, 'bdBEls'))
        Tfrom = {'M': Mfrom, 'W': Wfrom}
        for k, v in bdB.items():
            b = fitz.open()
            if len(lst := v['l']) < 2:
                continue
            c = {'W': 0, 'M': 0}
            for ll in lst:
                e = ll[-1]
                c[(t := e.Hn[0])] += 1
                fromTo(Tfrom[t][e.Hn], e.pN, b)
            unk2 = join(unk, f'w{c["W"]:02}m{c["M"]:02}')
            if not os.path.exists(unk2):
                os.mkdir(unk2)
            savepdf2(b, join(
                unk2, f'w{c["W"]:02}m{c["M"]:02}_{b.page_count:>04}_{k.rjust(10,"_")}.pdf'))

    print(timing.log('4_E', "Отсохронялись"))

    # остатки(незамаскированные мековские)


def WM_mergingFromOnePages(srcW, srcM, outfld):
    out2, count2, out1, count1, T, i = fitz.open(), 0, fitz.open(), 0, '2', 0
    srcW = srcW or f'{outfld}\\{"Wrez_2022-12-01 17-31-08"}'
    srcM = srcM or f'{outfld}\\{"Mrez_2022-12-05 18-28-45"}'
    os.makedirs(outfld := outfld+f'\\{T}{rezname.rezname()}')
    os.chdir(outfld)

    def sw(doc, name):
        nonlocal i
        doc.save(name, garbage=2, deflate=True)
        print(timing.log(i := i+1, name))
        return fitz.open(), 0

    def ReOp2(): nonlocal out2, count2;   out2, count2 = sw(out2,  f'2{nm}_{count2:05}.pdf')
    def ReOp(t): nonlocal out1, count1;   out1, count1 = sw(out1, f'{t}{nm}_{count1:05}.pdf')
    def res(t): count1 and ReOp(t)
    def res2(): count2 and ReOp2(); res(t)

    def rm(f):
        try:
            os.remove(f)
        except OSError as e:
            print(f'{f}!{e=}')
    t, nm = {'NNN': ''}, ''
    for pg in sorted(os.listdir(srcW)):
        Wp = f'{srcW}\\{pg}'
        if t['NNN'] != (p := getinfo(pg))['NNN']:
            res2()
            nm = f'pg_{(t:=p)["Package"]}'
        if m := v[1]['pg'] if len(v := bd[p['els']]) == 2 and v[0]['Type'] != v[1]['Type'] else None:
            out2.insert_pdf(fitz.open(Wp), links=0, annots=0, show_progress=0)
            out2.insert_pdf(
                fitz.open(Mp := f'{srcM}\\{m}'), links=0, annots=0, show_progress=0)
            rm(Mp)
            (count2 := count2+2) % 500 or ReOp2(count2)
        else:
            out1.insert_pdf(fitz.open(Wp), links=0, annots=0, show_progress=0)
            (count1 := count1+1) % 500 or ReOp('W')
        rm(Wp)
    res2()
    t, nm = {'NNN': ''}, ''
    for pg in sorted(os.listdir(srcM)):
        if t['NNN'] != (p := getinfo(pg))['NNN']:
            res('M')
            nm = f'pg {"-".join((t:=p)["Package"].split("-",5)[:4])}'
        out1.insert_pdf(
            fitz.open(Mp := f'{srcM}\\{pg}'), links=0, annots=0, show_progress=0)
        rm(Mp)
        count1 = count1+1
    res('M')
    print(srcW, srcM, outfld, 'Step \u03c0', "   π пиу пиу")


"""
W, M, E, = {}, {}, {}
def buildDBofEls(srcW, srcM):
    #     srcW=os.path.join(srcW,'');
    #     lw=sorted(os.popen(f'dir {srcW} /s /b |wsl grep -v Сопро|wsl grep pdf').read().splitlines())
    # #    lw=[r"C:\AAA\_w_nov\СлужбаДоставки9\94-Л\г.Магнитогорск, п.18 Насосная Территория, д.    0, кв.    0   2173.pdf" ]
    #     for pkg,fpath in enumerate(lw):
    #         W[fpath]=doc=fitz.open(fpath)
    #         sz=doc.page_count
    #         for p in range(sz):
    #             els,iii,Adr,nonValidFIO=prsW(doc.get_page_text(p))
    #             E.setdefault(els,{'W':0,'M':0,'pgs':[]})#[0] isWcount pages
    #             E[els]['W']+=1
    #             E[els]['pgs'].append({'pos':p,'Type':'W',  #pos==NNN-1 #NNN start from 1  where pos from 0
    #                 'els':els,'fio':iii,'adr':Adr,'doc':doc,'ParaInfo':{'nonValidFio':nonValidFIO},'fpath':fpath,})
    #         print(timing.llgg(f'{os.path.dirname(fpath):^50}',f'Water{pkg:05} {sz:^6} '),flush=True)
    #     print(timing.llgg(f'total W: ',"WololoW"))
    #     #print('only W:',E)#баг на выгрузке lg_Wnov.№AtimingsW_M_of_E
    #     # уже тут можно поугарать на предмет !=1 E[els]['W']  и аналитики содержимого страниц
    #     return # timing of mek from c:
    # recache 5m09s  then 3m19s
    print(srcM, flush=True)
    srcM = os.path.join(srcM, '')  # r"V:\_mek_nov" )# test ram disk
    print(srcM, flush=True)
    # return
    lm = sorted(
        os.popen(f'dir {srcM} /s /b |wsl grep pdf').read().splitlines())
    for pkg, fpath in enumerate(lm):
        M[fpath] = doc = fitz.open(fpath)
        for p in range(doc.page_count):
            els, iii, Adr, nonValidFIO, *_ = prsM(M[fpath].get_page_text(p))
            # [0] isWcount pages
            E.setdefault(els, {'W': 0, 'M': 0, 'pgs': []})
            E[els]['M'] += 1
            E[els]['pgs'].append({'pos': p, 'Type': 'M',  # pos==NNN-1 #NNN start from 1  where pos from 0
                                  'els': els, 'fio': iii, 'adr': Adr, 'doc': doc, 'ParaInfo': {'nonValidFio': nonValidFIO}, 'fpath': fpath})
        print(timing.llgg(
            f'{os.getpid()}:Electricity{pkg:05}M ', fpath), flush=True)
    print(timing.llgg(f'total M: ', "MololoM"), flush=True)
    # print(E)

def ExistsElsNonW1M1(outfld):
    basefld = outfld
    os.makedirs(outfld := outfld+f'\\existsELSnonW1M1{rezname.rezname()}')
    os.chdir(outfld)
    pdfs = {'W': W, 'M': M}
    i = 0
    for k, v in E.items():
        if k.strip() == '':
            continue
        if (v['W'], v['M']) == (1, 1):
            continue
        b = fitz.open()
        for pg in v['pgs']:
            # pdfs[pg['Type']][pg['fpath']]
            b.insert_pdf(pg['doc'], pg['pos'], pg['pos'], links=0, annots=0)
        b.save(nm := f'W{v["W"]:03} M{v["M"]:03} ELS {k}.pdf',
               garbage=2, deflate=True)
        print(timing.llgg(i := i+1, nm))
        # del E[k] # lol +40min
        # #Надобы(бы бы бы) "бэкапить" E посредством SqlAlchemy для возможности "продолжения" от достигнутого
    print(timing.llgg('wmELSs', outfld))
    print('<Пусто елсные:')
    for k, v in E.items():
        if k.strip() != '':
            continue
        for pg in v['pgs']:
            print(pg)
    print(timing.llgg('emptELS', '>Пусто елсные:'))
    None

def getinfo(onePg):  # NNN,num in file,els,FIo,adr,NameOfPackage #cur just unparse from name
    pageInfo, pers, (out := {'pg': onePg})['Package'] = onePg.split('_')
    out['NNN'], out['Type'], out['els'], out['fio'], out['adr'] = pageInfo[:3], pageInfo[3], * \
        pers.split('#', 3)
    return out


def buildBaseOf(srcW, srcM):
    global bd

    bd = defaultdict(list)
    for pg in chain(os.listdir(srcW), os.listdir(srcM)):
        bd[(info := getinfo(pg))['els']].append(info)

    print(timing.log(0, "Построение словаря елс'ок"))
"""


if __name__ == '__main__':
    root = rezname.getArgOr(1, dirname(dirname(__file__)), 'Dir')
    print(f':\t Начало', timing.log('', f'{timing.pred-timing.base}'))
    main(join(root, ''))
    timing.ender()
# 133 # b+2
# TODO  асимметрия(на этапе в какие пучки из каких) в водотеплухе и электре - отдельные функции с существенным пересечением в далнейшем либо параметризация через функции либо через наследование от общего предка
"""
@ЛучшеВрагоХороший варик@ нижеследующий(следующий после будущьного) лобовой по сборке страниц на основе порядка из пучков w
def PairingFromSrcs(W,M,outfld,dbPairs):
    def getPairFor(frm,pos):None
    #W: список файлов с путями откуда и где сбоку(дублируя структуры путей после src) класть результаты
    #для извлечения(копирование и удаление) из M потребуется пул открытых с общим закрытием исчерании парностей индивидуальный
    # так извлечение идёт в порядке не
    #для нижеследующей стратегии критично количество страниц поэтому предыдущим (0) этапом
    #шинкуем (каждый)W-пучок по 1К(0-999)() и хвост с именованием NNNW-p-sze-
    for f in W:
        nf=getNf(f)
        outOnesW=fitz.open(f)
        inp=fitz.open(f)
        outPairs=fitz.open(f) #хм хм
        pDbl=0;pOnes=0
        for pin in range(inp.page_count):
            if pair:=getPairFor(inp,pin):
                outPairs.insert_pdf(pair["frm_M"],pg:=pair["pos_page"],pg,pDbl+1,links=0,annots=0,final=0);pDbl+=2
                outOnesW.delete_page(pOnes)
            else:
                outPairs.delete_page(pDbl)
                pOnes+=1
        outOnesW.save
 #"""
# long1 из шинкованных pdf сбор
# shorter then 1 пустые имена и сбор используя листинги файлов а сами наборы страниц из W-файла(последовательно набор пучков из M с выгрузкой непарных W) next: подгрузка пучков из М в хвост(-1: size p) и правильная последовательная (по порядку i из W() вставка на i+1 на доп inc(i))
# 162 # b+3 #realy not funny
