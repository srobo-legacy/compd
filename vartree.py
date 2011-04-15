# Copyright 2010 Robert Spanton
# This file is part of compd.
#
# compd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# compd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"Subscribable variables"
import re

def resolve(root, varname):
    """Resolve the given variable 'path' to an object
    i.e. Do all the necessary dictionary and list lookups."""

    r = re.compile( "\\]|\\." )
    val = root

    for sub in r.split(varname):
        if "[" in sub:
            vname = sub[0:sub.find("[")]
            index = int(sub[sub.find("[")+1:])

            val = val.get_entry(vname)
            val = val.get_entry(index)

        else:
            vname = sub
            val = val.get_entry(vname)

    return val

class PubSubVar(object):
    "A subscribable variable"
    def __init__(self, vartype, desc):
        self.vartype = vartype
        self.desc = desc
        self.subscribers = []

    def get_type(self):
        return self.vartype

    def get_desc(self):
        return self.desc

    def set_desc(self, val):
        self.desc = val

    def subscribe(self, fn, args = []):
        self.subscribers.append( (fn, args) )

    def unsubscribe(self, fn):
        self.subscribers = [ x for x in self.subscribers if x[0] != fn ]

    def _emit(self, val):
        for sub in self.subscribers:
            sub[0]( val, *sub[1] )

class PubSubDict(PubSubVar):
    def __init__(self, desc):
        self.vals = {}
        PubSubVar.__init__(self, "dict", desc)

    def set_entry(self, name, val):
        self.vals[name] = val

    def get_entry(self, name):
        return self.vals[name]

    def del_entry(self, name):
        self.vals.pop(name)

    def list_entries(self, name):
        return self.vals.keys()

class PubSubList(PubSubVar):
    def __init__(self, desc):
        self.vals = []
        PubSubVar.__init__(self, "list", desc)

    def len(self):
        return len(self.vals)

    def remove(self, index):
        self.vals.pop(index)

    def get_entry(self, index):
        return self.vals[index]

    def append(self, val):
        self.vals.append(val)

class PubSubScalar(PubSubVar):
    def __init__(self, val, vartype, desc):
        self.val = val
        PubSubVar.__init__(self, vartype, desc)

    def set(self, val):
        self.val = val
        self._emit(val)

    def get(self):
        return self.val

class PubSubInt(PubSubScalar):
    def __init__(self, val, desc):
        PubSubScalar.__init__(self, val, "int", desc)

class PubSubString(PubSubScalar):
    def __init__(self, val, desc):
        PubSubScalar.__init__(self, val, "string", desc)
