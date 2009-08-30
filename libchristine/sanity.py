#!/usr/bin/env python
# -*- encoding: latin-1 -*-
## Copyright (c) 2006 Marco Antonio Islas Cruz
## <markuz@islascruz.org>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os
from libchristine.globalvars import USERDIR

class sanity:
	'''
		Make all the sanity checks
	'''
	def __init__(self):
		self.__check_christine_dir()
		self.check_xgd_data_home()
		#=======================================================================
		# self.__check_dir(os.path.join(USERDIR,"sources"))
		# self.__check_dir(os.path.join(USERDIR,"uplugins"))
		# if not os.path.exists(os.path.join(USERDIR,"uplugins","__init__.py")):
		#		f = open(os.path.join(USERDIR,"uplugins","__init__.py"),"w+")
		#		f.write("#python")
		#		f.close()
		# if os.getgid() == 0:
		#	self.__check_dir(os.path.join(DATADIR,"christine","cplugins"))
		#=======================================================================

	def __check_christine_dir(self):
		if not os.path.exists(USERDIR):
			os.mkdir(USERDIR)
		else:
			if os.path.isfile(USERDIR):
				os.unlink(USERDIR)
				self.__check_christine_dir()

	def __check_dir(self,dir):
		if not os.path.exists(dir):
			os.mkdir (dir)
		else:
			if os.path.isfile(dir):
				os.unlink(dir)
				self.__check_dir(dir)
	
	def check_xgd_data_home(self):
		oldpath = os.path.join(os.environ["HOME"],".christine")
		#oldpath = "/home/markuz/.christine"
		if os.path.exists(oldpath):
			import shutil
			a = os.walk(oldpath)
			while 1:
				try:
					dirpath, dirnames, files = a.next()
					for i in dirnames:
						shutil.move(os.path.join(dirpath, i), USERDIR)
					for i in files:
						shutil.move(os.path.join(dirpath, i), USERDIR)
				except StopIteration:
					break
			#remove the old directory:
			try:
				shutil.rmtree(oldpath)
			except:
				pass
		return True