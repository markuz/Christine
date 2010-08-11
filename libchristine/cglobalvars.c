#include "Python.h"
#include "pythonrun.h"
#include "import.h"
#include "stdio.h"
#include "string.h"

/*
* This file is part of the Christine project
*
* Copyright (c) 2006-2007 Marco Antonio Islas Cruz
*
* Christine is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* Christine is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
*
* @category  GTK
* @package   Preferences
* @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
* @copyright 2006-2010 Christine Development Group
* @license   http://www.gnu.org/licenses/gpl.txt
*
* Module that holds all christine global vars.
*/
#define PROGRAM_VERSION ("0.8.0");
#define BUGURL ("http://github.com/markuz/Christine/issues");


void error(char *msg) {
	PyErr_Print();
	//printf("%s\n", msg);
	exit(1);
}

static PyMethodDef cglobalvarsMethods[] = { {NULL} };

static PyMethodDef ModuleMethods[] = { {NULL} };

#ifdef __cplusplus
extern "C"
#endif
PyMODINIT_FUNC
initcglobalvars(void)
{

	PyMethodDef *def;

	PyObject *module = NULL;
	PyObject *moduleDict = NULL;
	PyObject *classDict = NULL;
	PyObject *className = NULL;
	PyObject *fooClass = NULL;

    module = Py_InitModule("cglobalvars", ModuleMethods);
    moduleDict = PyModule_GetDict(module);
    classDict = PyDict_New();
    className = PyString_FromString("globalvars");
    fooClass = PyClass_New(NULL, classDict, className);

	PyImport_AddModule("cglobalvars");

    PyDict_SetItemString(moduleDict, "cglobalvars", fooClass);
    Py_DECREF(classDict);
    Py_DECREF(className);
    Py_DECREF(fooClass);

	/* add variables to class */
	PyDict_SetItemString(moduleDict, "BUGURL", Py_BuildValue("s","http://github.com/markuz/Christine/issues"));
	PyDict_SetItemString(moduleDict, "TRANSLATEURL", Py_BuildValue("s","https://translations.launchpad.net/christine"));
	

    /* add methods to class */
    for (def = cglobalvarsMethods; def->ml_name != NULL; def++) {
    	PyObject *func = PyCFunction_New(def, NULL);
    	PyObject *method = PyMethod_New(func, NULL, fooClass);
    	PyDict_SetItemString(classDict, def->ml_name, method);
    	Py_DECREF(func);
    	Py_DECREF(method);
     }

}
int
main(int argc, char *argv[])
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initcglobalvars();
    return 0;
}
