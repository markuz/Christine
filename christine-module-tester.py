#!/usr/bin/env python
# $Rev: 1201 $
# $Author: marco $
# $LastChangedDate: 2008-04-30 10:06:13 -0500 (Wed, 30 Apr 2008) $
import gc

import sys
import logging

if len(sys.argv) < 2:
	modulo = raw_input('Prueba a correr: \n')
	sys.argv.append(modulo)
if  '-p' in sys.argv:
	import pdb
	pdb.set_trace()


level = logging.DEBUG

logging.basicConfig(level=level,
          format='%(asctime)s %(name)-15s %(levelname)s:%(lineno)s %(message)s')

logger = logging.getLogger('guitest')

gc.set_debug(gc.DEBUG_LEAK)
gc.enable()

def showGarbage():
	'''
	Muestra la informacion de basura encontrada por el colector de basura
	'''
	#print gc.collect()
	for x in gc.garbage:
		s = str(x)
		if len(s) > 80: s = s[:80]
		print type(x), "\n  ", s
	return True

def importName(modulename, name):
	module = __import__(modulename, globals(), locals(), [name])
	return vars(module)[name]

importName('christinetests',sys.argv[1])

