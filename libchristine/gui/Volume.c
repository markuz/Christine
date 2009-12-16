/*
 * Copyright (c) 2006 Marco Antonio Islas Cruz
 * <markuz@islascruz.org>
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

#include "gtk/gtk.h"
#include "pygobject.h"
#include "pygtk/pygtk.h"
#include "Python.h"


/* global variable declared at top of file */
static PyTypeObject *PyGObject_Type=NULL;    
GtkWidget *Volume_widget = NULL;
/* ... */

static PyObject*
init(PyObject *self, PyObject *args){
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *set_value(PyObject *self, PyObject *args){
	float value;
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *Volume(PyObject *self, PyObject *args){
	PyGObject *py_container;
	PyObject *py_self;
	GtkWidget *hbox;

	if (!PyArg_ParseTuple(args, "OO!", &py_self, PyGObject_Type, &py_container)){
		return NULL;
	}
	hbox = GTK_WIDGET(py_container->obj);
	Volume_widget = gtk_volume_button_new();
	gtk_box_pack_start(GTK_BOX(hbox), Volume_widget, FALSE, FALSE, 0);
	gtk_widget_show(Volume_widget);
	//return Py_BuildValue('i', 0);
	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef VolumeMethods[] = {
	{"__init__", init, METH_VARARGS, "doc string"},
    {"Volume",  Volume, METH_VARARGS,"Returns a ref."},
    {NULL, NULL}
};

static PyMethodDef ModuleMethods[] = { {NULL} };

#ifdef __cplusplus
extern "C"
#endif
PyMODINIT_FUNC
initVolume(void)
{

	PyMethodDef *def;

	PyObject *module = NULL;
	PyObject *mod1 = NULL;
	PyObject *moduleDict = NULL;
	PyObject *classDict = NULL;
	PyObject *className = NULL;
	PyObject *fooClass = NULL;

	init_pygobject();
	init_pygtk();

	mod1 = PyImport_ImportModule("gobject");
	if (mod1) {
          PyGObject_Type =
           (PyTypeObject*)PyObject_GetAttrString(mod1, "GObject");
          Py_DECREF(mod1);
      }
	
    module = Py_InitModule("Volume", ModuleMethods);
    moduleDict = PyModule_GetDict(module);
    classDict = PyDict_New();
    className = PyString_FromString("Volume");
    fooClass = PyClass_New(NULL, classDict, className);

	PyImport_AddModule("Volume");

    PyDict_SetItemString(moduleDict, "Volume", fooClass);
    Py_DECREF(classDict);
    Py_DECREF(className);
    Py_DECREF(fooClass);

    /* add methods to class */
    for (def = VolumeMethods; def->ml_name != NULL; def++) {
    	PyObject *func = PyCFunction_New(def, NULL);
    	PyObject *method = PyMethod_New(func, NULL, fooClass);
    	PyDict_SetItemString(classDict, def->ml_name, method);
    	Py_DECREF(func);
    	Py_DECREF(method);
     }

}


int main(int argc, char *argv[]){
   /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initVolume();

	return 0;
}
