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


class OracleIndex:

    def __init__(self, name, data_dict):
        self.name = name
        table_name, type, uniqueness, include_column, generated, secondary = data_dict.all_indexes[name]
        self.table_name = table_name
        self.type = type
        self.uniqueness = uniqueness
        self.include_column = include_column
        self.generated = generated
        self.secondary = secondary

        self.columns = {}
        if data_dict.all_index_columns.has_key(name):
            for table_name, column , position in data_dict.all_index_columns[name]:
                self.columns[position] = column
        if data_dict.all_index_expressions.has_key(name):
            for table_name, expression , position in data_dict.all_index_expressions[name]:
                self.columns[position] = expression


    def getXML(self):
        """get data about index in xml"""
        xml_text = '''<index id="index-%s">
                        <name>%s</name>
                        <type>%s</type>
                        <table>table-%s</table>
                        <uniqueness>%s</uniqueness>
                        <generated>%s</generated>
                        <secondary>%s</secondary>''' % ( self.name, self.name, self.type, self.table_name,
                                                        self.uniqueness, self.generated, self.secondary)

        xml_text += '<ind_columns>'
        for position in self.columns.keys():
            xml_text += '<column>column-%s</column>' % self.columns[position]
        xml_text += '</ind_columns></index>'
        return xml_text
