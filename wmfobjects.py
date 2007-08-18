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

import wmfdoc

def CreatePalette(ctx,page,i):
    h,numofclr,data = page.cmds[i].args
    eo = wmfdoc.wmfobj()
    eo.type = 4
    for j in range(numofclr):
        clr = wmfdoc.color()
        clr.r,clr.g,clr.b = data[j*4],data[j*4+1],data[j*4+2]
        eo.palette[j]=clr
    page.wmfobjs[h]=eo
    print i,'Palette. Handle: ',h

def CreatePen(ctx,page,i):
    fgclr = wmfdoc.color()
    h,fgclr.r,fgclr.g,fgclr.b,width,style = page.cmds[i].args
    eo = wmfdoc.wmfobj()
    eo.type = 1
    eo.clr = fgclr
    eo.width = width
    eo.style = style
    page.wmfobjs[h]=eo
    print i,'Pen: ',fgclr.r,fgclr.g,fgclr.b,' Handle: ',h

def CreateBrushIndirect(ctx,page,i):
    bgclr = wmfdoc.color()
    h,bgclr.r,bgclr.g,bgclr.b,lbStyle,lbHatch = page.cmds[i].args
    eo = wmfdoc.wmfobj()
    eo.type = 2
    eo.clr = bgclr
    eo.style = lbStyle
    eo.hatch = lbHatch
    page.wmfobjs[h]=eo
    print i,'Brush: ',bgclr.r,bgclr.g,bgclr.b,lbStyle,' Handle: ',h

def DibCreatePatternBrush(ctx,page,i):
    h,biWidth,biHeight,biSize,bshift,data = page.cmds[i].args
    eo = wmfdoc.wmfobj()
    eo.type = 2
    eo.style = 3 ## pattern brush
    eo.data = biWidth,biHeight,biSize,bshift,data ## temporary assume 1 bpp image
    page.wmfobjs[h]=eo
    print i,'PatternBrush: ',biWidth,biHeight,bshift,' Handle: ',h

def CreateFontIndirect(ctx,page,i):
    h = page.cmds[i].args[0]
    eo = wmfdoc.wmfobj()
    eo.type = 3
    size = page.cmds[i].args[1][0]
    if size <0:
        size = -size
    if size == 0:
        size = 12
    eo.size = size
    eo.weight = page.cmds[i].args[1][4]
    eo.escape = page.cmds[i].args[1][2]
    eo.orient = page.cmds[i].args[1][3]
    eo.italic = page.cmds[i].args[1][5]
    eo.under = page.cmds[i].args[1][6]
    eo.strike = page.cmds[i].args[1][7]
    font = page.cmds[i].args[2]
    pos = font.find('\x00')
    font = font[0:pos]
    eo.font = font
    page.wmfobjs[h]=eo
    print i,'Font: ',font,size,eo.italic,eo.escape,eo.under,eo.weight,page.cmds[i].args[1],' Handle: ',h
