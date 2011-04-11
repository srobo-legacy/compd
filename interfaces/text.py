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
"A simple text-based socket interface"
import glib, socket, sys, os
from vartree import VarTree
import traceback

class TextClient:
    def __init__(self, sock, root, discon_cb):
        self.sock = sock
        self.root = root
        self.discon_cb = discon_cb

        # Incoming data buffer
        self.inbuf = ""

        self.sources = []
        self.sources += [glib.io_add_watch( self.sock, glib.IO_IN, self._read )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_HUP, self._hup )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_ERR, self._err )]

    def _read(self, source, cond):
        r = self.sock.recv( 4096, socket.MSG_DONTWAIT )

        if r == "":
            self._cleanup()
            return False

        self.inbuf = self.inbuf + r

        while "\n" in self.inbuf:
            line = self.inbuf[:self.inbuf.find("\n")]
            self.inbuf = self.inbuf[len(line)+1:]

            self._proc_cmd(line)

        return True

    def _proc_cmd(self, line):
        "Parse and process a single command"
        CMDS = { "sub": self._cmd_sub }

        l = line.strip().split()
        cmd = l[0].strip().lower()

        if cmd in CMDS:
            try:
                CMDS[cmd]( l[1:] )
            except:
                # TODO: Write error back
                traceback.print_exc()
                pass

    def _cmd_sub(self, args):
        if len(args) != 1:
            raise Exception, "Not enough arguments to sub command."

        varn = args[0]
        VarTree.subscribe( self.root, varn, self._event, args = [varn] )

    def _event(self, val, varn ):
        print "ev", val, varn

    def _hup(self, source, cond):
        print "HUP -- Currently unhandled"
        return False

    def _err(self, source, cond):
        print "ERR -- Currently unhandled"
        return False

    def _cleanup(self):
        "Clean up all stuff after disconnection"
        for source in self.sources:
            glib.source_remove( source )

        VarTree.unsubscribe( self.root, self._event )
        self.discon_cb(self)

class Text:
    def __init__(self, root):
        self.root = root

        self.clients = []
        self.sock = socket.socket(socket.AF_INET)
        self.sock.bind( ( "", 7600 ) )
        self.sock.listen(5)

        glib.io_add_watch( self.sock, glib.IO_IN, self._connect )

    def _connect(self, source, cond):
        "Accept a client's connection"

        conn, address = self.sock.accept()
        print "New Text connection from %s:%i" % address

        self.clients.append( TextClient(conn, self.root, self._cli_discon) )
        return True

    def _cli_discon(self, client):
        self.clients.remove(client)
        print "Client disconnected."
