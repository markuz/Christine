scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=__init__.pyc \
			Library.pyc \
			libs_christine.pyc \
			Player.pyc \
			sources_list.pyc \
			Translator.pyc \
			Christine.pyc \
			Share.pyc \
			Validator.pyc \
			christineConf.pyc \
			Tagger.pyc \
			LibraryModel.pyc \
			globalvars.pyc

DISTFILES= Makefile.in \
		   __init__.py \
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
			globalvars.py 


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


all-am: globalvars.py
	

clean:
	rm $(srcdir)/Share.pyc
	rm $(srcdir)/Christine.pyc
	rm $(srcdir)/GtkMisc.pyc
	rm $(srcdir)/About.pyc
	rm $(srcdir)/Translator.pyc
	rm $(srcdir)/Plugins.pyc
	rm $(srcdir)/libs_christine.pyc
