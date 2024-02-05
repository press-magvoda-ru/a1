# debundle
from reparseWxMx import bundle
from generXLS import typefilesOfdata
import os
from os.path import join
import sys


# ----------


def lst(path):
    return [
        a.replace(typefilesOfdata, "")
        for a in os.listdir(path)
        if a.endswith(typefilesOfdata)
    ]


def getstatWMw(b):
    r = {
        "m": 0,
        "w": 0,
    }
    for c in b:
        d = c.split()
        r["w"] += int(d[-1])
        r["m"] += int(d[-1]) if d[-2] == "2" else 0
    return r


def getstatMones(b):
    r = {"m": 0}
    for c in b:
        d = c.split()
        r["m"] += int(d[-1])
    return r


# print(getstatWMw(lst(join(path,'WMpdfs'))))
# print(getstatMones(lst(join(path,'MekOnes'))))
def getAllbundles(b):
    r = {}
    for c in b:
        d = c.split("$")
        r[d[0].strip()] = eval(d[1])
    return r


def getS(path):
    (allbundle := getAllbundles(lst(path)))
    import pandas as pd

    df = pd.DataFrame(allbundle)
    print(f"all is {(z:=bundle(*df.sum(1)))}")
    print(f"input stat: allM={z.m+z.P} allWT={z.w+z.P}")
    return df


if __name__ == "__main__":
    path = sys.argv[-1] if sys.argv[1:] else "."
    fld = "WMpdfs"
    getS(join(path, "" if path.endswith(fld) else fld))
