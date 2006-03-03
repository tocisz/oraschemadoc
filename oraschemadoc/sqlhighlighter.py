""" This module performs simple Oracle PL/SQL syntax highlighting.
It takes sql statement and produces colorized XHTML output (spanned).

"""

# Copyright (C) Petr Vanek <petr@scribus.info>, 2005
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


import string
import re


""" States of the parser """
WHITESPACE = 0
LINECOMMENT = 1
MULTICOMMENT = 2
KEYWORD = 3
NUMBER = 4
RESERVERD = 5
STRING = 6


keyWords = {
'ALL':RESERVERD, 'ALTER':RESERVERD, 'AND':RESERVERD, 'ANY':RESERVERD, 'ARRAY':RESERVERD, 'ARROW':RESERVERD, 'AS':RESERVERD, 'ASC':RESERVERD, 'AT':RESERVERD,
'BEGIN':RESERVERD, 'BETWEEN':RESERVERD, 'BY':RESERVERD,
'CASE':RESERVERD, 'CHECK':RESERVERD, 'CLUSTERS':RESERVERD, 'CLUSTER':RESERVERD, 'COLAUTH':RESERVERD, 'COLUMNS':RESERVERD, 'COMPRESS':RESERVERD, 'CONNECT':RESERVERD,
'CRASH':RESERVERD, 'CREATE':RESERVERD, 'CURRENT':RESERVERD,
'DECIMAL':RESERVERD, 'DECLARE':RESERVERD, 'DEFAULT':RESERVERD, 'DELETE':RESERVERD, 'DESC':RESERVERD, 'DISTINCT':RESERVERD, 'DROP':RESERVERD,
'ELSE':RESERVERD, 'END':RESERVERD, 'EXCEPTION':RESERVERD, 'EXCLUSIVE':RESERVERD, 'EXISTS'
'FETCH':RESERVERD, 'FORM':RESERVERD, 'FOR':RESERVERD, 'FROM':RESERVERD,
'GOTO':RESERVERD, 'GRANT':RESERVERD, 'GROUP':RESERVERD,
'HAVING':RESERVERD,
'IDENTIFIED':RESERVERD, 'IF':RESERVERD, 'IN':RESERVERD, 'INDEXES':RESERVERD, 'INDEX':RESERVERD, 'INSERT':RESERVERD, 'INTERSECT':RESERVERD, 'INTO':RESERVERD, 'IS':RESERVERD,
'LIKE':RESERVERD, 'LOCK':RESERVERD,
'MINUS':RESERVERD, 'MODE':RESERVERD,
'NOCOMPRESS':RESERVERD, 'NOT':RESERVERD, 'NOWAIT':RESERVERD, 'NULL':RESERVERD,
'OF':RESERVERD, 'ON':RESERVERD, 'OPTION':RESERVERD, 'OR':RESERVERD, 'ORDER':RESERVERD, 'OVERLAPS':RESERVERD,
'PRIOR':RESERVERD, 'PROCEDURE':RESERVERD, 'PUBLIC':RESERVERD,
'RANGE':RESERVERD, 'RECORD':RESERVERD, 'RESOURCE':RESERVERD, 'REVOKE':RESERVERD,
'SELECT':RESERVERD, 'SHARE':RESERVERD, 'SIZE':RESERVERD, 'SQL':RESERVERD, 'START':RESERVERD, 'SUBTYPE':RESERVERD,
'TABAUTH':RESERVERD, 'TABLE':RESERVERD, 'THEN':RESERVERD, 'TO':RESERVERD, 'TYPE':RESERVERD,
'UNION':RESERVERD, 'UNIQUE':RESERVERD, 'UPDATE':RESERVERD, 'USE':RESERVERD,
'VALUES':RESERVERD, 'VIEW':RESERVERD, 'VIEWS':RESERVERD,
'WHEN':RESERVERD, 'WHERE':RESERVERD, 'WITH':RESERVERD,
'A':KEYWORD, 'ADD':KEYWORD, 'AGENT':KEYWORD, 'AGGREGATE':KEYWORD, 'ARRAY':KEYWORD, 'ATTRIBUTE':KEYWORD, 'AUTHID':KEYWORD, 'AVG':KEYWORD,
'BFILE_BASE':KEYWORD, 'BINARY':KEYWORD, 'BLOB_BASE':KEYWORD, 'BLOCK':KEYWORD, 'BODY':KEYWORD, 'BOTH':KEYWORD, 'BOUND':KEYWORD, 'BULK':KEYWORD, 'BYTE':KEYWORD,
'C':KEYWORD, 'CALL':KEYWORD, 'CALLING':KEYWORD, 'CASCADE':KEYWORD, 'CHAR':KEYWORD, 'CHAR_BASE':KEYWORD, 'CHARACTER':KEYWORD, 'CHARSETFORM':KEYWORD, 'CHARSETID':KEYWORD,
'CHARSET':KEYWORD, 'CLOB_BASE':KEYWORD, 'CLOSE':KEYWORD, 'COLLECT':KEYWORD, 'COMMENT':KEYWORD, 'COMMIT':KEYWORD, 'COMMITTED':KEYWORD, 'COMPILED':KEYWORD,
'CONSTANT':KEYWORD, 'CONSTRUCTOR':KEYWORD, 'CONTEXT':KEYWORD, 'CONVERT':KEYWORD, 'COUNT':KEYWORD, 'CURSOR':KEYWORD, 'CUSTOMDATUM':KEYWORD,
'DANGLING':KEYWORD, 'DATA':KEYWORD, 'DATE':KEYWORD, 'DATE_BASE':KEYWORD, 'DAY':KEYWORD, 'DEFINE':KEYWORD, 'DETERMINISTIC':KEYWORD, 'DOUBLE':KEYWORD, 'DURATION':KEYWORD,
'ELEMENT':KEYWORD, 'ELSIF':KEYWORD, 'EMPTY':KEYWORD, 'ESCAPE':KEYWORD, 'EXCEPT':KEYWORD, 'EXCEPTIONS':KEYWORD, 'EXECUTE':KEYWORD, 'EXIT':KEYWORD, 'EXTERNAL':KEYWORD,
'FINAL':KEYWORD, 'FIXED':KEYWORD, 'FLOAT':KEYWORD, 'FORALL':KEYWORD, 'FORCE':KEYWORD, 'FUNCTION':KEYWORD,
'GENERAL':KEYWORD,
'HASH':KEYWORD, 'HEAP':KEYWORD, 'HIDDEN':KEYWORD, 'HOUR':KEYWORD,
'IMMEDIATE':KEYWORD, 'INCLUDING':KEYWORD, 'INDICATOR':KEYWORD, 'INDICES':KEYWORD, 'INFINITE':KEYWORD, 'INSTANTIABLE':KEYWORD, 'INT':KEYWORD,
'INTERFACE':KEYWORD, 'INTERVAL':KEYWORD, 'INVALIDATE':KEYWORD, 'ISOLATION':KEYWORD,
'JAVA':KEYWORD,
'LANGUAGE':KEYWORD, 'LARGE':KEYWORD, 'LEADING':KEYWORD, 'LENGTH':KEYWORD, 'LEVEL':KEYWORD, 'LIBRARY':KEYWORD, 'LIKE2':KEYWORD, 'LIKE4':KEYWORD, 'LIKEC':KEYWORD,
'LIMIT':KEYWORD, 'LIMITED':KEYWORD, 'LOCAL':KEYWORD, 'LONG':KEYWORD, 'LOOP':KEYWORD,
'MAP':KEYWORD, 'MAX':KEYWORD, 'MAXLEN':KEYWORD, 'MEMBER':KEYWORD, 'MERGE':KEYWORD, 'MIN':KEYWORD, 'MINUTE':KEYWORD, 'MOD':KEYWORD, 'MODIFY':KEYWORD, 'MONTH':KEYWORD, 'MULTISET':KEYWORD,
'NAME':KEYWORD, 'NAN':KEYWORD, 'NATIONAL':KEYWORD, 'NATIVE':KEYWORD, 'NCHAR':KEYWORD, 'NEW':KEYWORD, 'NOCOPY':KEYWORD, 'NUMBER_BASE':KEYWORD,
'OBJECT':KEYWORD, 'OCICOLL':KEYWORD, 'OCIDATETIME':KEYWORD, 'OCIDATE':KEYWORD, 'OCIDURATION':KEYWORD, 'OCIINTERVAL':KEYWORD, 'OCILOBLOCATOR':KEYWORD,
'OCINUMBER':KEYWORD, 'OCIRAW':KEYWORD, 'OCIREFCURSOR':KEYWORD, 'OCIREF':KEYWORD, 'OCIROWID':KEYWORD, 'OCISTRING':KEYWORD, 'OCITYPE':KEYWORD, 'ONLY':KEYWORD,
'OPAQUE':KEYWORD, 'OPEN':KEYWORD, 'OPERATOR':KEYWORD, 'ORACLE':KEYWORD, 'ORADATA':KEYWORD, 'ORGANIZATION':KEYWORD, 'ORLANY':KEYWORD, 'ORLVARY':KEYWORD,
'OTHERS':KEYWORD, 'OUT':KEYWORD, 'OVERRIDING':KEYWORD,
'PACKAGE':KEYWORD, 'PARALLEL_ENABLE':KEYWORD, 'PARAMETER':KEYWORD, 'PARAMETERS':KEYWORD, 'PARTITION':KEYWORD, 'PASCAL':KEYWORD, 'PIPE':KEYWORD,
'PIPELINED':KEYWORD, 'PRAGMA':KEYWORD, 'PRECISION':KEYWORD, 'PRIVATE':KEYWORD,
'RAISE':KEYWORD, 'RANGE':KEYWORD, 'RAW':KEYWORD, 'READ':KEYWORD, 'RECORD':KEYWORD, 'REF':KEYWORD, 'REFERENCE':KEYWORD, 'REM':KEYWORD, 'REMAINDER':KEYWORD,
'RENAME':KEYWORD, 'RESULT':KEYWORD, 'RETURN':KEYWORD, 'RETURNING':KEYWORD, 'REVERSE':KEYWORD, 'ROLLBACK':KEYWORD, 'ROW':KEYWORD,
'SAMPLE':KEYWORD, 'SAVE':KEYWORD, 'SAVEPOINT':KEYWORD, 'SB1':KEYWORD, 'SB2':KEYWORD, 'SB4':KEYWORD, 'SECOND':KEYWORD, 'SEGMENT':KEYWORD, 'SELF':KEYWORD,
'SEPARATE':KEYWORD, 'SEQUENCE':KEYWORD, 'SERIALIZABLE':KEYWORD, 'SET':KEYWORD, 'SHORT':KEYWORD, 'SIZE_T':KEYWORD, 'SOME':KEYWORD, 'SPARSE':KEYWORD,
'SQLCODE':KEYWORD, 'SQLDATA':KEYWORD, 'SQLNAME':KEYWORD, 'SQLSTATE':KEYWORD, 'STANDARD':KEYWORD, 'STATIC':KEYWORD, 'STDDEV':KEYWORD, 'STORED':KEYWORD,
'STRING':KEYWORD, 'STRUCT':KEYWORD, 'STYLE':KEYWORD, 'SUBMULTISET':KEYWORD, 'SUBPARTITION':KEYWORD, 'SUBSTITUTABLE':KEYWORD, 'SUBTYPE':KEYWORD,
'SUM':KEYWORD, 'SYNONYM':KEYWORD,
'TDO':KEYWORD, 'THE':KEYWORD, 'TIME':KEYWORD, 'TIMESTAMP':KEYWORD, 'TIMEZONE_ABBR':KEYWORD, 'TIMEZONE_HOUR':KEYWORD, 'TIMEZONE_MINUTE':KEYWORD,
'TIMEZONE_REGION':KEYWORD, 'TRAILING':KEYWORD, 'TRANSAC':KEYWORD, 'TRANSACTIONAL':KEYWORD, 'TRUSTED':KEYWORD, 'TYPE':KEYWORD,
'UB1':KEYWORD, 'UB2':KEYWORD, 'UB4':KEYWORD, 'UNDER':KEYWORD, 'UNSIGNED':KEYWORD, 'UNTRUSTED':KEYWORD, 'USE':KEYWORD, 'USING':KEYWORD,
'VALIST':KEYWORD, 'VALUE':KEYWORD, 'VARIABLE':KEYWORD, 'VARIANCE':KEYWORD, 'VARRAY':KEYWORD, 'VARYING':KEYWORD, 'VOID':KEYWORD,
'WHILE':KEYWORD, 'WORK':KEYWORD, 'WRAPPED':KEYWORD, 'WRITE':KEYWORD,
'YEAR':KEYWORD,
'ZONE':KEYWORD
}


class SqlHighlighter:
    """ SQL syntax highlighter """

    def __init__(self, sql='', highlight=True):
        """ Highlighting is very slow novadays.
        Optional parameter sql is highlighted statement.
        Call parse() to start highlighting.
        Parameter highlight: True=do syntax highlighting, False=without highlighting.
        """
        self.setStatement(sql)
        self.highlight = highlight


    def setHighlight(self, highlight=True):
        self.highlight = highlight


    def setStatementList(self, sql):
        """ Set statement as string from list"""
        self.sqlStatement = string.join(sql, '\n')


    def setStatement(self, sql):
        """ Provide sql statement to the class instance.
        It resets instance to the 'beginning' state too."""
        self.sqlStatement = sql
        self.status = WHITESPACE
        self.outputString = ''


    def getOutput(self):
        """ Returns the result aftre parsing """
        return self.outputString


    def getOutputList(self):
        """ Returns the text in list"""
        return string.split(self.outputString, '\n')

    def getHeader(self, block=False):
        """ Get simple HTML legend.
        If is block set to True, it's used with <br/>"""
        if self.highlight == False:
            return 'Note: Syntax highlighting off'
            return
        if block:
            br = '<br/>'
        else:
            br = ' '
        return 'Legend:' + br \
                + '<span class="comment">comment</span>' + br \
                + '<span class="string">string</span>' + br \
                + '<span class="keyword">keyword</span>' + br \
                + '<span class="reserved">reserved word</span>' + br \
                + '<span class="operator">operator</span>'


    def parse(self, sql=None):
        """ Start parsing with given statement (parameter sql) or
        with statement previously given."""
        if sql != None:
            self.setStatement(sql)
        if self.highlight == False:
            self.outputString = self.sqlStatement
            return
        for i in string.split(self.sqlStatement, '\n'):
            self._parseLine(i)
            self.outputString += '\n'


    def _parseLine(self, line):
        """ Private method. It parses one line.
        It walks through one line/string. It takes current character,
        the it compares it for comments, strings etc. conditions - then
        it sets new state of the parser.
        Serching keywords provides regular expression for single word
        finding. It's compared with keywords and resreved words lists
        (at the top of this file)."""
        i = -1
        while (i + 1) < len(line):
            i += 1
            # current character
            ch = line[i]
            # character +1
            try:
                ch1 = line[i+1]
            except:
                ch1 = ''
            # character -1
            try:
                ch2 = line[i-1]
            except:
                ch2 = ''
               

            # string handling 'foo'
            if self.status == WHITESPACE and ch == '\'':
                self.status = STRING
                self.outputString += '<span class="string">' + ch
                continue
            if self.status == STRING and ch == '\'':
                self.status = WHITESPACE
                self.outputString += ch + '</span>'
                continue
            # line comment --foo
            # rest of the line is comment
            if self.status == WHITESPACE and ch == '-' and ch1 == '-':
                self.outputString += '<span class="comment">' + line[i:] + '</span>'
                break
            # multiline comment
            if self.status == WHITESPACE and ch == '/' and ch1 == '*':
                self.status = MULTICOMMENT
                self.outputString += '<span class="comment">' + ch
                continue
            if self.status == MULTICOMMENT and ch == '/' and ch2 == '*':
                self.status = WHITESPACE
                self.outputString += ch + '</span>'
                continue
            # space ' ' to prevent keyword right regexp
            if self.status == WHITESPACE and ch == ' ':
                self.outputString += ch;
                continue
            # html
            if self.status == WHITESPACE and ch == '<':
                self.outputString += '<span class="operator">&lt;</span>'
                continue
            if self.status == WHITESPACE and ch == '>':
                self.outputString += '<span class="operator">&gt;</span>'
                continue
            # operators
            # ; removed due the speed-up
            if ch in ['>','<','(', ')', ':', '=', '%', '.', ',', '/', '*', '!', '|'] and self.status == WHITESPACE:
            	if ch == '<':
                    self.outputString += '<span class="operator">&lt;</span>'
                elif ch == '>':
                	self.outputString += '<span class="operator">&gt;</span>'                	
                else:
                	self.outputString += '<span class="operator">' + ch + '</span>'
                continue
            if ch == ';' and self.status == WHITESPACE:
                self.outputString += ch
            # aaagrh. killall tab users
            if ch == '\t' and self.status == WHITESPACE:
                self.outputString += ch
            # keywords and reserved words
            if self.status == WHITESPACE:
                words = re.split(r'\W+', line[i:])
                current = words[0].upper()
                if len(current) == 0:
                    continue
                if keyWords.has_key(current):
                    if keyWords[current] ==  KEYWORD:
                        self.outputString += '<span class="keyword">' + words[0] + '</span>'
                    else:
                        self.outputString += '<span class="reserved">' + words[0] + '</span>'
                    i += len(current) - 1
                    continue
                self.outputString += words[0]
                i += len(words[0]) - 1
                continue
            # none condition - just put character to the output
            self.outputString += ch


# unit test
if (__name__ == '__main__'):
    sql = """
FUNCTION numbers_only(
   	v_string                         	VARCHAR2)
 	RETURN INTEGER
 IS
   	d_length                        	NUMBER;
   	/*d_current							CHAR(1);
   	d_ascii                 		  	NUMBER; 
    */
 BEGIN
   --d_length := LENGTH(v_string);
   a := 8888 6666;
   FOR i IN 1 .. d_length LOOP
   	d_current := SUBSTR(v_string, i, 1);
 	IF (d_current NOT IN ('0','1','2','3','4','5','6','7','8','9')) THEN
 	  RETURN 1;
 	END IF;
    if 1 > 0 then
        null;
    end if;
   END LOOP;
   RETURN 0;
 END;
 """
    
    print """
    <html><head><title> Constraints </title>
                    <link rel="stylesheet" type="text/css" href="../oraschemadoc.css">
                    </head><body>
<pre>"""
    s = SqlHighlighter(sql, highlight=True)
    s.parse()
    print s.getHeader(block=True)
    print s.outputString
    print """</pre>
</body>
</html>"""

