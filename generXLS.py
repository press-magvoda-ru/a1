#import pdb; pdb.set_trace()
# breakpoint()

import openpyxl
import os
import sys
import reparseWxMx
import fitz
import rezname
import string
alf=string.ascii_uppercase
#добавил номер файла в листах для "облегчения ориентирования" заместо артикуляции елсника в межкоммуникации коллег 
def main(mnL, wb):
    #open dict of key-filename value=
    # all Pgs 
    # 
    # info about all (W|M)
    fl=0;
    for fullPathFile in mnL:
        if fullPathFile.find('$bundle')==-1:
            continue
        w1, w2, wSqsW, wpaW ,wSqsM,wNums = [0]*6
        c1, cSqsW,cuuuW,cpaW, cpaM,cuuuM,cSqsM,c2 = [0]*8
        wb.create_sheet(pdfname :=(sp:=fullPathFile.split('$'))[0].split('\\')[-1].strip())
        pdfPath='$'.join(sp[:-1])
        print(fl:=fl+1,fullPathFile)#, end=' ') print(pdfPath)
        sheet = wb[pdfname]
        #print(wb.sheetnames)
        r = 1
        c = 0
        #sheet.cell(row=(r := r+1), column=(c := 2)).value=f'{sp[-1]}:';wNums=len(sp[-1])+1
        
        Pgs=reparseWxMx.DictFromFile(fullPathFile)
        #os.system(f'del "{fullPathFile}"')
        def put(c, Thing):
            sheet.cell(row=r, column=c).value = str(Thing)
        #set header
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
        sz=c    
        for x,y in Pgs:
            r+=1
            l = 0
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

def makeXLS(path):
    s='*.py'
    (mnL := #sorted(
    os.popen(f'dir "{os.path.join(path,s)}" /S /O-S /b').read().splitlines()) # /OD get Size of pdf desc
    #)
    wb = openpyxl.Workbook()
    wb.remove_sheet(wb.active)
    main(mnL, wb)
    wb.save((nm:=f'{os.path.join(path,rezname.rezname())}.xlsx'))
    #os.system(f'start "" "cmd /c {nm}"')
    return nm

if __name__=='__main__':
    print(sys.argv)
    cur = (args := sys.argv)[1:] and args[1] or "."
    makeXLS(cur)

