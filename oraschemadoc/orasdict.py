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
    """
     structure all_table_names is list od table names
    
     structure of all_tables:
     [table] = (partitioned, secondary, index_organized, clustered, cluster_name, nested, temporary
    
     structure of all_table_comments:
     [table] = comments
    
     structure of all_col_comments
     [(table,column)] = comments

     structure of all_columns
     [table] = (column, _data_type, nullable, column_id, data_default)

     structure of all_constraints
     [constraint_name] (table_name, type, check_cond, r_owner, r_constraint_name, delete_rule)

     structure of all_constrainted_columns
     [constraint_name] ( table_name, column_name, position)

     structure of all_views
     [name] text

     structure of all_indexes
     indexes[index_name](table_name, type, uniqueness, include_column, generated, secondary)

     structure of all_index_columns
     indexes[index_name]( table_name, column_name, column_position)

     structure of all_index_expressions
     indexes[index_name](table_name, expression, position)
     
     structure of all_table_names
     list 

     TODO: describe all structures
    """
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
        
        self.all_table_names      = self.all_tables.keys()
        self.all_table_names.sort()

        self.all_view_names      = self.all_views.keys()
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
                 t = self.table_unique_key_map.get(table_name)
                 if not t:
                     t = []
                     self.table_unique_key_map[table_name] = t
                 t.append(constraint_name)
            elif type == 'C':
                 t = self.table_check_constraint_map.get(table_name)
                 if not t:
                     t = []
                     self.table_check_constraint_map[table_name] = t
                 t.append(constraint_name)
            elif type == 'R':
                 t = self.table_foreign_key_map.get(table_name)
                 if not t:
                     t = []
                     self.table_foreign_key_map[table_name] = t
                 t.append(constraint_name)
                 # put row in table_referenced_by
                 _table_name, _type, _check_cond, _r_owner, _r_constraint_name, _delete_rule = self.all_constraints[r_constraint_name]
                 t = self.table_referenced_by.get(_table_name)
                 if not t:
                     t= []
                     self.table_referenced_by[_table_name] = t
                 t.append((table_name, constraint_name))
            elif type in ('V','O'):
                 t = self.view_constraint_map.get(table_name)
                 if not t:
                     t = []
                     self.view_constraint_map[table_name] = t
                 t.append(constraint_name)
                

        self.table_constraint_map= {}
        
        for constraint_name in self.all_constraint_names:
            constraint = self.all_constraints[constraint_name]
            table_name = constraint[0]
            t = self.table_constraint_map.get(table_name, None)
            if not t:
                t = []
                self.table_constraint_map[table_name] = t
            t.append(constraint_name)  

        self.all_index_names = self.all_indexes.keys()
        self.all_index_names.sort()


        self.table_index_map = {}
        for index_name in self.all_index_names:
            table_name, type, uniqueness, include_column, generated, secondary = self.all_indexes[index_name]
            t = self.table_index_map.get(table_name)
            if not t:
                t = []
                self.table_index_map[table_name] = t
            t.append(index_name)
            

        #self._all_cons_columns     = _get_all_cons_columns(conn)
        #self._all_col_comments     = _get_all_col_comments(conn)




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

