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


from oracleview import OracleView


class OracleMView(OracleView):

    def __init__(self, name, data_dict):
        # FIXME: real inheritance! OracleView.__init__(self, name, data_dict)
        self.name = name
        self.columns = self._get_columns(data_dict)
        self.constraints = self._get_constraints(data_dict)
        self.comments = data_dict.all_table_comments.get(name)
        self.triggers = self._get_triggers(data_dict)
        self.container, self.query, self.mv_updatable = data_dict.all_mviews[name]
        self.text = self.query
