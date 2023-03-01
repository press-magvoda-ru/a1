from functools import lru_cache
from collections import namedtuple
import timing 
from os.path import dirname, basename
from os import sep
# print('попячено из a1/splitingOfMandV.py  c дополнением лицевых и площади')
# CluesOfPage('W',els,uuu,adr,src,pageNum,realuuu if realuuu!=uuu else ''))
Pg = namedtuple('Pg', 'pN Hn u els pa sq adr')
bundle = namedtuple('bundle','m w P kvt sps tot')

def makeEmptyPg():
    return Pg('','','','ПустоЛист','','','')
    return Pg(pN,*['Пусто']*6)
def PgIsEmpy(p:Pg):
    return p.els==''.join(p[2:])

def makeFakeNxtPg(v:Pg):
    t={v._fields[i]:'N/A'for i,fld in enumerate(v)}
    t['pN'],t['Hn'],t['els']=v.pN+1,v.Hn,'ХВОСТ' or v.els
    return Pg(*t.values())#e=  #==e.pN=v.pN+1 from same File

rname = {}
def DictFromFile(path):
    """TODO import ast;ast.literal_eval"""
    return eval(open(path).read())  # читаем словарь - куда деваться
def name2str(fVAReqVALUE):return fVAReqVALUE.split('=', 1)[0] # name2str(f'{var=}')
@lru_cache(999)
def Hn(path,Tp='M'):  # hash name from path ;#Tp  in ['M','W','R']
    a = basename(path).split('.', 1)[0].split('-')
    rez=''
    if Tp=='M':
        try:
            rez = f'M-{a[2]}-{a[3]}-{a[4]}-{a[5]}' 
        except Exception as e:
            print(msg:=f'{e=} & {locals()=}')
            raise Exception(msg)
    if Tp=='W':
        rez = f"W-{'-'.join(dirname(path).split(sep)[-1].strip().replace('-',' ').split()[-2:])}"
        #собираем "хэш" от имени для различения файлов одного каталога (хз режут по 3000)
        hsh='#'+''.join(w.strip()[0] for w in basename(path).split('.') if w.strip())[2:6]
        rez+=hsh
    if Tp=='R': # cose avg(M,W)  or as same chr(((ord('M')+ord('W'))//2)
        rez = basename(path).split('$')[0].strip()
    if rez:
        while rez in rname:
            rez+='_1'
        rname[rez] = path  # полный абсолютный путь файла для сборки страниц в итоге
        return rez
    raise Exception(f"Неожиданный тип квитанции:{locals()=}")
def add2Hn(paths,Tp='M'):
    for e in paths:
        rname[Hn(e,Tp)] = e
def clearAdr(a):
    #return a
    b = a.replace(',кв.', '__').replace(',д.', '_').replace(',ул ',',ул.')\
        .replace(',пр-кт ',',пр-кт.').split('.',1)[-1].replace(' ','')
    return b
def prsM(page, file, pN):
    if file not in rname:
        file = Hn(file,'M')
    adr = page.split('\n', 1)[0].strip().replace('/', '%').replace('Корпус','%').replace(
        ', ', ',').replace('. ', '.').replace(' %', '%').replace('г Магнитогорск', '')
    # Вычищение adr
    adr = clearAdr(adr)
    try:
        if adr[0] == '4' and adr[6] == ',':
            adr = adr[7:]
    except Exception as e:
        print(f'from PrsM {page=} ,{file=} , {pN=} , {adr=} ')
        raise e
    if not (l := page.split('Лицевой счет:', 1)[1]):
        return Pg(pN, file, '', '', '', '', adr)
    # print(l)
    pa = l.split('\n', 1)[0].strip()  # ''.join([e for e in l.split('\n',1)[0]
    sqS = l.split('помещения:')[1].split(maxsplit=1)[0]
    els = els[0].split('\n', 1)[0].strip() if (
        els := (l.split('Площад', 1)[0]).split('ЕЛС:', 1)[1:]) else ''
    uuu = ''.join(l.split('Плательщики:', 1)[1].replace(' ', '').split('\n'))[
        :6].replace('.', '')  # ?method  remove all from {. }
    if (rez := timing.fltru(uuu)) != uuu:
        uuu = f'{rez}|{uuu}'
    return Pg(pN, file, uuu, els, pa, sqS, adr)
_cache_ofprsW, b_c = {}, {ord(c): None for c in ' \xa0'}
def prsW(page, src, pageNum):
    global _cache_ofprsW
    if not page.startswith('ЕДИНЫЙ'):
        #3 хвоста:
        return (_cache_ofprsW:=makeFakeNxtPg(_cache_ofprsW))  # вероятней всего это выехавшее за 1 страницу примечание
    if src not in rname:
        src = Hn(src,'W')
    page = page.replace('\xa0', ' ')
    els = '' if len(t := page.split('ЕЛС:', 1)) < 2 else t[1].split(
        '\n', 1)[0].replace(' ', '')
    adr = (l := t[0].split('\n', 4))[1].replace('г.Магнитогорск', '').replace(
        '/', '%').replace('"', "'").translate(b_c).replace('корп.', '%').replace('корп', '%') #+4
    # Вычищение adr
    adr = clearAdr(adr)
    uuu = l[2].split(':', 1)[-1].translate(b_c)
    pa = '' if len(u := page.split('ЛИЦЕВОЙ СЧЕТ:', 1)
                   ) < 2 else u[1].split('\n', 1)[0].replace(' ', '')
    sqS = []
    sqS.append('' if len(v := u[-1].split('Общая площадь:', 1))
               < 2 else v[1].split('\n', 1)[0].split()[0].replace(' ', ''))
    sqS.append('' if len(w := v[-1].split('Отапливаемая площадь:', 1))
               < 2 else w[1].split('\n', 1)[0].split()[0].replace(' ', ''))
    sqS = sqS[0]+'|'+sqS[1]
    if (rez := timing.fltru(uuu)) != uuu:
        uuu = f'{rez}|{uuu}'
    return (_cache_ofprsW := Pg(pageNum, src, uuu, els, pa, sqS, adr))
""" from splitingOfMandV last
#CluesOfPage('W',els,uuu,adr,src,pageNum,realuuu if realuuu!=uuu else ''))
CluesOfPage=namedtuple('PageClues','type els uuu adr src pageNum realuuu')
def prsM(page,pdf,pageNum):
    adr=page.split('\n',1)[0].strip().replace(
        '/','%').replace(', ',',').replace('. ','.').replace(' %','%').replace('г Магнитогорск','')
    if adr[0]=='4' and adr[6]==',': adr=adr[7:]
    if not (l:=page.split('Лицевой счет',1)[1:]) : return ('','',adr,'')
    els=els[0].split('\n',1)[0].strip() if (
        els:=(l:=l[0].split('Площад',1)[0]).split('ЕЛС:',1)[1:]) else ''
    uuu=''.join(l.split('Плательщики:',1)[1].replace(' ','').split('\n'))[
                :6].replace('.','')#?method  remove all from {. }
    realuuu,uuu=uuu,timing.fltru(uuu)
    #return els,uuu,adr,realuuu if realuuu!=uuu else '',pdf,pageNum,'M'
    #need remap cose prsW is now
    return CluesOfPage(els,uuu,adr,realuuu if realuuu!=uuu else '',pdf,pageNum,'M')
_cache_ofprsW,b_c={},{ord(c):None for c in ' \xa0'}
def prsW(page,src,pageNum):
    global  _cache_ofprsW;
    #вероятней всего это выехавшее за 1 страницу примечание
    if not page.startswith('ЕДИНЫЙ'):return _cache_ofprsW
    els='' if len(t:=page.split('ЕЛС:',1))<2 else t[1].split(
        '\n',1)[0].replace(' ','')
    adr=(l:=t[0].split('\n',4))[1].replace('г.Магнитогорск','').replace('/','%').replace('"',"'").translate(b_c)
    uuu=l[2].split(':',1)[-1].translate(b_c)
    realuuu,uuu=uuu,timing.fltru(uuu)[-3:]
    #return (_cache_ofprsW:=(els,uuu,adr,realuuu if realuuu!=uuu else ''))
    #for log:  #nm=f'{NNN}{"W"}01 {p+1:04}_{els:10}#{iii:^3}#{Adr:^42}_{nf:^50}.pdf' #
    adr=f'{adr:^42}';src=f'{src:^50}';els=f'{els:10}';uuu=f'{uuu:^3}'
    return (_cache_ofprsW:=CluesOfPage('W',els,uuu,adr,src,pageNum,realuuu if realuuu!=uuu else ''))
"""