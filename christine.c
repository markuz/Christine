#include <Python.h>
#include <import.h>
#include <graminit.h>
#include <pythonrun.h>

#ifdef WINDOWS
    #include <direct.h>
    #define GetCurrentDir _getcwd
#else
    #include <unistd.h>
    #define GetCurrentDir getcwd
 #endif

void error(char *msg) {
	PyErr_Print();
	printf("%s\n", msg);
	exit(1);
}

int
main(int argc, char *argv[]){
	PyObject *t,*main_module, *main_dict, *main_dict_copy;
	PyObject *builtinMod,*c_argv, *runChristine,*name;
	PyObject *path,* os_getcwd, *osname;
	PyObject *sys_argv, *sys_path;
	PyObject *christine_module, *christine_dict;
	char cCurrentPath[FILENAME_MAX];
	int i;
	Py_Initialize();
	// Get a reference to the main module
	main_module = PyImport_AddModule("__main__");
	if (main_module == NULL)
		error ("Could not import __main__ module");
	main_dict = PyModule_GetDict(main_module);
	if (main_dict == NULL)
		error ("Could not get the __main__ module dictionary");
	if (PyDict_GetItemString(main_dict, "__import__") == NULL){
	        builtinMod = PyImport_ImportModule("__builtin__");
			PyObject *sys = PyImport_ImportModule("sys");
			if (sys == NULL)
				error("");
			PyObject *bdict = PyModule_GetDict(sys);
	        if (builtinMod == NULL)
				error("Could not import the __builtins__ module");
			if (PyDict_SetItemString(main_dict, "__builtins__", builtinMod) != 0)
				error("Could not assign the new dictionary");
			if (PyDict_SetItemString(main_dict,"sys", sys) !=0)
				error("");
			if (PyDict_GetItemString(main_dict, "__builtins__") == NULL)
				error ("Still there is no __builtins__!!!!");
			PyObject  *keys = PyDict_Keys(bdict);
			PyList_Sort(keys);
	}
	//Get the reference of sys.argv
	sys_argv = PySys_GetObject("argv");
	if (sys_argv == NULL)
		sys_argv = PyList_New(0);
	for (i = 0; i < argc ;i++)
		if (PyList_Append(sys_argv, PyString_FromString(argv[i]))!=0)
					error("Cannot append to sys_argv");
	PySys_SetObject("argv",sys_argv);
	main_dict_copy = PyDict_Copy(main_dict);
	if (main_dict_copy == NULL)
		error ("Can't get the main_dict _copy");
	if (!GetCurrentDir(cCurrentPath, sizeof(cCurrentPath)))
	     error("Can't get the current path");
	//Get the reference os sys.path
	sys_path = PySys_GetObject("path");
	if (PyList_Append(sys_path,  PyString_FromString(cCurrentPath)) < 0)
		error ("Cannot append the current path to sys");
	PySys_SetObject("path", sys_path);
	name = PyString_FromString("libchristine.Christine");
	christine_module= PyImport_Import(name);
	if (christine_module == NULL){
		error ("Cannot import libchristine.Christine.runChristine");
	}
	//getting the module dict
	christine_dict =  PyModule_GetDict(christine_module);
	//Get the runChristine function
	runChristine = PyDict_GetItemString(christine_dict, "runChristine");
	if (!PyCallable_Check(runChristine)) {
				error("runChristine is not callable");
	            return NULL;
	        }
	Py_XINCREF(runChristine);
	PyObject_CallObject(runChristine,  PyTuple_New(0));
	Py_XDECREF(runChristine);
	if (t == NULL){
		error("Error while trying to run christine");
	}
	Py_Finalize();
	return 0;
}


