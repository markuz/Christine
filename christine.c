#include <Python.h>
int
main(int argc, char *argv[])
{
  Py_Initialize();
  PyRun_SimpleString("from lib_christine.libs_christine import *\n"
					 "sanity()\n"
					 "from lib_christine.christine import *\n"
					 "import sys,os\n"
					 "sys.path.insert(0,os.getcwd())\n"
					 "#print sys.path\n"
                     "a = christine()\n"
					 "a.main()\n");
  Py_Finalize();
  return 0;
}


