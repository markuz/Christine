scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=christineConf.py \
			christineLogger.py \
			Christine.py \
			Events.py \
			globalvars.py \
			__init__.py \
			LibraryModel.py \
			Library.py \
			libs_christine.py \
			Logger.py \
			options.py \
			Player.py \
			Sanity.py \
			Share.py \
			sources_list.py \
			Tagger.py \
			Translator.py \
			ui.py \
			Validator.py

DISTFILES= Makefile.in \
		   globalvars.py.in\
			${scripts_DATA}


pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonincludedir = @PYTHON_INCLUDE_DIR@
pythonlibdir = @PYTHON_LIB_DIR@
usr_libdir = @includedir@

programname=@PROGRAM_NAME@
version=@VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@pythonlibdir\@,$(pythonlibdir),g' \
	   -e 's,@version\@,$(version),g'

globalvars.py: Makefile $(srcdir)/globalvars.py.in
	$(edit) $(srcdir)/globalvars.py.in > globalvars.py

all: globalvars.py

clean:
	rm $(srcdir)/*.pyc
	rm globalvars.py
