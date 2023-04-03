import logging,sys,re
logger =logging.getLogger(__name__)
from collections import Counter #Pg = namedtuple('Pg', 'pN Hn u els pa sq adr UrFcs Deliv')
def StructFromFile(path):    #"""TODO import ast;ast.literal_eval"""
    return eval(open(path).read())
isW=len(sys.argv)==2;isM=not isW;v=StructFromFile(sys.argv[-1]) # list of pairs  num,adr
bsD='.';fldD=bsD if isW else ' ';print(isW,sys.argv)
DELIMS="\
г|*|г^\
ул|пер|квартал|проезд|п|пр-кт|заезд|б-р|карьер|пл|разъезд|сад|ст|ш|*\
|ул|пр-кт|проезд|пер|ш|п|пл|заезд|б-р|сад^\
д|*|д.^\
корп|/|*|^\
кв|пом|*|кв."
#
s,p='|','^';lvl=[set(e.partition('|*|')[0 if isW else 2].split(s))for e in DELIMS.split(p)]
def out_el(el):print(f"[{el[0]:02},{el[1]},{el[2]},],")
sh=[15,48,15,44,0]
SfxBld=[];SfxKva=[]
def mk_el(tks,normi,i,ll):
    if normi and normi[-1]=='':normi=normi[:-1]
    #if tks:breakpoint()
    l=0;toSfxBld=0;toSfxKva=0
    #normi=normi[:]#локализация
    Renorm=[]#можно и без хвостования чисто двигай границу
    if normi[l:]:
        rez=f'{normi[l]}';                    sh[l]=max(sh[l],len(rez));
        Renorm.append(rez)#населённый пункт
    if normi[(l:=l+1):]:#@улица@
        tp,_,nm=normi[l].partition('.')
        rez=f'{nm:<40}@{tp:<7}';                 sh[l]=max(sh[l],len(rez));
        Renorm.append(rez)
    if normi[(l:=l+1):]:#домо
        tp,_,FullNum=normi[l].partition('.');   sh[l]=max(sh[l],len(FullNum));
        Num=re.search(r'\d+', FullNum).group()
        Sfx=FullNum[len(Num):]
        #if Sfx[:1]!='/':Sfx=f' {Sfx}' # что бы Буквы раньше дробей но теперь просто дома после
        rez=f'{Num:>04}{Sfx.ljust(8,"_")}@@{tp}';       
        if(toSfxBld:=len(rez)>sh[l]):
            SfxBld.append([len(rez),rez])
        sh[l]=max(sh[l],len(rez));
        Renorm.append(rez);
    if normi[(l:=l+1):]:#квартирно
        #if normi[l]in['кв.СОИ','кв.А']:#пилАть,            normi[l]='кв.0СОИ'
        tp,_,FullNum=normi[l].partition('.');
        try:
            Num=re.search(r'\d+', FullNum).group()
        except Exception as e:
            Num=''
        Sfx=FullNum[len(Num):]
        rez=f'{Num:>04}{Sfx:30}@@@{tp:10}';       sh[l]=max(sh[l],len(rez));
        if(toSfxKva:=len(rez)>sh[l]):
            SfxKva.append([len(rez),rez])
        sh[l]=max(sh[l],len(rez));
        Renorm.append(rez);
    if normi[(l:=l+1):]:#Ну а вдруг
        Renorm.extend(normi[l:])
    T='M'if isM else 'W'
    out=[f'{len(tks):02}',','.join(Renorm),[T]+tks,[i,ll]] # для [i,v] выхода в отладке i
    if toSfxBld:SfxBld[-1].append(out)
    if toSfxKva:SfxKva[-1].append(out)
    return out
def restoreFld(l):
    #print(f"*1 {fldD=}",l,flush=1)
    return fldD.join(e.strip() for e in l)
def normFld(l):   return bsD.join(e.strip('.').strip() for e in l)
underTown=set(i[0] for i in (('п Хуторки', 133),('п Лесопарк', 123),('п 18 Насосная Территория', 15),('п 10 Насосная Территория', 12),))
toTown=set(i[0] for i in (('п Дзержинского', 1439),('п Димитрова', 1349),('п Западный 2', 1302),('п Новая Стройка', 1130),('п Старая Магнитка', 519),('п Западный 1', 487),
('п Коммунальный', 475),('п Нежный', 373),('п Горького', 330),('п Некрасова', 311),('п Прибрежный', 256),('п Поля Орошения', 235),('п Рабочий 2-й', 193),('п Новотуковый', 184),
('п Ново-Магнитный', 171),('п Брусковый', 131),('п Горнорудный', 130),('п Первооктябрьский', 115),('п Карадырский', 111),
('п Первомайский', 102),('п Супряк', 99),('п Молодежный', 78),('п Надежда', 76),))
toSave=set(i[0] for i in (('тер. СНТ Энергетик', 448),('п Новоянгелька', 223),('п Озерный', 166),('п Муравейник', 117),('п Куйбас', 92),('с Агаповка', 85),('п Ближний', 71),
('сад Забота', 35),('тер. СНТ Лазурный', 16),('нп 2 Плотина', 4),('Красная Башкирия', 3),('р-н Агаповский', 2),('тер. СНТ Металлург-9', 1)))
KVdelim=':';KOMdelim='/';delim=f'г{fldD}Магнитогорск'    #если s==aFb где F=f'г{fldD}Магнитогорск' то s=Fb :
rez=[];nonCity=Counter();byLvlStr=Counter();nonStreetsHs=Counter();Ogryzk=Counter();
tpStr=Counter();HsLong=Counter();SlashWithoutSpace=Counter();HouseNotHouse=[];NUiKva=[];
Uch=[];nFor=[];Tails=[];Iranga=[];OgryzkL=[];NONEIND=[];
MustZ=0;er=0;nor=0;ukv=0;tls=0
normi=[]#Counter()###
lvlUk=0
def tonormi(tks,lvlUk=0):
    normi.append(normFld(tks[0]));return tks[1:]# curFld)
for i,inp in v:
    while ~inp.find(', ,'): inp=inp.replace(', ,',',')
    inp=inp.strip(',').strip('.'); normi=[]
    ~inp.find(delim) and (inp:=''.join(inp.partition(delim)[1:])) # всё что левее г?Магнитогорск
    tks=[e.strip().split(fldD)for e in inp.split(',')] #glob , in rec FldD {W:'.', M:' '}
    # delim отсекло  индексы пред г?Магнитогорск пред пос инд хехе    #фильтр индекса:
    dlt=0;
    while tks and tks[0].__len__()==1 and tks[0][0].isdigit():        tks=tks[1:];MustZ+=1;dlt=1;
    if False and dlt:
        print("ИНДЕКС???",mk_el(tks,normi,i,inp),file=sys.stderr)
        rez.append(f"ИНДЕКС???{mk_el(tks,normi,i,inp)}")
    if tks[0].__len__()==1:
        print("всяко НЕ индекс",mk_el(tks,normi,i,inp),file=sys.stderr)
        NONEIND.append([i,inp,mk_el(tks,normi,i,inp)]);  er+=1;continue
    #0Фильтрация  #Самара городок:   #жомкаем город
    curFld=restoreFld(tks[0]) #уровень населённый пунт 
    if curFld in underTown:
        tks[0:0]=[delim.split(fldD)];curFld=delim
    elif curFld in toTown:
        tks[0]=delim.split(fldD);curFld=delim
    if tks[0][0] in lvl[0]: tks=tonormi(tks)
    else:
        print("всяко НИ(рыцар)Городок",mk_el(tks,normi,i,inp),file=sys.stderr)
        nonCity[restoreFld(tks[0])]+=1;        er+=1;continue
    #1протяжённость(линии-улицы и пр ЛИБО "комплекс"(пос с домами и прочая нумерная )
    curFld=restoreFld(tks[0]) 
    byLvlStr[curFld]+=1 # подсчёт и узнавание какие есть дома аж улицы
    if False: # артефакт вставки необёрнутого подмассива
        if curFld==(aza:='М а г н и т о г о р с к'):
            print(aza,mk_el(tks,normi,i,inp),file=sys.stderr)
    if tks[0][0]=='д.':
        print("дома уличные сИротные",mk_el(tks,normi,i,inp),file=sys.stderr)
        nonStreetsHs[restoreFld(tks[0])]+=1;        er+=1;continue
    if tks[0][0] in lvl[1]: tks=tonormi(tks)
    else:
        print("что за огрызок",mk_el(tks,normi,i,inp),file=sys.stderr)
        Ogryzk[restoreFld(tks[0])]+=1;tpStr[tks[0][0]]+=1
        OgryzkL.append([i,inp,mk_el(tks,normi,i,inp)]);  er+=1;continue
        
    if tks:#добор дома
        curFld=restoreFld(tks[0])
        # вид вт д.№ корпХ где корп появляется в случае наличия как Буквы так и  Натурального 
        # в случае одновременного получается крокодил д.№ корп.Б /Н
        #формат Мэк ближе к "нормативному"(хз какому) д. № [Буква] [/Н]
        #у Мэк'а есть и КОРПУС но это параСит см гу-карта Тургенава 16 и корпус 1 и /1
        # у мэк не всегда слэшу предшествует пробел со:
        #блят! у вт есть дома без префикса д. например:'г.Магнитогорск, ул.Комсомольская, 59А, 0'
        # if ~curFld.find('уч'):
        #     #print("блят!2 уч уч уч :",mk_el(tks,normi,i,inp),file=sys.stderr)
        #     Uch.append([i,inp,mk_el(tks,normi,i,inp)]);  er+=1;continue  
        if curFld.startswith('уч'):
            curFld=curFld.replace('уч.','уч ',1).replace('уч','д.уч',1);    tks[0]=curFld.split(fldD)
            #print("блят!2 уч уч уч :",mk_el(tks,normi,i,inp),file=sys.stderr)
            #Uch.append([i,inp,mk_el(tks,normi,i,inp)]);  er+=1;continue  
        if curFld.startswith('д.уч'): curFld=curFld.replace('д.уч','д.',1); tks[0]=curFld.split(fldD)
        if curFld[0]!='д': curFld=f'д{fldD}{curFld}';                       tks[0]=curFld.split(fldD)
            #print("блят! дом не дом:",mk_el(tks,normi,i,inp),file=sys.stderr)
            #HouseNotHouse.append([i,inp,mk_el(tks,normi,i,inp)]);  er+=1;continue  
        hd=tks[0]; hd[1:2]=hd[1].split()
        if hd[2:] and hd[2]=='корп': # есть влитый корп но нах(пока) ибо 3 случая аж
            if hd[3:]:
                if hd[3].isdigit():hd[2]='/'
                else:hd[2]='';hd[3]=hd[3].upper()   #прим Буквы UPCASEить -"в надежде что а и А всёж одно"
        hd[1]=''.join(hd[1:]);tks[0]=tks[0][:2]
            
        if False and len(tks[0])!=2:
            print("не просто номер:",mk_el(tks,normi,i,inp),file=sys.stderr)
            HsLong[curFld]+=1;  er+=1;continue
        tks=tonormi(tks) 
    if tks:#добор квартив(ррр)ы и сцепка комнат
        tks=[' '.join(' '.join(l) for l in tks).split()]
        curFld=restoreFld(tks[0]).replace('пом ','пом.',1).replace('кв.пом.','кв.',1)
        hd=tks[0]=curFld.split(fldD)
        if hd[0]=='пом':hd[0]='кв'
        #if isM and ~hd[0].find('кв.']:hd[0]=hd[0][:-1] #ХЗ ['asdf'] а не просто 'asdf'!!!!нонХЗ
        if isM:
            curFld=restoreFld(tks[0]).replace('кв.','кв',1)
            hd=tks[0]=curFld.split(fldD)# hd[0]=hd[0].replace('кв.','кв',1)
        if isW and len(hd)==1 and hd[0].isdigit():  hd[0:0]=['кв']#21 случай из nFor024.7
        if isW and( curFld:=restoreFld(tks[0])) in {'б/н','кв.б/н','кв.0',}:tks[0]=[curFld:='']
        elif tks[0][0]!='кв':
            print(f"nonForward ква{len(nFor):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr)
            nFor.append(t);  continue
        if ~curFld.find('-'):# 9 случаев из Тыранга09.004.0
            if isM:
                curFld=curFld.replace('-','/',1);tks[0]=curFld.split(fldD)
            else:
                #print(f"ты-ранги ква ком{len(Iranga):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr);
                out=[]
                for e in hd:
                    a,b,c=e.partition('-')
                    if not b:
                        out.append(a)
                        continue
                    for i in range(int(a),int(c)+1):
                        out.append(str(i))
                tks=[out];  curFld=restoreFld(out)
                #print(f"Мы-ранги шарлиом{len(Iranga):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr);Iranga.append(t);  #continue
        if curFld.split(fldD,2)!=1:
            Kvs,_,Koms=curFld.partition('/')
            Kvs and (Kvs:=Kvs[:3]+Kvs[3:].replace(fldD,':'))
            Koms and(Koms:=Koms.replace(fldD,';'))
            tks[0]=Kvs.split(fldD)
            if Koms:tks[0][-1]+=f'|;{Koms}'
        if len(tks[0])!=2 and curFld!='':
            print(f"ну и ква{len(NUiKva):03}:",t:=mk_el(tks,normi,i,inp),file=sys.stderr)
            NUiKva.append(t);  ukv+=1;continue
        if tks[0]:tks=tonormi(tks)
        elif tks[0]=='':tks=tks[1:]
    rez.append(mk_el(tks,normi,i,inp));nor+=1;
print("['00'",*rez,']',sep=',\n')
print(f"['99',{sh=}{len(Iranga)=}, {tls=}, {len(NUiKva)=}, {len(nFor)=}, {ukv=},{nor=}, {er=}, {MustZ=}, {nonCity=},{len(HouseNotHouse)=},{len(Uch)=}],")
pes=',\t' if isW else ',' ##',\n'
print(*sorted(nonCity.items(),key=lambda x:-x[1]),sep=pes,file=sys.stderr)
#print('*\n*\nАлфавитно:',*sorted(byLvlStr.items()),sep=pes,file=sys.stderr)
#print('*\n*\nЧастотно:',*sorted(byLvlStr.items(),key=lambda x:-x[1]),sep=pes,file=sys.stderr)
#print(f'*\n*\nСиротДома {sum(nonStreetsHs.values())=}',*sorted(nonStreetsHs.items()),sep=pes,file=sys.stderr)
#print('*\n*\nЧастоДома:',*sorted(nonStreetsHs.items(),key=lambda x:-x[1]),sep=pes,file=sys.stderr)
print('*\n*\nПрефиУл:',*sorted(Ogryzk.items(),key=lambda x:-x[1]),sep=',\t' if isW else ',\n',file=sys.stderr)
print('*\n*\ntpStr:',*sorted(tpStr.items(),key=lambda x:-x[1]),sep=',\t' if isW else ',\n',file=sys.stderr)
#print('*\n*\nHouseOfWonders:',*(f'{b:^14}:{a:^5}'for a,b  in sorted(HsLong.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
#print('*\n*\nHouseOfWonders:',*(sorted(HsLong.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
#print('*\n*\nСлитый /:',*(sorted(SlashWithoutSpace.items(),key=lambda x:-x[1])),sep='',file=sys.stderr)
#print('*\n*\nДомаНеДома:',*HouseNotHouse,sep=',\n',file=sys.stderr)
#print('*\n*\nГрёб уч:',*Uch,sep=',\n',file=sys.stderr)
#print(f'*\n*\nХвостанутое({len(Tails)}):',*Tails,sep=',\n',file=sys.stderr)
print(f'*\n*\nНу и квашки({len(NUiKva)}):',*NUiKva,sep=',\n',file=sys.stderr)
print(f'*\n*\nтыранги ква ком({len(Iranga)}):',*Iranga,sep=',\n',file=sys.stderr)
print(f'*\n*\nогрызОЧКИ({len(OgryzkL)}):',*OgryzkL,sep=',\n',file=sys.stderr)
print(f'*\n*\nнонФорвард Ква({len(nFor)}):',*nFor,sep=',\n',file=sys.stderr)
print(f'*\n*\nНонИнды({len(NONEIND)}):',*NONEIND,sep=',\n',file=sys.stderr)
print(f'*\n*\nSfxBld({len(SfxBld)}):',*SfxBld,sep=',\n',file=sys.stderr)

print(f'*\n*\nSfxKva({len(SfxKva)}):',*SfxKva,sep=',\n',file=sys.stderr)
