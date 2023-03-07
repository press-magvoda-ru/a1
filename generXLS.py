#import pdb; pdb.set_trace()
# breakpoint()

import openpyxl
import os
import sys
import reparseWxMx
from reparseWxMx import PgIsEmpy,bundle,lstInWithExtention,Deliveries,defMekDeliv
#import fitz
import rezname
import string
alf=string.ascii_uppercase
typefilesOfdata=".dict_of_pages"
ZZ=[0]
"""Urs по мере увелечения контрАгентов выбирать из Gui c нижеследующим умолчанием"""
Urs='ВОДОКАНАЛ&ТЕПЛОФИКАЦИЯ&МЭК&АЗИМУТ&ГКС МКД'

def mainXLSsheetAndFresh(mnL, wb,wf): ## пока один поток сбора в два потока выгруза
    #фарш#
    """
    wf - выход для фреша - выкатки номеров пустых по файл-вкладка
    """
    #open dict of key-filename value=
    # all Pgs 
    # 
    # info about all (W|M)
    strTotal='ИТОГОВАЯ'; fl=0
    wf.create_sheet(strTotal)
    total=wf[strTotal]
    for fullPathFile in mnL:
        if fullPathFile.find('$bundle')<0:
            continue
        bI=1;
        bC=1+1 # len bundle is 6
        bT=bI+2
        r,c,freR,freC = 0,0,0,1
        def put(c, Thing):
            sheet.cell(row=r, column=c).value = str(Thing)
        def putfre(freR,Thing):
            shfre.cell(row=freR+bI, column=freC).value = str(Thing)
            putTot(freR+bT,fl,Thing)
        def putTot(r,c,Thing):
            total.cell(row=r, column=c).value = str(Thing)
        w1, w2, wSqsW, wpaW ,wSqsM,wNums = [0]*6
        c1, cSqsW,cuuuW,cpaW, cpaM,cuuuM,cSqsM,c2 = [0]*8
        (pdfname :=(sp:=fullPathFile.split('$'))[0].split('\\')[-1].strip())
        stat=sp[1].replace(typefilesOfdata,'')
        print(f'{stat=}');  stat=eval(stat) #ОЛОЛО опаснАсте тся ться гауби
        
        wb.create_sheet(pdfname)
        wf.create_sheet(pdfname)
        pdfPath='$'.join(sp[:-1])
        print(fl:=fl+1,fullPathFile)#, end=' ') print(pdfPath)
        putTot(2,fl,pdfname)
        #bundle = namedtuple('bundle','m w P kvt sps tot')
        sheet = wb[pdfname]
        shfre = wf[pdfname]
        def Hehehe(n): # 1-26 A-Z; 27-... AB ... for first 26**2 ?
            if (n:=n-1)<26:return alf[n]
            return alf[n//26-1]+alf[n%26]   # n явно меньше 625
        total.column_dimensions[Hehehe(fl)].width = 12

        r+=1
        for i in 'b':
            put(1,f'толькоМЭК')
            put(2,f'толькоВдТ') #
            put(3,f'двухСторо')
            put(4,f'стрСодерж')
            put(5,f'стрПустых')
            put(6,f'стрОбщее')
        r+=1    
        for i in 'c':
            put(1,f'{stat.m:^9}')
            put(2,f'{stat.w:^9}')
            put(3,f'{stat.P:^9}')
            put(4,f'{stat.kvt:^9}')
            put(5,f'{stat.sps:^9}')
            put(6,f'{stat.tot:^9}')
        
        #print(wb.sheetnames)
        #sheet.cell(row=(r := r+1), column=(c := 2)).value=f'{sp[-1]}:';wNums=len(sp[-1])+1
        
        Pgs=reparseWxMx.DictFromFile(fullPathFile)
        #os.system(f'del "{fullPathFile}"')
        #set header
        r+=1
        for i in 'a':
            put(c:=c+1,"W-№");
            put(c:=c+1,"W-ЛС");
            put(c:=c+1,"W-Адрес");
            put(c:=c+1,"W-площадь");
            put(c:=c+1,"W-ФИО");
            put(c:=c+1,"W-ЕЛС");
    
            put(c:=c+1,"M-ЕЛС");
            put(c:=c+1,"M-ФИО");
            put(c:=c+1,"M-площадь");
            put(c:=c+1,"M-Адрес");
            put(c:=c+1,"M-ЛС");
            put(c:=c+1,"M-№");
            
            put(c:=c+1,"Доставщик")

            put(c:=c+1,"ВсеКонтрА")
            for j in Urs.split('&'):
                put(c:=c+1,f'{j}:')
        sz=c    
        for x,y in Pgs:
            PgIsEmpy(x) and putfre(freR:=freR+1,x.pN+1)
            PgIsEmpy(y) and putfre(freR:=freR+1,y.pN+1)
            r+=1;  l = 0
            # cell = sheet.cell(row=(r := r+1), column=(c := c+1))
            # els = x.els
            # cell.value = f'=HYPERLINK("{pdfPath}.pdf","{els}")'
            # cell.style = "Hyperlink"
            put(l := l+1, f'={x.pN+1}')
            put(cpaW:=(l := l+1), x.pa); wpaW=max(wpaW,len(x.pa))
            put(c1 := (l := l+1), x.adr.replace('%', '/').rjust(w1 := max(w1, len(x.adr))))
            put(cSqsW := (l := l+1), x.sq)#.rjust
            (wSqsW := max(wSqsW, len(x.sq)))#)
            put(cuuuW:=(l := l+1), x.u)
            put(l := l+1, x.els)
            z=y
            put(l := l+1, z.els)
            put(cuuuM:=( l:= l+1), z.u)
            put(cSqsM:=(l := l+1), z.sq.rjust(wSqsM:=max(wSqsM,len(z.sq))))
            put(l := l+1, z.adr.replace('%', '/'))
            w2, c2 = max(w2, len(z.adr)), l
            put(cpaM := (l := l+1), z.pa)
            put(l := l+1, f'={z.pN+1}')
            
            D=x.Deliv or y.Deliv 
            for i in Deliveries.split('&'):
                if ~D.find(i):
                    DD=i;break;
            else:
                    DD=D#defMekDeliv
            put(l:=l+1,DD) # выбор из управляек и фолбэк Ливицкая здесь или при сборе ?
            V='&'.join([x.UrFcs,y.UrFcs]).strip('&')
            put(l:=l+1,V)
            for j in Urs.split('&'):
                put(l:=l+1,f'={int(not not ~V.find(j))}')  #"пока так" если имена могут префиксоватся что искать &ndl& с предварительным оборачиванием &V& 
        putfre(0,f'{freR}');shfre.column_dimensions[alf[0]].width = 20 #Кол-во: в левленный столбец пояснение если чё
        ZZ[0]+=freR

        for i in range(sz):
            sheet.column_dimensions[alf[i]].width = 13
        for i in [2,9]:
            sheet.column_dimensions[alf[i]].width = 40
        continue
        sheet.column_dimensions['A'].width = 13
        sheet.column_dimensions[alf[1]].width = wNums+1 #len(str(w))+1
        sheet.column_dimensions[alf[c1-1]].width = w1
        sheet.column_dimensions[alf[cSqsW-1]].width = wSqsW
        sheet.column_dimensions[alf[cuuuW-1]].width = 3+3
        sheet.column_dimensions[alf[cpaW-1]].width = wpaW+1.1
        
        sheet.column_dimensions[alf[cpaM-1]].width = len(z.pa)*1.2
        sheet.column_dimensions[alf[cuuuM-1]].width = 3+3
        sheet.column_dimensions[alf[cSqsM-1]].width = wSqsM
        sheet.column_dimensions[alf[c2-1]].width = w2 
        sheet.column_dimensions[alf[l-1]].width = len(f'{100}')+1
    putTot(1,1,f'{ZZ[0]}') #Общее кол-во:  в левленный столбец пояснение если чё
def makeXLS(path):
    #s=f'*{typefilesOfdata}'
    (mnL := #sorted(
   #os.popen(f'dir "{os.path.join(path,s)}" /S /O-S /b').read().splitlines()
    lstInWithExtention(path,ext=typefilesOfdata)
    ) # /OD get Size of pdf desc
    """ """
    #)
    wb = openpyxl.Workbook(); wb.remove_sheet(wb.active)
    wf = openpyxl.Workbook(); wf.remove_sheet(wf.active)
    mainXLSsheetAndFresh(mnL, wb,wf)
    tik=rezname.rezname()
    nm =f'SURV$${tik}.xlsx' ;#ЫГКМ  ну теперь ФСЁ ясНО # и выживальщики и pop-surv.gov74.ru lol
    nf =f'Fresh${tik}.xlsx'
    wb.save(nm:=f'{os.path.join(path,nm)}');wf.save(nf:=f'{os.path.join(path,nf)}')
    #os.system(f'start "" "cmd /c {nm}"')
    return nm,nf

if __name__=='__main__':
    print(sys.argv)
    cur = (args := sys.argv)[1:] and args[1] or "."
    makeXLS(cur)

