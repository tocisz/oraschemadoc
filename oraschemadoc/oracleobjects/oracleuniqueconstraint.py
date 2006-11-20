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


class OracleUniqueConstraint:

    def __init__(self, name, data_dict):
        self.name = name
        self.table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
        if type == "P":
            self.type = "Primary key"
        else:
            self.type = "Unique key"
        self.columns ={}
        for table_name, column_name, position in data_dict.all_constraited_columns[name]:
            self.columns[position]=column_name

        self.__name = name
        self.__table_name = table_name
        self.__type = type
        self.__columns = self.columns

    def getName(self):
        """ get constraint name"""
        return self.__name

    def getType(self):
        ''' returns type, where type is one of "Primary Key" or "Unique Key"'''
        return self.__type

    def getColumns(self):
        '''get columns as dictionary indexed by position in index'''
        return self.__columns

    def getXML(self):
        '''get xml for unique/primary key'''
        xml_text = '''<constraint id="constraint-%s" type="unique">
                      <name>%s</name>
                      <type>%s</type>
                      <ind_columns>''' % (self.__name, self.__name, self.__type)
        for position in self.__columns.keys():
            xml_text += '<column>column-%s.%s</column>' % (
                                                       self.__table_name, self.__columns[position])
        xml_text += '</ind_columns>\n</constraint>\n'
        return xml_text
