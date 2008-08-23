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
from libchristine.gui.BugReport import BugReport
a = Christine()
try:
	if len(sys.argv) > 1 and not "--devel" in sys.argv:
		for i in sys.argv[1:]:
			if os.path.isfile(i):
				a.Queue.add(i,prepend=True)
		a.play()
except:
	BugReport()

a.runGtk()
