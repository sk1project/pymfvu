# This program was made as part of the sk1project activity to improve UniConvertor
# See http://www.sk1project.org
#
# Copyright (C) 2007,	Valek Filippov (frob@df.ru)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 or later of the GNU General Public
# License as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA
#

import gtk
import gobject

class hexdump:
    def __init__(self):
        self.vbox =gtk.VBox()
        hbox1 =gtk.HBox()

        addrlabel = gtk.TextView();
        buffer = addrlabel.get_buffer()
        buffer.create_tag("monospace", family="monospace")
        iter_label = buffer.get_iter_at_offset(0)
        buffer.insert_with_tags_by_name(iter_label, "         ","monospace")
        
        hexlabel = gtk.TextView();
        buffer = hexlabel.get_buffer()
        buffer.create_tag("monospace", family="monospace")
        iter_label = buffer.get_iter_at_offset(0)
        buffer.insert_with_tags_by_name(iter_label, "00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f","monospace")
        
        hbox1.pack_start(addrlabel,False,True,2)
        hbox1.pack_start(hexlabel,False,True,2)
        self.vbox.pack_start(hbox1,False,True,2)
        
        vscroll2 = gtk.ScrolledWindow()
        hbox2 =gtk.HBox()
        self.txtdump_addr = gtk.TextView();
        self.txtdump_hex = gtk.TextView();
        self.txtdump_asc = gtk.TextView();
        buffer = self.txtdump_addr.get_buffer()
        buffer.create_tag("monospace", family="monospace")
        buffer = self.txtdump_asc.get_buffer()
        buffer.create_tag("monospace", family="monospace")
        buffer = self.txtdump_hex.get_buffer()
        buffer.create_tag("monospace", family="monospace")
        hbox2.pack_start(self.txtdump_addr, False,True,2)
        hbox2.pack_start(self.txtdump_hex, False,True,2)
        hbox2.pack_start(self.txtdump_asc, True,True,2)
        vscroll2.add_with_viewport(hbox2)
        self.vbox.pack_start(vscroll2,True,True,2)
        
    def update():
        pass
