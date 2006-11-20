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


class OraclePLSQLSource:
    def __init__(self, source):
        #debug_message("debug: generating plsql source ")
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


class OraclePLSQLSourceLine:

    def __init__(self, line_no, text):
        self.line_no = line_no
        self.text = text
