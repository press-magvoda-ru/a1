#!C:\Users\1\AppData\Local\Programs\Python\Python311\python.exe
"""
pycallgraph
This script is the command line interface to the pycallgraph Python library.

See http://pycallgraph.slowchop.com/ for more information.
"""
import sys
import os

import pycallgraph2 as __pycallgraph


# Inject the current working directory so modules can be imported.
sys.path.insert(0, os.getcwd())

__config = __pycallgraph.Config()
__config.parse_args()
__config.strip_argv()

globals()['__file__'] = __config.command

__file_content = open(__config.command).read()

with __pycallgraph.PyCallGraph(config=__config):
    exec(__file_content)
