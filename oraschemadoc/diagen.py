# OraSchemaDoc v0.24
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

# Dia XML File Generator

__author__ = 'Aram Kananov <arcanan@flashmail.com>'

__version__ = '$Version: 0.24'

import os 

class DiaFileGenerator:

    def __init__(self, schema, doc_dir, name, description, debug_mode, conf_file):
        
        self.schema = schema
        self.doc_dir = doc_dir
        self.name = name
        self.description = description

       # prepare file header
        header = '''<?xml version="1.0" encoding="UTF-8"?>
                     <dia:diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">
                     <dia:layer name="Background" visible="true">
                   '''  
        
        table_ids = {}
        i = 0
        table_text = ''
        self.export_tables = self.get_tables_for_export(conf_file)
        print self.export_tables
        for table in self.schema.tables:
            if self.export_tables.count(table.name) == 0:
                continue
            i = i+1
            table_ids[table.name] = i
            table_text = table_text +  '<dia:object type="UML - Class" version="0" id="%s">' % i
            table_text = table_text +  '  <dia:attribute name="name"> <dia:string>#%s#</dia:string></dia:attribute>'  % table.name
            table_text = table_text +  '''  <dia:attribute name="abstract"><dia:boolean val="false"/></dia:attribute>
                                      <dia:attribute name="suppress_attributes"><dia:boolean val="false"/></dia:attribute>
                                      <dia:attribute name="suppress_operations"><dia:boolean val="false"/></dia:attribute>
                                      <dia:attribute name="visible_attributes"><dia:boolean val="true"/></dia:attribute>'''
           
            table_text = table_text + self.get_columns_text(table)
            table_text = table_text + self.get_constraints_text(table)
            table_text = table_text + '''<dia:attribute name="visible_operations">
                                                        <dia:boolean val="false"/>
                                                        </dia:attribute>
                                                        <dia:attribute name="operations"/>
                                                        <dia:attribute name="template">
                                                        <dia:boolean val="false"/>
                                                        </dia:attribute>
                                                        <dia:attribute name="templates"/>
                                                        </dia:object>'''
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
	                
	            cs_text = cs_text + ''' <dia:object type="UML - Constraint" version="0" id="%s">
	      <dia:attribute name="constraint">
	        <dia:string>#%s#</dia:string>
	      </dia:attribute>
	      <dia:connections>
	      <dia:connection handle="0" to="%s" connection="%s"/>
	        <dia:connection handle="1" to="%s" connection="%s"/>
	      </dia:connections>
	    </dia:object>''' % ( i, col_list, t_id, col_pos, r_t_id, r_col_pos) 
            
        footer = '</dia:layer></dia:diagram>'

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
            text = text + '''<dia:composite type="umlattribute">
                            <dia:attribute name="name">
                               <dia:string>#%s#</dia:string>
                            </dia:attribute>
                            <dia:attribute name="type">
                              <dia:string>#%s#</dia:string>
                            </dia:attribute>''' % (column.name, column.data_type + nullable_text)
            
            # handle default value
            if column.data_default:
                text = text + '<dia:attribute name="value"><dia:string>#%s#</dia:string></dia:attribute>' % column.data_default
            else:
                text = text + '<dia:attribute name="value"><dia:string/></dia:attribute>'
                
            v_type = '3'
            if pk_columns and pk_columns.count(column.name) > 0:
                v_type = '2'
                
            text = text + '''<dia:attribute name="visibility">
                                    <dia:enum val="%s"/>
                                  </dia:attribute>
                                  <dia:attribute name="abstract">
                                    <dia:boolean val="false"/>
                                  </dia:attribute>
                                  <dia:attribute name="class_scope">
                                   <dia:boolean val="false"/>
                                  </dia:attribute>
                                    </dia:composite>''' % v_type
            
        return '<dia:attribute name="attributes">' + text + '</dia:attribute>'


    def get_constraints_text(self, table):
        if table.referential_constraints:
            cs_names = map(lambda cs: cs.name, table.referential_constraints)
            cs_text = ''
            for cs in table.referential_constraints:
                if self.export_tables.count(cs.r_table) == 0:
                    continue
                name = cs.name
                cs_text = cs_text + '''<dia:composite type="umloperation">
                     <dia:attribute name="name"><dia:string>##</dia:string></dia:attribute>
                     <dia:attribute name="visibility"><dia:enum val="3"/></dia:attribute>
                     <dia:attribute name="abstract"><dia:boolean val="false"/></dia:attribute>
                     <dia:attribute name="class_scope"><dia:boolean val="false"/></dia:attribute>
                     <dia:attribute name="parameters">
                            <dia:composite type="umlparameter">
				              <dia:attribute name="name"><dia:string>#%s#</dia:string></dia:attribute>
				              <dia:attribute name="value"><dia:string/></dia:attribute>
				              <dia:attribute name="kind"><dia:enum val="0"/></dia:attribute>
				            </dia:composite>
                     </dia:attribute>
				     </dia:composite>''' % name
            return cs_text
        else:
            return   '''<dia:attribute name="visible_operations"><dia:boolean val="false"/> 
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
                    r_list.append(t.strip())
        else:
            r_list = map(lambda t: t.name, self.schema.tables)
        return r_list
    

if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    import oraschema
    connection = cx_Oracle.connect('wcms12/wcms12')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle',0)
    schema = oraschema.OracleSchema(s,0)
    doclet = DiaFileGenerator(schema, "/tmp/oraschemadoc/", "vtr Data Model", "Really cool project",0,'/tmp/oraschemadoc/conf.txt')
        
        
