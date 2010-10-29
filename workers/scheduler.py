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
