scriptsdir = @PYTHON_LIB_DIR@/libchristine/pattern

scripts_DATA=__init__.pyc \
			 Singleton.pyc
DISTFILES= Makefile.in \
		   __init__.py \
			Singleton.py 


pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonincludedir = @PYTHON_INCLUDE_DIR@
usr_libdir = @includedir@

programname=@PROGRAM_NAME@
version=@VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@version\@,$(version),g'

all: all-am
	python -c "import compileall,re; compileall.compile_dir('./', rx=re.compile('/[.]svn'), force=True)"

all-am: 


