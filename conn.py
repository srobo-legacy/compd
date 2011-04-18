# Copyright 2011 Robert Spanton
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
import framer, socket

class CompdSyncConn(object):
    def __init__(self, path = "/tmp/compd" ):
        if isinstance(path, str):
            s = socket.socket( socket.AF_UNIX )
            s.connect( path )
        elif isinstance(path, tuple):
            s = socket.socket( socket.AF_INET )
            s.connect( path )
        else:
            raise TypeError, "Connection path must either be tuple or string."

        self.conn = framer.FramedSyncClient(s)

    def txrx(self, cmd):
        self.conn.write_frame(cmd)
        return self.conn.read_frame()
