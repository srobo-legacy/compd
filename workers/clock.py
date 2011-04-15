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
import glib
import time
from vartree import PubSubInt

class Clock:
    "Clock for the event"
    def __init__(self, root):
        self.clock = PubSubInt( val = int(time.time()),
                                desc = "The competition clock" )
        root.set_entry( "clock", self.clock )

        glib.timeout_add( 1000, self.tick )

    def tick(self):
        self.clock.set( self.clock.get() + 1 )
        return True
