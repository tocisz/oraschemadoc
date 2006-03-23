""" Oriented graph aka ERD painter """

# Copyright (C) Petr Vanek <petr@yarpen.cz> , 2005
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

__author__ = 'Petr Vanek <petr@yarpen.cz>'

import types
import os

class Dot:
    """ This class requires GraphViz installed because it calls 'dot'
    externally. If it does not find that programm, no images are included
    in html docs.
    Format for parent - children: parent and [child1, child2, ..., childN]
    Format for all - {
                      parent1: [child1, child2, ..., childN],
                      parent2: [child1, child2, ..., childN],
                      ...
                      parentN: [child1, child2, ..., childN]
                     }
    """

    def __init__(self, outPath):
        self.outPath = outPath
        self.haveDot = self.haveDot()
        self.graphTemplate = """
            digraph G
            {
            label="%s";fontname="Helvetica";labelfontsize="12";
            labelloc="t";labeljust="l";labeldistance="5.0";
            edge [fontname="Helvetica",fontsize=10,labelfontname="Helvetica",labelfontsize=10];
            node [fontname="Helvetica",fontsize=10,shape=record];
            rankdir=LR;
            %s
            }
        """

    def uniq(self, aList):
        """ Create a list with unique values """
        set = {}
        map(set.__setitem__, aList, [])
        return set.keys()


    def makeKeyNode(self, node):
        """ Make base node """
        s = '%s [label="%s" height=0.2,width=0.4,color="black",fillcolor="white",style="filled",fontcolor="black",href="table-%s.html#t-fk"];\n' % (node, node, node)
        return s

    def graphList(self, mainName, children=[]):
        """ Make relations between the nodes """
        s = ''
        for i in children:
            s += '''%s -> %s [color="black",fontsize=10,style="solid",arrowhead="crow"];\n''' % (i, mainName)
        return s

    def haveDot(self):
        """ Check if there is a dot installed in PATH """
        try:
            if os.spawnlp(os.P_WAIT, 'dot', 'dot', '-V') == 0:
                return True
        except:
            print 'Unknown error in Dot.haveDot() method. ERD disabled'
        return False

    def callDot(self, fname):
        """ Create the PNGs and image maps from DOT files """
        f = fname + '.dot'
        retval = 1
        os.spawnlp(os.P_WAIT,'dot','dot', '-Tcmap', '-o', fname + '.map', f)
        retval = os.spawnlp(os.P_WAIT,'dot','dot', '-Tpng', '-o', fname + '.png', f)
        if retval == 0:
             try:
                 os.remove(f)
             except IOError:
                 print 'cannot delete %s' % f
        return retval


    def fileGraphList(self, mainName, children=[]):
        """ Make a graph of the mainName's children """
        allNodes = self.uniq(children + [mainName])
        s = ''
        for i in allNodes:
            s += self.makeKeyNode(i)
        s += self.graphList(mainName, children)
        s = self.graphTemplate % ('ERD related to the table', s)
        fname = os.path.join(self.outPath, mainName)
        f = file(fname+'.dot', 'w')
        f.write(s)
        f.close()
        if self.callDot(fname) == 0:
            return mainName+'.png'
        return None


    def fileGraphDict(self, all={}):
        """ Make wide graph for the whole schema """
        allNodes = all.keys()
        for i in all.keys():
            if type(i) != types.ListType:
                continue
            for j in i:
                allNodes.append(j)
        allNodes = self.uniq(allNodes)
        s = ''
        for i in allNodes:
            s += self.makeKeyNode(i)
        for i in all.keys():
            s += self.graphList(i, all[i])
        s = self.graphTemplate % ('ERD of the schema', s)
        fname = os.path.join(self.outPath, 'main')
        f = file(fname + '.dot', 'w')
        f.write(s)
        f.close()
        if self.callDot(fname) == 0:
            return 'main.png'
        return None


if __name__ == '__main__':
    d = Dot()
    d.fileGraphList('rodic', ['ch1', 'ch2', 'ch3'])
    d.fileGraphDict({'rodic1': ['ch1', 'ch2', 'ch3', 'rodic2'], 'rodic2': ['x1', 'rodic1']})
