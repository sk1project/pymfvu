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
import emfdoc
import emfcmd

## horiz 0 -
## vertc 1 |
## fdiag 2 \
## bdiag 3 /
## cross 4 +
## dcros 5 x

def render(self,ctx,page):
    drawcmds = {0:Noop,2:Polybezier,3:Polygone,4:Polyline,5:PolybezierTo,6:PolylineTo,7:PolyPolyline,8:PolyPolygone,\
                        27:MoveTo,54:LineTo,55:ArcTo,42:Ellipse,43:Rectangle,44:RoundRect,45:Arc,46:Chord,47:Pie,\
                        84:ExtTextOutW,82:ExtCreateFontIndirectW,22:SetTextAlign,24:SetTextColor,\
                        9:SetWindowExtEx,10:SetWindowOrgEx,11:SetViewportExtEx,12:SetViewportOrgEx,\
                        33:SaveDC,34:RestoreDC,35:SetWorldTransform,36:ModifyWorldTransform,\
                        37:SelectObject,38:CreatePen,39:CreateBrushIndirect,40:DeleteObject,95:ExtCreatePen,\
                        59:BeginPath,60:EndPath,61:CloseFigure,62:FillPath, 63:StrokeAndFillPath,64:StrokePath,67:SelectClipPath,\
                        81:StretchDIBits,19:SetPolyfillMode}
    ctx.set_source_rgba(0,0,0,1)
    ctx.set_fill_rule(0) ## seems to be EMF default
##    nums = len(page.cmds)
    nums = int(page.hadj.value)+1
    for i in range(nums):
        if drawcmds.has_key(page.cmds[i].type):
            drawcmds[page.cmds[i].type](ctx,page,i)
        else:
            print i,'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^UNSUPPORTED: ',emfcmd.emr_ids[page.cmds[i].type],page.cmds[i].args

def convx(page,x):
    xr = (x- page.x)*(page.VPx*1./page.Wx)+page.VPOx
    return xr

def convy(page,y):
    yr = (y- page.y)*(page.VPy*1./page.Wy)+page.VPOy
    return yr
    
def Noop(ctx,page,i):
    pass
    
def Polybezier(ctx,page,i):
    x0,y0 = ctx.get_current_point()
    x,y = page.cmds[i].args[0]
    x = convx(page,x)
    y = convy(page,y)
    ctx.move_to(x,y)
    print i,'Polybezier: ',x0,y0,x,y
    for j in range(len(page.cmds[i].args)/3):
        x1,y1 = page.cmds[i].args[j*3+1]
        x1 = convx(page,x1)
        y1 = convy(page,y1)
        x2,y2 = page.cmds[i].args[j*3+2]
        x2 = convx(page,x2)
        y2 = convy(page,y2)
        x3,y3 = page.cmds[i].args[j*3+3]
        x3 = convx(page,x3)
        y3 = convy(page,y3)
        ctx.curve_to(x1,y1,x2,y2,x3,y3)
##    ctx.set_source_rgba(1,1,0,0.5)  ## for debug
##    ctx.stroke()
##    StrokePath(ctx,page,i) ## WRONG
    
def Polygone(ctx,page,i):
    x,y = page.cmds[i].args[1][0]
    x = convx(page,x)
    y = convy(page,y)
    ctx.move_to(x,y)
    for j in range(len(page.cmds[i].args[1])):
        x,y = page.cmds[i].args[1][j]
        x = convx(page,x)
        y = convy(page,y)
        ctx.line_to(x,y)
    print i,'Polygone: ',page.cmds[i].args[1]
    FillPath(ctx,page,i)
    StrokePath(ctx,page,i)

def Polyline(ctx,page,i):
    x,y = page.cmds[i].args[0]
    x = convx(page,x)
    y = convy(page,y)
    ctx.move_to(x,y)
    print i,'Polyline: ',page.cmds[i].args[0]
    PolylineTo(ctx,page,i)
    StrokePath(ctx,page,i)

def PolybezierTo(ctx,page,i):
    for j in range(len(page.cmds[i].args)/3):
        x1,y1 = page.cmds[i].args[j*3]
        x1 = convx(page,x1)
        y1 = convy(page,y1)
        x2,y2 = page.cmds[i].args[j*3+1]
        x2 = convx(page,x2)
        y2 = convy(page,y2)
        x3,y3 = page.cmds[i].args[j*3+2]
        x3 = convx(page,x3)
        y3 = convy(page,y3)
        ctx.curve_to(x1,y1,x2,y2,x3,y3)
    print i,'PolybezierTo: ',page.cmds[i].args

def PolylineTo(ctx,page,i):
    for j in range(len(page.cmds[i].args)):
        x1,y1 = page.cmds[i].args[j]
        x1 = convx(page,x1)
        y1 = convy(page,y1)
        ctx.line_to(x1,y1)
    print i,'PolylineTo: ',page.cmds[i].args
    
def PolyPolyline(ctx,page,i):
    aPolyCounts = page.cmds[i].args[0]
    aptl = page.cmds[i].args[1]
    shift = 0
    for k in range(len(aPolyCounts)): ## number of polygones
        x,y = aptl[shift]
        x = convx(page,x)
        y = convy(page,y)
        ctx.move_to(x,y)
        for j in range(aPolyCounts[k]-1): ## number of gones for i-th polygone
            x,y = aptl[j+1+shift]
            x = convx(page,x)
            y = convy(page,y)
            ctx.line_to(x,y)
        shift+=aPolyCounts[k]
        print i,'Poly  Polyline: ',k,shift
##    FillPathPreserve(ctx,page,i)
##    StrokePath(ctx,page,i)
    
def PolyPolygone(ctx,page,i):
    aPolyCounts = page.cmds[i].args[0]
    aptl = page.cmds[i].args[1]
    shift = 0
    for k in range(len(aPolyCounts)): ## number of polygones
        x,y = aptl[shift]
        x = convx(page,x)
        y = convy(page,y)
        ctx.move_to(x,y)
        for j in range(aPolyCounts[k]-1): ## number of gones for i-th polygone
            x,y = aptl[j+1+shift]
            x = convx(page,x)
            y = convy(page,y)
            ctx.line_to(x,y)
        shift+=aPolyCounts[k]
        print i,'Poly  Polygone: ',k,shift
    FillPath(ctx,page,i)
    StrokePath(ctx,page,i)
    
def SetWorldTransform(ctx,page,i):
    em11,em12,em21,em22,dx,dy,mode = page.cmds[i].args
    matrix = cairo.Matrix(em11,em12,em21,em22,dx,dy)
    ctx.set_matrix(matrix)
    print i,'----------------- Initialize World! -------------------'
    
def ModifyWorldTransform(ctx,page,i):
    em11,em12,em21,em22,dx,dy,mode = page.cmds[i].args
    curmtrx = ctx.get_matrix()
    matrix = cairo.Matrix(em11,em12,em21,em22,dx,dy)
    if mode == 1 or mode > 3:
        ctx.set_matrix(matrix)
    if mode == 2:
        ctx.transform(matrix)
    if mode == 3:
        ctx.set_matrix(matrix)
        ctx.transform(curmtrx)
    print i,'------------------ MODIFY WORLD! -----------------------',mode,em11,em12,em21,em22,dx,dy

def ExtTextOutW(ctx,page,i):
    x,y,ye,text = page.cmds[i].args
#    size = (convy(page,1)-convy(page,0))*page.emfobjs[page.curfnt].size
    size = 0.9*(ye-y)
    txtalign ={0:0,6:1,2:2,8:0,14:1,16:2,18:0,24:1,20:2}
    alignh = txtalign[page.txtalign]
    if page.txtalign < 8:
        ctx.move_to(x,y)
    else:
        ctx.move_to(x,ye)
    if page.txtalign > 17:
        ctx.move_to(x,y+0.8*size) ##have to get baseline here
    layout = ctx.create_layout()
    eonum = page.curfnt
    eo = page.emfobjs[eonum]
    bld = ''
    itl = ''
    if eo.weight > 400:
        bld = 'Bold '
    if eo.italic !=0:
        itl = 'Italic '
    FONT = eo.font+' '+bld+itl+str(size/1.4)##*yscale/10.)##page.scale)
    fdesc = pango.FontDescription(FONT)
    ctx.set_source_rgba(page.txtclr.r/255.,page.txtclr.g/255.,page.txtclr.b/255.,1)
##    ctx.set_source_rgba(0,0,0,1)
    layout.set_font_description(fdesc)
    layout.set_alignment(alignh)
    layout.set_text(text)
    ctx.show_layout(layout)
##    ctx.restore()
    print 'Text: %u %u %s'%(x,y,text), FONT,page.txtclr.r,page.txtclr.g,page.txtclr.b,'SCALE: ',eo.size,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    
def SelectObject(ctx,page,i):
    eonum = page.cmds[i].args
    if page.emfobjs.has_key(eonum): ## I don't use TEXT things yet
        eo = page.emfobjs[eonum]
        type = eo.type
        if type == 1:
            page.curfg = eonum
        if type == 2:
            page.curbg = eonum
        if type == 3:
            page.curfnt = eonum
        print i,'Select Obj: %x %u'%(eonum,type)
    else:
        print i,'!!!!!!!!!! Select Unexist Obj: %x !!!!!!!!!!!!!!'%eonum

def DeleteObject(ctx,page,i):
    print i,'Delete Obj: ',page.cmds[i].args

def SelectClipPath(ctx,page,i):
    ctx.clip()
    print i,'Select clip path'

def SetWindowOrgEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.x = x
    page.y = y
    print i,'WinOrgEx: ',page.cmds[i].args

def SetWindowExtEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.Wx = x
    page.Wy = y
    print i,'WinExtEx: ',page.cmds[i].args

def SetViewportExtEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.VPx = x
    page.VPy = y
    print i,'ViewportExtEx: ',page.cmds[i].args

def SetViewportOrgEx(ctx,page,i):
    x,y = page.cmds[i].args
    page.VPOx = x
    page.VPOy = y
    print i,'ViewportOrgEx: ',page.cmds[i].args

def SaveDC(ctx,page,i):
    ctx.save()
    print i,'Save ctx'

def RestoreDC(ctx,page,i):
    ctx.restore()
    print i,'Restore ctx'
    
def CreatePen(ctx,page,i):
    fgclr = emfdoc.color()
    h,fgclr.r,fgclr.g,fgclr.b,width = page.cmds[i].args
    eo = emfdoc.emfobj()
    eo.type = 1
    eo.clr = fgclr
    eo.width = width
    page.emfobjs[h]=eo
    print i,'Pen: ',fgclr.r,fgclr.g,fgclr.b,' Handle: ',h

def ExtCreatePen(ctx,page,i):
    fgclr = emfdoc.color()
    h,fgclr.r,fgclr.g,fgclr.b = page.cmds[i].args
    eo = emfdoc.emfobj()
    eo.type = 1
    eo.clr = fgclr
    eo.width = 5. ## what is default?
    page.emfobjs[h]=eo
    print i,'ExtPen: ',fgclr.r,fgclr.g,fgclr.b,' Handle: ',h

def CreateBrushIndirect(ctx,page,i):
    bgclr = emfdoc.color()
    h,bgclr.r,bgclr.g,bgclr.b = page.cmds[i].args
    eo = emfdoc.emfobj()
    eo.type = 2
    eo.clr = bgclr
    page.emfobjs[h]=eo
    print i,'Brush: ',bgclr.r,bgclr.g,bgclr.b,' Handle: ',h
        
def FillPath(ctx,page,i):
    eonum = page.curbg
    if eonum == 0x80000005:
        print 'NO FILL'
    else:
        eo = page.emfobjs[eonum]
        r = eo.clr.r
        g = eo.clr.g
        b = eo.clr.b
        ctx.set_source_rgba(r/255.,g/255.,b/255.,page.alpha)
        ctx.fill_preserve()
        print i,'Fill %x'%eonum,r,g,b
 
def StrokePath(ctx,page,i):
    eonum = page.curfg
    if eonum == 0x80000008:
        print 'NO STROKE'
    else:
        eo = page.emfobjs[eonum]
        r = eo.clr.r
        g = eo.clr.g
        b = eo.clr.b
        ctx.set_line_width(0.1*eo.width/page.zoom)
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
        ctx.stroke()
        print i,'Stroke %x'%eonum,r,g,b,eo.width

def BeginPath(ctx,page,i):
    ctx.new_path()
    print i,'BeginPath'

def EndPath(ctx,page,i):
    ctx.close_path()
    print i,'EndPath'

def CloseFigure(ctx,page,i):
    ctx.close_path()
    print i,'CloseFigure'

def StrokeAndFillPath(ctx,page,i):
    FillPathPreserve(ctx,page,i)
    StrokePath(ctx,page,i)
    print i,'Fill&Stroke'

def MoveTo(ctx,page,i):
    x,y = page.cmds[i].args
    x = convx(page,x)
    y = convy(page,y)
    ctx.move_to(x,y)
    print i,'MoveTo ',page.cmds[i].args
    
def LineTo(ctx,page,i):
    x,y = page.cmds[i].args
    x = convx(page,x)
    y = convy(page,y)
    ctx.line_to(x,y)
    print i,'LineTo ',page.cmds[i].args

def Ellipse(ctx,page,i):
    x,y = ctx.get_current_point()
    x = convx(page,x)
    y = convy(page,y)
    x1,y1,x2,y2 = page.cmds[i].args
    x1 = convx(page,x1)
    y1 = convy(page,y1)
    x2 = convx(page,x2)
    y2 = convy(page,y2)
    xc = 0.5*(x1+x2)
    yc = 0.5*(y1+y2)
    dx = x2-x1
    dy = y2-y1
    print i,'Ellipse: c(%u %u) d(%u %u)'%(xc,yc,dx,dy)
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(dx/2., 0)
    ctx.scale(dx/2., dy/2.)
    ctx.arc(0.,0.,1.,0.,2*math.pi)
    ctx.restore()
    FillPath(ctx,page,i)
    StrokePath(ctx,page,i)

def Arc(ctx,page,i):
    l,t,r,b,xs,ys,xe,ye = page.cmds[i].args
    xc = convx(page,(l+r)/2.)
    yc = convy(page,(t+b)/2.)
    dx = math.fabs(r-l)
    dy = math.fabs(b-t)
    ang1 = math.atan2((ys-yc),(xs-xc))
    ang2 = math.atan2((ye-yc),(xe-xc))
    x1 = math.cos(ang1)
    y1 = math.sin(ang1)
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(x1,y1)
    ctx.scale(dx/2., dy/2.)
    ctx.arc_negative(0.,0.,1.,ang1,ang2)
    ctx.restore()
    
def ArcTo(ctx,page,i):
    l,t,r,b,xs,ys,xe,ye = page.cmds[i].args
    xc = convx(page,(l+r)/2.)
    yc = convy(page,(t+b)/2.)
    dx = math.fabs(r-l)
    dy = math.fabs(b-t)
    ang1 = math.atan2((ys-yc),(xs-xc))
    ang2 = math.atan2((ye-yc),(xe-xc))
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.scale(dx/2., dy/2.)
    ctx.arc_negative(0.,0.,1.,ang1,ang2)
    ctx.restore()
    
def Chord(ctx,page,i):
    Arc(ctx,page,i)
    ctx.close_path()
    FillPathPreserve(ctx,page,i)
    StrokePath(ctx,page,i)

def Pie(ctx,page,i):
    l,t,r,b,xs,ys,xe,ye = page.cmds[i].args
    xc = convx(page,(l+r)/2.)
    yc = convy(page,(t+b)/2.)
    Arc(ctx,page,i)
    ctx.line_to(xc,yc)
    ctx.close_path()
    FillPathPreserve(ctx,page,i)
    StrokePath(ctx,page,i)

def Rectangle(ctx,page,i):
    x1,y1,x2,y2 = page.cmds[i].args
    x1 = convx(page,x1)
    y1 = convy(page,y1)
    x2 = convx(page,x2)
    y2 = convy(page,y2)
    ctx.move_to(x1,y1)
    ctx.line_to(x1,y2)
    ctx.line_to(x2,y2)
    ctx.line_to(x2,y1)
    ctx.close_path()
    FillPathPreserve(ctx,page,i)
    StrokePath(ctx,page,i)
    
def RoundRect(ctx,page,i):
    x1,y1,x2,y2,cx,cy = page.cmds[i].args
    x1 = convx(page,x1)
    y1 = convy(page,y1)
    x2 = convx(page,x2)
    y2 = convy(page,y2)
    if x1 > x2:
        x = x1
        x1 = x2
        x2 = x
    if y1 > y2:
        x = y1
        y1 = y2
        y2 = x
    ctx.move_to(x2-cx/2.,y1)
    ## here elliptical arc to next point (x2,y1+cy/2) xc = x2-cx/2., yc = y1+cy/2.  90 0
    xc = x2-cx/2.
    yc = y1+cy/2.
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(x2-cx/2.-xc,y1-yc)
    ctx.scale(cx/2., cy/2.)
    ctx.arc_negative(0.,0.,1.,0.5*math.pi,0)
    ctx.restore()
    ctx.line_to(x2,y2-cy/2.)
    ## here elliptical arc to next point x2-cx/2. ,y2  xc = x2-cx/2.,yc=y2-cy/2.  0 -90
    xc = x2-cx/2.
    yc = y2-cy/2.
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(x2-xc,y2-cy/2.-yc)
    ctx.scale(cx/2., cy/2.)
    ctx.arc_negative(0.,0.,1.,0,-0.5*math.pi)
    ctx.restore()
    ctx.line_to(x1+cx/2.,y2)
    ## here elliptical arc to next point x1,y2-cy/2.  xc = x1+cx/2.,yc=y2-cy/2.  -90  180
    xc = x1+cx/2.
    yc = y2-cy/2.
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(x1+cx/2.-xc,y2-yc)
    ctx.scale(cx/2., cy/2.)
    ctx.arc_negative(0.,0.,1.,-0.5*math.pi,math.pi)
    ctx.restore()
    ctx.line_to(x1,y1+cy/2.)
    ## here elliptical arc to next point x1+cx/2,y1  xc = x1+cx/2.,yc=y1+cy/2.  180  90
    xc = x1+cx/2.
    yc = y2-cy/2.
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(x1-xc,y1+cy/2.-yc)
    ctx.scale(cx/2., cy/2.)
    ctx.arc_negative(0.,0.,1.,math.pi,0.5*math.pi)
    ctx.restore()
    ctx.close_path()
    FillPath(ctx,page,i)
    StrokePath(ctx,page,i)
    
def ExtCreateFontIndirectW(ctx,page,i):
    h = page.cmds[i].args[0]
    size = page.cmds[i].args[1]
    if size <0:
        size = -size
    weight = page.cmds[i].args[5]
    italic = page.cmds[i].args[6]
    font = page.cmds[i].args[14]
    font = unicode(font,'utf-16').encode('utf-8')
    pos = font.find('\x00')
    font = font[0:pos]
    eo = emfdoc.emfobj()
    eo.type = 3
    eo.font = font
    eo.italic = italic
    eo.size = size
    eo.weight = weight
    page.emfobjs[h]=eo
    print i,'Font: ',font,italic,weight,page.cmds[i].args[1],' Handle: ',h

def SetTextColor(ctx,page,i):
    page.txtclr.r,page.txtclr.g,page.txtclr.b = page.cmds[i].args
    print i,'Text Color: ',page.txtclr.r,page.txtclr.g,page.txtclr.b

def SetTextAlign(ctx,page,i):
    page.txtalign = page.cmds[i].args
    print i,'Text Align: ',page.txtalign

def StretchDIBits(ctx,page,i):
##    x = convx(page,page.cmds[i].args[0])
##    y = convy(page,page.cmds[i].args[1])
    x = page.cmds[i].args[0]				##xDest
    y = page.cmds[i].args[1]				##yDest
    dx = page.cmds[i].args[2]				##cxSrc
    dy = page.cmds[i].args[3]				##cySrc
    bmpsize = struct.pack('<I',page.cmds[i].args[4])	##nSize-header+14
    bmpshift = struct.pack('<I',page.cmds[i].args[5])	##cbBmiSrc+14
    dxdst = page.cmds[i].args[6]			##cxDest
    dydst = page.cmds[i].args[7]			##cyDest
    dwROP = page.cmds[i].args[8]			##dwRop
    bmpdata = page.cmds[i].args[9]			##data
    bmp = '\x42\x4d'+bmpsize+'\x00\x00\x00\x00'+bmpshift+bmpdata
    pixbufloader = gtk.gdk.PixbufLoader()
    pixbufloader.write(bmp)
    f = open('file_%u_%x'%(i,dwROP)+'.bmp','w')
    f.write(bmp)
    f.flush()
    f.close()
    pixbufloader.close()
    pixbuf = pixbufloader.get_pixbuf()
    ctx.save()
    ctx.translate(x,y)
    ctx.scale(dxdst*1./dx,dydst*1./dy)
    if dwROP == 0xee0086: ## SRCPAINT
        cs = cairo.ImageSurface(3,dxdst,dydst)
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
    print i,'Bitmap: %u %u %u %u ROP: %x'%(x,y,dxdst,dydst,dwROP)
    
def SetPolyfillMode(ctx,page,i):
    ctx.set_fill_rule(page.cmds[i].args)
