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
import pywmf
import wmfdraw
import hexdump
import wmfcmd

class Page:
    def __init__(self):
        self.Face = Face(self)
        self.alpha = 1
        self.file = pywmf.WMF()
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
        self.wmfobjs = {}
        self.palette = {}
        self.cmds = []
        self.txtclr = color()
        self.txtclr.r = 0.
        self.txtclr.g = 0.
        self.txtclr.b = 0.
        self.txtalign = 0
        self.bkmode = 0
        self.bkcolor = color()
        self.bkcolor.r,self.bkcolor.g,self.bkcolor.b = 255.,0.,0.
    def usage():
        class_cmds = cmd()
        class_DCs = DC()

    def parse(self):
        wmfcmd.parse(self)

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

class wmfobj:
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

class Face(gtk.DrawingArea):
    def __init__(self,page):
        self.page = page
        self.comms  = 10
        super(Face, self).__init__()
        self.connect("expose_event", self.expose)
        self._dragging = False # true if the interface is being dragged
        self.page.width = 1.
        self.page.height = 1.
        
    def expose(self, widget, event):
        self.ctx = widget.window.cairo_create()
        self.ctx.rectangle(event.area.x, event.area.y,event.area.width, event.area.height)
        self.ctx.clip()
        self.draw(self.ctx)
        return False

    def draw(self, ctx):
        ratio = 1
        print 'W/H/R: ',self.page.width,self.page.height,ratio
        if self.page.width !=1 and self.page.height != 1:
            matrix = cairo.Matrix(ratio*self.page.width*1.*self.page.zoom,0,0,ratio*self.page.height*1.*self.page.zoom,0,0)
            ctx.transform(matrix)
        wmfdraw.render(self,ctx)
        
