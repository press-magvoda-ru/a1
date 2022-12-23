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
def main(folders, out):
    for inF in mnL:
        w1, w2, wSqsW, wpaW ,wSqsM,wNums = [0]*6
        c1, cSqsW,cuuuW,cpaW, cpaM,cuuuM,cSqsM,c2 = [0]*8
        wb.create_sheet(t :=(tt:=inF.split('.'))[0])
        print(inF, end=' ')
        sheet = wb[t]
        
        # print(wb.sheetnames)
        # следующего раза не будя: шапку и шИрины столбцов мона(imho) драйверам ввывода выставлять не на
        # как сейчас из говна говна 
        r = 0
        sheet.cell(row=(r := r+1), column=(c := 2)).value=f'{tt[-1]}:';wNums=len(tt[-1])+1

        w, m = int((m := t.split('m'))[0][1:]), int(m[1])
        (lfiles := sorted(
            os.popen(f'dir {inF} /s /b |wsl grep pdf').read().splitlines()))
        for N,v in enumerate(lfiles,1):
            n, z, = 0, 0

            def put(c, Thing):
                sheet.cell(row=k, column=c).value = str(Thing)
            c = 0
            cell = sheet.cell(row=(r := r+1), column=(c := c+1))
            els = os.path.basename(v).split('ELS ')[1].split('.pdf')[0]
            cell.value = f'=HYPERLINK("{os.sep.join(v.split(os.sep)[-2:])}","{els}")'
            cell.style = "Hyperlink"
            
            cell = sheet.cell(row=r, column=(c := c+1));    cell.value=f'{N}:'.rjust(wNums)
            doc = fitz.open(v)
            k, l = r, c-1
            for p in range(w):
                k, l, z = k+1, c-1, reparseWxMx.prsW(doc.get_page_text(p), v, p)
                put(l := l+1, f'={z.pageNum+1}')
                put(c1 := (l := l+1), z.adr.replace('%','/').rjust(w1 := max(w1, len(z.adr))))
                put(cSqsW := (l := l+1), z.sqS)#.rjust
                (wSqsW := max(wSqsW, len(z.sqS)))#)
                put(cuuuW:=(l := l+1), z.realuuu or z.uuu)
                put(cpaW:=(l := l+1), z.pa); wpaW=max(wpaW,len(z.pa))
            k = r
            for p in range(w, w+m):
                k, n, z = k+1, l+1, reparseWxMx.prsM(doc.get_page_text(p), v, p)
                put(cpaM := (n := n+1), '='+z.pa)
                put(cuuuM:=(n := n+1), z.realuuu or z.uuu)
                put(cSqsM:=(n := n+1), z.sqS.rjust(wSqsM:=max(wSqsM,len(z.sqS))))
                put(n := n+1, z.adr.replace('%', '/'))
                w2, c2 = max(w2, len(z.adr)), n
                put(n := n+1, f'={z.pageNum+1}')
            r = r+max(w, m)
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
        sheet.column_dimensions[alf[n-1]].width = len(f'{m+w}')+1

cur = (args := sys.argv)[1:] and args[1] or "."
(mnL := sorted(os.popen(f'dir {cur} /AD /b |wsl grep w').read().splitlines()))
wb = openpyxl.Workbook()
wb.remove_sheet(wb.active)
main(mnL, wb)
wb.save(f'{rezname.rezname()}.xlsx')
