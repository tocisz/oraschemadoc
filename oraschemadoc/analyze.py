# OraSchemaDoc v0.23
# Copyright (C) Aram Kananov <arcanan@flashmail.com>, 2002
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

class SchemaAnalyzer:

    def __init__(self, schema):
        self.schema = schema
        self.name_prefix = 'fk_no_index_'
        self.fk_no_indexes = []
        self.fk_no_indexes_sql = ''

        self._analyze_fk_indexes()

    def _analyze_fk_indexes(self):
        j = 0
        for table in self.schema.tables:
            if table.referential_constraints:
                for constraint in table.referential_constraints:
                    if self._find_index(constraint.columns, table.indexes) == 0:
                        self.fk_no_indexes.append(constraint)
                        self.fk_no_indexes_sql += "--missed index on %s table for %s constraint \n" \
                                                  % (table.name, constraint.name)
                        _columns = ''
                        for i in range(len(constraint.columns)):
                            _columns = _columns + constraint.columns[i+1]
                        if i+1 != len(constraint.columns):
                            _columns = _columns + ', '
                        self.fk_no_indexes_sql += "create index %s%s on %s (%s);\n\n" \
                                                  % (self.name_prefix, j , table.name , _columns )
                        j = j + 1

    def _find_index(self, columns, indexes):
        if not indexes:
            return 0
        else:
            for index in indexes:
                if len(columns) <= len(index.columns):
                    for i in range(len(columns)):
                        if columns[i+1] != index.columns[i+1]:
                            break
                        elif i+1 == len(columns):
                            return 1
            return 0


    
    
if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    import oraschema
    connection = cx_Oracle.connect('aram_v1/aram_v1')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle')
    schema = oraschema.OracleSchema(s)
    d = SchemaAnalyzer(schema)
    d._analyze_fk_indexes()
