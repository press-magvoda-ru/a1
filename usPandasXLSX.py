import pandas as pd
import debundle
import rezname
import os
from reparseWxMx import bundle


#args for real use nm as fullpath source of df
def hehe(df):
    nm='hehe.xlsx'
    mode='wa'[int(os.path.exists(nm))]
    with pd.ExcelWriter(nm,mode=mode) as ExW:
#       df.sum(1).to_excel(ExW,sheet_name=rezname.rezname(),index=list('mwPksT')) 
       df.sum(1).to_excel(ExW,sheet_name='same',index=list('mwPksT'),startrow=10) 


if __name__=='__main__':
    df =debundle.getS(rezname.getArgOr(1,'..\\MWrez_2023-02-15__08-38-16\\WMpdfs\\'))
    df.index=bundle._fields
    hehe(df)