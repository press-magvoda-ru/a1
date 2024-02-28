(проект в стадии интенсивного прихорашивания)

заплатка v.0.0.0 : 
------------------
главный( main.py) это splitingOfMandV.py
------------------
до (внедрения)программы : 
две отдельные A и B коммунальные организации изготовив наборы pdf файлов квитанций видаА и видаB соответсвенно  печатали  у печатника P  и "рассылали" своим потребителям посредстом службы доставки S
после (внедрения)программы:
программа  по возможности совмещает на один лист страницы квитанций от A и B адрессованные одному потребителю и полученные наборы отправляет печатнику P в печать для дальнейшей "разноски" по потребителям доставщиком S

всё элементарно при игнорировании нюансов существующих реализаций :)

lst - это список для билда  костыльным
------------------------------------------------------
Файл:~2distNxt.py :
import os, sys
p=os.path.abspath(sys.argv[0])
p=os.path.dirname(p)
a=list(os.walk(p))[0][1]
print(a)
b=f'{int(max(a))+1:02}'
os.makedirs(dst:=p+'\\'+b)
lst=open('lst','r').read().splitlines()
for fl in lst:
	f=f'copy  "{fl}" "{dst}"'
	print(f,':')
	os.system(f)


Файл(по факту вызов ~2distNxt.py полуручное):~makerDist.py:
------------------------------------------------------
from  rezname  import rezname
import os
pyuic5 guiForPairing.ui -o guiForPairing.py
~2distNxt.py to next
os.system(f'(tm&&pyinstaller splitingOfMandV.py  -n splitingOfMandV{rezname()} -c -F -i logo.ico&&tm)>o{rezname()}')



недо requirements.txt: 
------------------------------------------------------
  pymupdf для fitz
  PyQt5 для гуя 
  openpyxl
  pandas - саммый децл для кой какой статистики
  .
  .
  .

зы  - это набросок
