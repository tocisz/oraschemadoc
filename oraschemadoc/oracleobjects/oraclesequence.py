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


class OracleSequence:
    """! \brief Represents Oracle sequence database object"""

    def __init__(self, name, min_value, max_value, step, cycle_flag, ordered, cache_size):
        #debug_message("debug: genarating sequence %s" % name)
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
