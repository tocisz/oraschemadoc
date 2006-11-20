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