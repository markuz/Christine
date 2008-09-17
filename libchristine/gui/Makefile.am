scriptsdir = @PYTHON_LIB_DIR@/libchristine/gui/

scripts_DATA=__init__.py \
			About.py \
			BugReport.py \
			Display.py \
			Preferences.py \
			GtkMisc.py \
			openRemote.py

DISTFILES= Makefile.in \
			${scripts_DATA}


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
