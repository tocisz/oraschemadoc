# OraSchemaDoc v0.23
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

# OraSchemaDataDictionary class queries data from Oracle Data Dictionary 

__author__ = 'Aram Kananov <arcanan@flashmail.com>'

__version__ = '$Version: 0.23'

from oraverbose import *

class OracleSchema:

    def __init__(self, data_dict , debug_mode):

        set_verbose_mode(debug_mode)
        
        self.tables = self._get_all_tables(data_dict)
        self.indexes = self._get_all_indexes(data_dict)
        self.constraints = self._get_all_constraints(data_dict)
        self.views = self._get_all_views(data_dict)
        self.triggers = self._get_all_table_triggers(data_dict)
        self.procedures = self._get_all_procedures(data_dict)
        self.functions = self._get_all_functions(data_dict)
        self.packages = self._get_all_packages(data_dict)
        self.sequences = self._get_all_sequences(data_dict)
        self.java_sources = self._get_all_java_sources(data_dict)
        # TODO: why i need that name? 
        self.name = "Foobarizm" 

    def _get_all_tables(self, data_dict):
        tables = []
        print 'generating tables'
        for table_name in data_dict.all_table_names:
            tables.append(OracleTable(table_name, data_dict))
        return tables
    
    def _get_all_indexes(self, data_dict):
        print 'generating indexes'
        indexes = []
        for index_name in data_dict.all_index_names:
            indexes.append(OracleIndex(index_name, data_dict))
        return indexes
    
    def _get_all_constraints(self, data_dict):
        print 'generating constraints'
        constraints = []
        for name in data_dict.all_constraint_names:
             table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
             if type in ("P", "U"):
                 constraints.append(OracleUniqueConstraint(name, data_dict))
             elif type == "R":
                 constraints.append(OracleReferentialConstraint(name, data_dict))
             elif type == "C":
                 constraints.append(OracleCheckConstraint(name, data_dict))
        return constraints

    def _get_all_views(self, data_dict):
        print 'generating views'
        views = []
        for view_name in data_dict.all_view_names:
            views.append(OracleView(view_name, data_dict))
        return views

    def _get_all_table_triggers(self, data_dict):
        print 'generating triggers'
        triggers = []
        for trigger_name in data_dict.table_triggers:
            triggers.append(OracleTrigger(trigger_name, data_dict))
        return triggers

    def _get_all_procedures(self, data_dict):
        print 'generating procedures'
        procedures = []
        for name in data_dict.all_procedure_names:
            procedure = OracleProcedure(name, data_dict.proc_arguments.get(name, None), \
                                        data_dict.all_procedures.get(name, None))
            procedures.append(procedure)
        return procedures

    def _get_all_java_sources(self, data_dict):
        print 'generating java sources'
        java_sources = []
        for name in data_dict.all_java_source_names:
            java_source = OracleJavaSource(name,data_dict.all_java_sources.get(name, None))
            java_sources.append(java_source)
        return java_sources
    
    def _get_all_functions(self, data_dict):
        print 'generating functions'
        functions = []
        for name in data_dict.all_function_names:
            function = OracleFunction(name, data_dict.proc_arguments.get(name, None), \
                                      data_dict.func_return_arguments.get(name, None),\
                                      data_dict.all_functions.get(name, None))
            functions.append(function)
        return functions
    
    def _get_all_packages(self, data_dict):
        print 'generating packages'
        packages = []
        for name in data_dict.all_package_names:
            all_arguments = data_dict.package_arguments.get(name, None)
            all_return_values = data_dict.package_return_values.get(name, None)
            def_source = data_dict.all_packages[name]
            body_source = data_dict.all_package_bodies.get(name, None)
            package = OraclePackage(name, all_arguments, all_return_values, def_source, body_source)
            packages.append(package)
        return packages

    def _get_all_sequences(self, data_dict):
        print "generating sequences"
        sequences = []
        for name in data_dict.sequence_names:
            min_value, max_value, step, cycled, ordered, cache_size = data_dict.sequences[name]
            seq = OracleSequence(name, min_value, max_value, step, cycled, ordered, cache_size)
            sequences.append(seq)
        return sequences
        
class OracleTable:

    def __init__(self, name, data_dict):
        debug_message('debug: creating table object '+ name)
        self.name = name
        self.partitioned, self.secondary, self.index_organized, self.clustered, self.cluster_name, self.nested, self.temporary = data_dict.all_tables[name]
        self.comments = data_dict.all_table_comments.get(name)
        self.columns = self._get_columns(data_dict)

        self.primary_key             = self._get_primary_key(name, data_dict)
        self.unique_keys             = self._get_unique_keys(name, data_dict)
        self.check_constraints       = self._get_check_constraints(name, data_dict)
        self.referential_constraints = self._get_ref_constraints(name, data_dict)
        self.indexes                 = self._get_indexes(name, data_dict)
        self.triggers                = self._get_triggers(data_dict)
        self.referenced_by = None
        if data_dict.table_referenced_by.has_key(name):
            self.referenced_by       = data_dict.table_referenced_by[name]


    def _get_primary_key(self, table_name, data_dict):
        
        _primary_key_name = data_dict.table_primary_key_map.get(table_name)
        primary_key = None
        if _primary_key_name:
            debug_message('debug: generating primary key ' + _primary_key_name)
            primary_key = OracleUniqueConstraint(_primary_key_name, data_dict)
        return primary_key

    def _get_unique_keys(self, table_name, data_dict):
        debug_message('debug: generating unique keys')
        unique_keys = []
        t = data_dict.table_unique_key_map.get(table_name)
        if not t:
            return None
        for key_name in t:
            debug_message('debug: generating unique key ' + key_name )
            unique_key = OracleUniqueConstraint(key_name, data_dict)
            unique_keys.append(unique_key)
        return unique_keys

    def _get_check_constraints(self, table_name, data_dict):
        debug_message('debug: generating check constraints')
        check_constraints = []
        t = data_dict.table_check_constraint_map.get(table_name)
        if not t:
            return None
        for constraint_name in t:
            debug_message('debug: generating check constraint ' + constraint_name)  
            constraint = OracleCheckConstraint(constraint_name, data_dict)
            check_constraints.append(constraint)
        return check_constraints

    def _get_ref_constraints(self, table_name, data_dict):
        debug_message('debug: generating foreign key constraints')
        referential_constraints = []
        t = data_dict.table_foreign_key_map.get(table_name)
        if not t:
            return None
        for constraint_name in t:
            debug_message('debug: generating foreign key ' + constraint_name)
            constraint = OracleReferentialConstraint(constraint_name, data_dict)
            referential_constraints.append(constraint)
        return referential_constraints
    

    def _get_columns(self, data_dict):
        debug_message('debug: generating columns')
        columns = {}
        # Fixme: need proper hadling iot overflow segment columns
        if data_dict.all_columns.has_key(self.name):
            for column, data_type, nullable, column_id, data_default in data_dict.all_columns[self.name]:
                debug_message('debug: generating column ' + column)
                if data_dict.all_col_comments.has_key((self.name, column)):
                    comments = data_dict.all_col_comments[self.name, column]
                else:
                    comments = ''
                columns[column_id] = OracleColumn(column, column_id, data_type, nullable, data_default, comments)
        return columns


    def _get_indexes(self, table_name, data_dict):
        debug_message('debug: generating indexes')
        indexes = []
        if  data_dict.table_index_map.has_key(table_name):
            for index_name in data_dict.table_index_map[table_name]:
                debug_message('debug: generating index ' + index_name)
                index = OracleIndex(index_name, data_dict)
                indexes.append(index)
        return indexes
            
    def _get_triggers(self, data_dict):
        debug_message('debug: generating triggers')
        triggers = []
        if  data_dict.table_trigger_map.has_key(self.name):
            for trigger_name in data_dict.table_trigger_map[self.name]:
                debug_message('debug: generating trigger ' + trigger_name)
                triggers.append(OracleTrigger(trigger_name, data_dict))
        return triggers

class OracleColumn:

    def __init__(self, name, column_id, data_type, nullable, data_default, comments):
        self.column_id = column_id
        self.name = name
        self.data_type =data_type
        self.nullable = nullable
        self.data_default = data_default
        self.comments = comments

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

class OracleCheckConstraint:

    def __init__(self, name, data_dict):
        self.name = name
        self.table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
        self.type = "Check"
        self.check_cond = check_cond
        self.columns = {}
        for table_name, column_name, position in data_dict.all_constraited_columns[name]:
            self.columns[position]=column_name        

class OracleReferentialConstraint:

    def __init__(self, name, data_dict):
        self.name = name
        self.table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[name]
        self.type = "Referential"
        self.r_owner = r_owner
        self.r_constraint_name = r_constraint_name
        self.delete_rule = delete_rule
        table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = data_dict.all_constraints[self.r_constraint_name]
        self.r_table = table_name
        self.columns = {}
        for table_name, column_name, position in data_dict.all_constraited_columns[name]:
            self.columns[position]=column_name



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

class OracleView:

    def __init__(self, name, data_dict):
        debug_message("debug: generating view" + name)
        self.name = name
        self.text = data_dict.all_views[name]
        self.columns = self._get_columns(data_dict)
        self.constraints = self._get_constraints(data_dict)
        self.comments = data_dict.all_table_comments.get(name)
        self.triggers                = self._get_triggers(data_dict)
    
    
    def _get_columns(self, data_dict):
        columns = {}
        for column, data_type, nullable, column_id, data_default in data_dict.all_columns[self.name]:
            if data_dict.all_col_comments.has_key((self.name, column)):
                comments = data_dict.all_col_comments[self.name, column]
            else:
                comments = ''
            columns[column_id] = OracleViewColumn(column, column_id, data_type, nullable, data_default, comments, self.name, data_dict)
        return columns
    
    def _get_constraints(self, data_dict):
        constraints = []
        t = data_dict.view_constraint_map.get(self.name)
        if not t:
            return None
        for constraint_name in t:
            constraint = OracleViewConstraint(constraint_name, data_dict)
            constraints.append(constraint)
        return constraints

    def _get_triggers(self, data_dict):
        triggers = []
        if  data_dict.table_trigger_map.has_key(self.name):
            for trigger_name in data_dict.table_trigger_map[self.name]:
                triggers.append(OracleTrigger(trigger_name, data_dict))
        return triggers    

class OracleViewColumn(OracleColumn):

    def __init__(self, name, column_id, data_type, nullable, data_default, comments, table_name, data_dict):
        debug_message("debug: generating view column" + name)
        OracleColumn.__init__(self, name, column_id, data_type, nullable, data_default, comments)
        self.insertable, self.updatable, self.deletable = data_dict.all_updatable_columns[table_name, name]
    

class OracleViewConstraint:

    def __init__(self, name, data_dict):
        debug_message("debug: generating view constraint " + name)
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



class OracleTrigger:

    def __init__(self, name, data_dict):
        debug_message("debug: generating trigger " + name)
        self.name, self.type, self.event, self.base_object_type, self.table_name, self.nested_column_name, \
                   self.referencing_names, self.when_clause, self.status, self.description, self.action_type,\
                   self.body = data_dict.all_triggers[name]
        # initalize trigger columns
        self.columns = []
        if data_dict.all_trigger_columns.has_key(self.name):
            for name, table_name, column_name, column_list, column_usage in data_dict.all_trigger_columns[self.name]:
                self.columns.append(OracleTriggerColumn(column_name, column_list, column_usage))

class OracleTriggerColumn:

    def __init__(self, column_name, column_list, column_usage):
        debug_message("debug: generating trigger column " + column_name)
        self.column_name = column_name
        self.column_list = column_list
        self.column_usage = column_usage

class OracleProcedure:

    def __init__(self, name, arguments, source = None):
        debug_message("debug: generating plsql procedure " + name)
        self.name = name
        self.arguments = []
        self.source = None

        if arguments:
            arg_keys = arguments.keys()
            arg_keys.sort()
            for key in arg_keys:
                name, data_type, default_value, in_out = arguments[key]
                argument = OracleProcedureArgument(name, data_type, default_value, in_out)
                self.arguments.append(argument)
        if source:
            self.source = OraclePLSQLSource(source)
            

class OracleFunction(OracleProcedure):
    
    def __init__(self, name, arguments, return_data_type, source = None):
        debug_message("debug: generating plsql function " + name)
        OracleProcedure.__init__(self, name, arguments, source)
        self.return_data_type = ''
        if return_data_type:
            self.return_data_type = return_data_type
    
            

class OracleProcedureArgument:
    def __init__(self, name, data_type, default_value, in_out ):
        debug_message("debug: generating plsql argument "+ name)
        self.name = name
        self.data_type = data_type
        self.default_value = default_value
        self.in_out = in_out

class OraclePLSQLSource:
    def __init__(self, source):
        debug_message("debug: generating plsql source ")
        self.source = []
        lines = source.keys()
        lines.sort()
        for line_no in lines:
            self.source.append(OraclePLSQLSourceLine(line_no, source[line_no]))

class OracleJavaSource(OraclePLSQLSource):
    def__init__(self, name, source):
        debug_message("debug: generating java source ")
        OraclePLSQLSource.__init__(self,source)
            

class OraclePLSQLSourceLine:
    
    def __init__(self, line_no, text):
        self.line_no = line_no
        self.text = text
    
class OraclePackage:

    def __init__(self, name, all_arguments, all_return_values, definition_source, body_source):
        debug_message("debug: generating plsql package " + name)
        self.name = name
        self.source = OraclePLSQLSource(definition_source)
        self.body_source = None
        if body_source:
            self.body_source = OraclePLSQLSource(body_source)


class OracleSequence:

    def __init__(self, name, min_value, max_value, step, cycle_flag, ordered, cache_size):
        debug_message("debug: genarating sequence " + name)
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.cycle_flag = cycle_flag
        self.ordered = ordered
        self.cache_size = cache_size
        
        
if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    connection = cx_Oracle.connect('aram_v1/aram_v1')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle')
    schema = OracleSchema(s)
        
    
