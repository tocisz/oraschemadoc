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

__version__ = '$Revision$'

import cx_Oracle
import os.path
import os
import time


class OraDDLSource:
    """ Obtaining the DDL script depends on the DBMS_METADATA package.
        So it's limited only for version 9 and greater and for users
        with EXECUTE privilege on this package.
        When it cannot be found there is only a message written. """

    def __init__(self, conn, outputDir='sql_sources'):
        self.connection = conn
        self.enabled = self.checkForMetadata()
        self.fname = None
        self.directory = None
        if self.mkdir(outputDir):
            self.directory = outputDir
        else:
            self.enabled = False


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
        print 'WARNING: No EXECUTE grant on DBMS_METADATA (>9) or feature disabled (8)'
        return False


    def getDDLScript(self, objType, objName):
        if not self.enabled or self.directory == None:
            return False
        par = {'type': objType, 'name': objName}
        try:
            ddl = self.query(statement="select to_char(dbms_metadata.get_ddl(:type, :name)) from dual",
                         params=par)[0][0]
        except cx_Oracle.DatabaseError, e:
            print 'ERROR: DDL creation is inconsistent'
            print '       %s' % e.__str__()[:e.__str__().find('\n')]
            return False
        self.fname = '%s.sql' % objName.lower()
        currentDir = os.path.join(self.directory, objType.replace(' ', '_').lower())
        if not self.mkdir(currentDir):
            self.enabled = False
            return
        f = file(os.path.join(currentDir, self.fname), 'w')
        f.write('-- created by Oraschemadoc %s\n' % time.ctime())
        f.write(ddl.strip())
        f.write('\n/\n')
        f.close()
        return True


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
    o.getDDLScript('TABLE', 'ENCODING')
    #o.getDDLScript('TABLE', 'ENCODIN')
    #o.getDDLScript('FOO', 'TABLE2')
