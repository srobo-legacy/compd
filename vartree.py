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
# along with compd.  If not, see <http://www.gnu.org/licenses/>.
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

def unsubscribe(root, callback):
    "Unsubscribe callback from all items under root"

    root.unsubscribe(callback)

    if isinstance( root, PubSubDict ):
        "Unsubscribe all children"
        for key in root.list_entries():
            unsubscribe( root.get_entry(key), callback )

    elif isinstance( root, PubSubList ):
        "Unsubscribe all list entries"
        for i in range(0, root.len()):
            unsubscribe( root.get_entry(i), callback )

class PubSubVar(object):
    "A subscribable variable"
    def __init__(self, vartype, desc):
        self.vartype = vartype
        self.desc = desc
        self.subscribers = []
        self.rpc_funcs = { "get_type": self.get_type,
                           "get_desc": self.get_desc,
                           "set_desc": self.set_desc }

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

        self.rpc_funcs.update( { "set_entry": self.set_entry,
                                 "del_entry": self.del_entry,
                                 "list_entries": self.list_entries } )

    def set_entry(self, name, desc, entry_type):
        if entry_type not in TYPES:
            raise Exception, "%s is not a valid type." % entry_type

        v = TYPES[entry_type]( desc = desc )
        self.vals[name] = v

    def get_entry(self, name):
        return self.vals[name]

    def del_entry(self, name):
        self.vals.pop(name)

    def list_entries(self):
        return self.vals.keys()

class PubSubList(PubSubVar):
    def __init__(self, desc):
        self.vals = []
        PubSubVar.__init__(self, "list", desc)

        self.rpc_funcs.update( { "append": self.append,
                                 "remove": self.remove,
                                 "len": self.len } )

    def len(self):
        return len(self.vals)

    def remove(self, index):
        self.vals.pop(index)

    def get_entry(self, index):
        return self.vals[index]

    def append(self, desc, entry_type):
        if entry_type not in TYPES:
            raise Exception, "%s is not a valid type." % entry_type

        v = TYPES[entry_type]( desc = desc )
        self.vals.append(v)

class PubSubScalar(PubSubVar):
    def __init__(self, val, vartype, desc):
        self.val = val
        PubSubVar.__init__(self, vartype, desc)

        self.rpc_funcs.update( { "set": self.set,
                                 "get": self.get } )

    def set(self, val):
        self.val = val
        self._emit(val)

    def get(self):
        return self.val

class PubSubInt(PubSubScalar):
    def __init__(self, desc):
        PubSubScalar.__init__(self, 0, "int", desc)

class PubSubString(PubSubScalar):
    def __init__(self, desc):
        PubSubScalar.__init__(self, "", "string", desc)

TYPES = { "int": PubSubInt,
          "string": PubSubString,
          "dict": PubSubDict,
          "list": PubSubList }
