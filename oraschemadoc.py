#!/usr/bin/env python

# OraSchemaDoc v0.24
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
    print 'Oracle Schema Documentation Generator v0.24'
    print 'usage: oraschemadoc [--verbose] oracleuser/password[@dbalias] output_dir  "application name" '

def main():

    verbose_mode = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help','verbose'])
    except getopt.error, e:
        # print help information and exit:
        usage()
        sys.exit(2)
    for opt, value in opts:
        if opt in ('-h' , '--help'):
            # print help information and exit:
            usage()
            sys.exit()
        if opt == '--verbose':
            #print verbose messages
            verbose_mode = 1

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
    s = oraschemadoc.orasdict.OraSchemaDataDictionary(connection, name, verbose_mode)
    schema = oraschemadoc.oraschema.OracleSchema(s, verbose_mode)
    doclet = oraschemadoc.docgen.OraSchemaDoclet(schema, output_dir, name, "", verbose_mode)
       
    
if __name__ == '__main__':
    main()
