from vartree import VarTree

class Scheduler:
    "Tells us what slot we're currently in"

    def __init__(self, root):
        self.tree = VarTree()
        root.scheduler = self.tree

        self.tree.curslot_id = 0
        self.tree.curslot_duration = 0
        self.tree.curslot_time = 0
        self.tree.curslot_type = 0

        root.subscribe( "sr.clock.event_time", self.tick )

    def tick(self, event_time):
        if event_time % 20 == 0:
            self.tree.curslot_id += 1
