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


class OracleCheckConstraint:

    def __init__(self, name, data_dict):
        self.name = name
        self.table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
        self.type = "Check"
        self.check_cond = check_cond
        self.columns = {}
        for table_name, column_name, position in data_dict.all_constraited_columns[name]:
            self.columns[position]=column_name        
        # TODO all above should be deleted
        self.__name = name
        self.__table_name = table_name
        self.__type = "Check"
        self.__check_cond = check_cond
        self.__columns = self.columns

    def getName(self):
        return self.__name

    def getCheckCondition(self):
        return self.__check_cond

    def getXML(self):
        '''get xml for check constraint'''
        xml_text = '''<constraint id="constraint-%s" type="check">
                      <name>%s</name>
                      <check_condition><![CDATA[%s]]></check_condition>''' % (
                                                          self.__name, self.__name, self.__check_cond)
        xml_text += '</constraint>\n'
        return xml_text
