import time
from  datetime import datetime 
st=a=time.time()
def llgg(i,msg,nonValidFIO=None):
    def delta2dHMS(f,tm):
        decDay=lambda s:f'{int(s[:2])-1:02}{s[2:]}'
        return decDay(time.strftime(tm,time.gmtime(f)))
    warg= f'badFIO:{nonValidFIO}' if nonValidFIO else ''
    global a
    b=time.time()
    t=b-st 
    out,a=f'{msg:80}!{i:6} {datetime.now().strftime(tm:="%dd%Hh%Mm%Ss")}{delta2dHMS(t,tm)} {b-st:10.4f} {b-a:1.3f}{warg}',b
    return out 

print(f':\t Начало',llgg('',f'{a-st}'));

#module of RuChars Start>:
import re
fltru=lambda x:''.join(re.findall(r'[ЁА-Яа-яЁ]',x))
#module of RuChars   End<


def ender():
    print(f"TOTAL:{llgg(' ','thatsALL')}")