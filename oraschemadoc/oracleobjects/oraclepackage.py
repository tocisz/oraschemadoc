# Copyright (C) Petr Vanek <petr@yarpen.cz>, 2005
# Copyright (C) Aram Kananov <arcanan@flashmail.com> , 2002
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

__author__ = 'Aram Kananov <arcanan@flashmail.com>, Petr Vanek, <petr@yarpen.cz>'


from oracleplsqlsource import OraclePLSQLSource


class OraclePackage:

    def __init__(self, name, all_arguments, all_return_values, definition_source, body_source):
        #debug_message("debug: generating plsql package %s" % name)
        self.name = name
        self.source = OraclePLSQLSource(definition_source)
        self.body_source = None
        if body_source:
            self.body_source = OraclePLSQLSource(body_source)

    def getXML(self):
        """get package metadata"""
        xml_text = '''<package id="package-%s">
                        <name>%s</name>
                        <declaration>%s</declaration>
                        <body>%s</body>
                      </package>''' % ( self.name, self.name, self.source.getXML(), self.body_source.getXML())
        return xml_text
