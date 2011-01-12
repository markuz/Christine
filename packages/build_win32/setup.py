import distutils
from distutils import debug
distutils.debug.DEBUG = "true"
from distutils.core import setup, Extension
import os
import glob
import sys
import py2exe
import shutil
import subprocess
from optparse import OptionParser


#Current path, add the subdir to the system path.
top_dir= os.path.abspath(os.path.dirname(os.path.dirname(\
    os.path.abspath((__file__)))))
sys.path.append(top_dir)

# ModuleFinder can't handle runtime changes to __path__, but win32com uses
# them, particularly for people who build from sources.  Hook this in.
try:
    import py2exe.mf as modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ("win32com.shell", ):
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass


PROGRAM_VERSION = '0.7.0'

sys.argv.append("py2exe")


print sys.argv

usage = "Christine [args]\n"
usage += "if you are building with mingw use \"build --compiler=mingw32\""
version = PROGRAM_VERSION

parser = OptionParser(usage=usage, version=version)
parser.allow_interspersed_args = True
parser.error = lambda msg: None
parser.add_option('-C',"--compiler", dest='compiler', action="store",
        type='string',help='Compiler to use')
parser.add_option('-G','--gst-path',dest='gst_path',action='store',
        type='string',help='Path to Gstreamer installation')
parser.add_option('-T','--gtk-path',dest='gtk_path',action='store',
        type='string',help='Path to GTK+ Runtime installation')
parser.add_option('-H','--help-commands', dest='help_commands',
        action = 'store_true',help='Show help about the  supported commands')
options, args = parser.parse_args()
print options

required_modules = {
        'GTK':options.gtk_path,
        'GStreamer': options.gst_path,
        }
error = ''
for k, v in required_modules.iteritems():
    if not v:
        error += "Can't get %s path, build will fail\n"%k
if error:
    sys.stderr.write(error)
    sys.stderr.flush()
    print usage
    sys.exit(-1)

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
                  'Development Status :: 5 - Stable',
                  'Environment :: GUI',
                  'Intended Audience :: End Users/Desktop',
                  'License :: OSI Approved :: GNU/GPL v.2.0',
                  'Operating System :: Microsoft :: Windows',
                  'Operating System :: POSIX',
                  'Programming Language :: Python',
                  'Programming Language :: C',
                  ]
            self.platforms = ['Posix','Windows XP', 'Windows 2000','Windows Vista']
            self.version        = "0.7.0"
            self.compay_name    = "Christine Project"
            self.copyright      = "(c) 2006-2009, Marco Islas"
            self.name           = "Christine Media Player"
            self.description = 'Christine Media Player'
            self.icon_resources =  [(0, "win32resources/christine.ico")]

target = Target(script = "christine.py")

CLibraryModel = Extension(name = 'libchristine.CLibraryModel',
                    language = 'c',
                    sources = ['libchristine/CLibraryModel.c'])

ChristineGtkBuilder= Extension(name = 'libchristine.gui.ChristineGtkBuilder',
                    language = 'c',
                    sources = ['libchristine/gui/ChristineGtkBuilder.c'],
                include_dirs=['./gtksrc', 'c:\Python26\include',
                              'c:\Python26\include\pygtk-2.0',
                              'c:\Python26\include\pycairo'],
                )



setup(
    windows = [target],
    #Useful for debuggin?, I don't know, but if you want you can use the
    #sources.
    #console = [target],
    options = {
                  'py2exe': {
                      'packages':'encodings,libchristine',
                      'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
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
    ext_modules=[CLibraryModel]#,ChristineGtkBuilder],
)

gst_libs = ((os.path.join(options.gst_path,"lib","gstreamer-0.10"),
        "lib/gstreamer-0.10"),)
gtk_shares = tuple([(os.path.join(options.gtk_path, k),k) for k in ['etc','lib','share']])

for i in ['gui/icons/','libchristine/Plugins/webservices/glade/', gst_libs,
        gtk_shares]:
    try:
        if isinstance(i,tuple):
            src, dest  = i
        else:
            src = i[0]
            dest = i[1]
        shutil.copytree(src,os.path.join('dist',dest))
    except Exception, e:
        print e
        t = raw_input('Terminate ? [y/N]: ')
        if t.lower() == 'y':
            sys.exit(-1)

try:
    path = os.path.join('C:\\','gstreamer','bin')
    for i in os.listdir(path):
        if os.path.isfile(i):
            shutil.copy(os.path.join(path, i), 
                    os.path.join('dist',i))
except Exception,e:
    print e
    t = raw_input('Terminate ? [y/N]: ')
    if t.lower() == 'y':
        sys.exit(-1)
try:
    shutil.copy(os.path.join('c:\\','GTK','bin','jpeg62.dll'),
                             os.path.join('dist','jpeg62.dll'))
except:
    pass

shutil.copy(os.path.join("./",'build','lib.win32-%d.%d'%tuple(sys.version_info[:2]),'libchristine','CLibraryModel.pyd'),
        os.path.join('dist','libchristine','CLibraryModel.pyd'))
#shutil.copy(os.path.join("./",'build','lib.win32-%d.%d'%tuple(sys.version_info[:2]),'libchristine','ChristineGtkBuilder.pyd'),
#        os.path.join('dist','libchristine','ChristineGtkBuilder.pyd'))


# Create installer
# Requires NSIS to be installed and in the system PATH
print "Building the installer"

program_info = {
        'program_name':'Christine',
        'exe_name':'christine',
        'full_product_name': 'Christine Media Player',
        'version':PROGRAM_VERSION,
        'release_name':'',
        'publisher':'Christine Develpment Team',
        }

build_script = file("christine.nsh").read()
build_script = build_script % program_info
header_file = file("_christine.nsh", "w")
header_file.write(build_script)
header_file.close()

print "Building installer..."
build_script = file("chistine.nsi").read()
# Dynamically insert details into the build script.
build_script = build_script % program_info
makensis = subprocess.Popen("makensis.exe -", shell=True,
                            stdin=subprocess.PIPE,
                            cwd=os.path.join(top_dir, "build_win32"))
makensis.communicate(build_script)

