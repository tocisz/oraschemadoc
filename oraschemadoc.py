#!/usr/bin/env python

# OraSchemaDoc v0.25
# Copyright (C) Aram Kananov <arcanan@flashmail.com>, 2002
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

# Generates "JavaDoc" style information about Oracle schema objects


import getopt, sys, os

def usage():
    print 'Oracle Schema Documentation Generator v0.25'
    print 'usage: oraschemadoc [--verbose] [-d|--dia [--dia-table-list file]] oracleuser/password[@dbalias] output_dir  "application name"'
    print ''
    print 'Arguments:'
    print 'oracleuser/password[@dbalias] -  db connect string'
    print 'output_dir                    -  directory where files will be generated'
    print 'application_name              -  short name for application/datamodel'
    print ''
    print 'Optional arguments:'
    print '-v --verbose         turns on debuging messages'
    print '-d --dia             export datamodel to dia uml diagram'
    print '   --dia-table-list  path to file which contains table names for export to dia diagram'
    print '-h --help            print this help screen'
    print ''
    print 'For more information see README'

    
def main():

    # variable used for turning on debug messages
    verbose_mode = None
    # if specified dia_uml_output turns on export to dia uml diagram
    dia_uml_output = None
    # if specified, restrict export to dia only for table names included in file 
    dia_conf_file = None
    
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hdv', ['help','verbose','dia','dia-table-list'])
    except getopt.error, e:
        # print help information and exit:
        usage()
        sys.exit(2)
    for opt, value in opts:
        if opt in ('-h', '--help'):
            # print help information and exit:
            usage()
            sys.exit()
        if opt in ('v', '--verbose'):
            #print verbose messages
            verbose_mode = 1
        if opt in ('-d', '--dia'):
            dia_uml_output = 1;
        if opt == '--dia-table-list':
            dia_conf_file = value

    if len(args) == 3: 
        connect_string, output_dir, name = args
    else:
        usage()
        sys.exit()

    # see if output_dir is exsits, if not try to create one.
    if os.access(output_dir, os.F_OK) != 1:
        # dir not exists
        try: 
            os.makedirs(output_dir)
        except os.error, e:
            print 'ERROR: Cannot create directory ', output_dir
            sys.exit(2)
    else:
        # if directory exists see if its writable
        if os.access(output_dir, os.W_OK) != 1:
            print 'ERROR: Cannot write into directory ', output_dir
            sys.exit(2)
            
    import cx_Oracle
    connection = cx_Oracle.connect(connect_string)
    import oraschemadoc.orasdict
    import oraschemadoc.oraschema
    import oraschemadoc.docgen
    import oraschemadoc.diagen
    s = oraschemadoc.orasdict.OraSchemaDataDictionary(connection, name, verbose_mode)
    schema = oraschemadoc.oraschema.OracleSchema(s, verbose_mode)

    file_name = os.path.join(output_dir, "schema.xml")
    f = open(file_name, 'w')
    f.write(schema.getXML())
    f.close()

    doclet = oraschemadoc.docgen.OraSchemaDoclet(schema, output_dir, name, "", verbose_mode)
    if dia_uml_output:
        dia_diagram = oraschemadoc.diagen.DiaUmlDiagramGenerator(schema, "/tmp/oraschemadoc/", "vtr Data Model", "Really cool project", 0, dia_conf_file)
        
    
if __name__ == '__main__':
    main()
