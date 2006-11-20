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


class OracleColumn:
    """! \brief Oracle column represents table column object"""

    def __init__(self, name, column_id, data_type, nullable, data_default, comments):
        self.column_id = column_id
        self.name = name
        self.data_type =data_type
        self.nullable = nullable
        self.data_default = data_default
        self.comments = comments

    def getXML(self, table_name):
        """! \brief get xml representation of column"""
        #TODO: and it sucks to pass table_name via getXML, fix it
        return '''<column id="column-%s.%s">
                    <name>%s</name>
                    <position>%s</position>
                    <datatype>%s</datatype>
                    <default_value>%s</default_value>
                    <nullable>%s</nullable>
                    <comments><![CDATA[%s]]></comments>
                  </column>\n''' % (table_name, self.name,
                    self.name, self.column_id, self.data_type,
                    self.default_value, self.nullable,
                    self.comments)

