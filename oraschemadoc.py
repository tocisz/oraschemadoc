#!/usr/bin/env python

""" Generates "JavaDoc" style information about Oracle schema objects """

## \mainpage Oraschemadoc
# Oraschemadoc is an easy to use Oracle database documention
# tool. It takes all objects in schema covering Oracle specific
# features.
#
# Copyright (C) Aram Kananov <arcanan@flashmail.com>, 2002
#
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


import getopt, sys, os
from oraschemadoc.oracleencoding import OracleNLSCharset
from oraschemadoc.osdconfig import OSDConfig


try:
    sys.setappdefaultencoding('utf-8')
except AttributeError, e:
    print '\nYour system is not able to handle UTF8 correctly.'
    print 'Disabling internal UTF8 handling.'
    print 'Error message: %s\n' % e


try:
    import cx_Oracle
except ImportError:
    print '\nProblem with cx_Oracle importing.'
    print 'You are using unsupported oracle home or module cx_Oracle not found.'
    print 'You have to install it to use oraschemadoc'
    print ''
    print 'UN*X: set your ORACLE_HOME to the path with oracle libraries'
    print '      cx_Oracle compilled with'
    print 'Windows: set your path to the right value (found in registry)'
    print ''
    sys.exit(1)


def usage():
    """! \brief Print quick help."""
    print '\nOracle Schema Documentation Generator '
    print 'usage: oraschemadoc [-v|--verbose] [-d|--dia [--dia-table-list=file]] [--no-html]'
    print '                    [--xml-file=filename] [-s|--syntax] [--schema="[list]"]'
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
    print '   --nn                 Index NOT NULL constraints too. It\'s skipped by default:'
    print '                        NOT NULL constraints are reported in columns list only.'
    print '   --schema=schemalist  specify schema/usernames to select from ALL_% objects.'
    print '                        If it\'s not given standard USER_% objects are used.'
    print '                        schemalist can be e.g. "SCOTT,FOO,BAR" - coma separated list'
    print '                        or empty - it means all granted objects will be documented.'
    print '                        See README file for more info and examples.'
    print '-h --help               print this help screen'
    print ''
    print 'For more information see README\n'


def main():
    """! \brief Parse CLI arguments and call tasks."""

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hdvs',
                                   ['help', 'verbose', 'dia=', 'dia-table-list=',
                                    'syntax', 'css=', 'desc=', 'pb', 'no-html',
                                    'xml-file=', 'nn', 'schema='])
    except getopt.error, e:
        # print help information and exit:
        usage()
        sys.exit(2)

    cfg = OSDConfig()

    for opt, value in opts:
        if opt in ('-h', '--help'):
            # print help information and exit:
            usage()
            sys.exit()
        if opt in ('-v', '--verbose'):
            #print verbose messages
            cfg.verbose_mode = True
        if opt == '--no-html':
            cfg.html_output = None
        if opt in ('-d', '--dia'):
            cfg.dia_uml_output = 1;
            cfg.dia_file_name = value;
        if opt == '--dia-table-list':
            cfg.dia_conf_file = value
        if opt == '--xml-file':
            cfg.xml_file = value
        if opt in ('-s', '--syntax'):
            cfg.syntaxHighlighting = True
        if opt == '--css':
            if not os.path.exists(os.path.join(csspath, value)):
                print '\nWARNING: %s doesn\'t exists. Using default instead.\n' % value
            else:
                cfg.css = value
        if opt == '--desc':
            if not os.path.exists(value):
                cfg.desc = value
            else:
                f = file(value, 'r')
                cfg.desc = f.read()
                f.close()
        if opt == '--pb':
            cfg.pb = True
        if opt == '--nn':
            cfg.notNulls = True
        if opt == '--schema':
            cfg.useOwners = True
            if len(value) > 0:
                cfg.owners = value.split(',')


    if len(args) == 3: 
        connect_string, cfg.output_dir, cfg.name = args
        cfg.output_dir = os.path.abspath(cfg.output_dir)
    else:
        usage()
        sys.exit()

    # see if output_dir is exsits, if not try to create one.
    if os.access(cfg.output_dir, os.F_OK) != 1:
        # dir not exists
        try: 
            os.makedirs(cfg.output_dir)
        except os.error, e:
            print 'ERROR: Cannot create directory ', cfg.output_dir
            sys.exit(2)
    else:
        # if directory exists see if its writable
        if os.access(cfg.output_dir, os.W_OK) != 1:
            print 'ERROR: Cannot write into directory ', cfg.output_dir
            sys.exit(2)

    try:
        cfg.connection = cx_Oracle.connect(connect_string)
    except cx_Oracle.DatabaseError, e:
        print e
        sys.exit(2)

    if len(cfg.owners) > 0:
        # simulate slect user from dual;
        cfg.currentUser = "'" + connect_string[:connect_string.find('/')].upper() + "'"

    # know encoding we will use
    oraenc = OracleNLSCharset()
    encoding = oraenc.getClientNLSCharset()
    if encoding == None:
        encoding = oraenc.getPythonEncoding(oraenc.getOracleNLSCharacterset(cfg.connection))
    else:
        encoding = oraenc.getPythonEncoding(encoding)
    cfg.webEncoding = encoding[1]
    cfg.encoding = encoding[0]
    print 'Using codec: %s' % cfg.encoding
    print 'HTML encoding: %s\n' % cfg.webEncoding

    # recode the inputs into final encoding
    try:
        if cfg.desc != None:
            cfg.desc = cfg.encode(cfg.desc)
        cfg.name = cfg.encode(cfg.name)
    except:
        print '\nConvert your description and given name into %s failed.' % cfg.encoding
        print 'You can get index documentation page screwed...'
        print '\nYou can try to set NLS_LANG variable to the value you have'
        print 'your environment configured. E.g. in windows:'
        print 'set NLS_LANG=CZECH_CZECH REPUBLIC.EE8MSWIN1250'
        print 'export NLS_LANG in bash etc. This problem is mainly in Windows.\n'

    # start the show...
    import oraschemadoc.orasdict
    import oraschemadoc.oraschema
    # common db meta structures
    cfg.dictionary = oraschemadoc.orasdict.OraSchemaDataDictionary(cfg)
    cfg.schema = oraschemadoc.oraschema.OracleSchema(cfg)
    # crate requested outputs
    cfg.crateXML()
    cfg.createXHTML()
    cfg.createDia()


if __name__ == '__main__':
    main()

