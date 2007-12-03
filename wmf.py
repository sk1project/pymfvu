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

import gmodel

class State:
    def __init__(self):
        self.DCs = []
        self.clips = []
        dc = DC()
        self.DCs.append(dc)
        self.curdc = 0
        self.curobj = 0        
        self.mfobjs = {}
        self.curpen = 0
        self.curbrush = 0
        self.curpal = 0
        self.curfnt = 0
        self.palette = {}
        self.txt = TXT()
        self.bk = BK()
        self.maxobj = 0
        self.ROP2 = None
        self.PFMode = 1 ## set_fill_rule in cairo terms
        self.zoomx = 1
        self.zoomy = 1
        self.clipflag = 0 ## supposed to be copyied to Shape.clipflag and dropped
        
    def usage():
        class_DCs = DC()

    def obj_init(self):
        bgcolor = Color()
        bgcolor.r,bgcolor.g,bgcolor.b = (255.,255.,255.)
        bgcolor2 = Color()
        bgcolor2.r,bgcolor2.g,bgcolor2.b = (192.,192.,192.)
        bgcolor3 = Color()
        bgcolor3.r,bgcolor3.g,bgcolor3.b = (128.,128.,128.)
        bgcolor4 = Color()
        bgcolor4.r,bgcolor4.g,bgcolor4.b = (64.,64.,64.)
        fgcolor = Color()
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
        
class BK:
    def __init__(self):
        self.mode = 0
        self.color = Color()
        self.color.r,self.color.g,self.color.b = 255.,255.,255.

class Color:
    r = 0
    g = 0
    b = 0
    a = 1
    
class TXT:
    def __init__(self):    
        self.color = Color()
        self.align = 0
    
class DC:
    def __init__(self):
        self.VPx = 1.
        self.VPy = 1.
        self.VPOx = 0.
        self.VPOy = 0.
        self.Wx = 1.
        self.Wy = 1.
        self.x = 0.
        self.y = 0.
        self.p0x = 0.
        self.p0y = 0.
        self.trafo = None
        self.trafomode = 0
        self.pathmode = 0
        self.pathobj = 0
        self.clipset = 0 ## if clip was touched in the DC
        self.cliplist = []

    def usage():
        class_cliplist = gmodel.Path()
        
class mfobj:
    def __init__(self):
        self.type = 0 # 1-- pen, 2 -- brush, 3 -- font
        self.clr = Color()
        self.width = 5. ## use for pen
        self.font = 'Arial'
        self.italic = 0
        self.size = 20
        self.style = 0
        self.escape = 0
        self.orient = 0
        self.under = 0
        self.strike = 0
        self.charset = 1
        self.hatch = 0
        self.data = None
        self.weight = 0
