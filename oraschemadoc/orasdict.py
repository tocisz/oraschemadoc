# OraSchemaDoc v0.10
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

__version__ = '$Version: 0.1'

import time

class OraSchemaDataDictionary:

    def __init__(self, conn, name):
        self.name                      = name
        self.all_tables               = _get_all_tables(conn)        
        self.all_table_comments       = _get_all_table_comments(conn)
        self.all_col_comments         = _get_all_col_comments(conn)
        self.all_columns              = _get_all_columns(conn)        
        self.all_constraints          = _get_all_constraints(conn)
        self.all_constraited_columns  = _get_all_constraited_columns(conn)
        self.all_views                = _get_all_views(conn)
        self.all_updatable_columns    = _get_all_updatable_columns(conn)
        self.all_indexes              = _get_all_indexes(conn)
        self.all_index_columns        = _get_all_index_columns(conn)
        self.all_index_expressions    = _get_all_index_expressions(conn)
        
        self.all_table_names = self.all_tables.keys()
        self.all_table_names.sort()

        self.all_view_names  = self.all_views.keys()
        self.all_view_names.sort()
        
        self.all_constraint_names = self.all_constraints.keys()
        self.all_constraint_names.sort()

        self.table_primary_key_map = {}
        self.table_unique_key_map = {}
        self.table_check_constraint_map = {}
        self.table_foreign_key_map = {}
        self.table_check_constraint_map = {}
        self.view_constraint_map = {}
        self.table_referenced_by = {}
        for constraint_name in self.all_constraint_names:
            table_name, type, check_cond, r_owner, r_constraint_name, delete_rule = self.all_constraints[constraint_name]
            if type == 'P':
               self.table_primary_key_map[table_name] = constraint_name
            elif type == 'U':
                 self.table_unique_key_map.setdefault(table_name,[]).append(constraint_name)
            elif type == 'C':
                 self.table_check_constraint_map.setdefault(table_name,[]).append(constraint_name)
            elif type == 'R':
                 self.table_foreign_key_map.setdefault(table_name,[]).append(constraint_name)
                 # put row in table_referenced_by
                 _table_name = self.all_constraints[r_constraint_name][0]
                 self.table_referenced_by.setdefault(_table_name,[]).append((table_name, constraint_name))
            elif type in ('V','O'):
                 self.view_constraint_map.setdefault(table_name,[]).append(constraint_name)

        self.table_constraint_map= {}
        for constraint_name in self.all_constraint_names:
            table_name = self.all_constraints[constraint_name][0]
            self.table_constraint_map.setdefault(table_name, []).append(constraint_name)  

        self.all_index_names = self.all_indexes.keys()
        self.all_index_names.sort()

        self.table_index_map = {}
        for index_name in self.all_index_names:
            table_name = self.all_indexes[index_name][0]
            self.table_index_map.setdefault(table_name,[]).append(index_name)
            
        self.all_triggers = _get_all_triggers(conn)
        self.all_trigger_names = self.all_triggers.keys()
        self.all_trigger_names.sort()
        self.all_trigger_columns = _get_all_trigger_columns(conn)
        # attention that holds mapping for views as well
        self.table_triggers = []
        self.table_trigger_map = {}
        self.schema_triggers = []
        for trigger_name in self.all_trigger_names:
            name, type, event, base_object_type, table_name, column_name, referencing_names, \
                          when_clause, status, description, action_type, body \
                          = self.all_triggers[trigger_name]
            if base_object_type in ('TABLE', 'VIEW'):
                self.table_triggers.append(trigger_name)
                self.table_trigger_map.setdefault(table_name,[]).append(name)
            elif base_object_type  == 'SCHEMA':
                self.schema_triggers.append(trigger_name)
        self.table_triggers.sort()
        
        #process user_source
        self.all_functions = {}
        self.all_procedures = {}
        self.all_packages = {}
        self.all_package_bodies = {}
        for name, type, line, text in _get_user_source(conn):
            if type == 'PROCEDURE':
                t = self.all_procedures.setdefault(name, {})
            elif type == 'FUNCTION':
                t = self.all_functions.setdefault(name, {})
            elif type == 'PACKAGE':
                t = self.all_packages.setdefault(name, {})
            elif type == 'PACKAGE BODY':
                t = self.all_package_bodies.setdefault(name, {})
            t[int(float(line))] = text

        self.all_procedure_names = self.all_procedures.keys()
        self.all_procedure_names.sort()
        self.all_function_names = self.all_functions.keys()
        self.all_function_names.sort()
        self.all_package_names = self.all_packages.keys()
        self.all_package_names.sort()
        
        # convert all_arguments
        all_arguments = _get_all_arguments(conn)
        self.proc_arguments = {}
        self.func_return_arguments = {}
        self.package_arguments = {}
        self.package_return_values = {}
        for name, package_name, argument_name, position, data_type, default_value, in_out in all_arguments:
            if not package_name:
                if position:
                    t = self.proc_arguments.setdefault(name, {})
                    t[int(float(position))]= [argument_name, data_type, default_value, in_out]
                else:
                    self.func_return_arguments[name] = data_type
            else:
                if float(position) > 0:
                    t = self.package_arguments.setdefault(package_name, {}).setdefault(name, {})
                    t[int(float(position))] =  argument_name, data_type, default_value, in_out 
                else:
                    self.package_return_values.setdefault(package_name, {})[name]= data_type

        


################################################
# INTERNAL FUNCTIONS FOR QUERY DATA DICTIONARY #
################################################

def _get_all_tables(conn):
    "get tables"
    # fix me with iot_table overflow segments
    stmt = """select table_name, partitioned, secondary, cluster_name, iot_type, temporary,  nested
                  from user_tables"""        
    tables = {}
    print "get tables"
    for table, partitioned, secondary, cluster, iot_type, temporary, nested in _query(conn, stmt):
        _partitioned = 'No'
        _secondary = 'No'
        _index_organized = 'No'
        _clustered = 'No'
        _cluster_name = ''
        _nested = 'No'
        _temporary = 'No'
        if partitioned == 'YES':
            _partitioned = 'Yes'
        if secondary == 'Y':
            _secondary = 'Yes'
        if iot_type:
            _index_organized = 'Yes'
        if cluster:
            _clustered = 'Yes'
            _cluster_name = cluster
        if nested == 'Y':
            _nested = 'Yes'
        if temporary == 'Y':
            _temporary = 'Yes'
        tables[table] = _partitioned, _secondary, _index_organized, _clustered, _cluster_name, _nested, _temporary
    return tables


def _get_all_table_comments(conn):
    "get comments on tables and views"
    stmt = """SELECT table_name, comments
              FROM user_tab_comments
              WHERE comments is not null"""
    comments = {}
    print "get comments on tables and views"
    for table, comment in _query(conn, stmt):
        comments[table] = comment
    return comments 

def _get_all_col_comments(conn):
    "get all tables/views column comments"
    stmt = """ SELECT table_name, column_name, comments
                   FROM user_col_comments
                   where comments is not null"""
    col_comments = {}
    print "get all tables/views column comments"
    for table, column, comment in _query(conn, stmt):
        col_comments[table,column] = comment
    return col_comments;

def _get_all_columns(conn):
    "get all columns for tables, views and clusters"
    stmt = """select table_name, column_name, data_type , data_length, data_precision,
                      data_scale, nullable, column_id, data_default
                   from user_tab_columns order by table_name, column_id"""
    all_columns = {}
    print "get all columns for tables, views and clusters"
    for table, column, data_type, data_length, data_precision, data_scale, nullable, column_id, data_default in _query(conn, stmt):
        _data_type = data_type
        t = all_columns.get(table, None)
        if not t:
            t = []
            all_columns[table] = t
        if data_type == 'NUMBER':
            if not data_precision:
                data_precision = "38"
            _data_type = _data_type + '(%s' %data_precision
            if data_scale and data_scale <> 0:
                _data_type = _data_type + ',%s' %data_scale
            _data_type = _data_type + ')'
        elif data_type in ('CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','UROWID'):
            _data_type = _data_type + '(%s)' %data_length
        
        t.append((column, _data_type, nullable, column_id, data_default))
    return all_columns


def _get_all_constraints(conn):
    "get all_table/view constraints"
    stmt = """select  table_name, constraint_name, constraint_type, search_condition, r_owner,
                     r_constraint_name , delete_rule
                     from user_constraints"""
    cons ={}
    print  "get all_table/view constraints"
    for   table_name,name, type, check_cond, r_owner, r_constraint_name, delete_rule in _query(conn, stmt):
        cons[name]=(table_name, type, check_cond, r_owner, r_constraint_name, delete_rule)
    return cons        


def _get_all_constraited_columns(conn):
    "get all constrainted columns"
    stmt  = """select constraint_name, table_name, column_name, position from
                     user_cons_columns"""
    cs_cols = {}
    print  "get all constrainted columns"
    for name , table_name, column_name, position in _query(conn, stmt):
        t = cs_cols.get(name, None)
        if not t:
            t = []
            cs_cols[name] = t
        t.append( (table_name, column_name, position))
    return cs_cols;

def _get_all_views(conn):
    "get all views"
    stmt = """ select view_name , text from user_views"""
    views = {}
    print "get all views"
    for name, text in _query(conn,stmt):
        views[name]= text
    return views

def _get_all_indexes(conn):
    "get all indexes"
    stmt = """select index_name, table_name, index_type, uniqueness, include_column, generated, secondary from user_indexes"""
    indexes = {}
    print "get all indexes"
    for name, table_name, type, uniqueness, include_column, generated, secondary in _query(conn,stmt):
        indexes[name] = (table_name, type, uniqueness, include_column, generated, secondary)
    return indexes


def _get_all_index_columns(conn):
    "get all index columns"
    stmt = """select index_name, table_name, column_name, column_position from user_ind_columns"""
    ind_columns = {}
    print "get all index columns"
    for name, table_name, column_name, column_position in _query(conn,stmt):
        t = ind_columns.get(name)
        if not t:
            t = []
            ind_columns[name] = t
        t.append(( table_name, column_name, column_position))
    return ind_columns

def _get_all_index_expressions(conn):
    "get all index expressions"
    stmt = """select index_name, table_name, column_expression, column_position from user_ind_expressions"""
    ind_expressions = {}
    print "get all index_expressions"
    for name, table_name, expression, position in _query(conn, stmt):
        t = ind_expressions.get(name)
        if not t:
            t = []
            ind_expressions[name] = t
        t.append((table_name, expression, position))
    return ind_expressions

def _get_all_updatable_columns(conn):
    "get updatable columns on views"
    stmt = """select table_name, column_name, insertable, updatable, deletable
                  from all_updatable_columns
                  where table_name in (select view_name from user_views)"""
    view_updatable_columns = {}
    print "get  updatable columns"
    for table_name, column_name, insertable, updatable, deletable in _query(conn, stmt):
        view_updatable_columns[table_name, column_name] = (insertable, updatable, deletable)
    return view_updatable_columns
    
def _get_all_triggers(conn):
    "get all triggers"
    stmt = """select trigger_name, trigger_type, triggering_event, base_object_type, table_name,
                   column_name, referencing_names, when_clause, status, description, action_type, trigger_body
                   from user_triggers"""
    triggers = {}
    print "get all triggers"
    for name, type, event, base_object_type, table_name, column_name, referencing_names, when_clause, status,\
        description, action_type, body in _query(conn, stmt):
        triggers[name] = (name, type, event, base_object_type, table_name, column_name, referencing_names, \
                          when_clause, status, description, action_type, body)
    return triggers

def _get_all_trigger_columns(conn):
    "get all trigger columns"
    stmt = "select trigger_name, table_name, column_name, column_list, column_usage from user_trigger_cols"
    trigger_columns = {}
    print "get all trigger columns"
    for name, table_name, column_name, column_list, column_usage in _query(conn, stmt):
        t = trigger_columns.get(name)
        if not t:
            t = []
            trigger_columns[name] = t
        t.append((name, table_name, column_name, column_list, column_usage))
    return trigger_columns

def _get_all_arguments(conn):
    "get all function/procedure argumets"
    stmt = """select object_name, package_name, argument_name, position, data_type, default_value, in_out, pls_type,
                   data_scale, data_precision, data_length
                from user_arguments"""
    all_arguments = []
    print "get all pl/sql arguments"
    for name, package_name, argument_name, position, data_type, default_value, in_out, pls_type, data_scale, \
        data_precision, data_length in _query(conn, stmt):
        _data_type = ''
        if pls_type:
            _data_type = pls_type
        else:
            _data_type = data_type
        if data_type == 'NUMBER':
            if not data_precision:
                data_precision = "38"
            _data_type = _data_type + '(%s' %data_precision
            if data_scale and data_scale <> 0:
                _data_type = _data_type + ',%s' %data_scale
            _data_type = _data_type + ')'
        elif data_type in ('CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','UROWID'):
            if data_length:
                _data_type = _data_type + '(%s)' %data_length
        all_arguments.append\
                ((name, package_name, argument_name, position, _data_type, default_value, in_out))
    return all_arguments

def _get_user_source(conn):
    "get pl/sql source for procedures, functions and packages"
    stmt = "select name, type, line, text from user_source order by name, line"
    user_source = []
    print "get pl/sql source for procedures, functions and packages"
    for name, type, line, text in _query(conn, stmt):
        user_source.append((name, type, line, text))
    return user_source


        
def _query(conn, querystr):
    "execute query end return results in array"    
    cur = conn.cursor()
    cur.execute(querystr)
    results = cur.fetchall()
    cur.close()
    return results

if __name__ == '__main__':
    import cx_Oracle
    connection = cx_Oracle.connect('aram_v1/aram_v1')
    s = OraSchemaDataDictionary(connection, 'Oracle')

