#include <Python.h>
int
main(int argc, char *argv[])
{
  Py_Initialize();
  PyRun_SimpleString("from lib_christine.christine import *\n"
                     "a = christine()\n"
					 "a.main()\n");
  Py_Finalize();
  return 0;
}


