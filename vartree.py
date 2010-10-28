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
            self.__dict__[name] = value
            return

        _vars = self.__dict__["_vars"]

        if isinstance( value, VarTree ):
            value._name = "%s.%s" % (self._name, name)
            _vars[name] = value

        else:
            if name not in _vars:
                _vars[name] = SVar()

            _vars[name].set(value)

    def __getattr__(self, name):
        if name in self._vars:
            val = self._vars[name]

            if isinstance( val, VarTree ):
                return val

            return val.get()

        raise AttributeError

    def __delattr__(self, name):
        self._vars.popitem(name)

    def subscribe(root, name, fn, args = []):
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
