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
from oracleprocedureargument import OracleProcedureArgument


class OracleProcedure:

    def __init__(self, name, arguments, source = None):
        #debug_message("debug: generating plsql procedure %s" % name)
        self.name = name
        self.arguments = []
        self.source = None

        if arguments:
            arg_keys = arguments.keys()
            arg_keys.sort()
            for key in arg_keys:
                name, data_type, default_value, in_out = arguments[key]
                argument = OracleProcedureArgument(name, data_type, default_value, in_out)
                self.arguments.append(argument)
        if source:
            self.source = OraclePLSQLSource(source)

    def getXML(self):
        """get procedure metadata"""
        xml_text = '''<procedure id="procedure-%s">
                        <name>%s</name>
                        <source>%s</source>''' % (self.name, self.name, self.source.getXML())
        if self.arguments:
            xml_text += '<arguments>'
            for argument in self.arguments:
                xml_text += argument.getXML()
            xml_text += '</arguments>'

        xml_text += '</procedure>'
        return xml_text
