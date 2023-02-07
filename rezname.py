import sys
import fitz
from datetime import datetime
from os.path import join

import timing


def getArgOr(pos, default, isDir=None):
    rez = sys.argv[pos:] and sys.argv[pos] or default
    return rez if not isDir else join(rez, '')


def rezname():
    return 'rez_'+f'{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}'


# чисто обвязка:

def SimpleJoinPdffromListOf(l, path, doc):
    for i, pdf in enumerate(l):
        doc.insert_pdf(fitz.open(f'{path}{pdf}'),
                       links=0, annots=0, show_progress=0)
        print(timing.log(i, pdf))
    return doc
