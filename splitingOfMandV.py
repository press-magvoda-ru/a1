inN,=5,
from collections import defaultdict
from itertools import chain
from functools import lru_cache
from datetime import datetime
import multiprocessing as mp
import sys
import os
import fitz
# import os.path
import rezname
import pprint
import timing
from os.path import dirname, join, basename
from reparseWxMx import prsM, prsW, Pg, Hn, rname, name2str,add2Hn
from collections import namedtuple
Nparts = namedtuple('Nparts', 's c i')
# 33 lol with }; 17 llaaag on W; 4 M is 1m30s;
( mainpid,) = ( os.getpid(),)
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
Mpages2time = {
    1: 0.0030,   2: 0.0090,   3: 0.0145,   4: 0.0268,   6: 0.0260,   9: 0.0390,  12: 0.0530,  17: 0.0820,  20: 0.0890,  30: 0.1380, 31: 0.1380,  36: 0.1680,  38: 0.1873,  45: 0.2550,  50: 0.2383,  51: 0.2350,
    66: 0.3020,  74: 0.3540,  88: 0.4650, 89: 0.4650,  90: 0.4646,  92: 0.4498,  94: 0.5963,  98: 0.5549,  99: 0.5764, 102: 0.5666, 115: 0.7066, 118: 0.5694, 128: 0.7462, 130: 0.6954, 132: 0.8287, 135: 0.6524,
    139: 0.8339, 144: 0.6899, 156: 0.7190, 161: 0.8312, 162: 0.8536, 174: 0.8060, 175: 0.8020, 191: 1.0527, 196: 1.1310, 199: 1.1215, 206: 1.0995, 219: 1.4275, 225: 5.8552, 238: 4.3170, 263: 7.0041,
    292: 1.5012, 295: 1.7988, 296: 1.6624, 327: 1.6466, 335: 1.7411, 342: 1.7676, 387: 2.5890, 404: 2.1864, 407: 2.9501, 409: 2.1208, 427: 2.5174, 435: 2.6380, 445: 2.2108, 447: 2.8338, 453: 2.5068,
    455: 4.0784, 460: 2.7527, 494: 3.5601, 514: 3.5387, 518: 2.5778, 520: 3.8566, 539: 3.5938, 543: 3.7930, 547: 2.7861, 555: 3.5197, 556: 2.6985, 569: 3.4309, 570: 3.3965, 580: 3.0530, 614: 3.5789,
    657: 4.2440, 660: 4.1803, 663: 4.1165, 665: 3.8395, 669: 4.2581, 683: 3.7920, 694: 4.4470, 720: 4.2234, 728: 4.1546, 737: 3.7626, 742: 6.2911, 746: 5.0300, 755: 9.1913, 766: 5.9401, 775: 6.6480,
    779: 4.2097, 810: 4.7389, 824: 5.2514, 830: 4.7476, 847: 9.1537, 854: 5.0737, 855: 10.3093, 869: 5.2589, 870: 5.2685, 876: 10.3269, 879: 10.3270, 894: 6.7237, 902: 7.6602, 908: 4.7613, 920: 5.6136,
    941: 5.5570, 958: 5.8541, 962: 5.9240, 967: 5.7880, 968: 5.7454, 976: 10.2881, 977: 5.4905, 979: 5.4905, 996: 11.2110, 1002: 5.6536, 1004: 5.9174, 1007: 6.3281, 1008: 6.4650, 1013: 5.8380, 1015: 5.8380, 1019: 7.2117, 1064: 6.1261,
    1096: 5.8918, 1114: 5.7600, 1121: 6.2705, 1128: 5.7456, 1150: 6.8091, 1202: 6.7658, 1204: 6.7772, 1224: 7.4149, 1241: 5.9250, 1263: 11.8820, 1268: 7.5943, 1281: 11.5301, 1309: 9.0319, 1322: 7.8720, 1323: 12.9740,
    1356: 9.9600, 1371: 12.7787, 1372: 8.5281, 1378: 12.7394, 1413: 9.7538, 1414: 12.9606, 1417: 13.5051, 1425: 8.1877, 1427: 14.8995, 1486: 11.3548, 1553: 9.3582, 1562: 12.8201, 1573: 9.5624, 1576: 9.6913, 1589: 9.6400,
    1639: 10.0099, 1707: 10.5130, 1764: 11.2161, 1832: 15.9827, 1872: 16.1610, 1880: 14.0519, 1898: 16.6987, 1914: 12.7837, 1933: 15.0000, 1993: 15.9360, 2000: 16.0000,
    2001: 16.0000,
}
Wpages2time = {k: k for k in range(12000)}
def SumMap(wf, l): return sum(map(wf, l))


def toNparts(lfs, n, p2t, wf):
    """Разбивка {lfs} на {n} близковзвешенных по сумме {p2t[wf(i)]} частей"""  # if n < 2: return [lfs]
    rez = [Nparts([0], [], i+1) for i in range(n)]
    for e in lfs:
        (v := min(rez)).s[0] += p2t[wf(e)]
        v.c.append(e)
    return rez
    # def PartWeight(lfs, p2t, wf): return sum(p2t[wf(f)] for f in lfs)


def inSubProcM(Tp, base, prt):
    i, pid = base, os.getpid()
    print(f'>>{Tp} from {prt.i} {os.getpid()} {os.getcwd()}')
    pagestxt = open(f'M{prt.i:>03}', 'w')  # {pid:>6}
    if (prt.i == 1):  # само пикленье Рика
        # + pprint.print(rname,stream=pagestxt)+'\n,' BUT:
        # nfild = f'{rname=}'.split('=', 1)[0]
        # A = '{'
        # B = '},'
        # head = '\n'.join([f'{A}\n{nfild:>6}:{A}', '\n'.join(
        #     f'{k:20}:{v},\n'for k, v in rname.items()), f'{B:>8}\n'])
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
    print(timing.log('wTotB', of))
    sys.stdout = stdout
    os.chdir(dirname(src))
    return of


def main(root, rout=None):
    rout = rout or root
    srcM = f'{root}"_mek_nov"'
    srcW = f'{root}{"_w_nov"}'
    
    # srcM = f'{root}{"_mek_nov_shrt"}'
    # srcW = f'{root}{"_w_nov_shrt"}'  # тЭсто сливание сразу из pdf
    print(root, rout, srcM, srcW, sep="\t")
    # MW for 1st 2nd then all
    os.mkdir(fld := f'{rout}\\MW{rezname.rezname()}\\')
    os.chdir(fld)

    M_data_spliting(srcM, fld)
    W_data_spliting(srcW, fld)
    pprint.pprint(rname, stream=open(join(fld,name2str(f'{rname=}')),'w'),width=333) # nero are 
    WM_mergeFromMultiPagePdf(fld, fld, fld)

#различные DS(ах если бы - чисто воборьи и пушки) для быстро-быстрого паренья: 
W, M, bdB = None, None, defaultdict(list)
bdByAdr = defaultdict(list)
Wpa, Mpa = defaultdict(list), defaultdict(list)
emptyEls = []
#outFileName = 'bdB.defaultdict.txt'
Wfa, Mfa = defaultdict(list), defaultdict(list)

# WfaMfa - таблица пересечений - список общих(парных) в возрастающем по Wfa номерам - пора бы и pandas подсобить сюдыть
WbyM={} #{ HnW:{HnM:{номерв(HnM):номерв(HnW)}}} ...

def buildWowDataStructureTM(WW, MM):
    # out = open(outFileName, 'a')
    # out.write('\n---------------\n')

    paByT = {'M': Mpa, 'W': Wpa}
    faByT = {'M': Mfa, 'W': Wfa}
    for k, v in chain(WW.items(), MM.items()):
        bdByAdr[v.adr].append(v)
        paByT[v.Hn[0]][v.pa].append(v)
        faByT[v.Hn[0]][v.pa].append(v)
        if v.els:
            bdB[v.els].append(v)
        else:
            emptyEls.append(v)  # какой нить
    print(timing.log('3', "Построение словаря елс'ок"))


def WM_mergeFromMultiPagePdf(srcW, srcM, outfld):
    global W, M,rname
    def getPgs(path):
        f = open(path)
        txt = f.read()
        rez = eval(txt)  # читаем словарь - куда деваться
        return rez

    buildWowDataStructureTM(W := getPgs(join(srcW, 'wTotB')),
                            M := getPgs(join(srcM, 'mTotB')))

    rname= getPgs(join(outfld,name2str(f'{rname=}'))) # test in wrk rname or get...
    
    
    # WbyM  # {Hn(w)}-спектр страниц по  "мэк пространству"

    # цикл по Wfa  строим карты('чертежи') по которым собираем из основы втыкая из мэк группы

    # цикл по W ключ в рез по src  - проще переоткрыть(но медленее)
    # по критерию ELS|+ из набираем rez[src]=[pars.push(),unik.push,possible?]

    None


"""
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
    buildBaseOf()
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
