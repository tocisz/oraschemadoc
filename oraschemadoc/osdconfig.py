# Copyright (C) Petr Vanek <petr@yarpen.cz>, 2005
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

"""Configure attributes packed together"""

import os.path
import sys
import shutil

import docgen
import diagen


class OSDConfig:
    """! \brief Configure attributes packed together"""

    def __init__(self):
        """! \brief  Default values """
        #! \brief text string to display "project"/schema name
        self.name = 'Example'
        #! \brief  variable used for turning on debug messages
        self.verbose_mode = False
        #! \brief directory to store outputs
        self.output_dir = '.'
        #! \brief Generate "javadocish" html output, by default yes
        self.html_output = True
        #! \brief if specified dia_uml_output turns on export to dia uml diagram
        self.dia_uml_output = False
        #! \brief if specified, restrict export to dia only for table names included in file
        self.dia_conf_file = None
        #! \brief if specified, dumps data into xml
        self.xml_file = None
        #! \brief if true then sources will have syntax highlighting
        self.syntaxHighlighting = False
        #! \brief path to css (default here)
        self.csspath = os.path.join(sys.path[0], 'css')
        #! \brief file with css styles
        self.css = 'oraschemadoc.css'
        #! \brief decription
        self.desc = ''
        #! \brief package bodies
        self.pb = False
        #! \brief take NOT NULL constraints. False = don't take NOT NULL constraints
        self.notNulls = False
        #! \brief DB connection
        self.connection = None
        #! \brief DB attributes
        self.encoding = 'utf8'
        self.webEncoding = 'utf8'
        #! \brief internals
        self.dictionary = None
        self.schema = None


    def encode(self, text=''):
        """! \brief Encode given string with 'encoding' """
        return text.encode(self.encoding)


    def crateXML(self):
        """! \brief Base XML creattion """
        if not self.xml_file:
            return
        file_name = os.path.join(self.output_dir, self.xml_file)
        print '\nCreating XML file: %s', file_name
        f = open(file_name, 'w')
        f.write(self.schema.getXML())
        f.close()


    def createDia(self):
        """! \brief Base Dia creation""" 
        if not self.dia_uml_output:
            return
        file_name = os.path.join(self.output_dir, self.dia_file_name)
        print '\nCreating DIA file: %s', file_name
        dia_diagram = diagen.DiaUmlDiagramGenerator(self.schema, file_name, self.desc, 0, self.dia_conf_file)


    def createXHTML(self):
        """! \brief Base XHTML creattion"""
        if not self.html_output:
            return
        print '\nCreating HTML docs'
        doclet = docgen.OraSchemaDoclet(self)
        # copy css
        # There is problem with sys.path[0] in cx_Freeze. These exceptionse
        # are here as I try to find css file freezy way
        try:
            print 'Copying CSS style'
            shutil.copy(os.path.join(self.csspath, self.css), self.output_dir)
            print 'css: done'
        except IOError, (errno, errmsg):
            print os.path.join(self.csspath, self.css) + ' not fround. Trying to find another'
            print 'Error copying CSS style. You are running precompiled version propably.'
            print 'Related info: (%s) %s' % (errno, errmsg)
            try:
                print 'Trying: ' + os.path.join(os.path.dirname(sys.executable), 'css', self.css)
                shutil.copy(os.path.join(os.path.dirname(sys.executable), 'css', self.css), self.output_dir)
                print 'css: done'
            except IOError:
                print 'Error: (%s) %s' % (errno, errmsg)
                print 'Please copy some css style into output directory manually.'


if __name__ == '__main__':
    print 'This module can be used only as a library for Oraschemadoc'
