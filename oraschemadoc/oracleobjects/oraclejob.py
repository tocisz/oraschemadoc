# Copyright (C) Petr Vanek <petr@yarpen.cz>, 2007
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


class OracleJob:
    """! \brief Represents Oracle job"""

    def __init__(self, job, log_user, priv_user, schema_user,
                 total_time, broken, interval, failures, what):
        self.job = job
        self.log_user = log_user
        self.priv_user = priv_user
        self.schema_user = schema_user
        self.total_time = str(total_time)
        self.broken = broken
        self.interval = interval
        self.failures = str(failures)
        self.what = what


    def getXML(self):
        """get job's metadata in xml"""
        xml_text = '''<job id="job-%s">
                        <job>%s</job>
                        <log_user>%s</log_user>
                        <priv_user>%s</priv_user>
                        <schema_user>%s</schema_user>
                        <total_time>%s</total_time>
                        <broken>%s</broken>
                        <interval>%s</interval>
                        <failures>%s</failures>
                        <what>%s</what>
                      </sequence>''' % (self.job, self.job, self.log_user, self.priv_user,
                                        self.schema_user, self.total_time, self.broken,
                                        self.interval, self.failures, self.what)
        return xml_text 

