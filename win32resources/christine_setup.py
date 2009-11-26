from distutils.core import setup, Extension
import os
import glob
import sys
import py2exe
import shutil

def getFiles(dir):
	"""
	Retorna una tupla de tuplas del directorio
	"""
	# dig looking for files
	a= os.walk(dir)
	b = True
	filenames = []

	while (b):
		try: 
			(dirpath, dirnames, files) = a.next()
			filenames.append([dirpath, tuple(files)])
		except:
			b = False
	return filenames


origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
	dlls = ("msvcp71.dll", "dwmapi.dll", "jpeg62.dll","mfc71.dll")
	if os.path.basename(pathname).lower() in dlls:
		return 0
	return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

class Target:
	def __init__(self,**kw):
			self.__dict__.update(kw)
			self.author = 'Marco Islas'
			self.maintainer = 'Marco Antonio Islas Cruz'
			self.maintainer_email = 'markuz@islascruz.org'
			self.url='http://www.christine-project.org'
			self.classifiers=[
		          'Development Status :: 4 - Beta',
		          'Environment :: GUI',
		          'Intended Audience :: End Users/Desktop',
		          'License :: OSI Approved :: GNU/GPL v.2.0',
		          'Operating System :: Microsoft :: Windows',
		          'Operating System :: POSIX',
		          'Programming Language :: Python',
		          'Programming Language :: C',
		          ]
			self.platforms = ['Posix','Windows XP', 'Windows 2000','Windows Vista']
			self.version        = "0.6.0"
			self.compay_name    = "Christine Project"
			self.copyright      = "(c) 2006-2009, Marco Islas"
			self.name           = "Christine Media Player"
			self.description = 'Christine Media Player'
			self.icon_resources =  [(0, "win32resources/christine.ico")]

target = Target(script = "christine.py")

CLibraryModel = Extension(name = 'libchristine.CLibraryModel',
					language = 'c',
                    sources = ['libchristine/CLibraryModel.c'])


setup(
    windows = [target],
	#Useful for debuggin?, I don't know, but if you want you can use the
	#sources.
    #console = [target],
    options = {
                  'py2exe': {
                      'packages':'encodings,libchristine',
                      'includes': 'cairo, pango, pangocairo, atk, gobject',
                      'optimize': 0,
                      'excludes':'doctest,pdb,unittest,difflib,inspect',
					  'compressed': 0,
					  'skip_archive':1,
					  'unbuffered':True,
                  }
              },

     data_files=[("gui", glob.glob("gui/*.*")),
                 ("gui/pixmaps",glob.glob("gui/pixmaps/*.*")),
    ],
	ext_modules=[CLibraryModel,],
)

try:
	for i in ['etc','lib','share']:
		shutil.copytree(i,os.path.join('dist',i))
	shutil.copy(os.path.join('c:\\','GTK','bin','jpeg62.dll'),
                             os.path.join('dist','jpeg62.dll'))
except Exception, e:
	pass

shutil.copy(os.path.join("./",'build','lib.win32-%d.%d'%tuple(sys.version_info[:2]),'libchristine','CLibraryModel.pyd'),
		os.path.join('dist','libchristine','CLibraryModel.pyd'))
