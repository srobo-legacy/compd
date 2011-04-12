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
        # Outgoing data buffer
        self.outbuf = ""

        self.sources = []
        self.sources += [glib.io_add_watch( self.sock, glib.IO_IN, self._read )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_HUP, self._hup )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_ERR, self._err )]

        self.write_source = None

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
        if len(l) == 0:
            return
        cmd = l[0].strip().lower()

        if cmd in CMDS:
            try:
                CMDS[cmd]( l[1:] )
            except Exception as e:
                "Send the client the error"
                self._write( "Error: %s\n" % str(e) )

    def _cmd_sub(self, args):
        if len(args) != 1:
            raise Exception, "Not enough arguments to sub command."

        varn = args[0]
        VarTree.subscribe( self.root, varn, self._event, args = [varn] )
        self._write( "OK" )

    def _event(self, val, varn ):
        self._write( "%s = '%s'\n" % (varn, val) )

    def _write(self, s):
        "Add the given string to the output queue"
        self.outbuf += s

        if self.write_source == None:
            glib.io_add_watch( self.sock, glib.IO_OUT, self._txready )

    def _txready(self, source, cond):
        "Called by mainloop when socket is ready for writing"

        if len(self.outbuf) == 0:
            "No data to send -- stop calling me"
            self.write_source = None
            return False

        r = self.sock.send( self.outbuf )
        self.outbuf = self.outbuf[r:]

        if len(self.outbuf):
            "More to send later"
            return True
        else:
            "No more to send"
            self.write_source = None
            return False

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
