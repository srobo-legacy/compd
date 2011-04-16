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

def str_to_u32(s):
    assert len(s) == 4
    val = 0

    for v in s:
        "MSB first"
        val <<= 8
        val |= ord(v)

    return val

def u32_to_str(i):
    assert i > -1
    assert i < 0x100000000
    s = ""

    for j in range(3,-1,-1):
        s += chr( (i >> (j*8)) & 0xff )
    return s

class FramedClient:
    def __init__(self, sock, discon_cb):
        self.sock = sock
        self.discon_cb = discon_cb

        # Incoming data buffer
        self.inbuf = ""
        # Outgoing data buffer
        self.outbuf = ""

        # Length of incoming frame
        self.in_len = None
        self.len_buf = ""

        self.sources = []
        self.sources += [glib.io_add_watch( self.sock, glib.IO_IN, self._read )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_HUP, self._hup )]
        self.sources += [glib.io_add_watch( self.sock, glib.IO_ERR, self._err )]

        self.write_source = None

    def _read(self, source, cond):
        r = self.sock.recv( 4096, socket.MSG_DONTWAIT )

        if r == "":
            "We've reached EOF"
            self._cleanup()
            return False

        self.inbuf += r
        self._proc_incoming()
        return True

    def _proc_incoming(self):
        if self.in_len == None:
            "We're waiting for the length field"
            self.len_buf += self._shift_read( 4 - len(self.len_buf) )

            if len(self.len_buf) == 4:
                "Convert length bytes into integer"
                self.in_len = str_to_u32(self.len_buf)
                self.len_buf = ""

        if self.in_len == None:
            "No more data to process"
            assert len(self.inbuf) == 0
            return True

        # Now we're waiting for the data block itself
        if len(self.inbuf) < self.in_len:
            "Not enough data yet"
            return

        block_data = self._shift_read(self.in_len)
        self.rx_frame(block_data)

        # Reset the receiver
        self.in_len = None

    def rx_frame(frame):
        print "Received frame: %s" % frame

    def _shift_read(self, n_bytes):
        """Read n_bytes from the (already received) input buffer
        Returns at most n_bytes."""
        d = self.inbuf[0:n_bytes]
        self.inbuf = self.inbuf[len(d):]
        return d

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

        self.discon_cb(self)

    def write_frame(self, fdata):
        "Send the given frame"

        self.outbuf += u32_to_str(len(fdata))
        self.outbuf += fdata

        if self.write_source == None:
            glib.io_add_watch( self.sock, glib.IO_OUT, self._txready )
