#!/usr/bin/env python
#
# Generates "JavaDoc" style information about Oracle schema objects


import getopt, sys

def usage():
    print 'Oracle Schema Documentation Generator v0.10'
    print 'usage: oraschemadoc oracleuser/password[@dbalias] output_dir  "application name"'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help'])
    except getopt.error, e:
        # print help information and exit:
        usage()
        sys.exit(2)
    for opt, value in opts:
        if opt in ('-h' , '--help'):
            # print help information and exit:
            usage()
            sys.exit()
    if len(args) == 3:
        connect_string, output_dir, name = args
    else:
        usage()
        sys.exit()

    import cx_Oracle
    connection = cx_Oracle.connect(connect_string)
    import oraschemadoc.orasdict
    import oraschemadoc.oraschema
    import oraschemadoc.docgen
    s = oraschemadoc.orasdict.OraSchemaDataDictionary(connection, name)
    schema = oraschemadoc.oraschema.OracleSchema(s)
    doclet = oraschemadoc.docgen.OraSchemaDoclet(schema, output_dir, name, "")
       
    
if __name__ == '__main__':
    main()
