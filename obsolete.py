    
#from def buildWowDataStructureTM(WW, MM, ofld):
def loc_temp():
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
