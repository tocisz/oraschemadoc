""" OraSchemaDataDictionary class queries data from Oracle Data Dictionary """

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

__version__ = '$Version: 0.25'

from oraverbose import *
import oraddlsource
import os.path

class OracleSchema:

    def __init__(self, data_dict, debug_mode, connection, output_dir, packageBodies=False):

        set_verbose_mode(debug_mode)
        self.ddlSource = oraddlsource.OraDDLSource(connection, os.path.join(output_dir, 'sql_source'))

        self.packageBodies = packageBodies

        self.tables = self._get_all_tables(data_dict)
        self.indexes = self._get_all_indexes(data_dict)
        self.constraints = self._get_all_constraints(data_dict)
        self.views = self._get_all_views(data_dict)
        self.mviews = self._get_all_mviews(data_dict)
        self.triggers = self._get_all_table_triggers(data_dict)
        self.procedures = self._get_all_procedures(data_dict)
        self.functions = self._get_all_functions(data_dict)
        self.packages = self._get_all_packages(data_dict)
        self.sequences = self._get_all_sequences(data_dict)
        self.java_sources = self._get_all_java_sources(data_dict)
        # TODO: why i need that name? 
        self.name = "Foobarizm" 


    def getXML(self):
        """get xml representaion of given schema"""
        xml_text = '<schema>'
        for table in self.tables:
            xml_text += table.getXML()
            print "generating xml for %s" % table.getName()
        for view in self.views:
            xml_text += view.getXML()

        for mview in self.mviews:
            xml_text += mview.getXML()

        for sequence in self.sequences:
            xml_text += sequence.getXML()

        for procedure in self.procedures:
            xml_text += procedure.getXML()

        for function in self.functions:
            xml_text += function.getXML()

        for package in self.packages:
            xml_text += package.getXML()
 
        xml_text += '</schema>'
        return xml_text 


    def _get_all_tables(self, data_dict):
        tables = []
        print 'generating tables'
        for table_name in data_dict.all_table_names:
            tables.append(OracleTable(table_name, data_dict))
            self.ddlSource.getDDLScript('TABLE', table_name)
        return tables

    def _get_all_indexes(self, data_dict):
        print 'generating indexes'
        indexes = []
        for index_name in data_dict.all_index_names:
            indexes.append(OracleIndex(index_name, data_dict))
            self.ddlSource.getDDLScript('INDEX', index_name)
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
            self.ddlSource.getDDLScript('VIEW', view_name)
        return views


    def _get_all_mviews(self, data_dict):
        print 'generating materialized views'
        mviews = []
        for mv_name in data_dict.all_mview_names:
            mviews.append(OracleMView(mv_name, data_dict))
            self.ddlSource.getDDLScript('MATERIALIZED VIEW', mv_name)
        return mviews


    def _get_all_table_triggers(self, data_dict):
        print 'generating triggers'
        triggers = []
        for trigger_name in data_dict.table_triggers:
            triggers.append(OracleTrigger(trigger_name, data_dict))
            self.ddlSource.getDDLScript('TRIGGER', trigger_name)
        return triggers

    def _get_all_procedures(self, data_dict):
        print 'generating procedures'
        procedures = []
        for name in data_dict.all_procedure_names:
            procedure = OracleProcedure(name, data_dict.proc_arguments.get(name, None), \
                                        data_dict.all_procedures.get(name, None))
            procedures.append(procedure)
            self.ddlSource.getDDLScript('PROCEDURE', name)
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
            self.ddlSource.getDDLScript('FUNCTION', name)
        return functions

    def _get_all_packages(self, data_dict):
        print 'generating packages'
        packages = []
        for name in data_dict.all_package_names:
            all_arguments = data_dict.package_arguments.get(name, None)
            all_return_values = data_dict.package_return_values.get(name, None)
            def_source = data_dict.all_packages[name]
            if self.packageBodies == True:
                body_source = data_dict.all_package_bodies.get(name, None)
            else:
                body_source = {0: 'Source code generator disabled'}
            package = OraclePackage(name, all_arguments, all_return_values, def_source, body_source)
            packages.append(package)
            self.ddlSource.getDDLScript('PACKAGE', name)
            self.ddlSource.getDDLScript('PACKAGE_BODY', name)
        return packages

    def _get_all_sequences(self, data_dict):
        print "generating sequences"
        sequences = []
        for name in data_dict.sequence_names:
            min_value, max_value, step, cycled, ordered, cache_size = data_dict.sequences[name]
            seq = OracleSequence(name, min_value, max_value, step, cycled, ordered, cache_size)
            sequences.append(seq)
            self.ddlSource.getDDLScript('SEQUENCE', name)
        return sequences


class OracleTable:

    def __init__(self, name, data_dict):
        debug_message('debug: creating table object %s' % name)
        # TODO delete old crap below
        self.name = name
        self.partitioned, self.secondary, self.index_organized, \
            self.clustered, self.cluster_name, self.nested, \
            self.temporary, self.tablespace_name = data_dict.all_tables[name]

        self.comments = data_dict.all_table_comments.get(name)
        self.columns = self._get_columns(data_dict)

        self.primary_key             = self._get_primary_key(name, data_dict)
        self.unique_keys             = self._get_unique_keys(name, data_dict)
        self.check_constraints       = self._get_check_constraints(name, data_dict)
        self.referential_constraints = self._get_ref_constraints(name, data_dict)
        self.indexes                 = self._get_indexes(name, data_dict)
        self.triggers                = self._get_triggers(data_dict)

        self.tab_partitions          = self._get_tab_partitions(name, data_dict)
        self.referenced_by = None
        if data_dict.table_referenced_by.has_key(name):
            self.referenced_by       = data_dict.table_referenced_by[name]

        # all above should be replaced by this 
        self.__name = name 
        self.__partitioned, self.__secondary, self.__index_organized, self.__clustered, self.__cluster_name, \
            self.__nested, self.__temporary, self.__tablespace_name = data_dict.all_tables[name]
        self.__columns = self._get_columns(data_dict)
        self.__comments = self.comments
        self.__primary_key = self.primary_key
        self.__unique_keys = self.unique_keys
        self.__check_constraints = self.check_constraints
        self.__referential_constraints = self.referential_constraints
        self.__indexes = self.indexes
        self.__triggers = self.triggers
        self.__referenced_by = self.referenced_by

    def getName(self):
        """get name of table"""
        return self.__name

    def isPartitioned(self):
        """determines if table is partitioned"""
        return self.__partitioned

    def isIndexOrganized(self):
        """is IOT table"""
        return self.__index_organized

    def isSecondary(self):
        """is table is secondary, i.e. system generated"""
        return self.__secondary

    def isClustered(self):
        """is table clustered"""
        return self.__clustered

    def getClusterName(self):
        """returns cluster name if table is clustered"""
        return self.__cluster_name

    def isNested(self):
        """is table is nested table"""
        return self.__nested

    def isTemporary(self):
        """is table is temporary table"""
        return self.__temporary

    def getTablespaceName(self):
        """returns tbs name"""
        return self.__tablespace_name

    def _get_primary_key(self, table_name, data_dict):
        _primary_key_name = data_dict.table_primary_key_map.get(table_name)
        primary_key = None
        if _primary_key_name:
            debug_message('debug: generating primary key %s' % _primary_key_name)
            primary_key = OracleUniqueConstraint(_primary_key_name, data_dict)
        return primary_key

    def _get_unique_keys(self, table_name, data_dict):
        debug_message('debug: generating unique keys')
        unique_keys = []
        t = data_dict.table_unique_key_map.get(table_name)
        if not t:
            return None
        for key_name in t:
            debug_message('debug: generating unique key %s' % key_name )
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
            debug_message('debug: generating check constraint %s' % constraint_name)
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
            debug_message('debug: generating foreign key %s' % constraint_name)
            constraint = OracleReferentialConstraint(constraint_name, data_dict)
            referential_constraints.append(constraint)
        return referential_constraints


    def _get_tab_partitions(self, name, data_dict):
        debug_message('debug: generating partitions')
        partitions = []
        if not data_dict.all_tab_partitions.has_key(self.name):
            debug_message('debug: no partitons found')
            return []
        for partition_position, partition_name, tablespace_name, high_value in data_dict.all_tab_partitions[self.name]:
            partitions.append(OracleTabPartition(partition_position, partition_name, tablespace_name, high_value))
        return partitions


    def _get_columns(self, data_dict):
        debug_message('debug: generating columns')
        columns = {}
        # Fixme: need proper hadling iot overflow segment columns
        if data_dict.all_columns.has_key(self.name):
            for column, data_type, nullable, column_id, data_default in data_dict.all_columns[self.name]:
                debug_message('debug: generating column %s' % column)
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
                debug_message('debug: generating index %s' % index_name)
                index = OracleIndex(index_name, data_dict)
                indexes.append(index)
        return indexes

    def _get_triggers(self, data_dict):
        debug_message('debug: generating triggers')
        triggers = []
        if  data_dict.table_trigger_map.has_key(self.name):
            for trigger_name in data_dict.table_trigger_map[self.name]:
                debug_message('debug: generating trigger %s' % trigger_name)
                triggers.append(OracleTrigger(trigger_name, data_dict))
        return triggers

    def getXML(self):
        """get xml represention of table"""
        xml_text = '''<table id="table-%s">
                         <name>%s</name>
                         <index_orginized>%s</index_orginized>
                         <tablespace>%s</tablespace>
                         <partitioned>%s</partitioned>
                         <temporary>%s</temporary>
                         <nested>%s</nested>
                         <clustered>%s</clustered>
                         <cluster_name>%s</cluster_name>
                         <secondary>%s</secondary>
                         <comments><![CDATA[%s]]></comments>
                         ''' % (self.__name, 
                                self.__name,
                                self.__index_organized,
                                self.__tablespace_name,
                                self.__partitioned,
                                self.__temporary,
                                self.__nested,
                                self.__clustered,
                                self.__cluster_name,
                                self.__secondary,
                                self.__comments)
        xml_text += '<columns>'
        #xml for table columns
        for position in self.__columns.keys():
            xml_text += self.__columns[position].getXML(self.__name)
        xml_text += '</columns>\n'
        xml_text += '<constraints>\n'        
        if self.__primary_key:
            xml_text +=  self.__primary_key.getXML()
        if self.__unique_keys:
            for unique_key in self.__unique_keys:
                xml_text += unique_key.getXML()
        if self.__check_constraints:
            for constraint in self.__check_constraints:
                xml_text += constraint.getXML()
        if self.__referential_constraints:
            for constraint in self.__referential_constraints:
                xml_text += constraint.getXML()
        xml_text += '</constraints>\n'
        if self.__indexes:
            xml_text += '<indexes>\n'	            
            for index in self.__indexes:
                xml_text += index.getXML()
            xml_text += '</indexes>'
        if self.__triggers:
            xml_text += '<triggers>'
            for trigger in self.triggers:
                xml_text += trigger.getXML()
            xml_text += '</triggers>'
        if self.__referenced_by:
            xml_text += '<references>'
            for name in self.__referenced_by:
                xml_text += '<reference><table>table-%s</table><constraint>constraint-%s</constraint></reference>' % name
            xml_text += '</references>'
        xml_text += '</table>\n'
        return xml_text 


class OracleTabPartition:

    def __init__(self, partition_position, partition_name, tablespace_name, high_value):
        self.partition_position = partition_position
        self.partition_name = partition_name
        self.tablespace_name = tablespace_name
        self.high_value = high_value


class OracleColumn:
    """Oracle column represents table column object"""

    def __init__(self, name, column_id, data_type, nullable, data_default, comments):
        self.__position = column_id
        self.__name = name
        self.__data_type = data_type
        self.__nullable = nullable
        self.__default_value = data_default
        self.__comments = comments
        #TODO start using table name!
        self.__table_name = ''

        ### crap below should be deleted!
        self.column_id = column_id
        self.name = name
        self.data_type =data_type
        self.nullable = nullable
        self.data_default = data_default
        self.comments = comments

    def getName(self):
        """get column name"""
        return self.__name

    def getPosition(self):
        """get column position"""
        return self.__position

    def getDataType(self):
        """get column data Type"""
        return self.__data_type

    def getDefaultValue(self):
        """get default value for column"""
        return self.__default_value

    def getComments(self):
        """get Comments on the column"""
        return self.__comments

    def isNullable(self):
        """check if column is nullable"""
        return self.__nullable

    def getXML(self, table_name):
        """get xml representation of column"""
        #TODO: and it sucks to pass table_name via getXML, fix it
        return '''<column id="column-%s.%s">
                    <name>%s</name>
                    <position>%s</position>
                    <datatype>%s</datatype>
                    <default_value>%s</default_value>
                    <nullable>%s</nullable>
                    <comments><![CDATA[%s]]></comments>
                  </column>\n''' % (table_name, self.__name,
                    self.__name, self.__position, self.__data_type,
                    self.__default_value, self.__nullable, 
                    self.__comments)


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

        self.__name = name
        self.__table_name = table_name
        self.__type = type
        self.__columns = self.columns

    def getName(self):
        """ get constraint name"""
        return self.__name

    def getType(self):
        ''' returns type, where type is one of "Primary Key" or "Unique Key"'''
        return self.__type

    def getColumns(self):
        '''get columns as dictionary indexed by position in index'''
        return self.__columns

    def getXML(self):
        '''get xml for unique/primary key'''
        xml_text = '''<constraint id="constraint-%s" type="unique">
                      <name>%s</name>
                      <type>%s</type>
                      <ind_columns>''' % (self.__name, self.__name, self.__type)
        for position in self.__columns.keys():
            xml_text += '<column>column-%s.%s</column>' % (
                                                       self.__table_name, self.__columns[position])
        xml_text += '</ind_columns>\n</constraint>\n'
        return xml_text


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

        self.__name = name
        self.__table_name = self.table_name
        self.__type = type
        self.__r_owner = r_owner
        self.__r_table = self.r_table
        self.__r_constraint_name = r_constraint_name
        self.__delete_rule = delete_rule
        self.__columns = self.columns

    def getName(self): 
        """get constraint name"""
        return self.__columns

    def getXML(self):
        """get data about constraint in xml"""
        xml_text = '''<constraint id="constraint-%s" type="referential">
                      <name>%s</name>
                      <type>%s</type>
                      <ind_columns>''' % (self.__name, self.__name, self.__type)
        for position in self.__columns.keys():
            xml_text += '<column>column-%s.%s</column>' % (
                                                       self.__table_name, self.__columns[position])
        xml_text += '</ind_columns>\n'
        xml_text += '''<delete_rule>%s</delete_rule>
                       <master_table>table-%s</master_table>'''  % (self.__delete_rule, self.__delete_rule)

        xml_text += '</constraint>\n'
        return xml_text


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


    def getXML(self):
        """get data about index in xml"""
        xml_text = '''<index id="index-%s">
                        <name>%s</name>
                        <type>%s</type>
                        <table>table-%s</table>
                        <uniqueness>%s</uniqueness>
                        <generated>%s</generated>
                        <secondary>%s</secondary>''' % ( self.name, self.name, self.type, self.table_name,
                                                        self.uniqueness, self.generated, self.secondary)

        xml_text += '<ind_columns>'
        for position in self.columns.keys():
            xml_text += '<column>column-%s</column>' % self.columns[position]
        xml_text += '</ind_columns></index>'
        return xml_text


class OracleView:

    def __init__(self, name, data_dict):
        debug_message("debug: generating view %s" % name)
        self.name = name
        self.text = data_dict.all_views[name]
        self.columns = self._get_columns(data_dict)
        self.constraints = self._get_constraints(data_dict)
        self.comments = data_dict.all_table_comments.get(name)
        self.triggers = self._get_triggers(data_dict)


    def getXML(self):
        """get data about view in xml"""
        xml_text = '''<view id="view-%s">
                        <name>%s</name>
                        <comments><![CDATA[%s]]></comments>
                        <query_text><![CDATA[%s]]></query_text>''' % (
                    self.name, self.name, self.comments, self.text)
        if self.columns: 
            xml_text += '<columns>\n'
            for position in self.columns.keys():
                xml_text += self.columns[position].getXML(self.name)
            xml_text += '</columns>\n'

        if self.constraints:
            xml_text += '<constraints>'
            for constraint in self.constraints:
                xml_text += constraint.getXML
            xml_text += '</constraints>'

        if self.triggers:
            xml_text += '<triggers>'            
            for trigger in self.triggers:
                xml_text += trigger.getXML()
            xml_text += '</triggers>'
        xml_text += '</view>'
        return xml_text


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
        debug_message("debug: generating view column %s" % name)
        OracleColumn.__init__(self, name, column_id, data_type, nullable, data_default, comments)
        # check due the e.g. count(*) columns...
        try:
            self.insertable, self.updatable, self.deletable = data_dict.all_updatable_columns[table_name, name]
        except KeyError:
            self.insertable = self.updatable = self.deletable = 'n/a'

    def getXML(self, table_name):
        """get xml representation of column"""
        #TODO: and it sucks to pass table_name via getXML, fix it
        return '''<column id="column-%s.%s">
                    <name>%s</name>
                    <position>%s</position>
                    <datatype>%s</datatype>
                    <default_value>%s</default_value>
                    <nullable>%s</nullable>
                    <comments><![CDATA[%s]]></comments>
                    <insertable>%s</insertable>
                    <updatable>%s</updatable>
                    <deletable>%s</deletable>
                  </column>\n''' % (table_name, self.name,
                    self.name, self.column_id , self.data_type,
                    self.data_default , self.nullable, 
                    self.comments, self.insertable, self.updatable, self.deletable)


class OracleViewConstraint:

    def __init__(self, name, data_dict):
        debug_message("debug: generating view constraint %s" % name)
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


class OracleMView(OracleView):

    def __init__(self, name, data_dict):
        self.name = name
        self.columns = self._get_columns(data_dict)
        self.constraints = self._get_constraints(data_dict)
        self.comments = data_dict.all_table_comments.get(name)
        self.triggers = self._get_triggers(data_dict)
        self.container, self.query, self.mv_updatable = data_dict.all_mviews[name]


class OracleTrigger:

    def __init__(self, name, data_dict):
        debug_message("debug: generating trigger %s" % name)
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


class OracleTriggerColumn:

    def __init__(self, column_name, column_list, column_usage):
        debug_message("debug: generating trigger column %s" % column_name)
        self.column_name = column_name
        self.column_list = column_list
        self.column_usage = column_usage

class OracleProcedure:

    def __init__(self, name, arguments, source = None):
        debug_message("debug: generating plsql procedure %s" % name)
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

    def getXML(self):
        """get procedure metadata"""
        xml_text = '''<procedure id="procedure-%s">
                        <name>%s</name>
                        <source>%s</source>''' % (self.name, self.name, self.source.getXML())
        if self.arguments:
            xml_text += '<arguments>'
            for argument in self.arguments:
                xml_text += argument.getXML()
            xml_text += '</arguments>'

        xml_text += '</procedure>'
        return xml_text


class OracleFunction(OracleProcedure):

    def __init__(self, name, arguments, return_data_type, source = None):
        debug_message("debug: generating plsql function %s" % name)
        OracleProcedure.__init__(self, name, arguments, source)
        self.return_data_type = ''
        if return_data_type:
            self.return_data_type = return_data_type

    def getXML(self):
        """get function metadata"""
        xml_text = '''<function id="procedure-%s">
                        <name>%s</name>
                        <returns>%s</returns>
                        <source>%s</source>''' % (self.name, self.name, self.return_data_type, 
                                                              self.source.getXML())
        if self.arguments:
            xml_text += '<arguments>'
            for argument in self.arguments:
                xml_text += argument.getXML()
            xml_text += '</arguments>'

        xml_text += '</function>'
        return xml_text            


class OracleProcedureArgument:
    def __init__(self, name, data_type, default_value, in_out ):
        debug_message("debug: generating plsql argument %s" % name)
        self.name = name
        self.data_type = data_type
        self.default_value = default_value
        self.in_out = in_out

    def getXML(self):
        """get argument metadata in xml"""
        return '''<argument>
                    <name>%s</name>
                    <data_type>%s</data_type>
                    <default_value>%s</default_value>
                    <in_out>%s</in_out>
                  </argument>''' % (self.name, self.data_type, self.default_value, self.in_out)


class OraclePLSQLSource:
    def __init__(self, source):
        debug_message("debug: generating plsql source ")
        self.source = []
        lines = source.keys()
        lines.sort()
        for line_no in lines:
            self.source.append(OraclePLSQLSourceLine(line_no, source[line_no]))

    def getXML(self):
        """get source in xml"""
        xml_text = '<pl_sql_source>'
        for line in self.source:
            xml_text += '<line><line_no>%s</line_no><text><![CDATA[%s]]></text></line>' % (line.line_no, line.text)
        xml_text += '</pl_sql_source>'
        return xml_text


class OracleJavaSource(OraclePLSQLSource):
    def __init__(self, name, source):
        self.name = name
        debug_message("debug: generating java source ")
        OraclePLSQLSource.__init__(self,source)


class OraclePLSQLSourceLine:

    def __init__(self, line_no, text):
        self.line_no = line_no
        self.text = text

class OraclePackage:

    def __init__(self, name, all_arguments, all_return_values, definition_source, body_source):
        debug_message("debug: generating plsql package %s" % name)
        self.name = name
        self.source = OraclePLSQLSource(definition_source)
        self.body_source = None
        if body_source:
            self.body_source = OraclePLSQLSource(body_source)

    def getXML(self):
        """get package metadata"""
        xml_text = '''<package id="package-%s">
                        <name>%s</name>
                        <declaration>%s</declaration>
                        <body>%s</body>
                      </package>''' % ( self.name, self.name, self.source.getXML(), self.body_source.getXML())
        return xml_text


class OracleSequence:
    """Represents Oracle sequence database object"""

    def __init__(self, name, min_value, max_value, step, cycle_flag, ordered, cache_size):
        debug_message("debug: genarating sequence %s" % name)
        self.__name = name
        self.__min_value = min_value
        self.__max_value = max_value
        self.__step = step
        self.__cycle_flag = cycle_flag
        self.__ordered = ordered
        self.__cache_size = cache_size

    def getName(self):
        """Get sequence name"""
        return self.__name

    def getMinValue(self):
        """Get min value of the sequence"""
        return self.__min_value

    def getMaxValue(self):
        """Get max value of the sequence"""
        return self.__max_value

    def getStep(self):
        """Get step of the sequence"""
        return self.__step

    def isCycled(self):
        """Get cycled flag of the sequence"""
        return self.__cycle_flag

    def getCacheSize(self):
        """Get cache size of the sequence"""
        return self.__cache_size 

    def isOrdered(self):
        """Determines if values of the sequence ordered"""
        return self.__ordered

    def getXML(self):
        """get sequence metadata in xml"""
        xml_text = '''<sequence id="sequence-%s">
                        <name>%s</name>
                        <min_value>%s</min_value>
                        <max_value>%s</max_value>
                        <step>%s</step>
                        <cycled>%s</cycled>
                        <cache_size>%s</cache_size>
                        <ordered>%s</ordered>
                      </sequence>''' % (self.__name, self.__name, self.__min_value, self.__max_value,
                                        self.__step, self.__cycle_flag, self.__cache_size, self.__ordered)
        return xml_text


class OracleTypeSource(OraclePLSQLSource):
    """Source code of type"""
    pass


class OracleTypeAttribute:
    """Type attribute object"""

    def __init__(self, name, type_mod, type_owner, type_name, length, precision, \
                 scale, character_set_name):
        self.__name = name
        self.__type = type_name
        self.__type_mod = type_mod
        self.__type_owner = type_owner
        self.__length = length
        self.__precision = precision
        self.__scale = scale
        self.__character_set_name = character_set_name

    def getName(self):
        """Get attribute name"""
        return self.__name

    def getType(self):
        """Get type of the attribute"""
        return self.__type

    def getTypeModifier(self):
        """Type modifier of the attribute"""
        return self.__type_mod

    def getTypeOwner(self):
        """Get owner of attribute type"""
        return self.__type_owner

    def getLength(self):
        """Get type length of the attribute"""
        return self.__length

    def getPrettyType(self):
        """Get pretty formated type in the form of type(x,y)"""
        type_len = self.__type
        if self.__length is not None:
            type_len = '(%s)' % self.__length
        elif self.__precision is not None:
            if self.__scale is not None:
                type_len = '(%s,%s)' % (self.__precision, self.__scale)
            else:
                type_len = '(%s)' % self.__precision
        return type_len

    def getPrecision(self):
        """Get type precision of the attribute"""
        return self.__precision

    def getScale(self):
        """Get type scale of the attribute"""
        return self.__scale

    def getCharSetName(self):
        """Get character set name of the attribute"""
        return self.__character_set_name


class OracleTypeMethod:
    """Represents Oracle Type methods"""
    def __init__(self, name, method_type, param_count, results_count):
        self.__name = name 
        self.__type = method_type
        self.__results_count = results_count 
        self.__param_count = param_count

    def getName(self):
        """Get type method name"""
        return self.__name 

    def getType(self):
        """Get method type"""
        return self.__type

    def getResultsCount(self):
        """Get count of results returned by the method"""
        return self.__results_count

    def getParametersCount(self):
        """Get count of method parameters"""
        return self.__param_count


class OracleType:
    """Represents Oracle Object type"""

    def __init__(self, name, typecode, predefined, incomplete, 
                 type_oid, attributes_count,
                 methods_count):
        self.__name = name
        self.__typecode = typecode
        self.__predefined = predefined
        self.__incomplete = incomplete
        self.__source = None
        self.__body_source = None
        self.__type_oid = type_oid
        self.__attrubutes_count = attributes_count
        self.__methods_count = methods_count 

    def setDeclarationSource(self, source):
        """Set type declaration source code text"""
        self.__source = source

    def setImplementationSource(self, source):
        """Set Type implementation source code text"""
        self.__body_source = source

    def getName(self):
        """Get type name"""
        return self.__name

    def getTypeCode(self):
        """Get type typecode""" 
        return self.__typecode

    def isPredefined(self):
        """Indicates whether the type is a predefined type"""
        return self.__predefined == 'YES'

    def isIncomplete(self):
        """Indicates whether the type is an incomplete type"""
        return self.__incomplete == 'YES'

    def getDeclarationSource(self):
        """Get type declaration source code"""
        return self.__source

    def getImplementationSource(self):
        """Get implementation source code"""
        return self.__body_source

    def getTypeOID(self):
        """Get object identifier (OID) of type"""
        return self.__type_oid

    def getMethodsCount(self):
        """Get count of methods in the type"""
        return self.__methods_count

    def getAttributesCount(self):
        """Get count of attributes in the type"""
        return self.__attrubutes_count


if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    #connection = cx_Oracle.connect('s0/asgaard')
    connection = cx_Oracle.connect('system/asgaard')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle', False)
    schema = OracleSchema(s, 0, connection, './', True)
