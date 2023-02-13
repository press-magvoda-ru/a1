from reparseWxMx import Pg
import pandas as pd
from ast import literal_eval
df=pd.DataFrame(eval(open('..\\wTotB').read()))
print(df)