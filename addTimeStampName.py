﻿import os
import os.path
import sys
import rezname

if not sys.argv[:-1]:
    print("Какие ваши аргументы?")
    exit(1)
nm = sys.argv[-1]
fn = os.path.basename(nm)
fn = ".".join(fn.split(".")[:-1])
os.system(f'rename  "{nm}" "{fn}{rezname.rezname()[3:]}.exe"')
