import re
import time

# from datetime import datetime
base = pred = time.time()


def decDay(s):
    return f"{int(s[:2])-1:02}{s[2:]}"


def delta2dHMS(f, tm):
    return decDay(time.strftime(tm, time.gmtime(f)))


def log(i, msg, nonValidFIO=None):
    global pred
    (
        full,
        tm,
        warg,
    ) = (
        (curr := time.time()) - base,
        "%dd%Hh%Mm%Ss",
        nonValidFIO and f"badFIO:{nonValidFIO}" or "",
    )
    msg, pred = (
        f"{msg:<30}!{i:6} {delta2dHMS(full,tm)} {full:10.4f} {curr-pred:1.3f}{warg}",
        curr,
    )
    return msg


def fltru(x):
    return "".join(re.findall(r"[ЁА-Яа-яЁ]", x))


def ender():
    print(f"TOTAL:{log(' ','thatsALL')}")
