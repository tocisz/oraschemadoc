# Script to convert Pyhton to IN*X binary
# copy devel tree into cx_freeze directory

./FreezePython --include-modules=cx_Oracle --target-dir=oraschemadoc-linuxbin --base-binary=ConsoleKeepPath --init-script=ConsoleKeepPath.py oraschemadoc/oraschemadoc.py

