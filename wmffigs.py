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

import wmfdraw
import math
import struct
import cairo

def MoveTo(ctx,page,i):
    y,x = page.cmds[i].args
    x,y = wmfdraw.convcoords(page,ctx,x,y)
    ctx.move_to(x,y)
    print i,'MoveTo ',page.cmds[i].args
    
def LineTo(ctx,page,i):
    y,x = page.cmds[i].args
    x,y = wmfdraw.convcoords(page,ctx,x,y)
    ctx.save()
    ctx.line_to(x,y)
    print i,'LineTo ',page.cmds[i].args
    wmfdraw.StrokePath(ctx,page,i)    

def Ellipse(ctx,page,i):
    ctx.save()
    x,y = ctx.get_current_point()
    x,y = wmfdraw.convcoords(page,ctx,x,y)
    y2,x2,y1,x1 = page.cmds[i].args
    print i,'Ellipse: ',x2,y2,x1,y1
    x1,y1 = wmfdraw.convcoords(page,ctx,x1,y1)
    x2,y2 = wmfdraw.convcoords(page,ctx,x2,y2)
    xc = 0.5*(x1+x2)
    yc = 0.5*(y1+y2)
    dx = x2-x1
    dy = y2-y1
    print i,'Ellipse: c(%u %u) d(%u %u)'%(xc,yc,dx,dy),x2,x1,y2,y1
    ctx.move_to(xc,yc)
    ctx.save()
    ctx.translate(xc,yc)
    ctx.move_to(dx/2., 0)
    ctx.scale(dx/2., dy/2.)
    ctx.arc(0.,0.,1.,0.,2*math.pi)
    ctx.restore()
    ctx.move_to(x,y)
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def ArcTo(ctx,page,i):
    ctx.save()
    ye,xe,ys,xs,b,r,t,l = page.cmds[i].args
    xe,ye = wmfdraw.convcoords(page,ctx,xe,ye)
    xs,ys = wmfdraw.convcoords(page,ctx,xs,ys)
    xc,yc = wmfdraw.convcoords(page,ctx,(l+r)/2.,(t+b)/2.)
    dx = math.fabs((r-l)*1./page.DCs[page.curdc].Wx)
    dy = math.fabs((b-t)*1./page.DCs[page.curdc].Wy)
    ang1 = math.atan2((ys-yc),(xs-xc))
    ang2 = math.atan2((ye-yc),(xe-xc))
    ctx.save()
    m = cairo.Matrix(dx/2.,0,0,dy/2.,xc,yc)
    ctx.transform(m)
    ctx.arc_negative(0.,0.,1.,ang1,ang2)
    ctx.restore()
    print i,'Arc: c(%u %u) ang(%u %u) dx %f dy %f'%(xc,yc,180*ang1/math.pi,180*ang2/math.pi,dx,dy)
    
def Arc(ctx,page,i):
    ctx.save()    
    ArcTo(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)
    
def Chord(ctx,page,i):
    ctx.save()
    print 'Chord'
    ArcTo(ctx,page,i)
    ctx.close_path()
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def Pie(ctx,page,i):
    ctx.save()
    print 'Pie'
    ye,xe,ys,xs,b,r,t,l = page.cmds[i].args
    xc,yc = wmfdraw.convcoords(page,ctx,(l+r)/2.,(t+b)/2.)
    ArcTo(ctx,page,i)
    ctx.line_to(xc,yc)
    ctx.close_path()
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def Rectangle(ctx,page,i):
    ctx.save()
    y2,x2,y1,x1 = page.cmds[i].args
    x1,y1 = wmfdraw.convcoords(page,ctx,x1,y1)
    x2,y2 = wmfdraw.convcoords(page,ctx,x2,y2)
    ctx.move_to(x1,y1)
    ctx.line_to(x1,y2)
    ctx.line_to(x2,y2)
    ctx.line_to(x2,y1)
    ctx.close_path()
    print i,'Rectangle: ',x1,y1,x2,y2
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)
    
def RoundRect(ctx,page,i):
    ctx.save()
    cy,cx,y2,x2,y1,x1 = page.cmds[i].args
    x1,y1 = wmfdraw.convcoords(page,ctx,x1,y1)
    x2,y2 = wmfdraw.convcoords(page,ctx,x2,y2)
    if x1 > x2:
        x = x1
        x1 = x2
        x2 = x
    if y1 > y2:
        x = y1
        y1 = y2
        y2 = x
    cx=cx*1./page.DCs[page.curdc].Wx
    cy=cy*1./page.DCs[page.curdc].Wy
    print i,'Round rectangle: ',x1,y1,x2,y2,cx,cy
    ctx.move_to(x1+cx/2.,y1)
    ## here elliptical arc to next point (x2,y1+cy/2) xc = x2-cx/2., yc = y1+cy/2.  90 0
    xc = x1+cx/2.
    yc = y1+cy/2.
    ctx.save()
    m = cairo.Matrix(cx/2.,0,0,cy/2.,xc,yc)
    ctx.transform(m)

    ctx.arc_negative(0.,0.,1.,-0.5*math.pi,math.pi)
    ctx.restore()
    ctx.line_to(x1,y2-cy/2.)
    ## here elliptical arc to next point x2-cx/2. ,y2  xc = x2-cx/2.,yc=y2-cy/2.  0 -90
    xc = x1+cx/2.
    yc = y2-cy/2.
    ctx.save()
##    ctx.translate(xc,yc)
##    ctx.scale(cx/2., cy/2.)
    m = cairo.Matrix(cx/2.,0,0,cy/2.,xc,yc)
    ctx.transform(m)

    ctx.arc_negative(0.,0.,1.,math.pi,0.5*math.pi)
    ctx.restore()
    ctx.line_to(x2-cx/2.,y2)
##    ## here elliptical arc to next point x1,y2-cy/2.  xc = x1+cx/2.,yc=y2-cy/2.  -90  180
    xc = x2-cx/2.
    yc = y2-cy/2.
    ctx.save()
##    ctx.translate(xc,yc)
##    ctx.scale(cx/2., cy/2.)
    m = cairo.Matrix(cx/2.,0,0,cy/2.,xc,yc)
    ctx.transform(m)

    ctx.arc_negative(0.,0.,1.,0.5*math.pi,0)
    ctx.restore()
    ctx.line_to(x2,y1+cy/2.)
##    ## here elliptical arc to next point x1+cx/2,y1  xc = x1+cx/2.,yc=y1+cy/2.  180  90
    xc = x2-cx/2.
    yc = y1+cy/2.
    ctx.save()
##    ctx.translate(xc,yc)
##    ctx.scale(cx/2., cy/2.)
    m = cairo.Matrix(cx/2.,0,0,cy/2.,xc,yc)
    ctx.transform(m)

    ctx.arc_negative(0.,0.,1.,0,-0.5*math.pi)
    ctx.restore()
    ctx.close_path()
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def Polygone(ctx,page,i):
    ctx.save()
    x,y = page.cmds[i].args[0]
    x,y = wmfdraw.convcoords(page,ctx,x,y)
    ctx.move_to(x,y)
    for j in range(len(page.cmds[i].args)):
        x,y = page.cmds[i].args[j]
        x,y = wmfdraw.convcoords(page,ctx,x,y)
        ctx.line_to(x,y)
    print i,'Polygone: ',page.cmds[i].args
    ctx.close_path()
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def Polyline(ctx,page,i):
    ctx.save()
    x,y = page.cmds[i].args[0]
    x,y = wmfdraw.convcoords(page,ctx,x,y)
    ctx.move_to(x,y)
    print i,'Polyline: ',page.cmds[i].args[0]
    PolylineTo(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)

def PolylineTo(ctx,page,i):
    for j in range(len(page.cmds[i].args)):
        x1,y1 = page.cmds[i].args[j]
        x1,y1 = wmfdraw.convcoords(page,ctx,x1,y1)
        ctx.line_to(x1,y1)
    print i,'PolylineTo: ',page.cmds[i].args
   
def PolyPolygone(ctx,page,i):
    ctx.save()
    nPolys = page.cmds[i].args[0]
    aptl = page.cmds[i].args[1]
    data = page.cmds[i].args[2]
    shift = 0
    for k in range(nPolys): ## number of polygones
        [x] = struct.unpack('<h',data[shift:shift+2])
        [y] = struct.unpack('<h',data[shift+2:shift+4])
        x,y = wmfdraw.convcoords(page,ctx,x,y)
        ctx.move_to(x,y)
        for j in range(aptl[k]): ## number of gones for i-th polygone
            [x] = struct.unpack('<h',data[j*4+shift:j*4+shift+2])
            [y] = struct.unpack('<h',data[j*4+shift+2:j*4+shift+4])
            x,y = wmfdraw.convcoords(page,ctx,x,y)
            ctx.line_to(x,y)
        ctx.close_path()
        shift+=aptl[k]*4
        print i,'Poly  Polygone: ',k
    wmfdraw.FillPath(ctx,page,i)
    wmfdraw.StrokePath(ctx,page,i)
