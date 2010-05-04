#!/usr/bin/env python
# -*- encoding: latin-1 -*-
# -*- coding: latin-1 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2007 Marco Antonio Islas Cruz
#
# Christine is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Christine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
'''
Created on Jun 22, 2009

@author: markuz
'''
import gobject
from libchristine.Logger import LoggerManager
celogger = LoggerManager().getLogger('catch_exception')
cdlogger = LoggerManager().getLogger('cubic_deprecated')
cflogger = LoggerManager().getLogger('cubic_future')

def future(fn):
	'''
	Ejecuta la funcion guardando en bitacoras que la funcion es a futuro
	y que puede haber cambios, por lo que no deberia usarse
	@param fn:
	'''
	def func(*args):
		msg = "El uso de de %s.%s no deberia de usarse en esta version"%(
													fn.__module__,fn.__name__)
		msg+= "Su uso esta pensado a futuro. y puede haber cambios en el API"
		cflogger.warning(msg)
		result = fn(*args)
		return result
	return func

def deprecated(fn):
	'''
	Ejecuta la funcion guardando en bitacoras que la funcion esta deprecada y
	no deberia usarse 
	@param fn:
	'''
	def func(*args):
		msg = "El uso de %s.%s esta depreciado y no deberia usarse"%(
													fn.__module__,fn.__name__)
		cdlogger.warning(msg)
		result = fn(*args)
		return result
	return func

def idle_execute(*m):
	'''
	Ejecuta la funcion enpapelada tan pronto como exista un tiempo muerto 
	en el ciclo principal de GTK+.
	'''
	def wrapper (func, *args, **kwargs):
		def _func(*args,**kwargs):
			return gobject.idle_add(func, *args, **kwargs)
		return _func
	return wrapper

def catch_exception(fn):
	'''
	Ejecuta la funcion bajo un try/except, si hay una excepcion la guarda en 
	bitacora y permite la ejecucion del programa
	'''
	def _func(*args,**kwargs):
		try:
			return fn(*args, **kwargs)
		except Exception, e:
			celogger.exception(e)
	return _func
