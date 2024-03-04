from functools import lru_cache
from NormiW import NormiAdr as SmplAdr  # (inStr).smpl()
from collections import namedtuple
import timing
from os.path import dirname, basename, join
from os import sep, walk
from exceptlst import isBadMek

# print('попячено из a1/splitingOfMandV.py  c дополнением лицевых и площади')
# CluesOfPage('W',els,uuu,adr,src,pageNum,realuuu if realuuu!=uuu else ''))
Pg = namedtuple("Pg", "pN Hn u els pa sq adr adrNorm UrFcs Deliv isBad")
useExceptlst = False

bundle = namedtuple("bundle", "m w P kvt sps tot")
Deliveries = "Па-чин&Азимут&Мой дом&ГКС МКД&Левицкая"
defMekDeliv = Deliveries.split("&")[-1]


def lstInWithExtention(src, ext=".pdf", non="___"):
    lst = []
    for r, _, f in walk(src):
        for file in f:
            if file.endswith(ext):
                if file.find(non) == -1:
                    lst.append(join(r, file))  # фильтрация Сопроводитель
    return lst


def makeEmptyPg():
    # return Pg('','','','ПустоЛист','','','')
    return Pg(
        "", "", "", "ПустоСтр", "", "", "", "", "", "", ""
    )  # возвращать Стр ибо сторона а не дубль- TODO посмотреть где используется литерал ПустоЛист


def PgIsEmpy(p: Pg):
    return p.els == "".join(p[2:-1])  # заморочка с int isBad


def makeFakeNxtPg(v: Pg):
    t = {v._fields[i]: "N/A" for i, fld in enumerate(v)}
    try:
        t["pN"], t["Hn"], t["els"] = v.pN + 1, v.Hn, "ХВОСТ" or v.els
    except Exception as e:
        raise (e)

    return Pg(*t.values())  # e=  #==e.pN=v.pN+1 from same File


rname = {}  # словарь-трансляция(недокласс r(eal)name)) удобное имя Нт(,)-> полный реальный путь файла


def DictFromFile(path):
    """подъём в процесс сведений о квитанциях чтением 
    и исполнением(СВЯТ,СВЯТ,СВЯТ)определения (ожидаемого)словаря 
    в ИДЕАЛЕ TODO передавать сведенья о квитанциях через БД много-множную
    TODO import ast;ast.literal_eval"""
    return eval(open(path).read())  # читаем и исполняем весь файл - это не дыра - это база такая

def name2str(fVAReqVALUE):
    """ эксперементирование в освоении синтаксиса Python  нечто подобное name() из C# """
    return fVAReqVALUE.split("=", 1)[0]  # name2str(f'{var=}')


@lru_cache(999)
def Hn(path, Tp="M"):  # hash name from path ;#Tp  in ['M','W','R']
    """некое текстовое упрощение на входе абсолютное имя файла  пачки квитанций типа М либо W на выходе
    удобное(короткое)имя хэш"""
    rez, a = "", basename(path).split(".", 1)[0].split("-")
    if Tp == "M":
        try:
            rez = f"M-{a[2]}-{a[3]}-{a[4]}-{a[5]}"
        except Exception as e:
            print(msg := f"{e=} & {locals()=}")
            raise Exception(msg)
    if Tp == "W":
        rez = f"W-{'-'.join(dirname(path).split(sep)[-1].strip().replace('-',' ').split()[-2:])}"
        # собираем "хэш" от имени для различения файлов одного каталога (хз режут по 3000)
        hsh = (
            "_"
            + "".join(w.strip()[0] for w in basename(path).split(".") if w.strip())[2:6]
        )
        rez += hsh
    if Tp == "R":  # cose avg(M,W)  or as same chr(((ord('M')+ord('W'))//2)
        rez = basename(path).split("$")[0].strip()
    if rez:
        while rez in rname:
            rez += "_1"
        rname[rez] = path  # полный абсолютный путь файла для сборки страниц в итоге
        return rez
    raise Exception(f"Неожиданный тип квитанции:{locals()=}")


def add2Hn(paths, Tp="M"):
    """метод несуществующего класса Crname 
    массовое докидывание набора путей в словарь коротких имён
    """
    for e in paths:
        rname[Hn(e, Tp)] = e


def prsM(page, file, pN):
    """ парсинг значимых для совмещения данных из pdf-страницы квитанции M """
    UrFcs = "МЭК"  # Q? константа тут али чё как?
    if file not in rname:
        file = Hn(file, "M")
    adr = page.split("\n", 1)[0].strip()  # сырой адрес МЭК
    adrNorm = SmplAdr(adr, "M").smpl()
    isBad = useExceptlst and isBadMek(adr)
    if not (tail := page.split("Лицевой счет:", 1)[1]):
        return Pg(pN, file, "", "", "", "", adr, adrNorm, UrFcs, defMekDeliv, isBad)
    # print(l)
    pa = tail.split("\n", 1)[0].strip()  # ''.join([e for e in l.split('\n',1)[0]
    Deliv = tail.split("\n", 2)[1].strip()
    sqS = tail.split("помещения:")[1].split(maxsplit=1)[0]
    els = (
        els[0].split("\n", 1)[0].strip()
        if (els := (tail.split("Площад", 1)[0]).split("ЕЛС:", 1)[1:])
        else ""
    )
    uuu = "".join(tail.split("Плательщики:", 1)[1].replace(" ", "").split("\n"))[
        :6
    ].replace(".", "")  # ?method  remove all from {. }
    if (rez := timing.fltru(uuu)) != uuu:
        uuu = f"{rez}|{uuu}"
    return Pg(pN, file, uuu, els, pa, sqS, adr, adrNorm, UrFcs, defMekDeliv, isBad)


_cache_ofprsW, b_c = {}, {ord(c): None for c in " \xa0"}
lX = 0


def prsW(page, src, pageNum):
    """ парсинг значимых для совмещения данных из pdf-страницы квитанции W """
    global _cache_ofprsW, lX
    if not (page.startswith("ЕДИНЫЙ") or page.startswith("Погасите")):
        # 3 хвоста:
        lX += 1
        if lX > 1:
            breakpoint()
        return (
            _cache_ofprsW := makeFakeNxtPg(_cache_ofprsW)
        )  # вероятней всего это выехавшее за 1 страницу примечание
    if src not in rname:
        src = Hn(src, "W")
    dlg = ""
    if page.startswith("Погасите"):
        dlg = "DLG "
        page = page.partition("\n")[2]
    page = page.replace("\xa0", " ")

    UrFcs = "&".join(
        sorted(
            s.split('"')[1].upper() for s in page.split("\n") if s.startswith("ВСЕГО")
        )
    )

    els = (
        ""
        if len(t := page.split("ЕЛС:", 1)) < 2
        else t[1].split("\n", 1)[0].replace(" ", "")
    )
    adr = (tt := t[0].split("\n", 4))[1]  # сырой адрес ВоТе
    uuu = tt[2].split(":", 1)[-1].translate(b_c)
    pa = (
        ""
        if len(u := page.split("ЛИЦЕВОЙ СЧЕТ:", 1)) < 2
        else u[1].split("\n", 1)[0].replace(" ", "")
    )
    #    Deliv=''
    Deliv = u[1].split("\n", 2)[1].strip()  # какие ваще есть чисто посмотреть

    sqS = []
    sqS.append(
        ""
        if len(v := u[-1].split("Общая площадь:", 1)) < 2
        else v[1].split("\n", 1)[0].split()[0].replace(" ", "")
    )
    sqS.append(
        ""
        if len(w := v[-1].split("Отапливаемая площадь:", 1)) < 2
        else w[1].split("\n", 1)[0].split()[0].replace(" ", "")
    )
    # за воду: +3
    # за тепло: -1
    lns = page.split("\n")
    llst = [(i, e) for i, e in enumerate(lns) if e.startswith("ВСЕГО К ОПЛАТЕ")]

    def fnd(s):
        for i, e in llst:
            if ~e.find(s):
                return i
        return 0

    def getvalue(s, d):
        return lns[fld + d] if (fld := fnd(s)) else ""

    sqS[0] = getvalue("Водоканал", 3)
    sqS[1] = getvalue("Теплофикация", -1)

    sqS = dlg + sqS[0] + " | " + sqS[1]
    if (rez := timing.fltru(uuu)) != uuu:
        uuu = f"{rez}|{uuu}"
    lX = 0
    adrNorm = SmplAdr(adr, "W").smpl()
    return (
        _cache_ofprsW := Pg(
            pageNum, src, uuu, els, pa, sqS, adr, adrNorm, UrFcs, Deliv, 0
        )
    )
