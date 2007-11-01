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
import cairo
import math
import pyemf
import pywmf
import wmfdraw
import wmfcmd
import emfdraw
import emfcmd
import hexdump

class Page:
    def __init__(self):
        self.type = 0
        self.alpha = 1
        self.ai = 1
        self.fname = ''
        self.hadj = None
        self.hd = hexdump.hexdump()
        self.hdv = 0
        self.curdc = 0
        self.DCs = []
        dc = DC()
        self.DCs.append(dc)
        self.zoom = 1.
        self.scale = 1
        self.width = 1.
        self.height = 1.
        self.kx = 1.
        self.ky = 1.       
        self.VPx = 1.
        self.VPy = 1.
        self.VPOx = 0.
        self.VPOy = 0.
        self.maxobj = 0
        self.curobj = 0
        self.curbg = 0
        self.curfg = 0
        self.curpal = 0
        self.mfobjs = {}
        self.palette = {}
        self.cmds = []
        self.txtclr = color()
        self.txtclr.r = 0.
        self.txtclr.g = 0.
        self.txtclr.b = 0.
        self.txtalign = 0
        self.bkmode = 0
        self.bkcolor = color()
        self.bkcolor.r,self.bkcolor.g,self.bkcolor.b = 255.,255.,255.
        
    def usage():
        class_cmds = cmd()
        class_DCs = DC()

    def parse(self):
        pass

class DC:
    VPx = 1.
    VPy = 1.
    VPOx = 0.
    VPOy = 0.
    Wx = 1.
    Wy = 1.
    x = 0.
    y = 0.
        
class color:
    r = 0.
    g = 0.
    b = 0.
    a = 0.

class mfobj:
    type = 0 # 1-- pen, 2 -- brush, 3 -- font
    clr = color()
    width = 5. ## use for pen
    font = 'Arial'
    italic = 0
    size = 20
    style = 0
    escape = 0
    orient = 0
    under = 0
    strike = 0
    charset = 1
    hatch = 0
    data = None
    flag = 0
    
class cmd:
    type = ''
    args = ()
    
class wmfPage(Page):
    def __init__(self):
        Page.__init__(self)
        self.Face = wmfFace(self)      
        self.file = pywmf.WMF()        
        self.type = 1
        
    def parse(self):
        wmfcmd.parse(self)
        
class emfPage(Page):
    def __init__(self):
        Page.__init__(self)
        self.Face = emfFace(self)      
        self.file = pyemf.EMF()
        self.type = 2
        bgcolor = color()
        bgcolor.r,bgcolor.g,bgcolor.b = (255.,255.,255.)
        bgcolor2 = color()
        bgcolor2.r,bgcolor2.g,bgcolor2.b = (192.,192.,192.)
        bgcolor3 = color()
        bgcolor3.r,bgcolor3.g,bgcolor3.b = (128.,128.,128.)
        bgcolor4 = color()
        bgcolor4.r,bgcolor4.g,bgcolor4.b = (64.,64.,64.)
        fgcolor = color()
        fgcolor.r,fgcolor.g,fgcolor.b = (0,0,0)
        eo = mfobj()
        eo.clr = bgcolor
        eo.type = 2
        self.mfobjs[0x80000000] = eo
        eo = mfobj()
        eo.clr = bgcolor2
        eo.type = 2
        self.mfobjs[0x80000001] = eo
        eo = mfobj()
        eo.clr = bgcolor3
        eo.type = 2
        self.mfobjs[0x80000002] = eo
        eo = mfobj()
        eo.clr = bgcolor4
        eo.type = 2
        self.mfobjs[0x80000003] = eo
        self.mfobjs[0] = eo
        eo = mfobj()
        eo.clr = fgcolor
        eo.type = 2
        self.mfobjs[0x80000004] = eo
        self.mfobjs[0x80000005] = eo ## NULL brush -- don't fill
        eo = mfobj()
        eo.clr = bgcolor
        eo.type = 1
        self.mfobjs[0x80000006] = eo
        eo = mfobj()
        eo.clr = fgcolor
        eo.type = 1
        self.mfobjs[0x80000007] = eo
        self.mfobjs[0x80000008] = eo ## NULL pen -- don't stroke
        eo = mfobj()
        eo.type = 3
        self.mfobjs[0x8000000d] = eo ## system font
        self.mfobjs[0x8000000e] = eo ## default font
        self.cmds = []


    def parse(self):
        emfcmd.parse(self)
        
class Face(gtk.DrawingArea):
    def __init__(self,page):
        self.page = page
        self.comms  = 10
        super(Face, self).__init__()
        self.connect("expose_event", self.expose)
        self._dragging = False # true if the interface is being dragged

    def expose(self, widget, event):
        self.ctx = widget.window.cairo_create()
        self.ctx.rectangle(event.area.x,event.area.y,event.area.width,event.area.height)
        self.ctx.clip()
        self.draw(self.ctx)
        return False
        
    def draw(self, ctx):
        print 'WxH: ',self.page.width,self.page.height
        self.render(ctx,self.page)
    
    def render(self,ctx,page):
        pass

class wmfFace(Face):
    def __init__(self,page):
        Face.__init__(self,page)
        
    def render(self,ctx,page):
        if self.page.width !=1 and self.page.height != 1:
            ctx.scale(self.page.width*1.*self.page.zoom,self.page.height*1.*self.page.zoom)
        wmfdraw.render(self,ctx)

class emfFace(Face):
    def __init__(self,page):
        Face.__init__(self,page)

    def render(self,ctx,page):
##        ctx.scale(self.page.zoom,self.page.zoom)
        emfdraw.render(self,ctx,page)
