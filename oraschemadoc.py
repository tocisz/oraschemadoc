#!/usr/bin/env python

""" Generates "JavaDoc" style information about Oracle schema objects """

# OraSchemaDoc v0.25
# Copyright (C) Aram Kananov <arcanan@flashmail.com>, 2002
# Copyright (C) Petr Vanek <petr@scribus.info>, 2005
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


import getopt, sys, os, shutil
from oraschemadoc.oracleencoding import OracleNLSCharset

sys.setappdefaultencoding('utf-8')


try:
    import cx_Oracle
except ImportError:
    print ''
    print 'Problem with cx_Oracle importing.'
    print 'You are using unsupported oracle home or module cx_Oracle not found.'
    print 'You have to install it to use oraschemadoc'
    print ''
    print 'UN*X: set your ORACLE_HOME to the path with oracle libraries'
    print '      cx_Oracle compilled with'
    print 'Windows: set your path to the right value (found in registry)'
    print ''
    sys.exit(1)


def usage():
    print ''
    print 'Oracle Schema Documentation Generator v0.25'
    print 'usage: oraschemadoc [-v|--verbose] [-d|--dia [--dia-table-list=file]] [--no-html]'
    print '                    [--xml-file=filename] [-s|--syntax] '
    print '                    [--css=style] [--desc=description] oracleuser/password[@dbalias]'
    print '                    output_dir  "application name"'
    print ''
    print 'Arguments:'
    print 'oracleuser/password[@dbalias] -  db connect string'
    print 'output_dir                    -  directory where files will be generated'
    print 'application_name              -  short name for application/datamodel'
    print ''
    print 'Optional arguments:'
    print '-v --verbose            turns on debuging messages'
    print '   --no-html            turn off generation of html files'
    print '-d --dia=filename       export datamodel to dia uml diagram. File with file name will be'
    print '                        created under output_dir'
    print '   --dia-table-list=l   path to file which contains table names for export to dia diagram'
    print '   --xml-file=filename  dump dm into xml file. File will be created under output_dir'
    print '-s --syntax             sets syntax highlighting on (it will be very slow)'
    print '   --css=stylename      filename with CSS from css directory. If not given default used.'
    print '   --desc=description   If is description filename with path, the text from file is taken.'
    print '                        If the file doesn\'t exist the description is taken as text string.'
    print '   --pb                 Generates source code for package bodies too.'
    print '-h --help               print this help screen'
    print ''
    print 'For more information see README\n'


def main():

    # variable used for turning on debug messages
    verbose_mode = None
    # Generate "javadocish" html output, by default yes
    html_output = 1
    # if specified dia_uml_output turns on export to dia uml diagram
    dia_uml_output = None
    # if specified, restrict export to dia only for table names included in file 
    dia_conf_file = None
    # if specified, dumps data into xml
    xml_file = None   
    # if true then sources will have syntax highlighting
    syntaxHighlighting = False
    # path to css (default here)
    csspath = os.path.join(sys.path[0], 'css')
    css = 'oraschemadoc.css'
    # decription
    desc = None
    # package bodies
    pb = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hdvs',
                                   ['help', 'verbose', 'dia=', 'dia-table-list=',
                                    'syntax', 'css=', 'desc=', 'pb', 'no-html', 'xml-file='])
    except getopt.error, e:
        # print help information and exit:
        usage()
        sys.exit(2)

    for opt, value in opts:
        if opt in ('-h', '--help'):
            # print help information and exit:
            usage()
            sys.exit()
        if opt in ('-v', '--verbose'):
            #print verbose messages
            verbose_mode = 1
        if opt == '--no-html':
            html_output = None
        if opt in ('-d', '--dia'):
            dia_uml_output = 1;
            dia_file_name = value;
        if opt == '--dia-table-list':
            dia_conf_file = value
        if opt == '--xml-file':
            xml_file=value
        if opt in ('-s', '--syntax'):
            syntaxHighlighting = True
        if opt == '--css':
            if not os.path.exists(os.path.join(csspath, value)):
                print '\nWARNING: ' + value + ' doesn\'t exists. Using default instead.\n'
            else:
                css = value
        if opt == '--desc':
            if not os.path.exists(value):
                desc = value
            else:
                f = file(value, 'r')
                desc = f.read()
                f.close()
        if opt == '--pb':
            pb = True

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

    connection = cx_Oracle.connect(connect_string)

    # know encoding we will use
    oraenc = OracleNLSCharset()
    encoding = oraenc.getClientNLSCharset()
    if encoding == None:
        encoding = oraenc.getPythonEncoding(oraenc.getOracleNLSCharacterset(connection))
    else:
        encoding = oraenc.getPythonEncoding(encoding)
    print 'Using codec: %s\n' % encoding

    # recode the inputs into final encoding
    try:
        if desc != None:
            desc = desc.encode(encoding)
        name = name.encode(encoding)
    except:
        print 'Convert your description and given name into %s failed.' % encoding
        print 'You can get index documentation page screwed...'

    # start the show...
    import oraschemadoc.orasdict
    import oraschemadoc.oraschema
    import oraschemadoc.docgen
    import oraschemadoc.diagen

    s = oraschemadoc.orasdict.OraSchemaDataDictionary(connection, name, verbose_mode)
    schema = oraschemadoc.oraschema.OracleSchema(s, verbose_mode, pb)

    if xml_file:
        file_name = os.path.join(output_dir, xml_file)
        print '\nCreating XML file: %s', file_name
        f = open(file_name, 'w')
        f.write(schema.getXML())
        f.close()

    if html_output:
        print '\nCreating HTML docs'
        doclet = doclet = oraschemadoc.docgen.OraSchemaDoclet(connection, schema,
                                    output_dir, name, desc, verbose_mode,
                                    syntaxHighlighting, css, encoding)
        # copy css
        # There is problem with sys.path[0] in cx_Freeze. These exceptionse
        # are here as I try to find css file freezy way
        try:
            print 'Copying CSS style'
            shutil.copy(os.path.join(csspath, css), output_dir)
            print 'css: done'
        except IOError, (errno, errmsg):
            print os.path.join(csspath, css) + ' not fround. Trying to find another'
            print 'Error copying CSS style. You are running precompiled version propably.'
            print 'Related info: (%s) %s' % (errno, errmsg)
            try:
                print 'Trying: ' + os.path.join(os.path.dirname(sys.executable), 'css', css)
                shutil.copy(os.path.join(os.path.dirname(sys.executable), 'css', css), output_dir)
                print 'css: done'
            except IOError:
                print 'Error: (%s) %s' % (errno, errmsg)
                print 'Please copy some css style into output directory manually.'

    if dia_uml_output:
        file_name = os.path.join(output_dir, dia_file_name)
        print '\nCreating DIA file: %s', file_name
        dia_diagram = oraschemadoc.diagen.DiaUmlDiagramGenerator(schema, file_name, desc, 0, dia_conf_file)


if __name__ == '__main__':
    main()

