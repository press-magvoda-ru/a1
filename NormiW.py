﻿import sys
import re
import io  # logger =logging.getLogger(__name__)
from pprint import pprint
from collections import Counter
# Pg = namedtuple('Pg', 'pN Hn u els pa sq adr UrFcs Deliv')


def print_to_string(*args, **kwargs):
    kwargs["end"] = kwargs.get("end", "")  # TODOne
    with io.StringIO() as out:
        print(*args, file=out, **kwargs)
        return out.getvalue()


def pprint_to_string(obj, **kwargs):
    with io.StringIO() as out:
        pprint(obj, stream=out, **kwargs)
        return out.getvalue()


def StructFromFile(path):
    return eval(open(path).read())  # """TODO import ast;ast.literal_eval"""


# isW=True;isM=not isW; # по умолчанию ожидем адрес W - для M сообща...
bsD = "."
fldD = bsD  # if isW else ' ';
MustZ = 0
# print(isW,sys.argv)
DELIMS = "\
г|*|г^\
ул|пер|квартал|проезд|п|пр-кт|заезд|б-р|карьер|пл|разъезд|сад|ст|ш|*\
|ул|пр-кт|проезд|пер|ш|п|пл|заезд|б-р|сад^\
д|*|д.^\
корп|/|*|^\
кв|пом|*|кв."
lvl = {
    "W": [set(e.partition("|*|")[0].split("|")) for e in DELIMS.split("^")],
    "M": [set(e.partition("|*|")[2].split("|")) for e in DELIMS.split("^")],
}

underTown = set(
    i[0]
    for i in (
        ("п Хуторки", 133),
        ("п Лесопарк", 123),
        ("п 18 Насосная Территория", 15),
        ("п 10 Насосная Территория", 12),
    )
)
toTown = set(
    i[0]
    for i in (
        ("п Дзержинского", 1439),
        ("п Димитрова", 1349),
        ("п Западный 2", 1302),
        ("п Новая Стройка", 1130),
        ("п Старая Магнитка", 519),
        ("п Западный 1", 487),
        ("п Коммунальный", 475),
        ("п Нежный", 373),
        ("п Горького", 330),
        ("п Некрасова", 311),
        ("п Прибрежный", 256),
        ("п Поля Орошения", 235),
        ("п Рабочий 2-й", 193),
        ("п Новотуковый", 184),
        ("п Ново-Магнитный", 171),
        ("п Брусковый", 131),
        ("п Горнорудный", 130),
        ("п Первооктябрьский", 115),
        ("п Карадырский", 111),
        ("п Первомайский", 102),
        ("п Супряк", 99),
        ("п Куйбас", 92),
        ("п Молодежный", 78),
        ("п Надежда", 76),
    )
)
toSave = set(
    i[0]
    for i in (
        ("тер. СНТ Энергетик", 448),
        ("п Новоянгелька", 223),
        ("п Озерный", 166),
        ("п Муравейник", 117),
        ("с Агаповка", 85),
        ("п Ближний", 71),
        ("сад Забота", 35),
        ("тер. СНТ Лазурный", 16),
        ("нп 2 Плотина", 4),
        ("Красная Башкирия", 3),
        ("р-н Агаповский", 2),
        ("тер. СНТ Металлург-9", 1),
    )
)
KVdelim, KOMdelim = ":", "/"  # если s==aFb где F=f'г{fldD}Магнитогорск' то s=Fb :
nFor, NUiKva, Niknight, HsForsaken = [], [], [], []


def t1dtL(t0tL):
    return f"{t0tL[-1]}.{t0tL[0]}"


# def out_el(el):print(f"[{el[0]:02},{el[1]},{el[2]},],")
sh, SfxBld, SfxKva = [15, 48, 15, 44, 0], [], []
valueDelimType = "!"


def pad(st: str, width: int, ch=valueDelimType):
    """width<-len(st) предпишим слева >len(st) допишем справа"""
    (width > 0) and (width := min(5, width))
    (width < 0) and (width := max(-5, width))
    return st.rjust(abs(width), ch) if width < 0 else st.ljust(width, ch)


class NormiAdr:
    def smpl(s):  # sgml :)
        bld = (s.bld[0] + s.bld[1], s.bld[2])
        return ",".join(
            [
                s.city,
                t1dtL(s.street),
                t1dtL(bld),
                t1dtL(s.app),
            ]
        )

    def blding(s):
        return ",".join(s.smpl().split(",")[:3])

    def setself(self, inp, i, wrong, normi, tks):
        self.inp, self.i, self.wrong, self.normi, self.tks = inp, i, wrong, normi, tks
        self.set_out_adrflds()
        if wrong:
            self.er()

    def er(self):
        print(self.wrong, self.mk_el(), file=sys.stderr)

    def curFld(self):
        return restoreFld(self.tks[0])

    def __init__(
        self,
        inp: str,
        Tp="W",
        i=0,
    ) -> None:
        global fldD, MustZ
        #'M'if isM else 'W' #'M' if isM else 'W' if isW else 'U'
        self.T, normi, isM, isW = Tp, [], Tp == "M", Tp == "W"
        fldD = bsD if isW else " "
        delim = f"г{fldD}Магнитогорск"

        def tonormi(tks, lvlUk=0):
            normi.append(normFld(tks[0]))
            return tks[1:]  # curFld)

        while ~inp.find(", ,"):
            inp = inp.replace(", ,", ",")
        inp = inp.strip(",").strip(".")
        ~inp.find(delim) and (
            inp := "".join(inp.partition(delim)[1:])
        )  # всё что левее г?Магнитогорск
        ~inp.find(",  Тагильская,") and (
            inp := inp.replace(",  Тагильская,", ", ул Тагильская,", 1)
        )  # см МЕМО_№1
        ~inp.find(", в районе у") and (
            inp := inp.replace(", в районе у", ", у", 1)
        )  #', в районе ул. Лихачева, д.15, кв.0']
        ~inp.find(", зем.участки п.") and (
            inp := inp.replace(", зем.участки п.", ", п.", 1)
        )  # см МЕМО_№2

        ~inp.find(" Корпус ") and (
            inp := inp.replace(" Корпус ", "/", 1)
        )  # по апрелю (у мэка )
        ~inp.find("корп. ") and (
            inp := inp.replace("корп. ", "корп.", 1)
        )  # по апрелю (у мэка )
        ~inp.find(", кв.Гараж ") and (
            inp := inp.replace(", кв.Гараж ", "Гараж, кв.", 1)
        )  #  гаражи как вид литеры :)

        isW and ~inp.find("стр.") and (
            inp := inp.replace("стр.", "корп.", 1)
        )  # СалЩед д.3 стр.1 и 2 и Советская д123А стр НО г.Магнитогорск, ул.Некрасова, д.28 корп.стр.1, кв.0

        # тер. СНТ Энергетик, д. 108 /, кв'
        inp.endswith("кв") and (
            inp := ",".join(inp.split(",")[:-1])
        )  # (inp:=inp[:-2])#(inp:=inp+f'{fldD}0')

        tks = [
            e.strip().split(fldD) for e in inp.split(",")
        ]  # glob , in rec FldD {W:'.', M:' '}
        while tks and tks[0].__len__() == 1:
            if tks[0][0].isdigit():
                tks = tks[1:]
                MustZ += 1
            else:
                return self.setself(inp, i, "всяко НЕ индекс", normi, tks)

        # уровень населённый пунт:
        realNasP = tks[0]
        if (curFld := restoreFld(tks[0])) in underTown:
            tks[0:0] = [delim.split(fldD)]
            curFld = delim
        elif curFld in toTown:
            # MEMO_№1 случаи M ['п Дзержинского,  Тагильская, д. 2 С','п Дзержинского,  Тагильская, д. 3''п Дзержинского,  Тагильская, д. 5''п Дзержинского,  Тагильская, д. 7', 'п Дзержинского,  Тагильская, д. 19']
            # туда сюда - на сырой строке в начале проще
            # MEMO_№2 случаи W ['г.Магнитогорск, зем.участки п.Звездный, д.137 уч, кв.0','г.Магнитогорск, зем.участки п.Звездный, д.332 уч, кв.0','г.Магнитогорск, зем.участки п.Звездный, д.360 уч, кв.0','г.Магнитогорск, зем.участки п. Молодежный, д.33/1 уч., кв.0']
            tks[0] = delim.split(fldD)
            curFld = delim

        if tks[0][0] in lvl[Tp][0]:
            tks = tonormi(tks)
        else:
            tks = tonormi(tks)
            # return self.setself(inp,i,f"ДруГо{len(Niknight):04}",normi,tks)
        # 1протяжённость(линии-улицы и пр ЛИБО "комплекс"(пос с домами и прочая нумерная )
        # byLvlStr[curFld:=restoreFld(tks[0]) ]+=1 # подсчёт и узнавание какие есть дома аж улицы

        if tks[0][0] == "д.":
            # return self.setself(inp,i,f"безУлич{len(HsForsaken):05}",normi,tks)
            tks[0:0] = [["ш", " ".join(["Ядом", *realNasP])]]
            None
        if tks[0][0] in lvl[Tp][1]:
            tks = tonormi(tks)
        else:  # "временное"  офиктиченье улицами переферийных адресов если потребно
            curFld = "ул " + restoreFld(tks[0])  # 44 случая
            tks[0] = curFld.split(fldD)
            tks = tonormi(tks)
            # return self.setself(inp,i,"что за огрызок",normi,tks)

        if tks:  # добор дома
            curFld = restoreFld(tks[0])
            # вид вт д.№ корпХ где корп появляется в случае наличия как Буквы так и  Натурального
            # в случае одновременного получается крокодил д.№ корп.Б /Н
            # формат Мэк ближе к "нормативному"(хз какому) д. № [Буква] [/Н]
            # у Мэк'а есть и КОРПУС но это параСит см гу-карта Тургенава 16 и корпус 1 и /1
            # у мэк не всегда слэшу предшествует пробел со:
            # блят! у вт есть дома без префикса д. например:'г.Магнитогорск, ул.Комсомольская, 59А, 0'
            # if ~curFld.find('уч'):
            #     #print("блят!2 уч уч уч :",mk_el(tks,normi,i,inp),file=sys.stderr)
            #     Uch.append([i,inp,mk_el(tks,normi,i,inp)]);  er[0]+=1;continue
            if curFld.startswith("уч"):
                curFld = curFld.replace("уч.", "уч ", 1).replace("уч", "д.уч", 1)
                tks[0] = curFld.split(fldD)
                # print("блят!2 уч уч уч :",mk_el(tks,normi,i,inp),file=sys.stderr)
                # Uch.append([i,inp,mk_el(tks,normi,i,inp)]);  er[0]+=1;continue
            if curFld.startswith("д.уч"):
                curFld = curFld.replace("д.уч", "д.", 1)
                tks[0] = curFld.split(fldD)
            if curFld[0] != "д":
                curFld = f"д{fldD}{curFld}"
                tks[0] = curFld.split(fldD)
                # print("блят! дом не дом:",mk_el(tks,normi,i,inp),file=sys.stderr)
                # HouseNotHouse.append([i,inp,mk_el(tks,normi,i,inp)]);  er[0]+=1;continue
            hd = tks[0]
            hd[1:2] = hd[1].split()
            if (
                hd[2:] and hd[2] == "корп"
            ):  # есть влитый корп но нах(пока) ибо 3 случая аж
                if hd[3:]:
                    hd[2] = (
                        "/" if (hd[3].isdigit() or hd[3][:1].isdigit()) else ""
                    )  # / случай: г.Магнитогорск, пр-кт.Карла Маркса, д.141 корп.3А, кв.1
                    hd[3] = hd[
                        3
                    ].lower()  # прим Буквы UPCASEить -"в надежде что а и А всёж одно"
            hd[1] = "".join(hd[1:])
            tks[0] = tks[0][:2]

            if False and len(tks[0]) != 2:
                self.setself(inp, i, "не просто номер:", normi, tks)
            tks = tonormi(tks)
        if tks:  # добор квартив(ррр)ы и сцепка комнат
            tks = [" ".join(" ".join(ll) for ll in tks).split()]
            curFld = (
                restoreFld(tks[0])
                .replace("пом ", "пом.", 1)
                .replace("кв.пом.", "кв.", 1)
            )
            hd = tks[0] = curFld.split(fldD)
            if hd[0] in ["пом", "блок"]:
                hd[0] = "кв"
            # if isM and ~hd[0].find('кв.']:hd[0]=hd[0][:-1] #ХЗ ['asdf'] а не просто 'asdf'!!!!нонХЗ

            if (p := curFld.find("кв")) > 0:
                # часть "суфикса"(при перечислении домов) заехало в секцию квартир, случаи W:  'г.Магнитогорск, ул.Костромская, д.484,2 уч, кв.0', 'г.Магнитогорск, п.Зеленая Долина, д.уч 91, 92, кв.0'
                add, kv, curFld = curFld.partition("кв")
                # по условию add очевидно не пусто (да и не набор пробельных Imho - мыж пострипили  ведь да!? )
                normi[-1] += f'*{add[:-1].replace(bsD," ")}'
                hd = tks[0] = (curFld := kv + curFld).split(fldD)
                p, None
            if isM:
                curFld = restoreFld(tks[0]).replace("кв.", "кв", 1)
                hd = tks[0] = curFld.split(fldD)  # hd[0]=hd[0].replace('кв.','кв',1)
            if (isW or isM) and len(hd) == 1 and hd[0].isdigit():
                hd[0:0] = [
                    "кв"
                ]  # 21 случай из nFor024.7 и 5 M ['г Магнитогорск, ул Лучезарная, д. 32 /1, 12','г Магнитогорск, ул Красный Маяк, д. 57,'г Магнитогорск, ул Красный Маяк, д. 57, 2','п Горького, ул Одесская, д. 31, 1','п Горького, ул Одесская, д. 31, 2']
            if (isW or isM) and (curFld := restoreFld(tks[0])) in {
                "б/н",
                "кв.б/н",
                "кв.0",
            }:
                tks[0] = [curFld := ""]
            elif tks[0][0] != "кв":
                return self.setself(
                    inp, i, f"nonForward ква{len(nFor):03}:", normi, tks
                )
            if ~curFld.find("-"):  # 9 случаев из Тыранга09.004.0
                if isM:
                    curFld = curFld.replace("-", "/", 1)
                    tks[0] = curFld.split(fldD)
                else:
                    out = []
                    # print(f"ты-ранги ква ком{len(Iranga):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr);
                    for e in hd:
                        a, b, c = e.partition("-")
                        if not b:
                            out.append(a)
                            continue
                        for i in range(int(a), int(c) + 1):
                            out.append(str(i))
                    tks = [out]
                    curFld = restoreFld(out)
                    # print(f"Мы-ранги шарлиом{len(Iranga):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr);Iranga.append(t);  #continue
            if curFld.split(fldD, 2) != 1:
                Kvs, _, Koms = curFld.partition("/")
                Kvs and (Kvs := Kvs[:3] + Kvs[3:].replace(fldD, ":"))
                Koms and (Koms := Koms.replace(fldD, ";"))
                tks[0] = Kvs.split(fldD)
                if Koms:
                    tks[0][-1] += f"|;{Koms}"
            if len(tks[0]) != 2 and curFld != "":
                return self.setself(inp, i, f"ну и ква{len(NUiKva):03}:", normi, tks)
            if tks[0]:
                tks = tonormi(tks)
            elif tks[0] == "":
                tks = tks[1:]
        self.setself(inp, i, "", normi, tks)
        pass

    def set_out_adrflds(self):
        # city,#street,#building,#BuildingExt,#app,#appExt
        if self.normi and self.normi[-1] == "":
            self.normi = self.normi[:-1]
        normi = self.normi
        self.city = (normi[0] if normi else "").title()
        self.street = ("", "")
        self.bld = ("", "", "")  # self.buildingExt,
        self.app = ("", "", "")  # self.appExt='','','','','',''
        self.tail = ""
        if normi[1:]:
            tp, _, nm = normi[1].partition(".")
            nm = nm.replace(".", " ").title()
            # ибо: ('Им Газеты Правда_ул_W', 4114),('Имени Газеты Правда_ул_M', 3956),
            # ...
            nm = {
                "Им Газеты Правда": "Имени Газеты Правда",
                "Звёздная": "Звездная",
                "Вяземский": "Вяземского",
            }.get(nm, nm)
            # ('Правобережные Очистные Сооружения_п_W', 30),
            # ('Правобережные Очистные Сооружения_ул_M', 29),
            # ('Малый Заезд_ул_W', 6),
            # ('Малый_заезд_M', 7),
            # ('Зеленая Долина_п_W', 2),
            # ('Зеленая Долина_сад_M', 4),

            self.street = (nm, tp)
        if normi[2:]:
            tp, _, FullNum = (normi[2]).lower().partition(".")
            Num = re.search(r"\d+", FullNum).group()
            Sfx = FullNum[len(Num) :]
            # if Sfx[:1]!='/':Sfx=f' {Sfx}' # что бы Буквы раньше дробей но теперь просто дома после
            self.bld = (Num, Sfx, tp)
            # if(toSfxBld:=len(rez)>sh[l]):  SfxBld.append([len(rez),rez])
        if normi[3:]:
            # if normi[l]in['кв.СОИ','кв.А']:#пилАть,            normi[l]='кв.0СОИ'
            tp, _, FullNum = (normi[3]).lower().partition(".")
            try:
                Num = re.search(r"\d+", FullNum).group()
            except Exception:
                Num = ""
            Sfx = FullNum[len(Num) :]
            self.app = (Num, Sfx, tp)
            # sh[l]=max(sh[l],len(rez));if(toSfxKva:=len(rez)>sh[l]):SfxKva.append([len(rez),rez])
            # sh[l]=max(sh[l],len(rez));
        if normi[4:]:
            self.tail = ",".join(normi[4:])

    def __str__(self):
        return print_to_string(self.mk_el())

    def __repr__(self):
        return str(self)

    def getCor(s, key=""):
        return (
            s.wrong,
            s.city,
            s.street[0],
            s.street[1],
            pad(s.bld[0], -4),
            s.bld[1],
            pad(s.app[0], -4),
            s.app[1],
            s.T,
        )

    def __lt__(s, o):
        return s.getCor() < o.getCor()

    def mk_el(self):
        normi, i, inp = self.normi, self.i, self.inp
        # toSfxBld=0;toSfxKva=0 #normi=normi[:]#локализация
        Renorm = [
            self.smpl() + ":сОви:"
        ]  # можно и без хвостования чисто двигай границу
        if normi[(ll := 0) :]:  # населённый пункт
            Renorm.append(self.city)
        if normi[(ll := ll + 1) :]:  # @улица@
            nm, tp = self.street
            Renorm.append("<".join([pad(nm, 40), pad(tp, 7)]))
        if normi[(ll := ll + 1) :]:  # домо
            Num, Sfx, tp = self.bld
            Renorm.append("".join([pad(Num, -4, "0"), pad(Sfx, 8, "!"), f"<<{tp}"]))
        if normi[(ll := ll + 1) :]:  # квартирно
            # if normi[l]in['кв.СОИ','кв.А']:#пилАть,            normi[l]='кв.0СОИ'
            Num, Sfx, tp = self.app
            # rez=f'{str(Num).rjust(4," ")}{Sfx:30}@@@{tp:10}'
            Renorm.append(
                "".join([pad(Num, -4, " "), pad(Sfx, 30, " "), f'<<<{pad(tp,10," ")}'])
            )
        if normi[(ll := ll + 1) :]:  # Ну а вдруг
            Renorm.append(self.tail)  # normi[l:])

        out = [
            f"{len(self.tks):02}",
            ",".join(Renorm),
            [self.T] + self.tks,
            [i, inp],
        ]  # для [i,v] выхода в отладке i
        # if toSfxBld:SfxBld[-1].append(out)
        # if toSfxKva:SfxKva[-1].append(out)
        return out


def restoreFld(ll):
    return fldD.join(e.strip() for e in ll)  # print(f"*1 {fldD=}",l,flush=1)


def normFld(ll):
    return bsD.join(e.strip(".").strip() for e in ll)


def main(w=[], m=[]):
    rez, nonCity, nonStreetsHs, Ogryzk = [], Counter(), Counter(), Counter()
    # byLvlStr=Counter(); #Tails=[];
    tpStr, HsLong, HouseNotHouse = (Counter(), Counter(), [])
    # ;SlashWithoutSpace=Counter();
    ur2, Uch, Iranga, OgryzkL, NONEIND = Counter(), [], [], [], []
    er, nor, ukv, tls = [0], [0], 0, 0

    def InserterList(v, Tp, out):
        for i, inp in v:
            x = NormiAdr(inp, Tp, i)
            ur2[f"{x.street[0]}_{x.street[1]}_{x.T}"] += 1
            if not x.wrong:
                out.append(x)
                nor[0] += 1
                continue

            er[0] += 1
            if x.wrong == "всяко НЕ индекс":
                NONEIND.append([i, x.inp, x.mk_el()])
            elif x.wrong.startswith("ДруГо"):
                nonCity[restoreFld(x.tks[0])] += 1
                Niknight.append(x.mk_el())
            elif x.wrong.startswith("безУлич"):
                nonStreetsHs[restoreFld(x.tks[0])] += 1
                HsForsaken.append(x.mk_el())
            elif x.wrong == "что за огрызок":
                tpStr[x.tks[0][0]] += 1
                Ogryzk[restoreFld(x.tks[0])] += 1
                OgryzkL.append([i, inp, x.mk_el()])
            elif x.wrong == "не просто номер:":
                HsLong[x.curFld()] += 1
            else:
                er[0] -= 1
                if x.wrong.startswith("nonForward ква"):
                    nFor.append(x.mk_el())
                elif x.wrong.startswith("ну и ква"):
                    NUiKva.append(x.mk_el())

    InserterList(w, "W", rez)
    InserterList(m, "M", rez)

    print("['00'", *sorted(rez), "]", sep=",\n")
    sh = ""
    print(
        f"['99',{nor=} + {er=}=[{len(Niknight)=}+{len(HsForsaken)=}], {sh=}{len(Iranga)=}, {tls=}, {len(NUiKva)=}, {len(nFor)=}, {ukv=},{MustZ=}, {nonCity=},{len(HouseNotHouse)=},{len(Uch)=}],"
    )
    pes = ",\t"  ##',\n'
    print(*sorted(nonCity.items(), key=lambda x: -x[1]), sep=pes, file=sys.stderr)
    # print('*\n*\nАлфавитно:',*sorted(byLvlStr.items()),sep=pes,file=sys.stderr)
    # print('*\n*\nЧастотно:',*sorted(byLvlStr.items(),key=lambda x:-x[1]),sep=pes,file=sys.stderr)
    # print(f'*\n*\nСиротДома {sum(nonStreetsHs.values())=}',*sorted(nonStreetsHs.items()),sep=pes,file=sys.stderr)
    # print('*\n*\nЧастоДома:',*sorted(nonStreetsHs.items(),key=lambda x:-x[1]),sep=pes,file=sys.stderr)
    print(
        "*\n*\nПрефиУл:",
        *sorted(Ogryzk.items(), key=lambda x: -x[1]),
        sep=",\n",
        file=sys.stderr,
    )
    print(
        "*\n*\ntpStr:",
        *sorted(tpStr.items(), key=lambda x: -x[1]),
        sep=",\n",
        file=sys.stderr,
    )
    # print('*\n*\nHouseOfWonders:',*(f'{b:^14}:{a:^5}'for a,b  in sorted(HsLong.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
    # print('*\n*\nHouseOfWonders:',*(sorted(HsLong.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
    # print('*\n*\nСлитый /:',*(sorted(SlashWithoutSpace.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
    # print('*\n*\nДомаНеДома:',*HouseNotHouse,sep=',\n',file=sys.stderr)
    # print('*\n*\nГрёб уч:',*Uch,sep=',\n',file=sys.stderr)
    # print(f'*\n*\nХвостанутое({len(Tails)}):',*Tails,sep=',\n',file=sys.stderr)

    # print(f'*\n*\nплохГород({len(Niknight)}):',*Niknight,sep=',\n',file=sys.stderr)
    print(f"*\n*\nНу и квашки({len(NUiKva)}):", *NUiKva, sep=",\n", file=sys.stderr)
    print(f"*\n*\nтыранги ква ком({len(Iranga)}):", *Iranga, sep=",\n", file=sys.stderr)
    print(f"*\n*\nогрызОЧКИ({len(OgryzkL)}):", *OgryzkL, sep=",\n", file=sys.stderr)
    print(f"*\n*\nнонФорвард Ква({len(nFor)}):", *nFor, sep=",\n", file=sys.stderr)
    print(f"*\n*\nНонИнды({len(NONEIND)}):", *NONEIND, sep=",\n", file=sys.stderr)
    # print(f'*\n*\nSfxBld({len(SfxBld)}):',*SfxBld,sep=',\n',file=sys.stderr)
    # print(f'*\n*\nSfxKva({len(SfxKva)}):',*SfxKva,sep=',\n',file=sys.stderr)

    #    print(f'*\n*\nSfxKva({len(SfxKva)}):',*SfxKva,sep=',\n',file=sys.stderr)

    # print(*sorted(ur2.items(),key=lambda x:-x[1]),sep=',\n',file=sys.stderr)

    Niknight

    print(*(f"{print_to_string(e):^30}" for e in sorted(ur2.items())), file=sys.stderr)


if __name__ == "__main__":
    iswm = sys.argv[1] == "iswm"
    if iswm:
        w = StructFromFile(sys.argv[-1])
        m = StructFromFile(sys.argv[-2])
        main(w, m)
        sys.exit(0)

    for a in sys.argv[1:]:
        print(NormiAdr(a[1:], a[0]))

    # isW=len(sys.argv)==2;isM=not isW;
