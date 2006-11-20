# Copyright (C) Petr Vanek <petr@yarpen.cz>, 2005
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

__author__ = 'Petr Vanek, <petr@yarpen.cz>'


class OracleTabPartition:

    def __init__(self, partition_position, partition_name, tablespace_name, high_value):
        self.partition_position = partition_position
        self.partition_name = partition_name
        self.tablespace_name = tablespace_name
        self.high_value = high_value
