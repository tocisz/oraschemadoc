# OraSchemaDoc v0.25
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

# Dia UML Diagram XML File Generator

__author__ = 'Aram Kananov <arcanan@flashmail.com>'

__version__ = '$Version: 0.25'

# TODO: implement debug statements

import os 

class DiaUmlDiagramGenerator:

    def __init__(self, schema, doc_dir, name, description, debug_mode, conf_file):
        
        self.schema = schema
        self.doc_dir = doc_dir
        self.name = name
        self.description = description

        # prepare file header
        header = '<?xml version="1.0" encoding="UTF-8"?>'
        header += '<dia:diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">'
        header += '  <dia:layer name="Background" visible="true">'
        
        table_ids = {}
        i = 0
        table_text = ''
        self.export_tables = self.get_tables_for_export(conf_file)

        for table in self.schema.tables:
            if self.export_tables.count(table.name) == 0:
                continue
            i = i+1
            table_ids[table.name] = i
            table_text += '    <dia:object type="UML - Class" version="0" id="%s">' % i
            table_text += '      <dia:attribute name="name">'
            table_text += '        <dia:string>#%s#</dia:string>'  % table.name
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="abstract">'
            table_text += '        <dia:boolean val="false"/>'
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="suppress_attributes">'
            table_text += '        <dia:boolean val="false"/>'
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="suppress_operations">'
            table_text += '        <dia:boolean val="false"/>'
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="visible_attributes">'
            table_text += '        <dia:boolean val="true"/>'
            table_text += '      </dia:attribute>'
           
            table_text += self.get_columns_text(table)
            table_text += self.get_constraints_text(table)
            table_text += '      <dia:attribute name="visible_operations">'
            table_text += '        <dia:boolean val="false"/>'
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="operations"/>'
            table_text += '      <dia:attribute name="template">'
            table_text += '        <dia:boolean val="false"/>'
            table_text += '      </dia:attribute>'
            table_text += '      <dia:attribute name="templates"/>'
            table_text += '    </dia:object>'

        # link components together
        cs_text = ''
        for table in self.schema.tables:
            if table.referential_constraints:
                for cs in table.referential_constraints:
                    if self.export_tables.count(cs.table_name) == 0 or self.export_tables.count(cs.r_table) == 0:
                        continue                    
                    i = i + 1
                    col_list = reduce(lambda c1, c2: c1 + ', ' + c2, cs.columns.values())
                    t_id = table_ids[table.name]
                    col_pos = 7 + int(self.get_col_pos(cs.columns[1], table))
                    r_t_id = table_ids[cs.r_table]
                    r_cs = filter(lambda c: c.name == cs.r_constraint_name, self.schema.constraints)[0]
                    r_table = filter(lambda t: t.name == cs.r_table, self.schema.tables)[0]
                    r_col_pos = 7 + int(self.get_col_pos(r_cs.columns[1], r_table))
                    cs_text += '    <dia:object type="UML - Constraint" version="0" id="%s">' % i
                    cs_text += '      <dia:attribute name="constraint">'
                    cs_text += '        <dia:string>#%s#</dia:string>' % col_list
                    cs_text += '      </dia:attribute>'
                    cs_text += '      <dia:connections>'
                    cs_text += '        <dia:connection handle="0" to="%s" connection="%s"/>' % (t_id, col_pos)
                    cs_text += '        <dia:connection handle="1" to="%s" connection="%s"/>' % (r_t_id, r_col_pos)
                    cs_text += '      </dia:connections>'
                    cs_text += '    </dia:object>'
            
        footer = '  </dia:layer>'
        footer += '</dia:diagram>'

        file_name = os.path.join(self.doc_dir, "dm-diagram.dia")
        f = open(file_name, 'w')
        f.write(header + table_text + cs_text + footer)
        f.close()
        
    def get_columns_text(self, table):
        columns = table.columns
        if table.primary_key:
            pk_columns = table.primary_key.columns.values()
        else:
            pk_columns = None
        text = ''
        
        for i in range(len(columns)):
            column = columns[i+1]
            nullable_text = ''
            if column.nullable == 'N':
               nullable_text =  ' not null'
            text += '        <dia:composite type="umlattribute">'
            text += '          <dia:attribute name="name">'
            text += '            <dia:string>#%s#</dia:string>' % column.name
            text += '          </dia:attribute>'
            text += '          <dia:attribute name="type">'
            text += '            <dia:string>#%s#</dia:string>' % column.data_type + nullable_text
            text += '          </dia:attribute>'
            
            # handle default value
            if column.data_default:
                text += '          <dia:attribute name="value">'
                text += '            <dia:string>#%s#</dia:string>' % column.data_default
                text += '          </dia:attribute>'
            else:
                text += '          <dia:attribute name="value">'
                text += '            <dia:string/>'
                text += '          </dia:attribute>'
                
            v_type = '3'
            if pk_columns and pk_columns.count(column.name) > 0:
                v_type = '2'
                
            text += '          <dia:attribute name="visibility">'
            text += '            <dia:enum val="%s"/>' % v_type
            text += '          </dia:attribute>'
            text += '          <dia:attribute name="abstract">'
            text += '            <dia:boolean val="false"/>'
            text += '          </dia:attribute>'
            text += '            <dia:attribute name="class_scope">'
            text += '          <dia:boolean val="false"/>'
            text += '            </dia:attribute>'
            text += '        </dia:composite>' 
            
        return '       <dia:attribute name="attributes">' + text + '</dia:attribute>'


    def get_constraints_text(self, table):
        if table.referential_constraints:
            cs_text = ''
            for cs in table.referential_constraints:
                if self.export_tables.count(cs.r_table) == 0:
                    continue
                name = cs.name

                cs_text += '      <dia:composite type="umloperation">'
                cs_text += '        <dia:attribute name="name">'
                cs_text += '          <dia:string>##</dia:string>'
                cs_text += '        </dia:attribute>'
                cs_text += '        <dia:attribute name="visibility">'
                cs_text += '          <dia:enum val="3"/>'
                cs_text += '        </dia:attribute>'
                cs_text += '        <dia:attribute name="abstract">'
                cs_text += '          <dia:boolean val="false"/>'
                cs_text += '        </dia:attribute>'
                cs_text += '        <dia:attribute name="class_scope">'
                cs_text += '          <dia:boolean val="false"/>'
                cs_text += '        </dia:attribute>'
                cs_text += '        <dia:attribute name="parameters">'
                cs_text += '          <dia:composite type="umlparameter">'
                cs_text += '            <dia:attribute name="name">'
                cs_text += '              <dia:string>#%s#</dia:string>' % name 
                cs_text += '            </dia:attribute>'
                cs_text += '            <dia:attribute name="value">'
                cs_text += '              <dia:string/>'
                cs_text += '            </dia:attribute>'
                cs_text += '            <dia:attribute name="kind">'
                cs_text += '              <dia:enum val="0"/>'
                cs_text += '            </dia:attribute>'
                cs_text += '          </dia:composite>'
                cs_text += '        </dia:attribute>'
                cs_text += '      </dia:composite>'
            return cs_text
        else:
            return '''        <dia:attribute name="visible_operations">
          <dia:boolean val="false"/> 
        </dia:attribute>
        <dia:attribute name="operations"/>'''

    def get_col_pos(self, column_name, table):
        i = 0
        for j in table.columns.keys():
            i = i + 1
            if table.columns[j].name == column_name:
                return i

    def get_tables_for_export(self, conf_file):
        r_list = []
        if conf_file:
            f = open(conf_file, 'r')
            t_list = f.readlines()
            for t in t_list:
                if t and t.strip() != '': 
                    r_list.append(t.strip().upper())
        else:
            r_list = map(lambda t: t.name, self.schema.tables)
        return r_list
    

if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    import oraschema
    connection = cx_Oracle.connect('bugzilla/bugzilla')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle',0)
    schema = oraschema.OracleSchema(s,0)
    doclet = DiaUmlDiagramGenerator(schema, "/tmp/oraschemadoc/", "vtr Data Model", "Really cool project",0,None)
    
        
        
