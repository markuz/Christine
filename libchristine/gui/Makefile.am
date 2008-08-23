scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=__init__.pyc \
			About.pyc \
			BugReport.pyc \
			Display.pyc \
			Preferences.pyc \
			GtkMisc.pyc 

DISTFILES= Makefile.in \
		   __init__.py \
		   About.py \
			BugReport.py \
			Display.py \
			Preferences.py \
			GtkMisc.pyc  


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

clean:
	rm -v $(srcdir)/*.pyc 
