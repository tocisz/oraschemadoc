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
