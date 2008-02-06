/*
 * C code for the library fill
 * model
 *
 * This file is part of the Christine project
 *
 * Copyright (c) 2006-2007 Marco Antonio Islas Cruz
 *
 * Christine is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License.
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
 * @category  Multimedia
 * @package   Christine
 * @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
 * @copyright 2006-2007 Christine Development Group
 * @license   http://www.gnu.org/licenses/gpl.txt
 * */


#include <Python.h>
#include <string.h>
#include <stdlib.h>


void error(char *msg) { 
	PyErr_Print();
	printf("%s\n", msg); 
	exit(1); 
}

static PyObject *create_iter = NULL;
static PyObject *set = NULL;
PyObject *iter = NULL;
PyObject *dict;

static PyObject *
set_create_iter(PyObject *self, PyObject *args){
	PyObject *result = NULL;
	PyObject *temp;

	if (PyArg_ParseTuple(args,"O:set_callback",&temp)){
		if (!PyCallable_Check(temp)){
			PyErr_SetString(PyExc_TypeError, "parameter must be callable");
			return NULL;
		}
		Py_XINCREF(temp);
		Py_XDECREF(create_iter);
		create_iter = temp;
	}
	Py_INCREF(Py_None);
	result = Py_None;
	return result;
}

static PyObject *
set_set(PyObject *self, PyObject *args){
	PyObject *result = NULL;
	PyObject *temp;

	if (PyArg_ParseTuple(args,"O:set_callback",&temp)){
		if (!PyCallable_Check(temp)){
			PyErr_SetString(PyExc_TypeError, "parameter must be callable");
			return NULL;
		}
		Py_XINCREF(temp);
		Py_XDECREF(set);
		set = temp;
	}
	Py_INCREF(Py_None);
	result = Py_None;
	return result;

}

/*
static PyObject *
set_events_pending(PyObject *self, PyObject *args){
	PyObject *result = NULL;
	PyObject *temp;

	if (PyArg_ParseTuple(args,"O:set_callback",&temp)){
		if (!PyCallable_Check(temp)){
			PyErr_SetString(PyExc_TypeError, "parameter must be callable");
			return NULL;
		}
		Py_XINCREF(temp);
		Py_XDECREF(set);
		set = temp;
	}
	Py_INCREF(Py_None);
	result = Py_None;
	return result;

}


static PyObject *
gtk_main_iteration(PyObject *self, PyObject *args){
	PyObject *result = NULL;
	PyObject *temp;

	if (PyArg_ParseTuple(args,"O:set_callback",&temp)){
		if (!PyCallable_Check(temp)){
			PyErr_SetString(PyExc_TypeError, "parameter must be callable");
			return NULL;
		}
		Py_XINCREF(temp);
		Py_XDECREF(set);
		set = temp;
	}
	Py_INCREF(Py_None);
	result = Py_None;
	return result;

}
*/
static PyObject *
clibrary_fill_model(PyObject *self,PyObject *args){
	PyObject *sounds,*keys,*temp, *append_result, *arglist, *result,*path,*pix;
	PyObject *search=NULL;
	int cont = 0;
	int length = 0;
	if (!PyArg_ParseTuple(args,"OO",&sounds,&pix))
		return NULL;
	if (!PyDict_Check(sounds))
		return NULL;
	keys = PyDict_Keys(sounds);
	PyList_Sort(keys);
	length = PyList_Size(keys);
	int stat;
	while (cont < length){
		path = PyList_GetItem(keys,cont);
		temp = PyDict_GetItem(sounds,path);

		if (!PyDict_Contains(temp,PyString_FromString("name")))
			stat = PyDict_SetItemString(temp,"name",Py_BuildValue("s"," "));
		if (stat == -1)
			error("");
		/*
		if (!PyDict_Contains(temp,PyString_FromString("play_count")))
			stat = PyDict_SetItemString(temp,"play_count",Py_BuildValue("i",0));
		if (stat == -1)
			error("");

		if (!PyDict_Contains(temp,PyString_FromString("duration")))
			stat = PyDict_SetItemString(temp,"duration",Py_BuildValue("s","00:00"));
		if (stat == -1)
			error("");

		if (!PyDict_Contains(temp,PyString_FromString("genre")))
			stat =PyDict_SetItemString(temp,"genre",Py_BuildValue("s"," "));
		if (stat == -1)
			error("");

		if (!PyDict_Contains(temp,PyString_FromString("track_number")))
			stat =PyDict_SetItemString(temp,"track_number",Py_BuildValue("i",0));
		if (stat == -1)
			error("");

	
		if (!PyDict_Contains(temp,PyString_FromString("album")))
			stat = PyDict_SetItemString(temp,"album",Py_BuildValue("s"," "));
		if (stat == -1)
			error("");

		if (!PyDict_Contains(temp,PyString_FromString("artist")))
			stat = PyDict_SetItemString(temp,"artist",Py_BuildValue("s"," "));
		if (stat == -1)
			error("");*/
		
		// evaluating the create_iter
		arglist = Py_BuildValue("()");
		iter = PyEval_CallObject(create_iter,arglist);
		Py_DECREF(arglist);
		//checking if iter is not null, else, raise an error
		if (iter== NULL)
			return NULL;
		//Building the arglist for the set method
		
		search = PyString_FromString(" ");
		if (PyDict_GetItemString(temp,"name") != Py_None)
			PyString_Concat(&search,PyDict_GetItemString(temp,"name"));
		if (PyDict_GetItemString(temp,"album") != Py_None)
			PyString_Concat(&search,PyDict_GetItemString(temp,"album"));
		if (PyDict_GetItemString(temp,"artist") != Py_None)
			PyString_Concat(&search,PyDict_GetItemString(temp,"artist"));
		if (PyDict_GetItemString(temp,"type") != Py_None)
			PyString_Concat(&search,PyDict_GetItemString(temp,"type"));

		if (search == NULL){ // Check that the search sfuff is not empty
			error("");
			return NULL;
		}
	
		//arglist = Py_BuildValue("(OiOiOiOiOiOiOiOiOiOiOiO)",iter,
		arglist = Py_BuildValue("(OiOiOiO)",iter,
				0,path,
				1,PyDict_GetItemString(temp,"name"),
				/*2,PyDict_GetItemString(temp,"type"),
				3,pix,
				4,PyDict_GetItemString(temp,"album"),
				5,PyDict_GetItemString(temp,"artist"),
				6,PyDict_GetItemString(temp,"track_number"),*/
				7,search
				/*8,PyDict_GetItemString(temp,"play_count"),
				9,PyDict_GetItemString(temp,"duration"),
				10,PyDict_GetItemString(temp,"genre")*/
				);
		if (arglist == NULL){
			error("");
			return NULL;
		}
		append_result = PyEval_CallObject(set,arglist);
		Py_DECREF(arglist);
		if (append_result == NULL)
			return NULL;
		Py_DECREF(iter);
		Py_DECREF(append_result);
		cont++;
	}
	/*
	Py_DECREF(temp);
	Py_DECREF(search);
	Py_DECREF(path);*/

	Py_INCREF(Py_None);
	result = Py_None;
	return result;
}

static PyObject *
build_dict(PyObject *self,PyObject *args){
	char *text,*key=NULL;
	unsigned long int length=0,cont=0,t=0;
	PyObject *value;
	if (!PyArg_ParseTuple(args,"s",&text))
		return NULL;
	dict = PyDict_New();
	length = strlen(text);
	while (cont < length){
		++cont;
		value = Py_BuildValue("i",cont);
		t = PyInt_AsLong(value);
		sprintf(key,"%lu",t);
		PyDict_SetItemString(dict,key,value);
		Py_DECREF(value);
	}
	return dict;
}

static PyMethodDef clibrary_methods[] = {
	{"fill_model",clibrary_fill_model,METH_VARARGS,"receives a dict and check if it is a dict"},
	{"set_create_iter",set_create_iter,METH_VARARGS, "set the callback function to create a iter"},
	{"set_set",set_set,METH_VARARGS, "set the callback function that receives a dictionary and then loops in its keys to store the values in the model"},
	{"build_dict", build_dict, METH_VARARGS, "build a dictionary from a string using"},
//	{"set_events_pending". events_pending, METH_VARARGS, "Sets the gtk.events_pending"}
//	{"set_gtk_main_iteration". gtk_main_iteration, METH_VARARGS, "Sets the gtk.main_iteration"}
	{NULL,NULL,0,NULL}
};

PyMODINIT_FUNC 
initclibrary(void)
{
	(void) Py_InitModule("clibrary", clibrary_methods);
}

int main(int argc, char *argv[]){
	initclibrary();
	return 0;
}

