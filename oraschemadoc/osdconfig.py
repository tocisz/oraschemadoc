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
    """Configure attributes packed together"""

    def __init__(self):
        """ Default values """
        self.name = 'Example'
        # variable used for turning on debug messages
        self.verbose_mode = False
        self.output_dir = '.'
        # Generate "javadocish" html output, by default yes
        self.html_output = True
        # if specified dia_uml_output turns on export to dia uml diagram
        self.dia_uml_output = False
        # if specified, restrict export to dia only for table names included in file 
        self.dia_conf_file = None
        # if specified, dumps data into xml
        self.xml_file = None
        # if true then sources will have syntax highlighting
        self.syntaxHighlighting = False
        # path to css (default here)
        self.csspath = os.path.join(sys.path[0], 'css')
        self.css = 'oraschemadoc.css'
        # decription
        self.desc = ''
        # package bodies
        self.pb = False
        # take NOT NULL constraints. False = don't take NOT NULL constraints
        self.notNulls = False
        # DB connection
        self.connection = None
        # DB attributes
        self.encoding = 'utf8'
        self.webEncoding = 'utf8'
        # internals
        self.dictionary = None
        self.schema = None


    def encode(self, text):
        return text.encode(self.encoding)


    def crateXML(self):
        if not self.xml_file:
            return
        file_name = os.path.join(self.output_dir, self.xml_file)
        print '\nCreating XML file: %s', file_name
        f = open(file_name, 'w')
        f.write(self.schema.getXML())
        f.close()


    def createDia(self):
        if not self.dia_uml_output:
            return
        file_name = os.path.join(self.output_dir, self.dia_file_name)
        print '\nCreating DIA file: %s', file_name
        dia_diagram = diagen.DiaUmlDiagramGenerator(self.schema, file_name, self.desc, 0, self.dia_conf_file)


    def createXHTML(self):
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
