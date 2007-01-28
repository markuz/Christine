#include <Python.h>
#include <import.h>
#include <graminit.h>
#include <pythonrun.h>

void error(char *msg) { 
	PyErr_Print();
	printf("%s\n", msg); exit(1); 
}

char* python_code = "\
import sys\n\
from lib_christine.libs_christine import *\n\
sanity()\n\
from lib_christine.christine import *\n\
a = christine()\n\
print \"argumentos: \",sys.argv\n\
if len(sys.argv) > 1:\n\
	for i in sys.argv[1:]:\n\
		if os.path.isfile(i):\n\
			a.queue.add(i,prepend=True)\n\
a.main()\n\
";

int
main(int argc, char *argv[]){
	// Get a reference to the main module

	PyObject *t,*main_module, *main_dict, *main_dict_copy;
	PyObject *sys;
	Py_Initialize();
	main_module = PyImport_ImportModule("__main__");
	sys = PyImport_ImportModule("sys");
	if (main_module == NULL)
		error ("Could not import __main__ module");
	main_dict = PyModule_GetDict(main_module);
	//main_dict = PyModule_GetDict(sys);
	//main_dict = PyDict_New();
	//PyDict_SetItemString(main_dict,"__builtins__",main_module);
	if (main_dict == NULL)
		error ("Could not get the __main__ module dictionary");
	main_dict_copy = PyDict_Copy(main_dict);
	Py_DECREF(main_module);
	t = PyRun_String(python_code,Py_file_input,main_dict,main_dict_copy);
	if (t == NULL){
		error("Error while trying to run christine");
	}
	Py_DECREF(t);
	Py_Finalize();
	return 0;
}


