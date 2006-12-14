/*
 * C code for the library fill
 * model
 * */


#include <Python.h>
//#include <gtk/gtk.h>
#include <string.h>

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
		Py_INCREF(Py_None);
		result = Py_None;
		return result;
	}
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
		Py_INCREF(Py_None);
		result = Py_None;
		return result;
	}
}

static PyObject *
clibrary_fill_model(PyObject *self,PyObject *args){
	PyObject *sounds,*keys,*temp, *append_result, *arglist, *result,*path;
	PyObject *search=NULL;
	int cont = 0, pos=0;
	int length = 0;
	if (!PyArg_ParseTuple(args,"O",&sounds))
		return NULL;
	if (!PyDict_Check(sounds))
		return NULL;
	keys = PyDict_Keys(sounds);
	PyList_Sort(keys);
	length = PyList_Size(keys);
	//while (PyDict_Next(sounds,&pos,&path,&temp)){
	while (cont < length){
		path = PyList_GetItem(keys,cont);
		temp = PyDict_GetItem(sounds,path);
		if (!PyDict_Contains(temp,PyString_FromString("play_count")))
			PyDict_SetItemString(temp,"play_count",Py_BuildValue("i",0));
		if (!PyDict_Contains(temp,PyString_FromString("duration")))
			PyDict_SetItemString(temp,"duration",Py_BuildValue("s","00:00"));
		if (!PyDict_Contains(temp,PyString_FromString("genre")))
			PyDict_SetItemString(temp,"genre",Py_BuildValue("s"," "));

		// evalutaing the create_iter
		arglist = Py_BuildValue("()");
		iter = PyEval_CallObject(create_iter,arglist);
		Py_DECREF(arglist);
		//checking if iter is not null, else, raise an error
		if (iter== NULL)
			return NULL;
		//Building the arglist for the set method
		search = PyString_FromString(" ");
		
		PyString_Concat(&search,PyDict_GetItemString(temp,"name"));
		PyString_Concat(&search,PyDict_GetItemString(temp,"album"));
		PyString_Concat(&search,PyDict_GetItemString(temp,"artist"));

		if (search == NULL) // Check that the search sfuff is not empty
			return NULL;
		
		arglist = Py_BuildValue("(OiOiOiOiOiOiOiOiOiOiO)",iter,
				1,PyDict_GetItemString(temp,"name"),
				0,path,
				2,PyDict_GetItemString(temp,"type"),
				4,PyDict_GetItemString(temp,"album"),
				5,PyDict_GetItemString(temp,"artist"),
				6,PyDict_GetItemString(temp,"track_number"),
				7,search,
				8,PyDict_GetItemString(temp,"play_count"),
				9,PyDict_GetItemString(temp,"duration"),
				10,PyDict_GetItemString(temp,"genre")
				);
		if (arglist == NULL)
			return NULL;
		append_result = PyEval_CallObject(set,arglist);
		Py_DECREF(arglist);
		if (append_result == NULL)
			return NULL;
		Py_DECREF(iter);
		Py_DECREF(append_result);
		/*
		Py_DECREF(temp);
		Py_DECREF(search);
		Py_DECREF(path);*/
		//cont++;
	}
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
	{NULL,NULL,0,NULL}
};

PyMODINIT_FUNC 
initclibrary(void)
{
	(void) Py_InitModule("clibrary", clibrary_methods);
}

int main(char argc, char *argv[]){
	initclibrary();
	return 0;
}

