scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=__init__.py \
			Library.py \
			libs_christine.py \
			Player.py \
			sources_list.py \
			Translator.py \
			Christine.py \
			Share.py \
			Validator.py \
			christineConf.py \
			Tagger.py \
			LibraryModel.py \
			globalvars.py \
			christineLogger.py \
			sqlitedb.py \
			ui.py \
			tryicon.py

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

globalvars.py: Makefile $(srcdir)/globalvars.py.in
	$(edit) $(srcdir)/globalvars.py.in > globalvars.py

all: globalvars.py

clean:
	rm $(srcdir)/*.pyc
