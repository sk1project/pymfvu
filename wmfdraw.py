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

import math
import gtk
import pango
import cairo
import pangocairo
import struct
import mfpage
import wmfcmd
import wmfobjects
import wmftext
import wmffigs

def render(self,ctx):
    print 'WMF render'
    page = self.page
    ctx.set_source_rgba(0,0,0,1)
    ctx.set_line_cap(1)
    ctx.set_line_join(1)
    page.txtclr.r,page.txtclr.g,page.txtclr.b = 0,0,0
    page.bkcolor.r,page.bkcolor.g,page.bkcolor.b = 255.,255.,255.
    page.txtalign = 0
    ctx.set_fill_rule(1) ## seems to be EMF default
    if page.hadj == 1:
        nums = len(page.cmds)
        print 'NUMS'
    else:
        nums = int(page.hadj.value)
    for i in range(nums):
        if drawcmds.has_key(page.cmds[i].type):
            drawcmds[page.cmds[i].type](ctx,page,i)

def shift(x,sz):
  return  0.5-(x*sz)%1

def convcoords(page,ctx,x,y):
    pdc = page.DCs[page.curdc]
    xr = (x-pdc.x)*1.*page.VPx/pdc.Wx + page.VPOx
    yr = (y-pdc.y)*1.*page.VPy/pdc.Wy + page.VPOy
    szx = 1.*page.width*page.zoom
    dx = shift(xr,szx)/szx
    szy = 1.*page.height*page.zoom
    dy = shift(yr,szy)/szy 
    return xr+dx,yr+dy

def convlen(page,ctx,dx,dy):
    pass
    
def SetBKMode(ctx,page,i):
    page.bkmode = page.cmds[i].args[0]

def SetBKColor(ctx,page,i):
    r,g,b,flag = page.cmds[i].args
    if flag !=1:
        page.bkcolor.r,page.bkcolor.g,page.bkcolor.b = r,g,b
    else:
        clr = page.mfobjs[curpal].palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        page.bkcolor.r,page.bkcolor.g,page.bkcolor.b = clr.r,clr.g,clr.b
   
def SelectObject(ctx,page,i):
    otype = {1:'Pen',2:'Brush',3:'Font',4:'Palette'}
    eonum = page.cmds[i].args
    if page.mfobjs.has_key(eonum): 
        eo = page.mfobjs[eonum]
        type = eo.type
        if type == 1:
            page.curfg = eonum
        if type == 2:
            page.curbg = eonum
        if type == 3:
            page.curfnt = eonum

def DeleteObject(ctx,page,i):
    pass

def SelectPalette(ctx,page,i):
    page.curpal = page.cmds[i].args

def SelectClipRegion(ctx,page,i):
    pass

def IntersectClipRect(ctx,page,i):
    b,r,t,l = page.cmds[i].args
    l,t = convcoords(page,ctx,l,t)
    r,b = convcoords(page,ctx,r,b)
    ctx.move_to(l,t)
    ctx.line_to(l,b)
    ctx.line_to(r,b)
    ctx.line_to(r,t)
    ctx.close_path()
    ctx.clip()
    
def SetWindowOrgEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.DCs[page.curdc].x = x
    page.DCs[page.curdc].y = y
    
def SetWindowExtEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.DCs[page.curdc].Wx = x
    page.DCs[page.curdc].Wy = y
    print i,'WinExtEx: ',page.cmds[i].args
    
def SetViewportExtEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.DCs[page.curdc].VPx = x
    page.DCs[page.curdc].VPy = y

def SetViewportOrgEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.DCs[page.curdc].VPOx = x
    page.DCs[page.curdc].VPOy = y

def SaveDC(ctx,page,i):
    ctx.save()
    dc = mfpage.DC()
    page.DCs.append(dc)
    page.DCs[page.curdc+1].VPOx =  page.DCs[page.curdc].VPOx
    page.DCs[page.curdc+1].VPOy = page.DCs[page.curdc].VPOy 
    page.DCs[page.curdc+1].VPx = page.DCs[page.curdc].VPx 
    page.DCs[page.curdc+1].VPy = page.DCs[page.curdc].VPy 
    page.DCs[page.curdc+1].Wx = page.DCs[page.curdc].Wx 
    page.DCs[page.curdc+1].Wy = page.DCs[page.curdc].Wy 
    page.DCs[page.curdc+1].x = page.DCs[page.curdc].x 
    page.DCs[page.curdc+1].y = page.DCs[page.curdc].y 
    page.curdc+=1

def RestoreDC(ctx,page,i):
    ctx.restore()
    page.DCs.pop()
    page.curdc-=1
    
import array        
darr = (array.array('b','\xff'+'\x00'*7),
            array.array('b','\x80'*8),
            array.array('b','\x01\x02\x04\x08\x10\x20\x40\x80'),
            array.array('b','\x80\x40\x20\x10\x08\x04\x02\x01'),
            array.array('b','\xFF'+'\x80'*7),
            array.array('b','\x81\x42\x24\x18\x18\x24\x42\x81'))

def FillPath(ctx,page,i):
    ctx.save()
    matrix = cairo.Matrix(1./page.width,0,0,1./page.height,0,0)
    ctx.transform(matrix)
    eonum = page.curbg
    if eonum == 0x80000005 or page.mfobjs[eonum].style == 1: ## bkmode is temporary before hatch/bitmap brushes
        pass
    else:
        eo = page.mfobjs[eonum]
        if eo.style == 2 or eo.style == 3:
            if eo.style == 2:
                data = darr[eo.hatch]
                w,h = 8,8
            if eo.style == 3:
                w = eo.data[0]
                h = eo.data[1]
                bmpsize = struct.pack('<I',eo.data[2])
                bmpshift = struct.pack('<I',eo.data[3])
                bmp = '\x42\x4d'+bmpsize+'\x00\x00\x00\x00'+bmpshift+eo.data[4]
                pixbufloader = gtk.gdk.PixbufLoader()
                pixbufloader.write(bmp)
                pixbufloader.close()
                pixbuf = pixbufloader.get_pixbuf()
                cs = cairo.ImageSurface(0,w,h)
                ct = cairo.Context(cs)
                ct2 = gtk.gdk.CairoContext(ct)
                ct2.set_source_pixbuf(pixbuf,0,0)
                ct2.paint()
            if page.bkmode == 2:
                r = page.bkcolor.r
                g = page.bkcolor.g
                b = page.bkcolor.b
                ctx.set_source_rgba(r/255.,g/255.,b/255.,page.alpha)
                ctx.fill_preserve()
            StrokePathPreserve(ctx,page,i)
            if eo.flag !=1:
                r,g,b = eo.clr.r,eo.clr.g,eo.clr.b
            else:
                clr = page.palette[eo.clr.r]  ## FIXME! have to be 2 byte made of R and G.
                r,g,b = clr.r,clr.g,clr.b
                
            ctx.set_source_rgba(r/255.,g/255.,b/255.,page.alpha)

            if eo.style != 3:
                cs = cairo.ImageSurface.create_for_data(data,3,w,h,1)
                pat = cairo.SurfacePattern(cs)
                pat.set_filter(5)
                pat.set_extend(1)
                ctx.save()
                ctx.clip()
                ctx.scale(.8/page.scale+0.5,.8/page.scale+0.5)
                ctx.mask(pat)
                ctx.restore()
            else:
                pat = cairo.SurfacePattern(cs)
                pat.set_filter(5)
                pat.set_extend(1)
                ctx.save()
                ctx.clip()
                ctx.scale(.8/page.scale+0.5,.8/page.scale+0.5)
                ctx.set_source(pat)
                ctx.paint()
                ctx.restore()
        else:
            if eo.flag !=1:
                r,g,b = eo.clr.r,eo.clr.g,eo.clr.b
            else:
                clr = page.palette[eo.clr.r]  ## FIXME! have to be 2 byte made of R and G.
                r,g,b = ord(clr.r),ord(clr.g),ord(clr.b)

            ctx.set_source_rgba(r/255.,g/255.,b/255.,page.alpha)
            ctx.fill_preserve()
    ctx.restore()
    
capjoin = {0:1,1:2,2:0}
cap = {0:'Flat',1:'Round',2:'Square'}
join = {0:'Miter',1:'Round',2:'Bevel'}

def StrokePath(ctx,page,i):
    eonum = page.curfg
    ctx.save()
    if eonum == 0x80000008 or page.mfobjs[eonum].style == 5:
        ctx.set_line_width(0)
        ctx.stroke()
    else:
        eo = page.mfobjs[eonum]
        style = eo.style&0xF
        if eo.width < 2.1 or (style > 0 and style < 5):
            eo.width = 1./(page.scale*page.zoom)
        matrix = cairo.Matrix(1./page.width,0,0,1./page.height,0,0)
        ctx.transform(matrix)
        ctx.set_line_width(eo.width)    
        lcap,ljoin = 0,0
        if (eo.style&0xF00)>>8 <3:
            lcap = capjoin[(eo.style&0xF00)>>8]
        if (eo.style&0xF000)>>12 < 3:
            ljoin = capjoin[(eo.style&0xF000)>>12]
        ctx.set_line_cap(lcap)
        ctx.set_line_join(ljoin)
        if style > 5:
            style = 0
        if style > 0 and page.bkmode == 2:
            ctx.set_dash(dashes[0],len(dashes[0])/2)
            r = page.bkcolor.r
            g = page.bkcolor.g
            b = page.bkcolor.b
            ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
            ctx.stroke_preserve()

        ctx.set_dash(dashes[style],len(dashes[style])/2)
        if eo.flag !=1:
            r,g,b = eo.clr.r,eo.clr.g,eo.clr.b
        else:
            clr = page.palette[eo.clr.r]  ## FIXME! have to be 2 byte made of R and G.
            r,g,b = ord(clr.r),ord(clr.g),ord(clr.b)
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1.)
        ctx.stroke()
    ctx.restore()

def CloseFigure(ctx,page,i):
    ctx.close_path()

def StrokeAndFillPath(ctx,page,i):
    FillPath(ctx,page,i)
    StrokePath(ctx,page,i)
    
def SetTextColor(ctx,page,i):
    r,g,b,flag = page.cmds[i].args
    if flag !=1:
        page.txtclr.r,page.txtclr.g,page.txtclr.b = r,g,b
    else:
        clr = page.palette[r]  ## FIXME! have to be 2 byte made of R and G.
        page.txtclr.r,page.txtclr.g,page.txtclr.b = ord(r),ord(g),ord(b)

def SetTextAlign(ctx,page,i):
    page.txtalign = page.cmds[i].args
    
def StretchDIBits(ctx,page,i):
    ctx.save()
    matrix = cairo.Matrix(1./page.width,0,0,1./page.height,0,0)
    ctx.transform(matrix)
    y = page.cmds[i].args[0]				##xDest
    x = page.cmds[i].args[1]				##yDest
    x,y = convcoords(page,ctx,x,y)
    dx = page.cmds[i].args[2]				##cxSrc
    dy = page.cmds[i].args[3]				##cySrc
    bmpsize = struct.pack('<I',page.cmds[i].args[4])	##nSize-header+14
    bmpshift = struct.pack('<I',page.cmds[i].args[5])	##calculated shift to the bitmap data (stored after palette, if any palette exists)
    dxdst = page.cmds[i].args[6]			##cxDest
    dydst = page.cmds[i].args[7]			##cyDest
    dwROP = page.cmds[i].args[8]			##dwRop
    bmpdata = page.cmds[i].args[9]			##data
    bmp = '\x42\x4d'+bmpsize+'\x00\x00\x00\x00'+bmpshift+bmpdata
    pixbufloader = gtk.gdk.PixbufLoader()
    pixbufloader.write(bmp)
    pixbufloader.close()
    pixbuf = pixbufloader.get_pixbuf()
    ctx.save()
    ctx.translate(x,y)
    ctx.scale(dxdst*1./dx,dydst*1./dy)
    if dwROP == 0xee0086: ## SRCPAINT
        cssize = max(abs(dx),abs(dy))
        cs = cairo.ImageSurface(0,cssize,cssize)
        ct = cairo.Context(cs)
        ct2 = gtk.gdk.CairoContext(ct)
        ct2.set_source_pixbuf(pixbuf,0,0)
        ct2.paint()
        page.mask = cs
    if dwROP == 0x8800c6: ##SRCAND
        ctx.set_source_pixbuf(pixbuf,0,0)
        ctx.mask_surface(page.mask)
    if dwROP == 0xcc0020: ## SRCCOPY
        ctx.set_source_pixbuf(pixbuf,0,0)
        ctx.paint()
    ctx.restore()
    ctx.restore()
  
def SetPolyfillMode(ctx,page,i):
    ctx.set_fill_rule(page.cmds[i].args)
    
def StrokePathPreserve(ctx,page,i):
    eonum = page.curfg
    if eonum == 0x80000008 or page.mfobjs[eonum].style == 5:
        ctx.set_line_width(0)
        ctx.stroke()
    else:
        eo = page.mfobjs[eonum]
        if eo.flag !=1:
                r,g,b = eo.clr.r,eo.clr.g,eo.clr.b
        else:
            clr = page.palette[eo.clr.r]  ## FIXME! have to be 2 byte made of R and G.
            r,g,b = ord(clr.r),ord(clr.g),ord(clr.b)

        if eo.style > 5:
            eo.style = 0
        ctx.set_dash(dashes[eo.style],len(dashes[eo.style])/2)
        if eo.width <2:
            eo.width = 1+page.DCs[page.curdc].Wx/1024
        ctx.set_line_width(eo.width)
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1.)
        ctx.stroke_preserve()

##----------------------------------------------------------------------------------------------------------------------------------------------------------##
##----------------------------------------------------------------------------------------------------------------------------------------------------------##
##----------------------------------------------------------------------------------------------------------------------------------------------------------##
drawcmds  = {
            30:SaveDC, 295:RestoreDC, ##332:ResetDc, 
            
            ##53:'RealizePalette', 55:'SetPalEntries',
            247:wmfobjects.CreatePalette, ##313:'ResizePalette',1078:'AnimatePalette', 
            564:SelectPalette, 
            ##79:'StartPage', 80:'EndPage', 82:'AbortDoc', 94:'EndDoc', 333:'StartDoc', 
            
            ##248:CreateBrush, 505:'CreatePatternBrush',
            322:wmfobjects.DibCreatePatternBrush,
            762:wmfobjects.CreatePen,763:wmfobjects.CreateFontIndirect,
            764:wmfobjects.CreateBrushIndirect, ##765:'CreateBitmapIndirect', 
            496:DeleteObject, 301:SelectObject, 
            
            258:SetBKMode, ##259:SetMapMode, 260:SetROP2,
            262:SetPolyfillMode, ##263:SetStretchBltMode,##261:SetRelabs,
            ##561:SetMapperFlags, 
            ## 264:'SetTextCharExtra',
            302:SetTextAlign, 513:SetBKColor,
            521:SetTextColor, ##522:SetTextJustification, 
            
            ##298:'InvertRegion', 299:'PaintRegion',
            300:SelectClipRegion, ##544:'OffsetClipRgn', 552:'FillRegion', 1065:'FrameRegion', 1791:'CreateRegion',
            ##1045:'ExcludeClipRect',
            1046:IntersectClipRect,
            523:SetWindowOrgEx, 524:SetWindowExtEx,525:SetViewportOrgEx, 526:SetViewportExtEx, ##527:'OffsetWindowOrg', 529:'OffsetViewportOrgEx',
            ##1040:'ScaleWindowExtEx', 1042:'ScaleViewportExtEx',
            
            ##1049:'FloodFill', 1321:'META_MAGIC???', 1352:'ExtFloodFill', 1574:'Escape', 
            
            531:wmffigs.LineTo, 532:wmffigs.MoveTo, 804:wmffigs.Polygone, 805:wmffigs.Polyline, 1048:wmffigs.Ellipse, 1051:wmffigs.Rectangle, ##1055:'SetPixel', 
            1336:wmffigs.PolyPolygone, 1564:wmffigs.RoundRect, 2071:wmffigs.Arc, 2074:wmffigs.Pie, 2096:wmffigs.Chord, 
            1313:wmftext.TextOut, ##1313 is TextOut
            ## 1583:DrawText,
            2610:wmftext.ExtTextOut,
            #1790:'CreateBitmap', 1565:'PatBlt', 2338:'BitBlt', 2368:'DibBitblt', 2851:'StretchBlt', 2881:'DibStretchBlt', 3379:'SetDibToDev',
           3907:StretchDIBits
            }
            

dashes = ((), #solid
                (480.5,160.5), #dash
                (80.5,100.5), #dot
                (240.5,160.5,100.5,160.5), #dashdot
                (240.5,80.5,80.5,80.5,80.5,80.5)) #dashdotdot

