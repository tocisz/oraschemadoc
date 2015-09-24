""" Create a DDL script of the objects """

# Copyright (C) Petr Vanek, <petr@scribus.info>, 2005
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

__author__ = 'Petr Vanek <petr@scribus.info>'


import cx_Oracle
import os.path
import os
import time
import re


class OraDDLSource:
    """ Obtaining the DDL script depends on the DBMS_METADATA package.
        So it's limited only for version 9 and greater and for users
        with EXECUTE privilege on this package.
        When it cannot be found there is only a message written. """

    def __init__(self, conn, allowDLL, outputDir='.'):
        self.connection = conn
        self.enabled = self.checkForMetadata()
        self.fname = None
        self.directory = os.path.join(outputDir, 'sql_sources')
        self.rootDir = outputDir
        self.scriptCache = {}
        self.censorshipPatterns = {
            'SEQUENCE': [re.compile(r'START WITH [0-9]+ *')],
            'TABLE': [re.compile(r'[(]?PARTITION ".*"( *VALUES LESS THAN \(.*\)|) *(,|\)) *\n? *')]
        }
        if not self.mkdir(self.directory):
            self.enabled = False
        # disable DLL generators - but the previous stuff
        # is required to be set
        if not allowDLL:
            self.enabled = False
        cur = conn.cursor()
        print "db transform params init"
        cur.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, :sa, false);END;", {'sa': 'SEGMENT_ATTRIBUTES'})
        cur.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, :caa, true);END;", {'caa': 'CONSTRAINTS_AS_ALTER'})
        cur.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, :ste, true);END;", {'ste': 'SQLTERMINATOR'})
        cur.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, :str, false);END;", {'str': 'STORAGE'})
        cur.close()

    def censor(self, objType, text):
        if objType in self.censorshipPatterns:
            masks = self.censorshipPatterns[objType]
            for regex in masks:
                text = regex.sub('', text)
        return text


    def mkdir(self, dirname):
        if os.path.isdir(dirname):
            return True
        try:
            os.mkdir(dirname)
            return True
        except:
            return False
            print 'WARNING: cannot create directory %s' % outputDir
            print 'WARNING: DDL script creation is disabled'


    def checkForMetadata(self):
        print 'Checking for DDL scripts creating availability'
        res = self.query("""select count(1)
                        from all_tab_privs
                        where table_name = 'DBMS_METADATA'
                            and privilege = 'EXECUTE'
                            --and grantee in ('PUBLIC', 'S0')
                            """)
        if res[0][0] > 0:
            print 'DBMS_METADATA found\n'
            return True
        print 'WARNING: No EXECUTE grant on DBMS_METADATA (>8) or feature disabled (8)'
        return False



    def getCommentsForTables(self, ddl, tabName):

        def sqlEscape(str):
            return str.replace("'", "''");

        ownerStrip = tabName.find('.')
        if ownerStrip != -1:
            splitName = tabName.split('.')
            par = {'name': splitName[1], 'schema': splitName[0]}
            sql1 = "select comments from dba_tab_comments where comments is not null and table_name = :name and owner = :schema"
            sql2 = "select column_name, comments from dba_col_comments where comments is not null and table_name = :name and owner = :schema"
        else:
            par = {'name': tabName}
            sql1 = "select comments from user_tab_comments where comments is not null and table_name = :name"
            sql2 = "select column_name, comments from user_col_comments where comments is not null and table_name = :name"

        rows = self.query(sql1, par)
        for row in rows:
            ddl.append("\n  COMMENT ON TABLE " + tabName + " IS '" + sqlEscape(row[0]) + "';")

        rows = self.query(sql2, par)
        for row in rows:
            ddl.append("\n  COMMENT ON COLUMN " + tabName + "." + row[0] + " IS '" + sqlEscape(row[1]) + "';")

    def getDDLScript(self, objType, objName):

        def fetchRows(ddl, cursor):
            row = cursor.fetchone()
            while row:
                ddl.append(row[0].read())
                try:
                    row = cursor.next()
                except StopIteration:
                    break

        if not self.enabled or self.directory == None:
            return None
        if self.scriptCache.has_key(objName):
            return
        ownerStrip = objName.find('.')
        if ownerStrip != -1:
            splitName = objName.split('.')
            par = {'type': objType, 'name': splitName[1], 'schema': splitName[0]}
            sql = "select dbms_metadata.get_ddl(:type, :name, :schema) from dual"
        else:
            par = {'type': objType, 'name': objName}
            sql = "select dbms_metadata.get_ddl(:type, :name) from dual"
        try:
            # CLOBS cannot be fetchall()ed!
            cur = self.connection.cursor()
            cur.execute(sql, par)
            ddl = []
            fetchRows(ddl, cur)

            if objType == 'TABLE':
                self.getCommentsForTables(ddl, objName)
        except cx_Oracle.DatabaseError, e:
            print 'ERROR: DDL creation is inconsistent for: %s' % (par['name'])
            print '       %s' % e.__str__()[:e.__str__().find('\n')]
            return None

        try:
            if(objType in ['TABLE', 'VIEW', 'SEQUENCE', 'PROCEDURE']):
                if ownerStrip != -1:
                    par = {'obj': 'OBJECT_GRANT', 'name': splitName[1], 'schema': splitName[0]}
                    sql = "select dbms_metadata.get_dependent_ddl(:obj, :name, :schema) from dual"
                else:
                    par = {'obj': 'OBJECT_GRANT', 'name': objName}
                    sql = "select dbms_metadata.get_dependent_ddl(:obj, :name) from dual"
                cur = self.connection.cursor()
                cur.execute(sql, par)
                fetchRows(ddl, cur)

        except cx_Oracle.DatabaseError, e:
            print 'WARNING: no grants information available for: %s' % (par['name'])

        # remove unwanted information
        ddl = map(lambda txt: self.censor(objType, txt), ddl)

        self.fname = '%s.sql' % objName.lower()
        currentDir = os.path.join(self.directory, objType.replace(' ', '_').lower())
        if not self.mkdir(currentDir):
            self.enabled = False
            return None
        f = file(os.path.join(currentDir, self.fname), 'w')
        f.write('-- created by Oraschemadoc %s\n' % time.ctime())
        f.write('-- visit http://www.yarpen.cz/oraschemadoc/ for more info\n')
        f.write(''.join(ddl))
        f.write('\n')
        f.close()
        strippedName = os.path.join(currentDir, self.fname)[len(self.rootDir)+1:]
        self.scriptCache[objName] = strippedName
        return strippedName


    def query(self, statement, params={}):
        cur = self.connection.cursor()
        cur.execute(statement, params)
        results = cur.fetchall()
        cur.close()
        return results


# unit tests are for losers...
if __name__ == '__main__':
    c = cx_Oracle.connect('s0/asgaard')
    o = OraDDLSource(conn=c)#, outputDir='./foo')
    print o.getDDLScript('TABLE', 'ENCODING')
    print o.getDDLScript('TABLE', 'ENCODIN')
    print o.getDDLScript('FOO', 'TABLE2')
