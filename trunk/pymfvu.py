#!/usr/bin/env python
# pymfvu -- Utility to view and research WMF and EMF (Windows Metafile and Enchanced Metafile) files.
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
# pywmf was made on the base of Rob McMullen (robm@users.sourceforge.net) pyemf module
# http://pyemf.sourceforge.net
# and I hope one day we will merge those modules.
#
import sys
import gtk
import wmfdoc
import emfdoc
import wmfcmd
import pango
import cairo
import pangocairo
import string
import hexdump
import struct

__version__ = "0.0.5"
__author__ = "Valek Filippov"
__url__ = "http://www.sk1project.org"
__description__ = "Python Windows and Enchanced Metafile viewer"
__keywords__ = "graphics, scalable, vector, image, clipart, wmf"
__license__ = "GPL v3"


ui_info = \
'''<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='Open'/>
      <menuitem action='Close'/>
      <separator/>
      <menuitem action='SaveAs'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='ViewMenu'>
        <menuitem action='Records'/>
        <menuitem action='Hexdump'/>
        <menuitem action='Alpha'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
    </menu>
  </menubar>
</ui>'''

def register_stock_icons():
    ''' This function registers our custom toolbar icons, so they  can be themed. '''
    # Add our custom icon factory to the list of defaults
    factory = gtk.IconFactory()
    factory.add_default()

class ApplicationMainWindow(gtk.Window):
    def __init__(self, parent=None):
        register_stock_icons()
        # Create the toplevel window
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())

        self.set_title("Pymfvu")
        self.set_default_size(400, 300)

        merge = gtk.UIManager()
        self.set_data("ui-manager", merge)
        merge.insert_action_group(self.__create_action_group(), 0)
        self.add_accel_group(merge.get_accel_group())

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except gobject.GError, msg:
            print "building menus failed: %s" % msg
        bar = merge.get_widget("/MenuBar")
        bar.show()

        table = gtk.Table(1, 3, False)
        self.add(table)

        table.attach(bar,
            # X direction #          # Y direction
            0, 1,                      0, 1,
            gtk.EXPAND | gtk.FILL,     0,
            0,                         0);
        
        self.notebook =gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        table.attach(self.notebook,
            # X direction #          # Y direction
            0, 1,                      1, 2,
            gtk.EXPAND | gtk.FILL,     gtk.EXPAND | gtk.FILL,
            0,                         0);

        # Create statusbar
        self.statusbar = gtk.Statusbar()
        table.attach(self.statusbar,
            # X direction           Y direction
            0, 1,                   2, 3,
            gtk.EXPAND | gtk.FILL,  0,
            0,                      0)
        self.show_all()
        self.das = {}
        self.fname = ''
        if len(sys.argv) > 1:
            for i in range(len(sys.argv)-1):
                self.fname = sys.argv[i+1]
                self.activate_open()
 
    def __create_action_group(self):
        # GtkActionEntry
        entries = (
          ( "FileMenu", None, "_File" ),               # name, stock id, label
          ( "ViewMenu", None, "_View" ),               # name, stock id, label
          ( "HelpMenu", None, "_Help" ),               # name, stock id, label
          ( "Open", gtk.STOCK_OPEN,                    # name, stock id
            "_Open","<control>O",                      # label, accelerator
            "Open a file",                             # tooltip
            self.activate_open),
          ( "SaveAs", gtk.STOCK_SAVE_AS,                    # name, stock id
            "_SaveAs...","<control>S",                      # label, accelerator
            "Save the file",                             # tooltip
            self.activate_save),
          ( "Close", gtk.STOCK_CLOSE,                    # name, stock id
            "_Close","<control>C",                      # label, accelerator
            "Close the file",                             # tooltip
            self.activate_close),
          ( "Quit", gtk.STOCK_QUIT,                    # name, stock id
            "_Quit", "<control>Q",                     # label, accelerator
            "Quit",                                    # tooltip
            self.activate_quit ),
          ( "Alpha", gtk.STOCK_ZOOM_IN,                    # name, stock id
            "Alpha", "<control>T",                     # label, accelerator
            "Toggle semi-transparency of FillPath",                                    # tooltip
            self.activate_alpha),
          ( "Records", gtk.STOCK_INDEX,                    # name, stock id
            "_Records", "<control>R",                     # label, accelerator
            "Toggle records window",                                    # tooltip
            self.activate_records),
          ( "Hexdump", gtk.STOCK_FIND_AND_REPLACE,                    # name, stock id
            "_Hexdump", "<control>D",                     # label, accelerator
            "Toggle hexdump window",                                    # tooltip
            self.activate_hexdump),
          ( "About", gtk.STOCK_ABOUT,                             # name, stock id
            "_About", "<control>A",                    # label, accelerator
            "About",                                   # tooltip
            self.activate_about ),
        );
        # Create the menubar and toolbar
        action_group = gtk.ActionGroup("AppWindowActions")
        action_group.add_actions(entries)
        return action_group

    def activate_hexdump(self, action):
        pn = self.notebook.get_current_page()
        if pn != -1:
            if self.das[pn].page.hdv == 1:
                self.das[pn].page.hd.vbox.hide()
                self.das[pn].page.hdv = 0
            else:
                self.das[pn].page.hd.vbox.show()
                self.das[pn].page.hdv = 1
        
    def activate_records(self, action):
        pn = self.notebook.get_current_page()
        if pn != -1:
            string = ''
            offset = 0
            records = self.das[pn].page.file.records
            print 'Records: ',len(records)
            for i in range(len(records)):
                string = string+'%u  %04x   '%(i,offset)+unicode(records[i])
                offset+=records[i].nSize
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_resizable(True)
            window.set_default_size(650, 700)
            window.set_title("List of Records: "+self.das[pn].page.fname)
            window.set_border_width(0)
            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            textview = gtk.TextView()
            textview.set_justification(0)
            textbuffer = textview.get_buffer()
            textbuffer.create_tag("monospace", family="monospace")
            iter_label = textbuffer.get_iter_at_offset(0)
            textbuffer.insert_with_tags_by_name(iter_label, string,"monospace")
            sw.add(textview)
            sw.show()
            textview.show()
            window.add(sw)
            window.show()
            pass
        
    def activate_alpha(self, action):
        pn = self.notebook.get_current_page()
        if pn != -1:
            if self.das[pn].page.alpha == 1:
                self.das[pn].page.alpha = 0.5
            else:
                self.das[pn].page.alpha = 1
            self.das[pn].hide()
            self.das[pn].show()
            self.notebook.set_current_page(pn)
    
    def activate_about(self, action):
        dialog = gtk.AboutDialog()
        dialog.set_name("pywmfvu")
        dialog.set_copyright("     \302\251 Copyright 2007 Valek Filippov     ")
        dialog.set_website("http://www.sk1project.org/")
        dialog.set_default_size(700,400)
        ## Close dialog on user response
        dialog.connect ("response", lambda d, r: d.destroy())
        dialog.show()

    def activate_quit(self, action):
         gtk.main_quit()
         return

    def activate_close(self, action):
        pn = self.notebook.get_current_page()
        if pn == -1:
            gtk.main_quit()
        else:
            del self.das[pn]         
            self.notebook.remove_page(pn)
            if pn < len(self.das):  ## not the last page
                for i in range(pn,len(self.das)):
                        self.das[i] = self.das[i+1]
                del self.das[len(self.das)-1]
        return

    def update_hexdump(self,data):
        pn = self.notebook.get_current_page()
        if self.das[pn].page.hdv == 1: ## if hd is visible
            hd = self.das[pn].page.hd
            str_addr = ''
            str_hex = ''
            str_asc = ''
            for line in range(0, len(data), 16):
                str_addr+="%07x: "%line
                end = min(16, len(data) - line)
                for byte in range(0, 15):
                    if byte < end:
                        str_hex+="%02x " % ord(data[line + byte])
                        if ord(data[line + byte]) < 32 or 126<ord(data[line + byte]):
                            str_asc +='.'
                        else:
                            str_asc += data[line + byte]
                if end > 15:			
                    str_hex+="%02x" % ord(data[line + 15])
                    if ord(data[line + 15]) < 32 or 126<ord(data[line + 15]):
                        str_asc += '.'
                    else:
                        str_asc += data[line + 15]
                    str_hex+='\n'
                    str_asc+='\n'
                    str_addr+='\n'
            shl =  47 - len(str_hex)
            if shl >0:
                for i in range(shl/3):
                    str_hex+='   '
                str_hex+='  '
                
            buffer_addr = hd.txtdump_addr.get_buffer()
            iter_addr = buffer_addr.get_iter_at_offset(0)
            iter_addr_end = buffer_addr.get_iter_at_offset(buffer_addr.get_char_count())
            buffer_addr.delete(iter_addr, iter_addr_end)
            buffer_addr.insert_with_tags_by_name(iter_addr, str_addr,"monospace")
            buffer_hex = hd.txtdump_hex.get_buffer()
            iter_hex = buffer_hex.get_iter_at_offset(0)
            iter_hex_end = buffer_hex.get_iter_at_offset(buffer_hex.get_char_count())
            buffer_hex.delete(iter_hex, iter_hex_end)
            buffer_hex.insert_with_tags_by_name(iter_hex, str_hex,"monospace")
            buffer_asc = hd.txtdump_asc.get_buffer()
            iter_asc = buffer_asc.get_iter_at_offset(0)
            iter_asc_end = buffer_asc.get_iter_at_offset(buffer_asc.get_char_count())
            buffer_asc.delete(iter_asc, iter_asc_end)
            buffer_asc.insert_with_tags_by_name(iter_asc, str_asc,"monospace")

    def update_statusbar(self, buffer):
        # clear any previous message, underflow is allowed
        self.statusbar.push(0,'%s' % (buffer))

    def update_resize_grip(self, widget, event):
        mask = gtk.gdk.WINDOW_STATE_MAXIMIZED | gtk.gdk.WINDOW_STATE_FULLSCREEN
        if (event.changed_mask & mask):
            self.statusbar.set_has_resize_grip(not (event.new_window_state & mask))

    def file_open(self,parent=None, dirname=None, fname=None):
        dlg = gtk.FileChooserDialog('Open', parent, buttons=(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dlg.set_local_only(True)
        resp = dlg.run()
        fname = dlg.get_filename()
        dlg.hide()
        if resp == gtk.RESPONSE_CANCEL:
            return None
        return fname

    def file_save(self,parent=None, dirname=None, fname=None):
        dlg = gtk.FileChooserDialog('SaveAs...', action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dlg.set_local_only(True)
        resp = dlg.run()
        fname = dlg.get_filename()
        dlg.hide()
        if resp == gtk.RESPONSE_CANCEL:
            return None
        return fname

    def on_button_press(self,widget,event):
        pn = self.notebook.get_current_page()
        if event.button == 1:
            self.das[pn].page.zoom*=1.4
        if event.button == 3:
            self.das[pn].page.zoom/=1.4
        self.das[pn].hide()
        self.das[pn].show()
        self.notebook.set_current_page(pn)
        
    def adj_changed(self,widget):
        pn = self.notebook.get_current_page()
        self.das[pn].hide()
        self.das[pn].show()
        self.notebook.set_current_page(pn)
        data = self.das[pn].page.file.records[int(self.das[pn].page.hadj.value)].data
        self.update_hexdump(data)
        cmd = wmfcmd.mr_ids[self.das[pn].page.file.records[int(self.das[pn].page.hadj.value)].mr_id]+": "+str(self.das[pn].page.file.records[int(self.das[pn].page.hadj.value)].values)
        self.update_statusbar(cmd)
        
    def activate_open(self,parent=None):
        if self.fname !='':
           fname = self.fname
           self.fname = ''
        else:
           fname = self.file_open()
        if fname:
            input = open(fname)
            buf = input.read()
            [sig] = struct.unpack('i',buf[40:44])
            print 'Signature:',sig
            try:
                if sig == 0x464D4520:
                    page = emfdoc.Page()
                    hadjshift = 0
                else:
                    page = wmfdoc.Page()
                    hadjshift = 1
                page.file.loadmem(buf)
                page.parse()
                dnum = len(self.das)
                self.das[dnum] = page.Face
                self.das[dnum].connect("button_press_event",self.on_button_press)
                self.das[dnum].set_events(gtk.gdk.BUTTON_PRESS_MASK)
                pos = fname.rfind('/')
                if pos !=-1:
                    fname = fname[pos+1:]
                page.fname = fname
                label = gtk.Label(fname)
                vbox = gtk.VBox(homogeneous=False, spacing=0)
                vpaned = gtk.VPaned()
                vbox.pack_start(self.das[dnum], expand=True, fill=True, padding=0)
                self.das[dnum].page.hadj = gtk.Adjustment(0.0, 0.0,  len(self.das[dnum].page.cmds)+hadjshift, 0.1, 1.0, 1.0)
                self.das[dnum].page.hadj.connect("value_changed", self.adj_changed)
                hscale = gtk.HScale(self.das[dnum].page.hadj)
                hscale.set_digits(0)
                vbox.pack_end(hscale, expand=False, fill=True, padding=0)
                vpaned.pack2(self.das[dnum].page.hd.vbox,resize=False,shrink= True)                
                vpaned.pack1(vbox, resize=True,shrink= False)
                self.notebook.append_page(vpaned,label)
                self.notebook.show_tabs = True
                self.notebook.show_all()
                page.hd.vbox.hide()
            except:
                print 'Something wrong with a file.' ## FIXME! Bring up some dialog?
                pass
        return
        
    def activate_save(self,parent=None):
        fname = self.file_save()
        if fname:
            pn = self.notebook.get_current_page()
            surface = cairo.SVGSurface(fname,self.das[pn].page.width,self.das[pn].page.height)
            ct = cairo.Context(surface)
            cr = pangocairo.CairoContext(ct)
            cr.save()
            page.render(self.das[pn],cr,self.das[pn].page)
            cr.restore()
            cr.show_page()
            surface.flush()
            surface.finish()
            
    
def main():
    ApplicationMainWindow()
    gtk.main()

if __name__ == '__main__':
    main()
