#!/usr/bin/env python
import os
import sys
sys.path.insert(0,os.getcwd())
elements = locals()
#lista = [k for k in elements['arguments'] if type(k) == str]
#sys.argv = lista
from libchristine.libs_christine import sanity
sanity()
from libchristine.Christine import *
runChristine()