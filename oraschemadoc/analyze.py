class SchemaAnalyzer:

    def __init__(self, schema):
        self.schema = schema
        self.name_prefix = 'os_autogen_ind$'

    def _analyze_fk_indexes(self):
        j = 0
        for table in self.schema.tables:
            if table.referential_constraints:
                for constraint in table.referential_constraints:
                    if self._find_index(constraint.columns, table.indexes) == 0:
                        print "--missed index on %s table for %s constraint " % (table.name, constraint.name)
                        _columns = ''
                        for i in range(len(constraint.columns)):
                            _columns = _columns + constraint.columns[i+1]
                        if i+1 != len(constraint.columns):
                            _columns = _columns + ', '
                        print "create index %s%s on %s (%s);" % (self.name_prefix, j , table.name , _columns )
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
