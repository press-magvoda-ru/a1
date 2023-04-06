﻿__all__=["isBadMek"]
Except=[
'пер Пекинский, д. 30$',
'Расковой, д. 22$',
'Прибрежная, д. 1$',
'Галиуллина, д. 28,',
'Галиуллина, д. 25,',
'Галиуллина, д. 31,',
'Галиуллина, д. 33 /1,',
'пр-кт Карла Маркса, д. 176 /1,',
'Галиуллина, д. 41,',
'Галиуллина, д. 43,',
'Галиуллина, д. 49,',
'Советская, д. 195,',
'Советская, д. 195/1,',
'Советская, д. 195 /2,',
'Труда, д. 38 /1,',
'Жукова, д. 6,',
'50-летия Магнитки, д. 46,',
'Жукова, д. 4 /2,',
'Галиуллина, д. 7,',
'Фадеева, д. 18,',
'Цементная, д. 6,',
'Цементная, д. 13,',
'Цементная, д. 14,',
'Строителей, д. 26,',
'Строителей, д. 42,',
'Николая Шишка, д. 32 /1,',
'Ворошилова, д. 41,',
'Тевосяна, д. 31 /2,',
'Зеленый лог, д. 34,',
'Жукова, д. 17,',
' Жукова, д. 19,',
'Жукова, д. 19 /1,',
'Жукова, д. 21,',
'Жукова, д. 23,',
'Ленина, д. 125,',
'Ленина, д. 127,',
'Ленина, д. 129,',
'Ленина, д. 131,',
'Ленина, д. 133, ',
'Ленина, д. 135,',
'Ленина, д. 129 /1,',
'Ленина, д. 129 /2,',
'Ленина, д. 131 /1,',
'Ленина, д. 133 /1,',
'Ленина, д. 133 /2,',
'Ленина, д. 133 /3,',
'Ленина, д. 135 А,',
'Ленина, д. 135 /1,',
'Ленина, д. 135 /2,',
'Ленина, д. 135 /3,',
'Карла Маркса, д. 171,','Ленина, д. 138 /3,',]
for i in range(len(Except)):Except[i]=Except[i].replace(' ','')

def isBadMek(adr):
    adr=adr.replace(' ','')
    for e in Except:
        if e[-1]=='$':
            if adr.endswith(e[:-1]):
                return 1
        else:
            if ~adr.find(e):
                return 1
    return 0