import glib
from vartree import VarTree

class Clock:
    "Clock for the event"
    def __init__(self, root):
        self.tree = VarTree()
        root.clock = self.tree

        self.tree.event_time = 0
        self.tree.paused_time = 0
        self.tree.paused = False

        glib.timeout_add( 1000, self.tick )

    def tick(self):
        self.tree.event_time += 1

        return True
