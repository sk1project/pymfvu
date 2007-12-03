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

####################################
# contain model for storing shapes #
####################################

import gtk
import math
import cairo
import pango
import struct

class Face(gtk.DrawingArea):
    def __init__(self,page):
        self.page = page
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
        ctx.scale(self.page.zoom,self.page.zoom)
        self.page.render(ctx)

class Page:
 def __init__(self):
  self.type = 0
  self.width = 1
  self.height = 1
  self.objs = []
  self.Face = Face(self)
  self.fname = ""
  self.zoom = 1.
  self.trafo = None
  ## below this line are 'gui' objects
  self.hdv2 = 0
  self.hdv1 = 0
  self.hscale = None
  
 def usage():
  class_objs = Object()

 def render(self,ctx):
  ctx.set_fill_rule(1)
  ctx.save()
  for i in range(int(self.hadj.value)):
#    print i
    self.objs[i].draw(ctx)
  ctx.restore()
#  for i in self.objs:
#   i.draw(ctx)

class Object:
 def __init__(self):
  self.type = 0 ## shape or group
  
class Shape(Object):
 def __init__(self):
  Object.__init__(self)
  self.p0 = Point()
  self.pe = Point()
  self.trafo = None
  self.pagetrafo = None
  self.trafomode = 0
  self.cliplist = []
  self.clipflag = 0 ## 0 -- do nothing, 1 -- clip set, 2 clip reset and set by iterating from clips[0] to curclip

  def usage():
        class_cliplist = Path()  
        
 def draw(self,ctx):
    if self.trafomode == 1 or self.trafomode > 3:
        ctx.set_matrix(self.trafo)
    if self.trafomode == 2:
        ctx.transform(self.trafo)
    if self.trafomode == 3:
        curmtrx = ctx.get_matrix()
        ctx.set_matrix(self.trafo)
        ctx.transform(curmtrx)
    if self.pagetrafo:
        ctx.transform(self.pagetrafo)
#    print 'Clip:',self.clipflag,len(self.cliplist)
    if self.clipflag == 2: ## after RestoreDC clip has to be reapplied
        ctx.reset_clip()
    if self.clipflag == 1 or self.clipflag == 2:
        for i in self.cliplist:
            i.prep(ctx)
            ctx.clip()
    
    
 def get_info(self):
  str = 'p0: %u %u pe: %u %u\n'%(self.p0.x,self.p0.y,self.pe.x,self.pe.y)
  return str
  
class Point:
 def __init__(self):
  self.x = 0.
  self.y = 0.

class Color:
 def __init__(self):
  self.r = 0
  self.g = 0
  self.b = 0
  self.a = 1
  
 def get_info(self):
  return '0x%02x%02x%02x'%(self.r,self.g,self.b)
   

class Bitmap(Shape):
    def __init__(self):
        Shape.__init__(self)
        ## p0 -- x/y Dest
        ## pe -- xe/ye Dest
        ## ps0 -- x/y Src
        self.dx,self.dy = 1,1
        self.dxsrc,self.dysrc = 1,1
        self.dwROP = 0
        self.data = None
    
    def draw(self,ctx):
        pixbufloader = gtk.gdk.PixbufLoader()
        pixbufloader.write(self.data)
        pixbufloader.close()
        pixbuf = pixbufloader.get_pixbuf()
        ctx.save()
        ctx.translate(self.p0.x,self.p0.y)
        ctx.scale(self.dx*1./self.dxsrc,self.dy*1./self.dysrc)
        if self.dwROP == 0xee0086: ## SRCPAINT
            ctx.set_operator(11)
            ctx.set_source_pixbuf(pixbuf,0,0)
            ctx.paint()
        if self.dwROP == 0x8800c6: ##SRCAND
            ctx.set_operator(12)
            ctx.set_source_pixbuf(pixbuf,0,0)
            ctx.paint()
        if self.dwROP == 0xcc0020: ## SRCCOPY
            ctx.set_source_pixbuf(pixbuf,0,0)
            ctx.paint()
        ctx.restore()
    
    def get_info(self):
        str = Shape.get_info()
        str = str+'\ndx/dy: %u %u dxsrc/dysrc: %u %u'%(self.dx,self.dy,self.dxsrc,self.dysrc)
        str = str+'\ndwROP: %x'%self.dwROP
        return str
    
class Line(Shape):
 def __init__(self):
  Shape.__init__(self)
  self.clr = Color()
  self.width = 1 ## 0 - non-scalable (will be)
  self.pattern = 0
  self.noline = 0
  self.style = 0
  self.bkcolor = Color()
  self.bkmode = 1

 def get_info(self):
    pat = {0:'Solid',1:'Dash',2:'Dot',3:'Dashdot',4:'Dashdotdot'}
    str ='\n---- Line ----\nColor: '+self.clr.get_info()
    str+='\nWidth: %u'%self.width
    str+='\nPat: '+pat[self.pattern]
    str+='\nNo line: %u'%self.noline
    str+='\nStyle: %u'%self.style
    str+='\nBKMode: %u'%self.bkmode
    str+='\nBKColor: '+self.bkcolor.get_info()+'\n'
    return str
      
 def stroke_prep(self,ctx):
   capjoin = {0:1,1:2,2:0}
   cap = {0:'Flat',1:'Round',2:'Square'}
   join = {0:'Miter',1:'Round',2:'Bevel'}
   dashes = ((), #solid
                (480.5,160.5), #dash
                (80.5,100.5), #dot
                (240.5,160.5,100.5,160.5), #dashdot
                (240.5,80.5,80.5,80.5,80.5,80.5)) #dashdotdot
   if self.noline:
    ctx.set_line_width(0)
   else:
    ctx.set_line_width(self.width)
    lcap,ljoin = 0,0
    if (self.style&0xF00)>>8 <3:
        lcap = capjoin[(self.style&0xF00)>>8]
    if (self.style&0xF000)>>12 < 3:
        ljoin = capjoin[(self.style&0xF000)>>12]
    ctx.set_line_cap(lcap)
    ctx.set_line_join(ljoin)
    if self.style > 5:
        self.style = 0
    if self.style > 0 and self.bkmode == 2:
        ctx.set_dash(dashes[0],len(dashes[0])/2)
        r = self.bkcolor.r
        g = self.bkcolor.g
        b = self.bkcolor.b
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
        ctx.stroke_preserve()
    ctx.set_dash(dashes[self.style],len(dashes[self.style])/2)
    ctx.set_source_rgba(self.clr.r/255.,self.clr.g/255.,self.clr.b/255.,self.clr.a)
    
 def stroke(self,ctx):
    self.stroke_prep(ctx)
    ctx.stroke()
        
class Mesh(Line):
 def __init__(self):
  Line.__init__(self)
  self.fclr = Color() ## fill color
  self.fclr.r,self.fclr.g,self.fclr.b = 255.,255.,255.
  self.fstyle = 0 ## 0 - solid color
  self.hatch = 0
  self.nofill = 0
  self.PFMode = 1
  self.data = None ## fill pattern bitmap
  
 def get_info(self):
    hatch = {0:'--',1:'||',2:'\\',3:'///',4:'++',5:'xx'}
    str = Line.get_info(self)
    str+='\n---- Fill ----\nColor: '+self.fclr.get_info()
    str+='\nNo fill: %u'%self.noline
    str+='\nStyle: %u'%self.fstyle
    if self.fstyle == 2:
        str+='\nHatch: '+hatch[self.hatch]
    str+='\nPFMode: %u\n'%self.PFMode
    return str
  
 def fill(self,ctx):
    if self.nofill == 0:
        ctx.save()
        ctx.set_fill_rule(self.PFMode)
        if self.fstyle == 2 or self.fstyle == 3:
            if self.fstyle == 2:
                w,h = 8,8
                input = open('pat'+str(self.hatch)+'.png')
                imagebuf = input.read()
                pixbufloader = gtk.gdk.PixbufLoader()
                pixbufloader.write(imagebuf)
            else:
                w = self.data[0]
                h = self.data[1]
                bmpsize = struct.pack('<I',self.data[2])
                bmpshift = struct.pack('<I',self.data[3])
                bmp = '\x42\x4d'+bmpsize+'\x00\x00\x00\x00'+bmpshift+self.data[4]
                pixbufloader = gtk.gdk.PixbufLoader()
                pixbufloader.write(bmp)
            pixbufloader.close()
            pixbuf = pixbufloader.get_pixbuf()
            cs = cairo.ImageSurface(0,w,h)
            ct = cairo.Context(cs)
            ct2 = gtk.gdk.CairoContext(ct)
            ct2.set_source_pixbuf(pixbuf,0,0)
            ct2.paint()
            if self.bkmode == 2:
                ctx.set_source_rgba(self.bkcolor.r/255.,self.bkcolor.g/255.,self.bkcolor.b/255.,self.bkcolor.a)
                ctx.fill_preserve()
            self.stroke_prep(ctx)
            ctx.stroke_preserve()
            ctx.set_source_rgba(self.fclr.r/255.,self.fclr.g/255.,self.fclr.b/255.,self.fclr.a)
            pat = cairo.SurfacePattern(cs)
            pat.set_filter(5)
            pat.set_extend(1)
            ctx.clip()
            if self.fstyle == 2:
                ctx.mask(pat)
            else:
                ctx.set_source(pat)
                ctx.paint()
        else:
            ctx.set_source_rgba(self.fclr.r/255.,self.fclr.g/255.,self.fclr.b/255.,self.fclr.a)
            ctx.fill_preserve()
        ctx.restore()
        
class Text(Mesh):
 def __init__(self):
  Mesh.__init__(self)
## clr -- txt color
## fclr -- bg color
  self.text = ''
  self.font = 'Arial 12'
  self.size = 12
  self.dx = DX()
  self.orient = 0
  self.escape = 0
  self.under = 0
  self.over = 0
  self.alignh = 0
  self.alignv = 0
  self.cpupdate = 0

 def draw(self,ctx):
##    return
    ctx.save()
    Shape.draw(self,ctx)
    layout = ctx.create_layout()
    fdesc = pango.FontDescription(self.font)
    layout.set_font_description(fdesc)
    layout.set_text(self.text)
    xsize,ysize = layout.get_size()
    xsize=xsize/1000.
    ysize=ysize/1000.
    if self.dx.sum>0: ## there is shifts
        layout.set_text(self.text)
        x0,y0 = layout.get_size()
        xsize=x0/1000.+self.dx.sum
    if self.alignh == 0:
        xs = self.p0.x
    if self.alignh == 1:
        xs = self.p0.x-xsize/2.
    if self.alignh == 2:
        xs = self.p0.x-xsize
    if self.alignv == 0: ##top
        ys = self.p0.y + ysize
    if self.alignv == 1: ##bottom
        ys = self.p0.y 
    if self.alignv == 2: ##baseline
        ys = self.p0.y - ysize/1.25
    
    xe = xs+xsize
    ye = ys+ysize
    
    ctx.save()
    if self.escape !=0:  ## change it with transform
        ctx.translate(xs,ys)
        ctx.rotate(-self.escape*math.pi/1800) ## rotation angle is set in 10th of degree
        ctx.translate(-xs,-ys)
    if self.bkmode == 2:
        r = self.bkcolor.r
        g = self.bkcolor.g
        b = self.bkcolor.b
        ctx.save()
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
        ctx.move_to(xs,ys)
        ctx.line_to(xe,ys)
        ctx.line_to(xe,ye)
        ctx.line_to(xs,ye)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    ctx.set_source_rgba(self.clr.r/255.,self.clr.g/255.,self.clr.b/255.,1)
    if self.under == 1:
        if self.dx.sum > 0:
            xf = xs+self.dx.sum
            t = self.text[len(self.text)-1]
            layout.set_text(t)
            x0,y0 = layout.get_size()
            xf+=x0/1000.
        else:
            xf = xe
        ctx.move_to(xs,ys+ysize/1.05)
        ctx.line_to(xf,ys+ysize/1.05)
        ctx.set_line_width(self.size*0.06)
        ctx.stroke()
    if self.strike == 1:
        if self.dx.sum > 0:
            xf = xs+self.dx.sum
            t = self.text[len(self.text)-1]
            layout.set_text(t)
            x0,y0 = layout.get_size()
            xf+=x0/1000.
        else:
            xf = xe
        ctx.move_to(xs,ys+ysize/2.)
        ctx.line_to(xf,ys+ysize/2.)
        ctx.set_line_width(self.size*0.06)
        ctx.stroke()
    ctx.move_to(xs,ys)
    if self.dx.sum>0 or self.orient!=0: ## and page.ai==0): ## ai-bug workaround is not added yet
        ctx.save()
        for i in range(len(self.text)):
            t = self.text[i]
            layout.set_text(t)
            x0,y0 = layout.get_size()
            ctx.save()
            if self.orient!=0: ## and page.ai ==0: ##ai-bug workaround
                ctx.translate(xs+x0/2000.,ys+y0/2000.)
                ctx.rotate(-self.orient*math.pi/1800.) ## rotation angle is set in 10th of degree
                ctx.translate(-xs-x0/2000.,-ys-y0/2000.)
                xup = abs(x0*math.sin(self.orient*math.pi/1800.)/1000.+y0*math.cos(self.orient*math.pi/1800.)/1000.)
            ctx.show_layout(layout)
            if self.dx.sum >0:
                xs=xs+self.dx.list[i]*1.
            else:
                xs = xs+xup
            ctx.restore()
            ctx.move_to(xs,ys) 
        ctx.restore()
    else:
        layout.set_text(self.text)
        ctx.show_layout(layout)
    ctx.restore()
    ctx.restore()
    
class DX: ## dx-array for text in WMF
    def __init__(self):
        self.sum = 0
        self.list = []
    
class LineTo(Line):
 def __init__(self):
  Line.__init__(self)

 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.move_to(self.p0.x,self.p0.y)
  ctx.line_to(self.pe.x,self.pe.y)
  self.stroke(ctx)
  ctx.restore()
  
 def get_info(self):
  str='---- LineTo ----\n'+Shape.get_info(self)+'\n'+Line.get_info(self)
  return str

class ArcTo(Line):
 def __init__(self):
  Line.__init__(self)
  self.c = Point()
  self.rx = 1.
  self.ry = 1.
  self.a1 = 0.
  self.a2 = 0.

 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.save()
  m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,self.c.x,self.c.y)
  ctx.transform(m)
  ctx.arc_negative(0.,0.,1.,self.a1,self.a2)
  ctx.restore()
  self.stroke(ctx)
  ctx.restore()

 def get_info(self):
  str='---- ArcTo ----\n'+'cx/cy: %u %u\nrx/ry: %u %u\nang1/ang2: %u %u\n'%(self.c.x,self.c.y,self.rx,self.ry,self.a1*180/math.pi,self.a2*180/math.pi)+Line.get_info(self)
  return str
  
class Chord(Mesh):
 def __init__(self):
  Mesh.__init__(self)
  self.c = Point()
  self.rx = 1.
  self.ry = 1.
  self.a1 = 0.
  self.a2 = 0.

 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.save()
  m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,self.c.x,self.c.y)
  ctx.transform(m)
  ctx.arc_negative(0.,0.,1.,self.a1,self.a2)
  ctx.close_path()
  ctx.restore()
  self.fill(ctx)
  self.stroke(ctx)
  ctx.restore()
  
 def get_info(self):
  str='---- Chord ----\n'+'cx/cy: %u %u\nrx/ry: %u %u\nang1/ang2: %u %u\n'%(self.c.x,self.c.y,self.rx,self.ry,self.a1*180/math.pi,self.a2*180/math.pi)+Mesh.get_info(self)
  return str


class Pie(Chord):
 def __init__(self):
  Chord.__init__(self)
  
 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.save()
  m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,self.c.x,self.c.y)
  ctx.transform(m)
  ctx.arc_negative(0.,0.,1.,self.a1,self.a2)
  ctx.restore()
  ctx.line_to(self.c.x,self.c.y)
  ctx.close_path()
  self.fill(ctx)
  self.stroke(ctx)
  ctx.restore()
  
 def get_info(self):
  str='---- Pie ----\n'+'cx/cy: %u %u\nrx/ry: %u %u\nang1/ang2: %u %u\n'%(self.c.x,self.c.y,self.rx,self.ry,self.a1*180/math.pi,self.a2*180/math.pi)+Mesh.get_info(self)
  return str

class Rect(Mesh):
 def __init__(self):
  Mesh.__init__(self)
  
 def get_info(self):
  str='---- Rect ----\n'+Shape.get_info(self)+Mesh.get_info(self)
  return str
  
 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.move_to(self.p0.x,self.p0.y)
  ctx.line_to(self.p0.x,self.pe.y)
  ctx.line_to(self.p0.x,self.pe.y)
  ctx.line_to(self.pe.x,self.pe.y)
  ctx.line_to(self.pe.x,self.p0.y)
  ctx.close_path()
  self.fill(ctx)
  self.stroke(ctx)
  ctx.restore()
##  print 'Draw:',self.p0.x,self.p0.y,self.pe.x,self.pe.y,self.fclr.r,self.fclr.g,self.fclr.b,self.clr.r,self.clr.g,self.clr.b

class Ellipse(Mesh):
 def __init__(self):
  Mesh.__init__(self)
  self.c = Point()
  self.r = 0.
  self.e = 1.
  
 def get_info(self):
  str='---- Ellipse ----\ncx/cy: %u %u\nrx/ry: %u %u\n'%(self.c.x,self.c.y,self.r,self.r*self.e)+Mesh.get_info(self)
  return str

 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.move_to(self.c.x,self.c.y)
  ctx.save()
  ctx.translate(self.c.x,self.c.y)
  ctx.move_to(self.r, 0)
  ctx.scale(self.r, self.r*self.e)
  ctx.arc(0.,0.,1.,0.,2*math.pi)
  self.fill(ctx)
  ctx.restore()
  self.stroke(ctx)
  ctx.restore()
  
class Polyline(Line):
 def __init__(self):
  Line.__init__(self)
  self.pl0 = Point()
  self.pl = []

 def get_info(self):
  str='---- Polyline ----\n'+'p0: %u %u\n'%(self.pl0.x,self.pl0.y)
  for i in range(len(self.pl)):
    str+='p%u: %u %u\n'%(i+1,self.pl[i].x,self.pl[i].y)
  str+=Line.get_info(self)
  return str

 def usage():
  class_pl = Point()
  
 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.move_to(self.pl0.x,self.pl0.y)
  for i in self.pl:
   ctx.line_to(i.x,i.y)
  self.stroke(ctx)
  ctx.restore()
  
class Triple:
 def __init__(self):
  self.x1 = 0.
  self.y1 = 0.  
  self.x2 = 0.
  self.y2 = 0.   
  self.x3 = 0.
  self.y3 = 0.   
  
class Polybezier(Line):
 def __init__(self):
  Line.__init__(self)
  self.trpl = []
  
 def get_info(self):
  str='---- Polybezier ----\n'+'p0: %u %u\n'%(self.p0.x,self.p0.y)
  for i in range(len(self.trpl)):
    str+='p%u: (%u %u %u %u) %u %u\n'%(i+1,self.trpl[i].x1,self.trpl[i].y1,self.trpl[i].x2,self.trpl[i].y2,self.trpl[i].x3,self.trpl[i].y3)
  str+=Line.get_info(self)
  return str
  
 def usage():
  class_trpl = Triple()
  
 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  ctx.move_to(self.p0.x,self.p0.y)
  for i in self.trpl:
   ctx.curve_to(i.x1,i.y1,i.x2,i.y2,i.x3,i.y3)
  self.stroke(ctx)
  ctx.restore()
  
class Polygone(Mesh):
 def __init__(self):
  Mesh.__init__(self)
  self.pl0 = Point()
  self.pl = []

 def usage():
  class_pl = Point()
  
 def get_info(self):
  str='---- Polygone ----\n'+'p0: %u %u\n'%(self.pl0.x,self.pl0.y)
  for i in range(len(self.pl)):
    str+='p%u: %u %u\n'%(i+1,self.pl[i].x,self.pl[i].y)
  str+=Mesh.get_info(self)
  return str
  
 def draw(self,ctx):
    ctx.save()
    Shape.draw(self,ctx)
    ctx.move_to(self.pl0.x,self.pl0.y)
    for i in self.pl:
        ctx.line_to(i.x,i.y)
    ctx.close_path()
    self.fill(ctx)
    self.stroke(ctx)
    ctx.restore()
    
class PolyPolygone(Mesh):
 def __init__(self):
  Mesh.__init__(self)
##  self.nPoly = 0
  self.polys = []

 def usage():
  class_polys = Polygone()
  
 def get_info(self):
  str='---- PolyPolygone ----\nnPoly: %u\n'%len(self.polys)
  str+=Mesh.get_info(self)
  return str
  
 def draw(self,ctx):
  ctx.save()
  Shape.draw(self,ctx)
  for i in self.polys:
   ctx.move_to(i.pl0.x,i.pl0.y)
   for j in i.pl:
    ctx.line_to(j.x,j.y)
   ctx.close_path()
  self.fill(ctx)
  self.stroke(ctx)
  ctx.restore()
  
class RoundRect(Mesh):
 def __init__(self):
  Mesh.__init__(self)
  self.rx = 0
  self.ry = 0

 def get_info(self):
  str='---- RoundRect ----\n'+Shape.get_info(self)+'rx/ry: %u %u\n'%(self.rx,self.ry)+Mesh.get_info(self)
  return str
  
 def draw(self,ctx):
    ctx.save()
    Shape.draw(self,ctx)
    ctx.move_to(self.p0.x+self.rx/2.,self.p0.y)
    xc = self.p0.x+self.rx/2.
    yc = self.p0.y+self.ry/2.
    ctx.save()
    m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,xc,yc)
    ctx.transform(m)
    ctx.arc_negative(0.,0.,1.,-0.5*math.pi,math.pi)
    ctx.restore()
    ctx.line_to(self.p0.x,self.pe.y-self.ry/2.)
    xc = self.p0.x+self.rx/2.
    yc = self.pe.y-self.ry/2.
    ctx.save()
    m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,xc,yc)
    ctx.transform(m)
    ctx.arc_negative(0.,0.,1.,math.pi,0.5*math.pi)
    ctx.restore()
    ctx.line_to(self.pe.x-self.rx/2.,self.pe.y)
    xc = self.pe.x-self.rx/2.
    yc = self.pe.y-self.ry/2.
    ctx.save()
    m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,xc,yc)
    ctx.transform(m)
    ctx.arc_negative(0.,0.,1.,0.5*math.pi,0)
    ctx.restore()
    ctx.line_to(self.pe.x,self.p0.y+self.ry/2.)
    xc = self.pe.x-self.rx/2.
    yc = self.p0.y+self.ry/2.
    ctx.save()
    m = cairo.Matrix(self.rx/2.,0,0,self.ry/2.,xc,yc)
    ctx.transform(m)
    ctx.arc_negative(0.,0.,1.,0,-0.5*math.pi)
    ctx.restore()
    ctx.close_path()
    self.fill(ctx)
    self.stroke(ctx)
    ctx.restore()

class Path(Mesh):
    def __init__(self):
        Mesh.__init__(self)
        self.pplist = []
        self.clip = 0
  
    def usage(self):
        class_pplist = PathPoint()

    def get_info(self):
        str='---- Path ----\n'+Shape.get_info(self)+Mesh.get_info(self)
        return str
    
    def prep(self,ctx):
        pathdraw = {1:self.pathmove,2:self.pathline,3:self.pathcurve,4:self.pathclose}
        for i in self.pplist:
            pathdraw[i.type](i,ctx)
    
    def draw(self,ctx):
        ctx.save()
        Shape.draw(self,ctx)    
        self.prep(ctx)
        ctx.restore()
        if self.clip:
            ctx.clip()
#            print 'Clip path!'
        else:
            self.fill(ctx)
            self.stroke(ctx)
#            print 'Fill and/or Stroke path!'

            
    def pathmove(self,i,ctx):
        ctx.move_to(i.pts[0].x,i.pts[0].y)
#	print 'PMoveTo:',i.pts[0].x,i.pts[0].y
	
    def pathline(self,i,ctx):
        ctx.line_to(i.pts[0].x,i.pts[0].y)
#	print 'PLineTo:',i.pts[0].x,i.pts[0].y

    def pathcurve(self,i,ctx):
        ctx.curve_to(i.pts[0].x,i.pts[0].y,i.pts[1].x,i.pts[1].y,i.pts[2].x,i.pts[2].y)

    def pathclose(self,i,ctx):
        ctx.close_path()
#	print 'PClose'
        
class PathPoint:
    def __init__(self):
        self.type = 0 ## 0 - N/A, 1 - Move, 2 - Line, 3 - Curve, 4 - Close
        self.pts = []
        
    def usage(self):
        class_pts = Point()
