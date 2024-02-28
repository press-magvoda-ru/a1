__all__ = ["zuzazip"]
from generXLS import fscv
import zipfile as z
import os
from datetime import datetime
from os.path import join, getsize, dirname, abspath
from os import walk, system


def DistribResultByChanksForFollowZiping(fld=".", sz=600_000_000):
    step = 0

    def teeprint(arg):
        nonlocal step
        fn = f'{["_lst",'TREE'][step]}_st'
        step += 1
        print(fn)
        print(*arg, sep="\n")
        nm = join(
            fld, fn + f'_lst({str(datetime.now()).replace(':','').split('.')[0]}).txt'
        )
        print(*arg, sep="\n", file=open(nm, "wt"), end="")
        return nm

    o, sq, mfo, sum, num, cur = [], [], "", 0, 1, ""
    for v in (v for v in open(join(fld, fscv)).read().split(",\n") if v):
        fn, pars, Whom = v.split(",")
        o.append(
            [Whom, int(pars) > 0, fsz := getsize(join(fld, fn := fn + ".pdf")), fn]
        )
    teeprint(o := sorted(o, reverse=1))

    for f in o:
        Whom, lx, fsz, fn = f
        if (t := f'{Whom}_{['SM','DP'][int(bool(lx))]}LX') != mfo:
            mfo, sum, num = t, 0, 1
        elif sum + fsz > sz:
            sum, num = 0, num + 1
        if (nf := f"{mfo}_{num:03}") != cur:
            sq.append(cur := nf)
        sum += fsz
        sq.append(f"\t{fn}")
    return teeprint(sq)


def mover(fld, menu):
    z = join(fld, "ForZiping")
    os.makedirs(z)
    p = ""
    sq = [v for v in open(join(fld, menu)).read().split("\n") if v]
    for l in sq:
        if (fn := l.strip()) == l:
            os.makedirs(join(z, l))
            p = l
        else:
            (a := join(fld, fn), b := join(z, p, fn))
            os.rename(a, b)
    return z


def zipper(fld):  # get abspath
    fld = abspath(fld)
    for FOarc, sb, fns in list(walk(fld)):
        if sb:
            continue
        with z.ZipFile(FOarc + ".zip", "a", z.ZIP_DEFLATED, compresslevel=2) as arc:
            for fn in fns:
                if fn.endswith(".pdf"):
                    s = join(FOarc, fn)
                    arc.write(s, fn)
    system(f'move /y "{fld}\\*.zip" "{dirname(fld)}"')


def zuzazip(fld=".", sz=600_000_000):
    rez = DistribResultByChanksForFollowZiping(fld, sz)
    out = mover(fld, rez)
    zipper(out)


# if __name__=='__main__':
#     import sys
#     fld=abspath((a:=sys.argv)[-1])
#     if len(a)==1:fld=dirname(fld)
#     place=fld or r'C:\AAA\MWrez_2023-10-25__10-41-33\WMpdfs' or r'C:\AAA\MWrez_2023-10-25__11-00-15\WMpdfs'
#     zuzazip(place)
if __name__ == "__main__":
    zipper(r"C:\Users\1\Downloads\Zall_МЭК\wrk\a\z")
