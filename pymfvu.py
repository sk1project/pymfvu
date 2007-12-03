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
import pango
import cairo
import string
import struct
import gmodel
import parser
import eparser

__version__ = "0.1.0"
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
        <menuitem action='Slider'/>
        <menuitem action='Infowin'/>
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
          ( "Slider", None,                    # name, stock id
            "S_lider","<control>L",                      # label, accelerator
            "Slider to play file shape by shape",                             # tooltip
            self.activate_slider),
          ( "Infowin", None,                    # name, stock id
            "Info_win","<control>W",                      # label, accelerator
            "Info about shapes",                             # tooltip
            self.activate_infowin),
          ( "About", gtk.STOCK_ABOUT,                             # name, stock id
            "_About", "<control>A",                    # label, accelerator
            "About",                                   # tooltip
            self.activate_about ),
        );
        # Create the menubar and toolbar
        action_group = gtk.ActionGroup("AppWindowActions")
        action_group.add_actions(entries)
        return action_group


    def activate_infowin(self, action):
        pn = self.notebook.get_current_page()
        if pn != -1:
            if self.das[pn].page.hdv1 == 1:
                self.scrolled2.hide_all()
                self.das[pn].page.hdv1 = 0
            else:
                self.scrolled2.show_all()
                self.das[pn].page.hdv1 = 1

    def activate_slider(self, action):
        pn = self.notebook.get_current_page()
        if pn != -1:
            if self.das[pn].page.hdv2 == 1:
                self.das[pn].page.hscale.hide()
                self.das[pn].page.hdv2 = 0
                self.das[pn].page.hadj.value = len(self.das[pn].page.objs)
            else:
                self.das[pn].page.hscale.show()
                self.das[pn].page.hdv2 = 1
            
    def activate_about(self, action):
        dialog = gtk.AboutDialog()
        dialog.set_name("pywmfvu %s\nWMF/EMF file viewer"%__version__)
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
        self.das[pn].set_size_request(int(self.das[pn].page.width*self.das[pn].page.zoom),int(self.das[pn].page.height*self.das[pn].page.zoom))
        self.das[pn].show()
        self.notebook.set_current_page(pn)

    def adj_changed(self,widget,infowin):
        pn = self.notebook.get_current_page()
        if pn !=-1:
            self.das[pn].hide()
            self.das[pn].show()
            self.notebook.set_current_page(pn)

            buffer_iwin = infowin.get_buffer()
            iter_iwin = buffer_iwin.get_iter_at_offset(0)
            iter_iwin_end = buffer_iwin.get_iter_at_offset(buffer_iwin.get_char_count())
            buffer_iwin.delete(iter_iwin, iter_iwin_end)
            if self.das[pn].page.hadj.value!=-1:
                num = int(self.das[pn].page.hadj.value)-1
                str_iwin = self.das[pn].page.objs[num].get_info()
                buffer_iwin.insert_with_tags_by_name(iter_iwin, str_iwin,"monospace")

            
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
                pg = gmodel.Page()
                if sig == 0x464D4520:
                    eparser.parse(pg,buf)
                else:
                    parser.parse(pg,buf)
                dnum = len(self.das)
                self.das[dnum] = pg.Face
                scrolled = gtk.ScrolledWindow()
                scrolled.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
                scrolled.add_with_viewport(self.das[dnum])
                scrolled.set_events(gtk.gdk.BUTTON_PRESS_MASK)
                scrolled.connect("button_press_event",self.on_button_press)
                pos = fname.rfind('/')
                if pos !=-1:
                    fname = fname[pos+1:]
                pg.fname = fname
                nums = len(self.das[dnum].page.objs)
                label = gtk.Label(fname)
                vbox = gtk.VBox(homogeneous=False, spacing=0)
                self.infowin = gtk.TextView()
                buffer_iwin = self.infowin.get_buffer()
                buffer_iwin.create_tag("monospace", family="monospace")
                self.scrolled2 = gtk.ScrolledWindow()
                self.scrolled2.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
                self.scrolled2.add_with_viewport(self.infowin)
                vpaned = gtk.VPaned()
                vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
                self.das[dnum].page.hadj = gtk.Adjustment(0.0, 0.0, nums+1, 0.1, 1.0, 1.0)
                self.das[dnum].page.hadj.connect("value_changed", self.adj_changed,self.infowin)
                pg.hadj.value = nums
                self.das[dnum].page.hscale = gtk.HScale(self.das[dnum].page.hadj)
                self.das[dnum].page.hscale.set_digits(0)
                vbox.pack_end(self.das[dnum].page.hscale, expand=False, fill=True, padding=0)
                vpaned.pack2(self.scrolled2,resize=False,shrink= True)                
                vpaned.pack1(vbox, resize=True,shrink= False)
                self.notebook.append_page(vpaned,label)
                self.notebook.show_tabs = True
                scrolled.show()
                vbox.show()
                vpaned.show()
                self.das[dnum].show()
                self.notebook.show()
        return
        
    def activate_save(self,parent=None):
        print 'Save request'
    
def main():
    ApplicationMainWindow()
    gtk.main()

if __name__ == '__main__':
    main()
