rem Script to convert Pyhton to Windows exe
rem copy devel tree into cx_freeze directory

..\FreezePython --include-modules=cx_Oracle --target-dir=oraschemadoc-exe --base-binary=ConsoleKeepPath.exe --init-script=ConsoleKeepPath.py oraschemadoc-dev\oraschemadoc.py

