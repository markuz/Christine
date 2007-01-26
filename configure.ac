AC_INIT("christine","0.0.3",markuz@islascruz.org)
AM_INIT_AUTOMAKE("christine","0.0.3")

AC_CONFIG_SRCDIR(lib_christine)
AC_CONFIG_SRCDIR(gui)

AM_MAINTAINER_MODE

AC_PATH_X
AC_HEADER_STDC
AC_PROG_CC
AC_HEADER_STDC

AM_MAINTAINER_MODE
AM_PATH_PYTHON
AM_PROG_LIBTOOL
LIBTOOL="$LIBTOOL --silent"
AC_PROG_CC
AC_PROG_INSTALL
PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(pygtk, pygtk-2.0)
PKG_CHECK_MODULES(gstreamer,gstreamer-0.10)
PKG_CHECK_MODULES(gst_python,gst-python-0.10)
PKG_CHECK_MODULES(gnome_python,gnome-python-2.0)
PKG_CHECK_MODULES(gnome_python_extras,gnome-python-extras-2.0)
PKG_CHECK_MODULES(gconf,gconf-2.0)
PKG_CHECK_MODULES(glib,glib-2.0)

AC_SUBST(pygtk_CFLAGS)
AC_SUBST(pygtk_LIBS)

PROGRAM_NAME="christine"
VERSION="0.0.3"
PREFIX=/usr
PYTHON_INCLUDE_DIR=`python -c "from distutils import sysconfig; print sysconfig.get_python_inc()"`
PYTHON_LIB_DIR=`python -c "from distutils import sysconfig; print sysconfig.get_python_lib()"`

AC_SUBST(PROGRAM_NAME)
AC_SUBST(VERSION)
AC_SUBST(PREFIX)
AC_SUBST(PYTHON_INCLUDE_DIR)
AC_SUBST(PYTHON_LIB_DIR)

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
cplugins/Makefile
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

echo 
echo $PROGRAM_NAME will be installed in......: ${prefix}/bin

