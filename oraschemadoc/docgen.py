""" Doc Generator """

# Copyright (C) Petr Vanek <petr@yarpen.cz> , 2005
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

__author__ = 'Aram Kananov <arcanan@flashmail.com>, Petr Vanek <petr@yarpen.cz>'

__version__ = '$Version: 0.25'

import os, string, docwidgets, analyze
import sqlhighlighter
import dot

from oraverbose import *


class OraSchemaDoclet:


    def __init__(self, connection, schema, doc_dir, name, description,
                 debug_mode, syntaxHiglighting, css, webEncoding, notNulls):

        set_verbose_mode(debug_mode)

        self.syntaxHighlighter = sqlhighlighter.SqlHighlighter(highlight=syntaxHiglighting)
        self.dotEngine = dot.Dot(doc_dir)

        self.connection = connection

        self.schema = schema
        self.doc_dir = doc_dir
        self.name = name
        self.description = description
        self.html = docwidgets.HtmlWidgets(self.name, css, webEncoding, notNulls)
        self.index = {}

        # print html files
        self._print_index_frames()
        self._print_list_pages()
        self._sanity_check()
        self._print_common_pages()

        #print pages for objects
        print "print tables"
        for table in self.schema.tables:
            self._print_table(table)

        print "print views"
        for view in self.schema.views:
            self._print_view(view)

        print 'print materialized views'
        for mview in self.schema.mviews:
            self._print_mview(mview)

        print "print functions"
        for function in self.schema.functions:
            self._print_function(function)

        print "print procedures"
        for procedure in self.schema.procedures:
            self._print_procedure(procedure)

        print "print packages"
        for package in self.schema.packages:
            self._print_package(package)

        print "print java sources"
        for jsource in self.schema.java_sources:
            self._print_java_source(jsource)

        self._print_symbol_index_page()


    def _print_index_frames(self):
        #
        # print index frames 
        #

        # tables
        rows = []
        for table in self.schema.tables:
            link = self.html.href_to_table(table.name, "Main")
            if table.secondary == 'Yes':
                link = self.html.i(link)
            rows.append(link)
        self._print_index_frame("Tables", rows, "tables-index.html") 

        # indexes
        rows = []
        for index in self.schema.indexes:
            link = self.html.href_to_index(index.name, index.table_name, index.name, "Main")
            rows.append(link)
        self._print_index_frame("Indexes", rows, "indexes-index.html")

        # constraints
        rows = []
        for constraint in self.schema.constraints:
            link = self.html.href_to_constraint(constraint.name, constraint.table_name, constraint.name, "Main")
            rows.append(link)
        self._print_index_frame("Constraints", rows, "constraints-index.html")

        # views
        rows = []
        for view in self.schema.views:
            link = self.html.href_to_view(view.name, "Main")
            rows.append(link)
        self._print_index_frame("Views", rows, "views-index.html")

        # materialized views
        rows = []
        for mview in self.schema.mviews:
            link = self.html.href_to_mview(mview.name, "Main")
            rows.append(link)
        self._print_index_frame("Materialized&nbsp;Views", rows, "mviews-index.html")

        #procedures
        rows = []
        for procedure in self.schema.procedures:
            link = self.html.href_to_procedure(procedure.name, "Main")
            rows.append(link)
        self._print_index_frame("Procedures", rows, "procedures-index.html")

        #functions
        rows = []
        for function in self.schema.functions:
            link = self.html.href_to_function(function.name, "Main")
            rows.append(link)
        self._print_index_frame("Functions", rows, "functions-index.html")

        #packages
        rows = []
        for package in self.schema.packages:
            link = self.html.href_to_package(package.name, "Main")
            rows.append(link)
        self._print_index_frame("Packages", rows, "packages-index.html")

        #triggers
        rows = []
        for trigger in self.schema.triggers:
            link = self.html.href_to_trigger(trigger.name, trigger.table_name, trigger.name, "Main")
            rows.append(link)
        self._print_index_frame("Triggers", rows, "triggers-index.html")

        #sequences
        rows = []
        for sequence in self.schema.sequences:
            link = self.html.href_to_sequence(sequence.getName(), "Main")
            rows.append(link)
        self._print_index_frame("Sequences", rows, "sequences-index.html")

        #java sources
        rows = []
        for jsoursce in self.schema.java_sources:
            link = self.html.href_to_java_source(jsoursce.name, "Main")
            rows.append(link)
        self._print_index_frame("Java Sources", rows, "java-sources-index.html")


    def _print_list_pages(self):
        #
        # print list pages
        #

        #tables
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
        ht_table = self.html.table("Tables", headers, rows)
        self._print_list_page("Tables", ht_table, "tables-list.html")

        #indexes 
        rows = []
        for index in self.schema.indexes:
            name = self.html.href_to_index(index.name, index.table_name, index.name)
            #add entry to do index
            self._add_index_entry(index.name, name, "index on table %s" % index.table_name)
            type = index.type
            table_name = self.html.href_to_table(index.table_name)
            rows.append(( name, type, table_name ))
        headers = "Index", "Type", "Table"
        ht_table = self.html.table("Indexes", headers, rows)
        self._print_list_page("Indexes", ht_table, "indexes-list.html")

        #triggers
        rows = []
        for trigger in self.schema.triggers:
            name = self.html.href_to_trigger(trigger.name, trigger.table_name, trigger.name)
            #add entry to do index
            self._add_index_entry(trigger.name, name, "Trigger on table %s" % trigger.table_name)
            type = trigger.type
            table_name = self.html.href_to_table(trigger.table_name)
            rows.append(( name, type, table_name ))
        headers = "Trigger", "Type", "Table"
        ht_table = self.html.table("Triggers", headers, rows)
        self._print_list_page("Triggers", ht_table, "triggers-list.html")

        #constraints
        rows = []
        for constraint in self.schema.constraints:
            name = self.html.href_to_constraint(constraint.name, constraint.table_name, constraint.name)
            # add entry to doc index
            self._add_index_entry(constraint.name, name, "constraint on table %s" % constraint.table_name)
            type = constraint.type
            table_name = self.html.href_to_table(constraint.table_name)
            rows.append(( name, type, table_name ))
        headers = "Name", "Type", "Table"
        ht_table = self.html.table("Constraints", headers, rows)
        self._print_list_page("Constraints", ht_table, "constraints-list.html")

        #views
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
        ht_table = self.html.table("Views", headers, rows)
        self._print_list_page("Views", ht_table, "views-list.html")

        # mviews
        rows = []
        for mview in self.schema.mviews:
            name = self.html.href_to_mview(mview.name)
            # add entry to doc index
            self._add_index_entry(mview.name, name, "materialized view")
            rows.append([name])
        headers = [("Materialized View")]
        ht_table = self.html.table("Materialized Views", headers, rows)
        self._print_list_page("Materialized Views", ht_table, "mviews-list.html")

        #procedures
        rows = []
        for procedure in self.schema.procedures:
            name = self.html.href_to_procedure(procedure.name)
            # add entry to doc index
            self._add_index_entry(procedure.name, name, "procedure")
            rows.append([name])
        headers = ["Name"]
        ht_table = self.html.table("Procedures", headers, rows)
        self._print_list_page("Procedures", ht_table, "procedures-list.html")

        #functions
        rows = []
        for function in self.schema.functions:
            name = self.html.href_to_function(function.name)
            # add entry to doc index
            self._add_index_entry(function.name, name, "function")
            row = ([name])
            rows.append(row)
        headers = (["Name"])
        ht_table = self.html.table("Functions", headers, rows)
        self._print_list_page("Functions", ht_table, "functions-list.html")

        #packages
        rows = []
        for package in self.schema.packages:
            name = self.html.href_to_package(package.name)
            # add entry to doc index
            self._add_index_entry(package.name, name, "package")
            row = ([name])
            rows.append(row)
        headers = (["Name"])
        ht_table = self.html.table("Packages", headers, rows)
        self._print_list_page("Packages", ht_table, "packages-list.html")

        #sequences
        rows = []
        for s in self.schema.sequences:
            rows.append((s.getName() + self.html.anchor(s.getName()), 
                         s.getMinValue(), s.getMaxValue(), s.getStep(), 
                         s.isCycled(), s.isOrdered(), s.getCacheSize()))
            self._add_index_entry(s.getName(), 
                                  self.html.href_to_sequence(s.getName()), "index")
        headers = "Name", "Min Value", "Max Value", "Step", "Cycled", "Ordered", \
                "Cache Size"
        ht_table = self.html.table("Sequences", headers, rows)
        self._print_list_page("Sequences", ht_table, "sequences.html")

        #java sources 
        rows = []
        for jsource in self.schema.java_sources:
            name = self.html.href_to_java_source(jsource.name)
            self._add_index_entry(jsource.name, name, "java source")
            row = ([name])
            rows.append(row)
        headers = (["Name"])
        ht_table = self.html.table("Java Sources", headers, rows)
        self._print_list_page("Java Sources", ht_table, "java-sources-list.html")


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
        local_nav_bar.append(("Partitions", "t-parts"))

        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.heading(table.name, 2)
        # punt entry in doc index
        self._add_index_entry(table.name, self.html.href_to_table(table.name), "table")
        # print comments
        if table.comments:
            text = text + self.html.heading("Description:",3) + self.html.anchor("t-descr")
            text = text + self.html.p(self.html._quotehtml(table.comments))
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
        #print referential constraints
        if table.referential_constraints:
            title = "Foreign Keys:" + self.html.anchor("t-fk")
            # create an image
            rows = [] # html table
            aList = [] # list for dot image
            for constraint in table.referential_constraints:
                aList.append(constraint.r_table)
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
            if self.dotEngine.haveDot:
                imgname = self.dotEngine.fileGraphList(table.name, aList)
                if imgname != None:
                    try:
                        f = file(os.path.join(self.doc_dir, table.name+'.map'), 'r')
                        text += self.html.imgMap('erdmap', f.read())
                        f.close()
                    except IOError:
                        text = ''
                    text += self.html.img(imgname, htmlMap='erdmap', cssClass='erd')
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
        rows.append(("Tablespace", table.tablespace_name))
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
                text = text + self.html.anchor('trg-%s' % trigger.name)
                trigg = 'CREATE TRIGGER ' + trigger.description
                trigg = trigg + trigger.referencing_names+"\n"
                if trigger.when_clause:
                    trigg = trigg + "When " + trigger.when_clause +"\n"
                trigg = trigg + trigger.body
                self.syntaxHighlighter.setStatement(trigg)
                self.syntaxHighlighter.parse()
                text = text + self.html.pre(self.syntaxHighlighter.getHeader())
                text = text + self.html.pre(self.syntaxHighlighter.getOutput())

        # print partitions
        if table.tab_partitions:
            text = text + self.html.heading("Partitions", 3) + self.html.anchor("t-parts")
            headers = ["Partition name", "Position", "Tablespace name", "High value"]
            rows = []
            for partition in table.tab_partitions:
                rows.append([partition.partition_name, str(partition.partition_position),
                            partition.tablespace_name, str(partition.high_value)])
            text = text + self.html.table(None, headers, rows)

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "table-%s.html" % table.name)
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
        text = text + self.html.heading(view.name, 2)
        # print comments
        if view.comments:
            text = text + self.html.heading("Description:",3) + self.html.anchor("v-descr")
            text = text + self.html.p(self.html._quotehtml(view.comments))
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
        self.syntaxHighlighter.setStatement(view.text)
        self.syntaxHighlighter.parse()
        text = text + self.html.pre(self.syntaxHighlighter.getHeader())
        text = text + self.html.pre(self.syntaxHighlighter.getOutput())
        # print constraints
        if view.constraints:
            title = "Constraints:" + self.html.anchor("v-cc")
            rows = []
            for constraint in view.constraints:
                rows.append((constraint.name + self.html.anchor("cs-%s" % constraint.name),constraint.type))
            text = text + self.html.table(title, ("Constraint Name","Type"), rows)

        # print triggers
        if view.triggers:
            text = text + self.html.heading("Triggers",3) + self.html.anchor("v-trgs")
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
                text = text + self.html.table(None, headers, rows)

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "view-%s.html" % view.name)
        self._write(text, file_name)


    def _print_mview(self, mview):
        " print materialized view"
        text = self.html.page_header("MView-" + mview.name)
        local_nav_bar = []
        local_nav_bar.append(("Description", "v-descr"))
        local_nav_bar.append(("Columns", "v-cols"))
        local_nav_bar.append(("Query", "v-query"))
        local_nav_bar.append(("Constraints", "v-cc"))
        local_nav_bar.append(("Triggers", "v-trgs"))
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.heading(mview.name, 2)

        th = ['Container', 'Updatable']
        container = self.html.href_to_table(mview.container)
        td = [(container, mview.mv_updatable)]
        text = text + self.html.table(None, th, td)
        # print comments
        if mview.comments:
            text = text + self.html.heading("Description:",3) + self.html.anchor("v-descr")
            text = text + self.html.p(self.html._quotehtml(mview.comments))
        #print columns
        rows = []
        for i in range(len(mview.columns)):
            column = mview.columns[i+1]
            # add entry to doc index
            self._add_index_entry(column.name, self.html.href_to_view_column(column.name, mview.name, column.name), \
                                  "column of of view %s" % mview.name)
            rows.append((column.name+self.html.anchor('col-%s' % column.name), column.data_type, column.nullable,\
                         column.insertable, column.updatable, column.deletable, column.comments))
        headers = "Name", "Type", "Nullable","Insertable","Updatable", "Deletable", "Comment"
        text = text + self.html.table("Columns" + self.html.anchor('v-cols'), headers, rows)
        # print query
        text = text + self.html.heading("Query:",3) + self.html.anchor("v-query")
        self.syntaxHighlighter.setStatement(mview.query)
        self.syntaxHighlighter.parse()
        text = text + self.html.pre(self.syntaxHighlighter.getHeader())
        text = text + self.html.pre(self.syntaxHighlighter.getOutput())
        # print constraints
        if mview.constraints:
            title = "Constraints:" + self.html.anchor("v-cc")
            rows = []
            for constraint in mview.constraints:
                rows.append((constraint.name + self.html.anchor("cs-%s" % constraint.name),constraint.type))
            text = text + self.html.table(title, ("Constraint Name","Type"), rows)

        # print triggers
        if mview.triggers:
            text = text + self.html.heading("Triggers",3) + self.html.anchor("v-trgs")
            for trigger in mview.triggers:
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
                text = text + self.html.table(None, headers, rows)

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "mview-%s.html" % mview.name)
        self._write(text, file_name)


    def _print_procedure(self, procedure):
        "print procedure page"
        # create header and context bar
        text = self.html.page_header("Procedure-" + procedure.name)
        local_nav_bar = []
        local_nav_bar.append(("Arguments", "p-args"))
        local_nav_bar.append(("Source", "p-src"))
        text = text + self.html.context_bar(local_nav_bar)
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

        text = text + self.html.heading("Source", 2) + self.html.anchor("p-src")
        _src=""
        for line in procedure.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
        self.syntaxHighlighter.setStatement(_src)
        self.syntaxHighlighter.parse()
        text = text + self.html.pre(self.syntaxHighlighter.getHeader())
        text = text + self.html.pre(self.syntaxHighlighter.getOutput())

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "procedure-%s.html" % procedure.name)
        self._write(text, file_name)        


    def _print_function(self, function):
        "print function page"
        # create header and context bar
        text = self.html.page_header("Function-" + function.name + " returns " + function.return_data_type)
        local_nav_bar = []
        local_nav_bar.append(("Arguments", "f-args"))
        local_nav_bar.append(("Source", "f-src"))
        text = text + self.html.context_bar(local_nav_bar)
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

        text = text + self.html.heading("Source", 2) + self.html.anchor("f-src")

        _src=""
        for line in function.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
        self.syntaxHighlighter.setStatement(_src)
        self.syntaxHighlighter.parse()
        text = text + self.html.pre(self.syntaxHighlighter.getHeader())        
        text = text + self.html.pre(self.syntaxHighlighter.getOutput())

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "function-%s.html" % function.name)
        self._write(text, file_name)


    def _print_java_source(self, java_source):
        "print function page"
        # create header and context bar
        text = self.html.page_header("Source of " + java_source.name + " class")
        local_nav_bar = []
        text = text + self.html.context_bar(local_nav_bar)
        text = text + self.html.heading(java_source.name, 2)

        title = "Source" 
        headers = (["Source"])
        rows=[]
        _src=""
        for line in java_source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " 
            # in java source empty string is None, so need to check before adding text
            if line.text:
                _src = _src +  line.text
            _src = _src + "\n"
        rows.append([self.html.pre(self.html._quotehtml(_src))])
        text = text + self.html.table(title, headers, rows)

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "java-source-%s.html" % java_source.name.replace("/", "-"))
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
        text = text + self.html.heading(package.name, 2)

        title = self.html.heading("Package source", 2) + self.html.anchor("p-src")
        _src=""
        for line in package.source.source:
            _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text

        self.syntaxHighlighter.setStatement(_src)
        self.syntaxHighlighter.parse()
        text = text + title + self.html.pre(self.syntaxHighlighter.getHeader())
        text = text + self.html.pre(self.syntaxHighlighter.getOutput())

        title = self.html.heading("Package body source", 2) + self.html.anchor("p-bsrc")
        _src=""
        if package.body_source:
            for line in package.body_source.source:
                _src = _src + string.rjust(str(line.line_no),6) + ": " +  line.text
            self.syntaxHighlighter.setStatement(_src)
            self.syntaxHighlighter.parse()
            text = text + title + self.html.pre(self.syntaxHighlighter.getHeader())
            text = text + self.html.pre(self.syntaxHighlighter.getOutput())

        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "package-%s.html" % package.name)
        self._write(text, file_name)        


    def _sanity_check(self):
        print "print sanity check page"
        problems = False
        text = self.html.page_header("Sanity Check")
        local_nav_bar = []
        local_nav_bar.append(("FK indexes", "fk-ix"))
        local_nav_bar.append(("Invalid objects", "inv"))
        text += self.html.context_bar(local_nav_bar)

        text += self.html.heading("Sanity Check", 1)

        scheck = analyze.SchemaAnalyzer(self.connection, self.schema)
        if scheck.fk_no_indexes:
            text += self.html.anchor("fk-ix")
            text += self.html.heading("No indexes on columns involved in foreign key constraints",2)
            text += '''<p>You should almost always index foreign keys. The only exception is when
                        the matching unique or primary key is never updated or deleted. For
                        more information take a look on
                        <a href="http://oradoc.photo.net/ora817/DOC/server.817/a76965/c24integ.htm#2299">
                        Concurrency Control, Indexes, and Foreign Keys</a>.</p>
                        <p>The sql file which will
                        generate these indexes is <a href="fk-indexes.sql">created for you</a></p>'''

            title = '"Unindexed" foreign keys'
            headers = "Table Name", "Constraint name", "Columns"
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
            problems = True

        if len(scheck.invalids) != 0:
            problems = True
            text += self.html.anchor("inv")
            text += self.html.heading('Invalid objects', 2)
            text += '''<p>Invalid object does not mean a problem sometimes. Sometimes will 
                    fix itself as is is executed or accessed.  But if there is an error in
                    USER_ERRORS table, you are in trouble then...</p>
                    <p>The sql file which will compile these objects is 
                    <a href="compile-objects.sql">created for you</a>.</p>'''
            self._write(scheck.invalids_sql, os.path.join(self.doc_dir, 'compile-objects.sql'))
            invalids = scheck.invalids
            for i in invalids:
                if i[1] == 'PACKAGE' or i[1] == 'PACKAGE BODY':
                    i[0] = self.html.href_to_package(i[0])
                if i[1] == 'PROCEDURE':
                    i[0] = self.html.href_to_procedure(i[0])
                if i[1] == 'FUNCTION':
                    i[0] = self.html.href_to_function(i[0])
                if i[1] == 'VIEW':
                    i[0] = self.html.href_to_view(i[0])
                if i[1] == 'TRIGGER':
                    for j in self.schema.triggers:
                        if j.name == i[0]:
                            i[0] = self.html.href_to_trigger(i[0], j.table_name, i[0])
                            break
            text += self.html.table('Invalids', ['Object name', 'Type', 'Error', 'At line'], invalids)

        if problems == False:
            # no checks
            text += self.html.p('No known problems.')
        text = text + self.html.page_footer()
        file_name = os.path.join(self.doc_dir, "sanity-check.html")
        self._write(text, file_name)


    def _write(self, text, file_name):
        # write file to fs
        debug_message("debug: writing file %s" % file_name)
        f = open(file_name, 'w')
        f.write(text)
        f.close()


    def _add_index_entry(self, key , link, description):
        # add new entry to symbol index
        t = self.index.get(key)
        if not t:
            self.index[key] = t = []
        t.append((link, description))


    def _print_common_pages(self):
        # print index.html, nav.html and main.html
        text = self.html._index_page(self.name)
        file_name = os.path.join(self.doc_dir, "index.html")
        self._write(text, file_name)
        text = self.html._global_nav_frame(self.name)
        file_name = os.path.join(self.doc_dir, "nav.html")
        self._write(text, file_name)
        # er diagram
        imgname = None
        if self.dotEngine.haveDot:
            erdDict = {}
            for table in self.schema.tables:
                refs = []
                if table.referential_constraints:
                    for ref in table.referential_constraints:
                        refs.append(ref.r_table)
                erdDict[table.name] = refs
            imgname = self.dotEngine.fileGraphDict(erdDict)
            if imgname != None:
                try:
                    f = file(os.path.join(self.doc_dir, 'main.map'), 'r')
                    text = self.html.imgMap('mainmap', f.read())
                    f.close()
                    os.remove(os.path.join(self.doc_dir, 'main.map'))
                except IOError:
                    text = ''
                    print 'error reading main.map GraphViz file'
                imgname = text + self.html.img(imgname, htmlMap='mainmap', cssClass='erd')

        text = self.html._main_frame(self.name, self.description, self.syntaxHighlighter.highlight, imgname)
        file_name = os.path.join(self.doc_dir, "main.html")
        self._write(text, file_name)


    def _print_index_frame(self, header, item_list, file_name):
        # generic procedure to print index frame on left side
        # excpects:
        #          header    - title string, i.e "Tables"
        #          item_list - list of names with html links
        #          file_name - relative file name 
        print "index frame for %s" % header
        text = self.html.frame_header(header)
        text = text + self.html.href('nav.html', 'Categories')
        for row in item_list:
            text = text + row
        text = text + self.html.frame_footer()
        #java sources contain simbol / inside name, in file_names should be replaced with "-"
        f_name = os.path.join(self.doc_dir, file_name.replace("/","-"))
        self._write(text, f_name)


    def _print_list_page(self, title, ht_table, file_name):
        # print list pages
        print "print %s list page" % title
        text = self.html.page_header(title)
        text = text + self.html.context_bar( None)
        text = text + ht_table
        text = text + self.html.page_footer()

        file_name = os.path.join(self.doc_dir, file_name.replace("/", "-"))
        self._write(text, file_name)


if __name__ == '__main__':
    import cx_Oracle
    import orasdict
    import oraschema
    connection = cx_Oracle.connect('aram_v1/aram_v1')
    s = orasdict.OraSchemaDataDictionary(connection, 'Oracle')
    schema = oraschema.OracleSchema(s)
    doclet = OraSchemaDoclet(schema, "/tmp/oraschemadoc/", "vtr Data Model", "Really cool project")

