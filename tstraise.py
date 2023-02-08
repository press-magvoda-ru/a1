import traceback

def t(a,b,c):
    #traceback.print_stack()
    raise Exception(f'Неожиданый тип квитанции {locals()=}\n {0 and globals()=} \n')



t(1,2,3)