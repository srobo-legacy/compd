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
"A tree of subscribable variables"

class SVar:
    "A subscribable variable"
    def __init__(self):
        self.subscribers = []
        self.value = None

    def set(self, val):
        self.value = val
        self._emit()

    def get(self):
        return self.value

    def subscribe(self, fn, args):
        self.subscribers.append( (fn, args) )

    def unsubscribe(self, fn):
        self.subscribers = [ x for x in self.subscribers if x[0] != fn ]

    def _emit(self):
        for sub in self.subscribers:
            sub[0]( self.value, *sub[1] )

class VarTree:
    real_attrs = ["_vars", "_name"]

    def __init__(self, name = "Unknown"):
        self._vars = {}
        self._name = name

    def __setattr__(self, name, value):
        if name in self.__dict__ or name in VarTree.real_attrs:
            "Request for attribute that's not part of the vartree"
            self.__dict__[name] = value
            return

        _vars = self.__dict__["_vars"]

        if isinstance( value, VarTree ):
            "Inject the provided VarTree instance into the tree"
            value._name = "%s.%s" % (self._name, name)
            _vars[name] = value

        else:
            "It's a normal variable"
            if name not in _vars:
                _vars[name] = SVar()

            _vars[name].set(value)

    def __getattr__(self, name):
        if name in self._vars:
            val = self._vars[name]

            if isinstance( val, VarTree ):
                return val

            # Reached a leaf of the tree
            return val.get()

        raise AttributeError

    def __delattr__(self, name):
        "Remove the given variable from the tree"
        self._vars.popitem(name)

    def subscribe(root, name, fn, args = []):
        "Call fn with args when name variable changes"
        s = name.split(".")
        cur = root

        assert s[0] == "sr"
        s = s[1:]

        while len(s) > 0:
            cur = cur._vars[s[0]]
            s = s[1:]

        if not isinstance(cur, SVar):
            raise AttributeError

        cur.subscribe( fn, args )

    def unsubscribe(root, fn):
        # Traverse all nodes in the tree, unsubscribing things

        for x in root._vars.items():
            if isinstance(x, VarTree):
                VarTree.unsubscribe( x, fn )
            elif isinstance(x, SVar):
                x.unsubscribe(fn)
