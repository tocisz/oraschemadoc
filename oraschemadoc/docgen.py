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

# Doc Generator

__author__ = 'Aram Kananov <arcanan@flashmail.com>'

__version__ = '$Version: 0.21'

import os, string, docwidgets, analyze

from oraverbose import *

class OraSchemaDoclet:

    def __init__(self, schema, doc_dir, name, description, debug_mode):
        
        set_verbose_mode(debug_mode)
        
        self.schema = schema
        self.doc_dir = doc_dir
        self.name = name
        self.description = description
        self.html = docwidgets.HtmlWidgets(self.name)
        self.index = {}

        self._print_table_list_page()
        self._print_tables()
        self._print_table_index_frame()
        self._print_index_list_page()
        self._print_trigger_list_page()
        self._print_trigger_index_frame()
        self._print_index_index_frame()
        self._print_constraint_list_page()
        self._print_constraint_index_frame()
        self._print_view_list_page()
        self._print_view_index_frame()
        self._print_views()
        self._print_procedures()
        self._print_procedure_list_page()
        self._print_procedure_index_frame()
        self._print_functions()
        self._print_function_list_page()
        self._print_function_index_frame()        
        self._print_packages()
        self._print_package_list_page()
        self._print_package_index_frame()  
        self._print_symbol_index_page()
        self._sanity_check()
        self._print_common_pages()



    def _print_common_pages(self):
        text = self.html._index_page(self.name)
        file_name = os.path.join(self.doc_dir, "index.html")
        self._write(text, file_name)
        text = self.html._global_nav_frame(self.name)
        file_name = os.path.join(self.doc_dir, "nav.html")
        self._write(text, file_name)
        text = self.html._main_frame(self.name)
        file_name = os.path.join(self.doc_dir, "main.html")
        self._write(text, file_name)
    


    def _print_table_list_page(self):
        print "print table list page"
        text = self.html.page_header("Tables")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for table in self.schema.tables:
            name = self.html.href_to_table(table.name)
            if table.secondary == 'Yes':
                name = self.html.i(name)
            comments = table.comments 
            if comments:
                comments = self.html._quotehtml(comments[:50]+'...')
            rows.append(( name, comments ))
        headers = "Table", "Description"
        name = "Tables"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "tables-list.html")
        self._write(text, file_name)



    def _print_table_index_frame(self):
        print "print table list frame"
        text = self.html.frame_header("Tables")
        #text = text + self.html.heading("Tables",3)
        text = text + self.html.hr()
        rows = []
        for table in self.schema.tables:
            link = self.html.href_to_table(table.name, "Main")
            if table.secondary == 'Yes':
                link = self.html.i(link)
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "tables-index.html")
        self._write(text, file_name)



    def _print_index_index_frame(self):
        print "print indexes list frame"
        text = self.html.frame_header("Indexes")
        #text = text + self.html.heading("Indexes",3)
        text = text + self.html.hr()
        rows = []
        for index in self.schema.indexes:
            link = self.html.href_to_index(index.name, index.table_name, index.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "indexes-index.html")
        self._write(text, file_name)



    def _print_constraint_index_frame(self):
        print "print constraint list frame"
        text = self.html.frame_header("Constraints")
        #text = text + self.html.heading("Constraints",3)
        text = text + self.html.hr()
        rows = []
        for constraint in self.schema.constraints:
            link = self.html.href_to_constraint(constraint.name, constraint.table_name, constraint.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "constraints-index.html")
        self._write(text, file_name)



    def _print_view_index_frame(self):
        print "print view list frame"
        text = self.html.frame_header("Views")
        #text = text + self.html.heading("Views",3)
        text = text + self.html.hr()
        rows = []
        for view in self.schema.views:
            link = self.html.href_to_view(view.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "views-index.html")
        self._write(text, file_name)



    def _print_procedure_index_frame(self):
        print "print procedure list frame"
        text = self.html.frame_header("Procedures")
        text = text + self.html.hr()
        rows = []
        for procedure in self.schema.procedures:
            link = self.html.href_to_procedure(procedure.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "procedures-index.html")
        self._write(text, file_name)



    def _print_function_index_frame(self):
        print "print functions list frame"
        text = self.html.frame_header("Functions")
        text = text + self.html.hr()
        rows = []
        for function in self.schema.functions:
            link = self.html.href_to_function(function.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "functions-index.html")
        self._write(text, file_name)


    def _print_package_index_frame(self):
        print "print packages list frame"
        text = self.html.frame_header("Packages")
        text = text + self.html.hr()
        rows = []
        for package in self.schema.packages:
            link = self.html.href_to_package(package.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "packages-index.html")
        self._write(text, file_name)

        

    def _print_trigger_index_frame(self):
        print "print triggers list frame"
        text = self.html.frame_header("Triggers")
        text = text + self.html.hr()
        rows = []
        for trigger in self.schema.triggers:
            link = self.html.href_to_trigger(trigger.name, trigger.table_name, trigger.name, "Main")
            text = text + link + '<br>'
        text = text + self.html.frame_footer()
        file_name = os.path.join(self.doc_dir, "triggers-index.html")
        self._write(text, file_name)         



    def _print_tables(self):
        print "print tables"
        for table in self.schema.tables:
            self._print_table(table)
            


    def _print_views(self):
        print "print views"
        for view in self.schema.views:
            self._print_view(view)


    def _print_functions(self):
        print "print functions"
        for function in self.schema.functions:
            self._print_function(function)


    def _print_procedures(self):
        print "print procedures"
        for procedure in self.schema.procedures:
            self._print_procedure(procedure)



    def _print_packages(self):
        print "print packages"
        for package in self.schema.packages:
            self._print_package(package)
            
    def _print_table(self, table):
        "print table page"
        # create header and context bar
        text = self.html.page_header("Table-" + table.name)
        local_nav_bar = []
        local_nav_bar.append(("Description", "t-descr"))
        local_nav_bar.append(("Columns", "t-cols"))
        local_nav_bar.append(("Primary key", "t-pk"))
        local_nav_bar.append(("Check Constraints", "t-cc"))
        local_nav_bar.append(("Foreign keys", "t-fk"))
        local_nav_bar.append(("Unique Keys", "t-uc"))
        local_nav_bar.append(("Options", "t-opt"))
        local_nav_bar.append(("Indexes", "t-ind"))
        local_nav_bar.append(("Referenced by", "t-refs"))
        local_nav_bar.append(("Triggers", "t-trgs"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        text = text + self.html.heading(table.name, 2)
        # punt entry in doc index
        self._add_index_entry(table.name, self.html.href_to_table(table.name), "table")
        # print comments
        if table.comments:
            text = text + self.html.heading("Description:",3) + self.html.anchor("t-descr")
            text = text + self.html.pre(self.html._quotehtml(table.comments))
        #print columns
        rows = []
        # fixme iot table overflow segment column problem
        if len(table.columns) > 0:
            for i in range(len(table.columns)):
                column = table.columns[i+1]
                self._add_index_entry(column.name, self.html.href_to_column(column.name, table.name, column.name),\
                                      "column of table %s" % table.name)
                rows.append((column.name+self.html.anchor('col-%s' % column.name), column.data_type, \
                             column.nullable, column.data_default, column.comments))
            headers = "Name", "Type", "Nullable", "Default value", "Comment"
            text = text + self.html.table("Columns" + self.html.anchor('t-cols'), headers, rows)
        # print primary key
        if table.primary_key:
            title = "Primary key:" + self.html.anchor("t-pk")
            pk_name = table.primary_key.name + self.html.anchor("cs-%s" % table.primary_key.name)
            pk_columns = ''
            for i in range(len(table.primary_key.columns)):
                pk_columns = pk_columns + \
                      self.html.href_to_column(table.primary_key.columns[i+1],table.name, table.primary_key.columns[i+1])
                if i+1 != len(table.primary_key.columns):
                    pk_columns = pk_columns + ', '
            headers = "Constraint Name" , "Columns"
            rows = []
            rows.append((pk_name, pk_columns))
            text = text + self.html.table( title, headers, rows)
        # print check constraints
        if table.check_constraints:
            title = "Check Constraints:" + self.html.anchor("t-cc")
            rows = []
            for constraint in table.check_constraints:
                rows.append((constraint.name + self.html.anchor("cs-%s" % constraint.name), \
                             self.html._quotehtml(constraint.check_cond)))
            text = text + self.html.table(title, ("Constraint Name","Check Condition"), rows)
        # print referential constraints
        if table.referential_constraints:
            title = "Foreign Keys:" + self.html.anchor("t-fk")
            rows = []
            for constraint in table.referential_constraints:
                columns = ''
                for i in range(len(constraint.columns)):
                    columns = columns + self.html.href_to_column(constraint.columns[i+1], \
                                                        table.name, constraint.columns[i+1])
                    if i+1 != len(constraint.columns):
                        columns = columns + ', '
                name = constraint.name + self.html.anchor("cs-%s" % constraint.name)
                r_table = self.html.href_to_table(constraint.r_table)
                r_constraint_name = self.html.href_to_constraint(constraint.r_constraint_name, \
                                                  constraint.r_table, constraint.r_constraint_name)
                rows.append((name, columns, r_table, r_constraint_name, constraint.delete_rule))
            headers = "Constraint Name", "Columns", "Referenced table", "Referenced Constraint", "On Delete Rule"  
            text = text + self.html.table(title,headers, rows)
        # print unique keys
        if table.unique_keys:
            title = "Unique Keys:" + self.html.anchor("t-uc")
            rows = []           
            for constraint in table.unique_keys:
                columns = ''
                for i in range(len(constraint.columns)):
                    columns = columns + self.html.href_to_column(constraint.columns[i+1],table.name, \
                                                                 constraint.columns[i+1])
                    if i+1 != len(constraint.columns):
                        columns = columns + ', '
                name = constraint.name + self.html.anchor("cs-%s" % constraint.name)
                rows.append((name, columns))
            text = text + self.html.table(title,("Constraint name","Columns"), rows)
        # print table options
        title = "Options:" + self.html.anchor("t-opt")
        rows = []
        rows.append(("Index Organized", table.index_organized))
        rows.append(("Generated by Oracle", table.secondary))
        rows.append(("Clustered", table.clustered))
        if table.clustered == 'Yes':
            rows.append(("Cluster", table.cluster_name))
        rows.append(("Nested", table.nested))
        rows.append(("Temporary", table.temporary))                
        headers = "Option","Settings"
        text = text + self.html.table(title, headers, rows)
        # print indexes
        if table.indexes:
           title = "Indexes:" + self.html.anchor("t-ind")
           rows = []
           
           for index in table.indexes:
               columns = ''
               for i in  range(len(index.columns)):
                    columns = columns + self.html.href_to_column(index.columns[i+1],table.name, index.columns[i+1])
                    if i+1 != len(index.columns):
                        columns = columns + ', '
               name = index.name + self.html.anchor("ind-%s" % index.name)
               rows.append((name, index.type, index.uniqueness, columns))
           headers = "Index Name", "Type", "Unuqueness","Columns"
           text = text + self.html.table(title, headers, rows)

        # print list of tables with references to this table
        if table.referenced_by:
           title = "Referenced by:" + self.html.anchor("t-refs")
           rows = []
           for table_name, constraint_name in table.referenced_by:
               constraint_name = self.html.href_to_constraint(constraint_name, table_name, constraint_name)
               table_name = self.html.href_to_table(table_name)
               rows.append((table_name, constraint_name))
           headers = "Table", "Constraint"
           text = text + self.html.table(title, headers, rows)

        # print triggers
        if table.triggers:
            text = text +"<br>" + self.html.heading("Triggers",3) + self.html.anchor("t-trgs")
            for trigger in table.triggers:
                headers = []
                rows = []
                headers.append( "<b> Name: </b>"+trigger.name+"<br>" + self.html.anchor('trg-%s' % trigger.name))
                row = "<pre>"
                #if trigger.nested_column_name:
                #    row = row + "on " + trigger.nested_column_name+"\n"
                #row = row +  trigger.type+ " "+ trigger.event +"\n"
                row = row + 'CREATE TRIGGER ' + trigger.description
                row = row +   trigger.referencing_names+"\n"
                if trigger.when_clause:
                    row = row + "When " + self.html._quotehtml(trigger.when_clause)+"\n"
                row = row +   self.html._quotehtml(trigger.body)+"\n</pre>"
                t = []
                t.append(row)
                rows.append(t)
                text = text + self.html.table(None, headers, rows, '100')+"<p>"
                       
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "table-%s.html" % table.name)
        self._write(text, file_name)



    def _print_index_list_page(self):
        print "print indexes list page"
        text = self.html.page_header("Indexes")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for index in self.schema.indexes:
            name = self.html.href_to_index(index.name, index.table_name, index.name)
            #add entry to do index
            self._add_index_entry(index.name, name, "index on table %s" % index.table_name)
            type = index.type
            table_name = self.html.href_to_table(index.table_name)
            rows.append(( name, type, table_name ))
        headers = "Index", "Type", "Table"
        name = "Indexes"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "indexes-list.html")
        self._write(text, file_name)



    def _print_trigger_list_page(self):
        print "print triggers list page"
        text = self.html.page_header("Triggers")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for trigger in self.schema.triggers:
            name = self.html.href_to_trigger(trigger.name, trigger.table_name, trigger.name)
            #add entry to do index
            self._add_index_entry(trigger.name, name, "Trigger on table %s" % trigger.table_name)
            type = trigger.type
            table_name = self.html.href_to_table(trigger.table_name)
            rows.append(( name, type, table_name ))
        headers = "Trigger", "Type", "Table"
        name = "Triggers"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "triggers-list.html")
        self._write(text, file_name)



    def _print_constraint_list_page(self):
        print "print constraints list page"
        text = self.html.page_header("Constraints")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for constraint in self.schema.constraints:
            name = self.html.href_to_constraint(constraint.name, constraint.table_name, constraint.name)
            # add entry to doc index
            self._add_index_entry(constraint.name, name, "constraint on table %s" % constraint.table_name)
            type = constraint.type
            table_name = self.html.href_to_table(constraint.table_name)
            rows.append(( name, type, table_name ))
        headers = "Name", "Type", "Table"
        name = "Constraints"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "constraints-list.html")
        self._write(text, file_name)        



    def _print_view_list_page(self):
        print "print views list page"
        text = self.html.page_header("Views")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for view in self.schema.views:
            name = self.html.href_to_view(view.name)
            # add entry to doc index
            self._add_index_entry(view.name, name, "view")
            comments = view.comments 
            if comments:
                comments = self.html._quotehtml(comments[:50]+'...')
            rows.append(( name, comments ))
        headers = "View", "Description"
        name = "Views"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "views-list.html")
        self._write(text, file_name)



    def _print_view(self, view):
        "print view page"
        # create header and context bar
        text = self.html.page_header("View-" + view.name)
        local_nav_bar = []
        local_nav_bar.append(("Description", "v-descr"))
        local_nav_bar.append(("Columns", "v-cols"))
        local_nav_bar.append(("Query", "v-query"))
        local_nav_bar.append(("Constraints", "v-cc"))
        local_nav_bar.append(("Triggers", "v-trgs"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        text = text + self.html.heading(view.name, 2)
        # print comments
        if view.comments:
            text = text + self.html.heading("Description:",3) + self.html.anchor("v-descr")
            text = text + self.html.pre(self.html._quotehtml(view.comments))
        #print columns
        rows = []
        for i in range(len(view.columns)):
            column = view.columns[i+1]
            # add entry to doc index
            self._add_index_entry(column.name, self.html.href_to_view_column(column.name, view.name, column.name), \
                                  "column of of view %s" % view.name)
            rows.append((column.name+self.html.anchor('col-%s' % column.name), column.data_type, column.nullable,\
                         column.insertable, column.updatable, column.deletable, column.comments))
        headers = "Name", "Type", "Nullable","Insertable","Updatable", "Deletable", "Comment"
        text = text + self.html.table("Columns" + self.html.anchor('v-cols'), headers, rows)
        # print query
        text = text + self.html.heading("Query:",3) + self.html.anchor("v-query")
        text = text + self.html.pre(view.text)
        # print constraints
        if view.constraints:
            title = "Constraints:" + self.html.anchor("v-cc")
            rows = []
            for constraint in view.constraints:
                rows.append((constraint.name + self.html.anchor("cs-%s" % constraint.name),constraint.check_cond))
            text = text + self.html.table(title, ("Constraint Name","Check Condition"), rows)
            
        # print triggers
        if view.triggers:
            text = text +"<br>" + self.html.heading("Triggers",3) + self.html.anchor("v-trgs")
            for trigger in view.triggers:
                headers = []
                rows = []
                headers.append( "<b> Name: </b>"+trigger.name+"<br>" + self.html.anchor('trg-%s' % trigger.name))
                row = "<pre>"
                #if trigger.nested_column_name:
                #    row = row + "on " + trigger.nested_column_name+"\n"
                #row = row +  trigger.type+ " "+ trigger.event +"\n"
                row = row + 'CREATE TRIGGER ' + trigger.description
                row = row +   trigger.referencing_names+"\n"
                if trigger.when_clause:
                    row = row + "When " + self.html._quotehtml(trigger.when_clause)+"\n"
                row = row +   self.html._quotehtml(trigger.body)+"\n</pre>"
                t = []
                t.append(row)
                rows.append(t)
                text = text + self.html.table(None, headers, rows, '100')+"<p>"
        
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "view-%s.html" % view.name)
        self._write(text, file_name)

    def _print_procedure(self, procedure):
        "print procedure page"
        # create header and context bar
        text = self.html.page_header("Procedure-" + procedure.name)
        local_nav_bar = []
        local_nav_bar.append(("Arguments", "p-args"))
        local_nav_bar.append(("Source", "p-src"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        text = text + self.html.heading(procedure.name, 2)
        
        title = "Arguments:" + self.html.anchor("p-args")
        headers = "Name", "Data Type", "Default Value", "In/Out"
        rows = []
        for argument in procedure.arguments:
            if argument.default_value:
                _default_value = argument.default_value
            else:
                _default_value = ""
            row = argument.name, argument.data_type, self.html._quotehtml(_default_value), argument.in_out
            rows.append(row)
        text = text + self.html.table(title, headers, rows)
        
 #       text = text + self.html.heading("Source:",3) + self.html.anchor("p-src")
 #       text = text + self.html.pre(self.html._quotehtml(procedure.source))
        
        title = "Source" + self.html.anchor("p-src")
        headers = (["Source"])
        rows=[]
        _src=""
        for line in procedure.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
        rows.append([self.html.pre(self.html._quotehtml(_src))])
        text = text + self.html.table(title, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "procedure-%s.html" % procedure.name)
        self._write(text, file_name)        


        
    def _print_procedure_list_page(self):
        print "print procedures list page"
        text = self.html.page_header("Procedures")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for procedure in self.schema.procedures:
            name = self.html.href_to_procedure(procedure.name)
            # add entry to doc index
            self._add_index_entry(procedure.name, name, "procedure")
            rows.append([name])
        headers = ["Name"]
        name = "Procedures"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "procedures-list.html")
        self._write(text, file_name)



    def _print_function(self, function):
        "print function page"
        # create header and context bar
        text = self.html.page_header("Function-" + function.name + " returns " + function.return_data_type)
        local_nav_bar = []
        local_nav_bar.append(("Arguments", "f-args"))
        local_nav_bar.append(("Source", "f-src"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        text = text + self.html.heading(function.name, 2)
        
        title = "Arguments:" + self.html.anchor("f-args")
        headers = "Name", "Data Type", "Default Value", "In/Out"
        rows = []
        for argument in function.arguments:
            if argument.default_value:
                _default_value = argument.default_value
            else:
                _default_value = ""
            row = argument.name, argument.data_type, self.html._quotehtml(_default_value), argument.in_out
            rows.append(row)
        text = text + self.html.table(title, headers, rows)

        text = text + self.html.heading("Returns:",3) + function.return_data_type

        title = "Source" + self.html.anchor("f-src")
        headers = (["Source"])
        rows=[]
        _src=""
        for line in function.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
        rows.append([self.html.pre(self.html._quotehtml(_src))])
        text = text + self.html.table(title, headers, rows)
       
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "function-%s.html" % function.name)
        self._write(text, file_name)

    def _print_function_list_page(self):
        print "print functions list page"
        text = self.html.page_header("Functions")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for function in self.schema.functions:
            name = self.html.href_to_function(function.name)
            # add entry to doc index
            self._add_index_entry(function.name, name, "function")
            row = ([name])
            rows.append(row)
        headers = (["Name"])
        name = "Functions"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "functions-list.html")
        self._write(text, file_name)



    def _print_symbol_index_page(self):
        print "print symbols index page"
        text = self.html.page_header("Schema Objects Index")
        local_nav_bar = []

        keys = self.index.keys()
        keys.sort()
        letter = ""
        for key in keys:
            if (key[:1] != letter):
                letter = key[:1] 
                local_nav_bar.append((letter,letter))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        
        letter = ""
        for key in keys:
            if (key[:1] != letter):
                letter = key[:1]
                text = text + self.html.heading(letter, 3) + self.html.anchor(letter)
            for entry in self.index[key]:
                text = text + '%s %s<br>' % entry
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "symbol-index.html")
        self._write(text, file_name)        
        
    def _print_package(self, package):
        "print procedure page"
        # create header and context bar
        text = self.html.page_header("Package -" + package.name)
        local_nav_bar = []
        local_nav_bar.append(("Package source", "p-src"))
        local_nav_bar.append(("Package body source", "p-bsrc"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.hr()
        text = text + self.html.heading(package.name, 2)
        
        title = "Package source" + self.html.anchor("p-src")
        headers = (["Source"])
        rows=[]
        _src=""
        for line in package.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
        rows.append([self.html.pre(self.html._quotehtml(_src))])
        text = text + self.html.table(title, headers, rows)

        title = "Package body source" + self.html.anchor("p-bsrc")
        headers = (["Source"])
        rows=[]
        _src=""
        if package.body_source:
            for line in package.body_source.source:
                _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
            rows.append([self.html.pre(self.html._quotehtml(_src))])
            text = text + self.html.table(title, headers, rows)


        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "package-%s.html" % package.name)
        self._write(text, file_name)        

    def _print_package_list_page(self):
        print "print packages list page"
        text = self.html.page_header("Packages")
        text = text + self.html.context_bar( None)
        text = text + self.html.hr()
        rows = []
        for package in self.schema.packages:
            name = self.html.href_to_package(package.name)
            # add entry to doc index
            self._add_index_entry(package.name, name, "package")
            row = ([name])
            rows.append(row)
        headers = (["Name"])
        name = "Packages"
        text = text + self.html.table(name, headers, rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "packages-list.html")
        self._write(text, file_name)

    def _sanity_check(self):
        print "print sanity check page"
        text = self.html.page_header("Sanity Check")
        text += self.html.context_bar(None)
        text += self.html.hr()

        scheck = analyze.SchemaAnalyzer(self.schema)
        if scheck.fk_no_indexes:
            text += self.html.heading("No indexes on columns involved in foreign key constraints",2)
            text += ''' You should almost always index foreign keys. The only exception is when
                        the matching unique or primary key is never updated or deleted. For
                        more information take a look on
                        <a href="http://oradoc.photo.net/ora817/DOC/server.817/a76965/c24integ.htm#2299">
                        Concurrency Control, Indexes, and Foreign Keys</a>. <br> The sql file which will
                        generate these indexes is <a href="fk-indexes.sql"> here</a>'''
            
            title = '"Unindexed" foreign keys'
            headers = "Constraint name", "Table Name", "Columns"
            rows = []
            for constraint in scheck.fk_no_indexes:
                row=[]
                row.append( self.html.href_to_table(constraint.table_name))
                row.append( self.html.href_to_constraint(constraint.name, constraint.table_name, constraint.name))
                columns = ''
                columns_count = len(constraint.columns)
                i=0
                for j in constraint.columns.keys():
                    columns += constraint.columns[j]
                    i +=1
                    if i != columns_count:
                        columns += ', '
                row.append(columns)
                rows.append(row)
                #write sql
                file_name = os.path.join(self.doc_dir, "fk-indexes.sql")
                self._write(scheck.fk_no_indexes_sql,file_name)
            text += self.html.table(title,headers,rows)
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "sanity-check.html")
        self._write(text, file_name)
            
    def _write(self, text, file_name):
        debug_message("debug: writing file " + file_name)
        f = open(file_name, 'w')
        f.write(text)
        f.close()

    def _add_index_entry(self, key , link, description):
        t = self.index.get(key)
        if not t:
            self.index[key] = t = []
        t.append((link, description))

    
    
    
if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    import oraschema
    connection = cx_Oracle.connect('aram_v1/aram_v1')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle')
    schema = oraschema.OracleSchema(s)
    doclet = OraSchemaDoclet(schema, "/tmp/oraschemadoc/", "vtr Data Model", "Really cool project")
        
    
