#!/usr/bin/env python

# OraSchemaDoc v0.10
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
