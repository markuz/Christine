AC_INIT("christine","0.0.2",markuz@islascruz.org)
AM_INIT_AUTOMAKE("christine","0.0.2")

AC_CONFIG_SRCDIR(lib_christine)
AC_CONFIG_SRCDIR(gui)

AM_MAINTAINER_MODE

AC_PATH_X
AC_HEADER_STDC
AC_PROG_CC
AC_HEADER_STDC

AM_MAINTAINER_MODE
AM_PATH_PYTHON

PKG_CHECK_MODULES(pygtk, pygtk-2.0)
PKG_CHECK_MODULES(gstreamer,gstreamer-0.10)
PKG_CHECK_MODULES(gat_python,gst-python-0.10)
PKG_CHECK_MODULES(gnome_python,gnome-python-2.0)
PKG_CHECK_MODULES(gnome_python_extras,gnome-python-extras-2.0)
PKG_CHECK_MODULES(gconf,gconf-2.0)
PKG_CHECK_MODULES(glib,glib-2.0)

AC_SUBST(pygtk_CFLAGS)
AC_SUBST(pygtk_LIBS)

PROGRAM_NAME="christine"
VERSION="0.0.2"

AC_SUBST(PROGRAM_NAME)
AC_SUBST(VERSION)

GETTEXT_PACKAGE=christine
AC_SUBST(GETTEXT_PACKAGE)
ALL_LINGUAS="es_ES"
AC_SUBST(ALL_LINGUAS)
USE_NLS=yes
AC_SUBST(USE_NLS)
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL

AC_CONFIG_FILES([
Makefile
lib_christine/Makefile
gui/Makefile
gui/pixmaps/Makefile
po/Makefile.in
po/Makefile
po/POTFILES
intltool-extract
intltool-merge
intltool-update
])

AC_OUTPUT
