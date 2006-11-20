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


from oracletriggercolumn import OracleTriggerColumn

class OracleTrigger:

    def __init__(self, name, data_dict):
        #debug_message("debug: generating trigger %s" % name)
        self.name, self.type, self.event, self.base_object_type, self.table_name, self.nested_column_name, \
                   self.referencing_names, self.when_clause, self.status, self.description, self.action_type,\
                   self.body = data_dict.all_triggers[name]
        # initalize trigger columns
        self.columns = []
        if data_dict.all_trigger_columns.has_key(self.name):
            for name, table_name, column_name, column_list, column_usage in data_dict.all_trigger_columns[self.name]:
                self.columns.append(OracleTriggerColumn(column_name, column_list, column_usage))


    def getXML(self):
        code_text = 'CREATE TRIGGER %s\n' % self.description
        code_text += self.referencing_names + '\n'
        if self.when_clause:
            code_text += 'WHEN %s \n' % self.when_clause
        code_text += self.body

        xml_text = '''<trigger id="trigger-%s"> 
                        <name>%s</name>
                        <code><![CDATA[%s]]></code></trigger>''' % (self.name, self.name, code_text )
        return xml_text
