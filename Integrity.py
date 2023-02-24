# -*- coding: utf-8 -*-
import inspect

class code():
    def __init__(self):
        pass
    def myFunction(self):
        blabla = 'blabla'
        print(blabla)
        num = 19
        print(num)
    def findmethod(self, func_name):
        print(self.findmethod.__name__)
        func = getattr(self, func_name)
        print(inspect.getsource(func))
        import sys
        current_module = sys.modules[__name__]
        return inspect.getsource(current_module)
        
#print(inspect.getsource('myFunction'))
#c = code()
#mycode = c.findmethod('myFunction')

#import hashlib
#
#mycodehash = hashlib.sha512(mycode.encode()).hexdigest()
#
#print(mycodehash)

import sys
current_module = sys.modules[__name__]
#inspect_module = sys.modules[inspect.__name__]
#print(inspect.getsource(inspect_module))
import types
def imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            if val.__name__.lower() != 'builtins' and val.__name__.lower() != '__main__':
                yield val.__name__

print(list(imports()))

import os
print(os.getpid())
from subprocess import getoutput
process_info = getoutput('wmic process where "ProcessID={}" get Caption,ExecutablePath,Processid,CommandLine'.format(os.getppid()))
print(process_info)
