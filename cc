import os, sys
dst=os.path.join(sys.argv[-1],'') # без аргументов будет хм
lst=open('lst','r').read().splitlines()
for fl in lst:
	os.system(f'copy  {fl} {dst}')


