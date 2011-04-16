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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
import glib, socket, sys, os
import vartree, traceback
from framer import FramedClient

def str_to_u32(s):
    assert len(s) == 4
    val = 0

    for v in s:
        "MSB first"
        val <<= 8
        val |= ord(v)

    return val

class CompdClient(FramedClient):
    def __init__(self, sock, root, discon_cb):
        self.root = root
        FramedClient.__init__(self, sock, discon_cb)

    def rx_frame(self, frame):
        print "CompdClient received frame:", frame

        path = frame["path"]
        var = vartree.resolve( self.root, path )

        cmd_name = frame["command"]

        if "args" in frame:
            cmd_args = frame["args"]
        else:
            cmd_args = {}

        fn = var.rpc_funcs[cmd_name]

        res = fn( **cmd_args )

        self.write_frame( { "result": res } )

    def tx_frame(self, data):
        self.write_frame( data )


class CompdServer:
    def __init__(self, root, sock_type, address):
        self.root = root

        self.clients = []
        self.sock = socket.socket( sock_type )

        if sock_type == socket.AF_UNIX and os.path.exists( address ):
            os.remove( address )

        self.sock.bind( address )
        self.sock.listen(5)

        glib.io_add_watch( self.sock, glib.IO_IN, self._connect )

    def _connect(self, source, cond):
        "Accept a client's connection"

        conn, address = self.sock.accept()
        print "New connection from", address

        self.clients.append( CompdClient(conn, self.root, self._cli_discon) )
        return True

    def _cli_discon(self, client):
        self.clients.remove(client)
        print "Client disconnected."
