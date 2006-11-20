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


class OracleProcedureArgument:
    def __init__(self, name, data_type, default_value, in_out ):
        #debug_message("debug: generating plsql argument %s" % name)
        self.name = name
        self.data_type = data_type
        self.default_value = default_value
        self.in_out = in_out

    def getXML(self):
        """get argument metadata in xml"""
        return '''<argument>
                    <name>%s</name>
                    <data_type>%s</data_type>
                    <default_value>%s</default_value>
                    <in_out>%s</in_out>
                  </argument>''' % (self.name, self.data_type, self.default_value, self.in_out)
