#include "Python.h"
#include "pythonrun.h"
#include "import.h"
#include "stdio.h"
#include "string.h"

void error(char *msg) {
	PyErr_Print();
	printf("%s\n", msg);
	exit(1);
}

static PyObject*
init(PyObject *self, PyObject *args){
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
search_iter_on_column(PyObject *self, PyObject *args){
	int counter = 0; 
	static PyObject *data;
	static PyObject *sdatat;
	static PyObject *selfobj;
	static PyObject *column;
	int columnint;
	static PyObject *get_iter;
	static PyObject *result;
	static PyObject *nargs;
	static PyObject *lvalue;
	static PyObject *value;
	static PyObject *iter;
	int comp;

	if (!PyArg_ParseTuple(args, "OOO", &selfobj, &value, &column)){
		printf("Unable parse args\n");
		return NULL;
	}
	data = PyObject_GetAttrString(selfobj, "data");
	get_iter = PyObject_GetAttrString(selfobj, "get_iter");
	if (!data || !get_iter || !value ){
		printf("no data, get_iter, value or column\n");
		Py_INCREF(Py_None);
    	return Py_None;
	}
	iter = PyObject_GetIter(data);
	columnint = PyInt_AsLong(column);
	result = NULL;
	while (1){
		sdatat = PyIter_Next(iter);
		if (!sdatat){
			result = NULL;
			break;
		}
		if (!sdatat){
			printf("No sdatat\n");
			result = NULL;
			break;
		}
		lvalue = PyList_GetItem(sdatat, columnint); 
		Py_DECREF(sdatat);
		if (!lvalue){
			printf("No lvalue\n");
			result = NULL;
			break;
		}
		comp = PyObject_RichCompareBool(value, lvalue, Py_EQ);
		if ( comp == 1){
			nargs = Py_BuildValue("(i)", counter);
			result = PyEval_CallObject(get_iter, nargs);
			printf("dec get_iter\n");
			Py_DECREF(get_iter);
			break;
		}
		counter ++;
	}
	// Decrementar las referencias
	printf("dec data\n");
	Py_DECREF(data);
	printf("dec column\n");
	Py_DECREF(column);
	printf("dec iter\n");
	Py_DECREF(iter);

	if (result == NULL){
		printf("return None\n");
		Py_INCREF(Py_None);
    	return Py_None;
	}
	
	printf("return algun valor\n");
	//printf("dec lvalue\n");
	//Py_DECREF(lvalue);
	//printf("dec nargs\n");
	//Py_DECREF(nargs);

	return result;
}

static PyObject *
on_get_iter(PyObject *self, PyObject *args)
{
	static PyObject *rowref;
	static PyObject *result;
	static PyObject *selfobj;
	static PyObject *data;
	static PyObject *size;
	int index;
    if (!PyArg_ParseTuple(args, "OO", &selfobj, &rowref))
        return NULL;
    data = PyObject_GetAttrString(selfobj, "data");
    size = PyObject_GetAttrString(selfobj, "data_size");
    if (!data){
    	Py_DECREF(rowref);
		Py_DECREF(data);
		Py_DECREF(size);
    	Py_INCREF(Py_None);
    	return Py_None;
    }
    PyArg_ParseTuple(rowref, "i", &index);
    if (index <= PyInt_AsLong(size) -1){
    	result = PyList_GetItem(data, index);
    }
    else{
    	Py_DECREF(rowref);
		Py_DECREF(data);
    	Py_INCREF(Py_None);
    	return Py_None;
    }
	if (!result){
		Py_DECREF(rowref);
		Py_DECREF(data);
		Py_DECREF(result);
		Py_INCREF(Py_None);
		return Py_None;
	}
	Py_XDECREF(rowref);
	Py_XDECREF(size);
	Py_XDECREF(data);
    return  result;
}


static PyMethodDef CLibraryModelMethods[] = {
	{"__init__", init, METH_VARARGS, "doc string"},
    {"on_get_iter",  on_get_iter, METH_VARARGS,"Returns a ref."},
    {"search_iter_on_column",  search_iter_on_column, METH_VARARGS,"Return the reference of the row that first match the column and value"},
    {NULL, NULL}
};


static PyMethodDef ModuleMethods[] = { {NULL} };

#ifdef __cplusplus
extern "C"
#endif
PyMODINIT_FUNC
initCLibraryModel(void)
{

	PyMethodDef *def;

	PyObject *module = NULL;
	PyObject *moduleDict = NULL;
	PyObject *classDict = NULL;
	PyObject *className = NULL;
	PyObject *fooClass = NULL;

    module = Py_InitModule("CLibraryModel", ModuleMethods);
    moduleDict = PyModule_GetDict(module);
    classDict = PyDict_New();
    className = PyString_FromString("CLibraryModel");
    fooClass = PyClass_New(NULL, classDict, className);

	PyImport_AddModule("CLibraryModel");

    PyDict_SetItemString(moduleDict, "CLibraryModel", fooClass);
    Py_DECREF(classDict);
    Py_DECREF(className);
    Py_DECREF(fooClass);

    /* add methods to class */
    for (def = CLibraryModelMethods; def->ml_name != NULL; def++) {
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
    initCLibraryModel();
    return 0;
}

