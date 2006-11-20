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


class OracleViewConstraint:

    def __init__(self, name, data_dict):
        #debug_message("debug: generating view constraint %s" % name)
        self.name = name
        self.table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
        if type == 'O':
            self.type = "With read only on view"
            columns = []
        else:
            self.type = "With check option on view"
            self.columns = {}
            for table_name, column_name, position in data_dict.all_constraited_columns.get(name, []):
                self.columns[position]=column_name
        self.check_cond = check_cond

    def getXML(self):
        """get constraint metadata in xml"""
        xml_text = '''<constraint id="constraint-%s">
                    <name>%s</name>
                    <type>%s</type>'''
        if self.columns:
            xml_text += '<columns>'
            for position in self.columns.keys():
                xml_text += '<column>name</column>'
            xml_text += '</columns>'
        xml_text += '</constraint>'
        return xml_text
