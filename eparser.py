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

################################
# contain parser for emf files #
################################

import gmodel
import pyemf
import wmf
import struct
import math
import cairo ##I use it to create trafo (in my case it's cairo.Matrix
import parser ## to use the same functions from WMF parser

def parse(page,buf):
    file = pyemf.EMF()        
    file.loadmem(buf)
    state = wmf.State()
    state.obj_init()
## 'xformPlay' calculation
    ksx = file.records[0].values[17]/100./file.records[0].values[19]
    ksy = file.records[0].values[18]/100./file.records[0].values[20]
    sx0 = file.records[0].values[4]*ksx
    sy0 = file.records[0].values[5]*ksy
    sx1 = file.records[0].values[6]*ksx
    sy1 = file.records[0].values[7]*ksy
    dx = abs(file.records[0].values[2]-file.records[0].values[0])
    dy = abs(file.records[0].values[3]-file.records[0].values[1])
    rx = dx/(sx1 - sx0)
    ry = dy/(sy1 - sy0)
#    page.zoom = min(320./dx,240./dy)
#    state.DCs[0].W
    page.width = dx
    page.height = dy
    page.zoom = min(320./page.width,240./page.height)
##    state.zoomx,state.zoomy = page.width,page.height
##    page.trafo = cairo.Matrix(rx*pz,0,0,ry*pz,0,0)
    print 'Page trafo:',sx0,sy0,rx,ry
    for i in range(len(file.records)):
        id = file.records[i].emr_id
        if emr_ids.has_key(id):
            if emr_cmds.has_key(id):
                print 'COMMAND:',i,emr_ids[id]
                emr_cmds[id](file,i,page,state)
            else:
                print i,'UNSUPPORTED COMMAND!', emr_ids[id]
        else:
            print 'Unknown key: ',id
    print 'End of parsing'
    

def convcoords(state,x,y):
    pdc = state.DCs[state.curdc]
    xr = (x-pdc.x)*pdc.VPx/pdc.Wx + pdc.VPOx
    yr = (y-pdc.y)*pdc.VPy/pdc.Wy + pdc.VPOy
    xr = xr*state.zoomx + 0.5 - (xr*state.zoomx)%1
    yr = yr*state.zoomy + 0.5 - (xr*state.zoomy)%1
    return xr,yr
            
def Header(mf,num,page,state):
    pass
    
def SetBKMode(mf,num,page,state):
    [state.bk.mode] =  mf.records[num].values
    
def SetMapMode(mf,num,page,state):
    fixme =  mf.records[num].values

def SetBKColor(mf,num,page,state):
    bkColor = mf.records[num].crColor
    f =  (bkColor>>24)&0xFF
    b = (bkColor>>16)&0xFF
    g = (bkColor>>8)&0xFF
    r = bkColor&0xFF
    if f !=1:
        state.bk.color.r,state.bk.color.g,state.bk.color.b = r,g,b
    else:
        clr = state.mfobjs[curpal].palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        state.bk.color.r,state.bk.color.g,state.bk.color.b = clr.r,clr.g,clr.b
        
def SetROP2(mf,num,page,state):
    state.ROP2 =  mf.records[num].iMode

def SetPolyfillMode(mf,num,page,state):
    if mf.records[num].iMode == 2:
        state.PFMode =  0
    else:
        state.PFMode  =  1

def StretchDIBits(mf,num,page,state):
    palsize = {1:8,2:16,4:64,8:1024,16:0,24:0,32:0}
    er = mf.records[num]
    bd = er.bmpDepth
    bshift = palsize[bd]+54
    bmp = gmodel.Bitmap()
    x,y = er.leftDest,er.topDest        ## xDest, yDest
    bmp.p0.x,bmp.p0.y = convcoords(state,x,y)
    bmp.dxsrc,bmp.dysrc = er.rightSrc-er.leftSrc, er.topSrc-er.bottomSrc	##cxSrc, cySrc
    bmpsize = struct.pack('<I',er.nSize-14)	##nSize-header+14
    bmpshift = struct.pack('<I',bshift)	##calculated shift to the bitmap data (stored after palette, if any palette exists)
    bmp.dx = er.cxDest ##cxDest
    bmp.dy = er.cyDest ##cyDest
    bmp.dwROP = er.dwRop ##dwRop
    bmp.data = '\x42\x4d'+bmpsize+'\x00\x00\x00\x00'+bmpshift+er.data[22:]
    bmp.pagetrafo = page.trafo
    page.objs.append(bmp)

def SetStretchBltMode(mf,num,page,state):
    fixme =  mf.records[num].iMode
    
def SetTextAlign(mf,num,page,state):
    state.txt.align =  mf.records[num].iMode ## FIXME! parse here VAlign and HAlign?
    
def SetTextColor(mf,num,page,state):
    crColor = mf.records[num].crColor
    f =  (crColor>>24)&0xFF
    b = (crColor>>16)&0xFF
    g = (crColor>>8)&0xFF
    r = crColor&0xFF
    if f !=1:
        state.txt.color.r,state.txt.color.g,state.txt.color.b = r,g,b
    else:
        clr = state.mfobjs[curpal].palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        state.txt.color.r,state.txt.color.g,state.txt.color.b = clr.r,clr.g,clr.b
        
def CreateFontIndirect(mf,num,page,state):
    er = mf.records[num]
    eo = wmf.mfobj()
    eo.type = 3
    size = er.values[1]
    if size < 0:
        size = -size
    if size == 0:
        size = 12
    eo.size = size
    eo.weight = er.values[5]
    eo.escape = er.values[3]
    eo.orient = er.values[4]
    eo.italic = er.values[6]
    eo.under = er.values[7]
    eo.strike = er.values[8]
    eo.charset = er.values[9]
    font = er.data[18:]
    pos = font.find('\x00')
    font = font[0:pos]
    eo.font = font
    h = er.values[0]
    state.mfobjs[h]=eo

def ExtTextOut(mf,num,page,state):
    er = mf.records[num]
    text = er.string
    x = er.values[0]
    y = er.values[1]
    xscl = er.values[5]
    yscl = er.values[6]
##    x*=xscl*0.615
##    y*=yscl*0.75
    text = unicode(text,'utf-16').encode('utf-8')
    txt = gmodel.Text()
    txt.bkcolor.r = state.bk.color.r
    txt.bkcolor.g = state.bk.color.g
    txt.bkcolor.b = state.bk.color.b
    txt.bkmode = state.bk.mode
    txt.fclr.r = state.mfobjs[state.curbrush].clr.r
    txt.fclr.g = state.mfobjs[state.curbrush].clr.g
    txt.fclr.b = state.mfobjs[state.curbrush].clr.b
    txt.clr.r = state.txt.color.r
    txt.clr.g = state.txt.color.g
    txt.clr.b = state.txt.color.b
    eo = state.mfobjs[state.curfnt]
    txt.escape = eo.escape
    txt.orient = eo.orient
    txt.under = eo.under
    txt.strike = eo.strike
    size = eo.size*yscl
    txt.size = size
    bld = ''
    itl = ''
    if eo.weight > 400:
        bld = 'Bold '
    if eo.italic !=0:
        itl = 'Italic '
    FONT = eo.font+' '+bld+itl+str(size/1.5)
    txt.text = text
    txt.font = FONT
#    dxsum = 0
#    if len(dx)>3: ## there is shifts
#        dxoffs = 0
#        dxlist = []
#        if lentext/2. != lentext/2:
#            dxoffs = 1
#        for i in range(lentext-1):
#            [d] = struct.unpack('h',dx[i*2+dxoffs:i*2+2+dxoffs])
#            dxlist.append(d)
#            dxsum=dxsum+d
#        dxlist.append(0) ## to simplify my life later
#        txt.dx.list = dxlist
#    txt.dx.sum = dxsum
    txt.alignh = txtalign[state.txt.align]
    if state.txt.align<8: ##top
        txt.alignv = 0
    if state.txt.align>7 and state.txt.align<24: ##bottom
        txt.alignv = 1
    if state.txt.align>23: ##baseline
        txt.alignv = 2
    if cpupdate.has_key(state.txt.align):
        txt.cpupdate = 1
        txt.p0.x,txt.p0.y = state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y
    else:
        txt.p0.x,txt.p0.y = x,y
    txt.pagetrafo = page.trafo
    page.objs.append(txt)
    print '================= TextOut x,y, xscl,yscl:',x,y,xscl,yscl
    
def TextOut(mf,num,page,state):
    count = mf.records[num].values[0]
    textstr = mf.records[num].data[2:2+count]
    text = textstr
    lentext = len(text)
    [y] = struct.unpack('>h',mf.records[num].data[2+count:4+count])
    [x] = struct.unpack('>h',mf.records[num].data[4+count:6+count])
    x,y = convcoords(state,x,y)
    txt = gmodel.Text()
    txt.bkcolor.r = state.bk.color.r
    txt.bkcolor.g = state.bk.color.g
    txt.bkcolor.b = state.bk.color.b
    txt.bkmode = state.bk.mode
    txt.fclr.r = state.mfobjs[state.curbrush].clr.r
    txt.fclr.g = state.mfobjs[state.curbrush].clr.g
    txt.fclr.b = state.mfobjs[state.curbrush].clr.b
    txt.clr.r = state.txt.color.r
    txt.clr.g = state.txt.color.g
    txt.clr.b = state.txt.color.b
    eo = state.mfobjs[state.curfnt]
    txt.escape = eo.escape
    txt.orient = eo.orient
    txt.under = eo.under
    txt.strike = eo.strike
    size = eo.size
    txt.size = size
    bld = ''
    itl = ''
    if eo.weight > 400:
        bld = 'Bold '
    if eo.italic !=0:
        itl = 'Italic '
    FONT = eo.font+' '+bld+itl+str(size/1.5)
    if eo.font == 'Symbol':
        textstr=unicode(symbol_to_utf(text),'utf-16')
    if eo.charset > 77 and charsets.has_key(eo.charset):
        # have to reencode and have no idea about Mac encoding
        print 'Reencoding from charset %s'%charsets[eo.charset],'text: ',text
        textstr = unicode(text,charsets[eo.charset])
        textstr.encode('utf-8')
    txt.text = textstr
    txt.font = FONT
    txt.alignh = txtalign[state.txt.align]
    if state.txt.align<8: ##top
        txt.alignv = 0
    if state.txt.align>7 and state.txt.align<24: ##bottom
        txt.alignv = 1
    if state.txt.align>23: ##baseline
        txt.alignv = 2
##    if cpupdate.has_key(state.txt.align):
##        txt.cpupdate = 1
##        txt.p0.x,txt.p0.y = state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y
##    else:
    txt.p0.x,txt.p0.y = x,y
    txt.pagetrafo = page.trafo    
    page.objs.append(txt)
    
def DeleteObject(mf,num,page,state):
    del state.mfobjs[mf.records[num].handle]
    
def CreatePalette(mf,num,page,state):
    data = mf.records[num].data[4:]
    h = mf.records[num].handle
    eo = wmf.mfobj()
    eo.type = 4
    for j in range(mf.records[num].lpltNumofclr):
        clr = wmf.Color()
        clr.r,clr.g,clr.b = ord(data[j*4]),ord(data[j*4+1]),ord(data[j*4+2])
        state.palette[j]=clr
        state.mfobjs[h] = eo
            
def CreateBrushIndirect(mf,num,page,state):
    h = mf.records[num].handle
    lbStyle = mf.records[num].lbStyle
    lbColor = mf.records[num].lbColor
    lbHatch = mf.records[num].lbHatch
    f =  (lbColor>>24)&0xFF
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    if f ==1:
        clr = state.palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        r,g,b = clr.r,clr.g,clr.b
    mfo = wmf.mfobj()
    mfo.type = 2
    mfo.clr.r = r
    mfo.clr.g = g
    mfo.clr.b= b
    mfo.style = lbStyle
    mfo.hatch = lbHatch
    state.mfobjs[h] = mfo
    print 'Brush:',h,'Color:',r,g,b,'Style:',lbStyle,lbHatch
    
def DibCreatePatternBrush(mf,num,page,state):
    palsize = {1:8,2:16,4:64,8:1024,16:0,24:0,32:0}
    h = mf.records[num].handle
    ern = mf.records[num]
    bd = ern.biDepth
    bshift = palsize[bd]+54
    eo = wmf.mfobj()
    eo.type = 2
    eo.style = 3 ## pattern brush
    eo.data = ern.biWidth,ern.biHeight,ern.nSize+4,bshift,ern.data[4:] ## temporary assume 1 bpp image
    state.mfobjs[h] = eo
            
def CreatePatternBrush(mf,num,page,state):
    h = mf.records[num].handle
    fixme = mf.records[num].data
    state.mfobjs[h] = 0

def ExtCreatePen(mf,num,page,state):
    h = mf.records[num].handle
    width = mf.records[num].lopnWidth
    style = mf.records[num].lopnStyle
    brstyle = mf.records[num].lbStyle
    lbColor = mf.records[num].lbColor
    f =  (lbColor>>24)&0xFF    
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    if f ==1:
        clr = state.palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        r,g,b = clr.r,clr.g,clr.b 
    mfo = wmf.mfobj()
    mfo.type = 1
    mfo.clr.r = r
    mfo.clr.g = g
    mfo.clr.b= b
    mfo.style = style
    mfo.width = width
    state.mfobjs[h] = mfo
    
def CreatePenIndirect(mf,num,page,state):
    h = mf.records[num].handle
    lbColor = mf.records[num].lopn_color
    width = mf.records[num].lopn_width
    style = mf.records[num].lopn_style
    f =  (lbColor>>24)&0xFF    
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    if f ==1:
        clr = state.palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        r,g,b = clr.r,clr.g,clr.b 
    mfo = wmf.mfobj()
    mfo.type = 1
    mfo.clr.r = r
    mfo.clr.g = g
    mfo.clr.b= b
    mfo.style = style
    mfo.width = width
    state.mfobjs[h] = mfo
    print 'Pen:',h,'Color:',r,g,b,'Style:',style,width,f

def SelectObject(mf,num,page,state):
    eonum = mf.records[num].handle
    if state.mfobjs.has_key(eonum): 
        eo = state.mfobjs[eonum]
        type = eo.type
        if type == 1:
            state.curpen = eonum
        if type == 2:
            state.curbrush = eonum
        if type == 3:
            state.curfnt = eonum
    
def RestoreDC(mf,num,page,state):
    state.DCs.pop()
    state.curdc-=1
    
def SaveDC(mf,num,page,state):
    dc = wmf.DC()
    state.DCs.append(dc)
    state.DCs[state.curdc+1].VPOx =  state.DCs[state.curdc].VPOx
    state.DCs[state.curdc+1].VPOy = state.DCs[state.curdc].VPOy 
    state.DCs[state.curdc+1].VPx = state.DCs[state.curdc].VPx 
    state.DCs[state.curdc+1].VPy = state.DCs[state.curdc].VPy 
    state.DCs[state.curdc+1].Wx = state.DCs[state.curdc].Wx 
    state.DCs[state.curdc+1].Wy = state.DCs[state.curdc].Wy 
    state.DCs[state.curdc+1].x = state.DCs[state.curdc].x 
    state.DCs[state.curdc+1].y = state.DCs[state.curdc].y 
    state.curdc+=1
    
def SetViewportOrgEx(mf,num,page,state):
    state.DCs[state.curdc].VPOx,state.DCs[state.curdc].VPOy = mf.records[num].values
##    print 'SetVPOrg',mf.records[num].values
    
def SetViewportExtEx(mf,num,page,state):
    state.DCs[state.curdc].VPx, state.DCs[state.curdc].VPy = mf.records[num].values    
##    print 'SetVPExt',mf.records[num].values
    
def SetWindowOrgEx(mf,num,page,state):
    state.DCs[state.curdc].x, state.DCs[state.curdc].y = mf.records[num].ptlOrigin_x,mf.records[num].ptlOrigin_y
##    print 'SetWOrg',state.DCs[state.curdc].x, state.DCs[state.curdc].y
    
def SetWindowExtEx(mf,num,page,state):
    state.DCs[state.curdc].Wx, state.DCs[state.curdc].Wy = mf.records[num].szlExtent_cx,mf.records[num].szlExtent_cy
##    print 'SetWExt',state.DCs[state.curdc].Wx, state.DCs[state.curdc].Wy
    
def ShapeSetFill(obj,state):
    if state.mfobjs[state.curbrush].style == 1 or state.curbrush == 0x80000005:
        obj.nofill = 1
    else:
        obj.fclr.r = state.mfobjs[state.curbrush].clr.r
        obj.fclr.g = state.mfobjs[state.curbrush].clr.g
        obj.fclr.b = state.mfobjs[state.curbrush].clr.b
        obj.PFMode = state.PFMode
        obj.fstyle = state.mfobjs[state.curbrush].style
        obj.hatch = state.mfobjs[state.curbrush].hatch
        if obj.fstyle == 3:
            obj.data = state.mfobjs[state.curbrush].data
        
def ShapeSetStroke(obj,state,zoom):
    obj.bkcolor.r = state.bk.color.r
    obj.bkcolor.g = state.bk.color.g
    obj.bkcolor.b = state.bk.color.b
    obj.bkmode = state.bk.mode
    if state.mfobjs[state.curpen].style == 5 or state.curpen == 0x80000008:
        obj.noline = 1
    else:
        obj.clr.r = state.mfobjs[state.curpen].clr.r
        obj.clr.g = state.mfobjs[state.curpen].clr.g
        obj.clr.b = state.mfobjs[state.curpen].clr.b
        obj.style = state.mfobjs[state.curpen].style
        obj.width = state.mfobjs[state.curpen].width        
        if state.mfobjs[state.curpen].width < 2.1 or (state.mfobjs[state.curpen].style > 0 and state.mfobjs[state.curpen].style < 5):
            obj.width = 0.5/zoom
            
def Rectangle(mf,num,page,state):
    x1,y1,x2,y2 = mf.records[num].values
    xr1,yr1 = convcoords(state,x1,y1)
    xr2,yr2 = convcoords(state,x2,y2)
    if state.DCs[state.curdc].pathmode:
        path = page.obj(state.DCs[state.curdc].pathobj)
        pp = gmodel.PathPoint()
        pp.type = 1
        p = gmodel.Point()
        p.x,p.y = xr1,yr1
        pp.pts.append(p)
        path.pplist.append(pp)
        pp = gmodel.PathPoint()
        pp.type = 2
        p = gmodel.Point()
        p.x,p.y = xr1,yr2
        pp.pts.append(p)
        path.pplist.append(pp)
        pp = gmodel.PathPoint()
        pp.type = 2
        p = gmodel.Point()
        p.x,p.y = xr2,yr2
        pp.pts.append(p)
        path.pplist.append(pp)
        pp = gmodel.PathPoint()
        pp.type = 2
        p = gmodel.Point()
        p.x,p.y = xr2,yr1
        pp.pts.append(p)
        path.pplist.append(pp)
        pp = gmodel.PathPoint()
        pp.type = 4
        pp.pts.append(p)
        path.pplist.append(pp)
    else:
        rect = gmodel.Rect()
        rect.p0.x,rect.p0.y = xr1,yr1
        rect.pe.x,rect.pe.y = xr2,yr2
        ShapeSetFill(rect,state)
        ShapeSetStroke(rect,state,page.zoom)
        rect.pagetrafo = page.trafo
        page.objs.append(rect)
##    print 'Rectangle:',state.curbrush,state.curpen,'Pen w/s/b',rect.width,state.mfobjs[state.curpen].style,rect.clr.r,rect.clr.g,rect.clr.b,'Brush s/b',state.mfobjs[state.curbrush].style,rect.fclr.b

def RoundRect(mf,num,page,state):
    ry,rx,pey,pex,p0y,p0x = mf.records[num].values
    xr1,yr1 = convcoords(state,p0x,p0y)
    xr2,yr2 = convcoords(state,pex,pey)
    rrect = gmodel.RoundRect()
    rrect.p0.x,rrect.p0.y = xr1,yr1
    rrect.pe.x,rrect.pe.y = xr2,yr2
    rrect.rx = rx
    rrect.ry = ry
    ShapeSetFill(rrect,state)
    ShapeSetStroke(rrect,state,page.zoom)
    rrect.pagetrafo = page.trafo
    page.objs.append(rrect)

def Chord(mf,num,page,state):
    ye,xe,ys,xs,b,r,t,l = mf.records[num].values
    xe,ye = convcoords(state,xe,ye)
    xs,ys = convcoords(state,xs,ys)
    xc,yc = convcoords(state,(l+r)/2.,(t+b)/2.)
    dx = math.fabs((r-l))#*1./state.DCs[state.curdc].Wx)
    dy = math.fabs((b-t))#*1./state.DCs[state.curdc].Wy)
    chord = gmodel.Chord()
    chord.c.x,chord.c.y = xc,yc
    chord.a1 = math.atan2((ys-yc),(xs-xc))
    chord.a2 = math.atan2((ye-yc),(xe-xc))
    chord.rx = dx
    chord.ry = dy
    ShapeSetFill(chord,state)
    ShapeSetStroke(chord,state,page.zoom)
    chord.pagetrafo = page.trafo
    page.objs.append(chord)

def Pie(mf,num,page,state):
    ye,xe,ys,xs,b,r,t,l = mf.records[num].values
    xe,ye = convcoords(state,xe,ye)
    xs,ys = convcoords(state,xs,ys)
    xc,yc = convcoords(state,(l+r)/2.,(t+b)/2.)
    dx = math.fabs((r-l))#*1./state.DCs[state.curdc].Wx)
    dy = math.fabs((b-t))#*1./state.DCs[state.curdc].Wy)
    pie = gmodel.Pie()
    pie.c.x,pie.c.y = xc,yc
    pie.a1 = math.atan2((ys-yc),(xs-xc))
    pie.a2 = math.atan2((ye-yc),(xe-xc))
    pie.rx = dx
    pie.ry = dy
    ShapeSetFill(pie,state)
    ShapeSetStroke(pie,state,page.zoom)
    pie.pagetrafo = page.trafo
    page.objs.append(pie)
    
def MoveTo(mf,num,page,state):
    x,y = mf.records[num].values
    xr1,yr1 = convcoords(state,x,y)
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        pp = gmodel.PathPoint()
        pp.type = 1
        p = gmodel.Point()
        p.x,p.y = xr1,yr1
        pp.pts.append(p)
        path.pplist.append(pp)
    else:
        state.DCs[state.curdc].p0x = xr1
        state.DCs[state.curdc].p0y = yr1

def LineTo(mf,num,page,state):
    x,y = mf.records[num].values
    xr1,yr1 = convcoords(state,x,y)
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        pp = gmodel.PathPoint()
        pp.type = 2
        p = gmodel.Point()
        p.x,p.y = xr1,yr1
        pp.pts.append(p)
        path.pplist.append(pp)
    else:
        line = gmodel.LineTo()
        line.p0.x = state.DCs[state.curdc].p0x
        line.p0.y = state.DCs[state.curdc].p0y
        line.pe.x = xr1
        line.pe.y = yr1
        state.DCs[state.curdc].p0x = xr1
        state.DCs[state.curdc].p0y = yr1
        ShapeSetStroke(line,state,page.zoom)
        line.pagetrafo = page.trafo
        page.objs.append(line)

def Arc(mf,num,page,state):
    l,t,r,b,xs,ys,xe,ye = mf.records[num].values
    xe,ye = convcoords(state,xe,ye)
    xs,ys = convcoords(state,xs,ys)
    xc,yc = convcoords(state,(l+r)/2.,(t+b)/2.)
    dx = math.fabs((r-l))#*1./state.DCs[state.curdc].Wx)
    dy = math.fabs((b-t))#*1./state.DCs[state.curdc].Wy)
    arc = gmodel.ArcTo()
    arc.c.x,arc.c.y = xc,yc
    arc.a1 = math.atan2((ys-yc),(xs-xc))
    arc.a2 = math.atan2((ye-yc),(xe-xc))
    arc.rx = dx
    arc.ry = dy
    ShapeSetStroke(arc,state,page.zoom)
    arc.pagetrafo = page.trafo
    page.objs.append(arc)

def ArcTo(mf,num,page,state):
    l,t,r,b,xs,ys,xe,ye = mf.records[num].values
    xe,ye = convcoords(state,xe,ye)
    xs,ys = convcoords(state,xs,ys)
    xc,yc = convcoords(state,(l+r)/2.,(t+b)/2.)
    dx = math.fabs((r-l))#*1./state.DCs[state.curdc].Wx)
    dy = math.fabs((b-t))#*1./state.DCs[state.curdc].Wy)
    line = gmodel.LineTo()
    line.p0.x = state.DCs[state.curdc].p0x
    line.p0.y = state.DCs[state.curdc].p0y
    line.pe.x = xc+dx*math.sin(arc.a1)
    line.pe.y = yc+dy*math.cos(arc.a1)
    ShapeSetStroke(line,state,page.zoom)
    line.pagetrafo = page.trafo
    page.objs.append(line)
    arc = gmodel.ArcTo()
    arc.c.x,arc.c.y = xc,yc
    arc.a1 = math.atan2((ys-yc),(xs-xc))
    arc.a2 = math.atan2((ye-yc),(xe-xc))
    arc.rx = dx
    arc.ry = dy
    state.DCs[state.curdc].p0x = xc+dx*math.sin(arc.a2)
    state.DCs[state.curdc].p0y = yc+dy*math.cos(arc.a2)
    ShapeSetStroke(arc,state,page.zoom)
    arc.pagetrafo = page.trafo
    page.objs.append(arc)

def Ellipse(mf,num,page,state):
    x1,y1,x2,y2 = mf.records[num].values
    xr1,yr1 = convcoords(state,x1,y1)
    xr2,yr2 = convcoords(state,x2,y2)
    xc = 0.5*(xr1+xr2)
    yc = 0.5*(yr1+yr2)
    r = max(xr2-xc,xr1-xc)
    e = max(yr2-yc,yr1-yc)/r
    ellipse = gmodel.Ellipse()
    ellipse.c.x = xc
    ellipse.c.y = yc
    ellipse.r = r
    ellipse.e = e
    ShapeSetFill(ellipse,state)
    ShapeSetStroke(ellipse,state,page.zoom)
    ellipse.pagetrafo = page.trafo
    page.objs.append(ellipse)
    
def Polygone(mf,num,page,state):
    x,y = mf.records[num].aptl[0]
    xr,yr = convcoords(state,x,y)
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]    
        pp = gmodel.PathPoint()
        pp.type = 1
        p = gmodel.Point()
        p.x,p.y = xr,yr
        pp.pts.append(p)
        path.pplist.append(pp)
        for j in range(len(mf.records[num].aptl)-1):
            x,y = mf.records[num].aptl[j+1]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pp = gmodel.PathPoint()
            pp.type = 2
            pp.pts.append(p)
            path.pplist.append(pp)
        pp = gmodel.PathPoint()
        pp.type = 4
        path.pplist.append(pp)
    else:
        pgone = gmodel.Polygone()
        pgone.pl0.x,pgone.pl0.y = xr,yr
        for j in range(len(mf.records[num].aptl)-1):
            x,y = mf.records[num].aptl[j+1]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pgone.pl.append(p)
        ShapeSetFill(pgone,state)
        ShapeSetStroke(pgone,state,page.zoom)
        pgone.pagetrafo = page.trafo
        page.objs.append(pgone)
        print 'Polygone'

def Polyline(mf,num,page,state):
    x,y = mf.records[num].aptl[0]
    xr,yr = convcoords(state,x,y)
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        pp = gmodel.PathPoint()
        pp.type = 1
        p = gmodel.Point()
        p.x,p.y = xr,yr
        pp.pts.append(p)
        path.pplist.append(pp)
        for j in range(len(mf.records[num].aptl)-1):
            x,y = mf.records[num].aptl[j+1]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pp = gmodel.PathPoint()
            pp.type = 2
            pp.pts.append(p)
            path.pplist.append(pp)
    else:
        pline = gmodel.Polyline()
        pline.pl0.x,pline.pl0.y = xr,yr
        for j in range(len(mf.records[num].aptl)-1):
            x,y = mf.records[num].aptl[j+1]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pline.pl.append(p)
        ShapeSetStroke(pline,state,page.zoom)
        pline.pagetrafo = page.trafo
        page.objs.append(pline)
        print 'Polyline'

def PolylineTo(mf,num,page,state):
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        for j in range(len(mf.records[num].aptl)):
            x,y = mf.records[num].aptl[j]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pp = gmodel.PathPoint()
            pp.type = 2
            pp.pts.append(p)
            path.pplist.append(pp)
    else:
        pline = gmodel.Polyline()
        pline.pl0.x,pline.pl0.y = state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y
        for j in range(len(mf.records[num].aptl)):
            x,y = mf.records[num].aptl[j]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pline.pl.append(p)
        state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y = p.x,p.y
        ShapeSetStroke(pline,state,page.zoom)
        pline.pagetrafo = page.trafo
        page.objs.append(pline)
        print 'PolylineTo'
    
def PolyPolygone(mf,num,page,state):
    aPolyCounts = mf.records[num].aPolyCounts
    aptl = mf.records[num].aptl
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        shift = 0
        for k in range(len(aPolyCounts)): ## number of polygones
            x,y = aptl[shift]
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pp = gmodel.PathPoint()
            pp.type = 1
            pp.pts.append(p)
            path.pplist.append(pp)
            for j in range(aPolyCounts[k]-1): ## number of gones for i-th polygone
                x,y = aptl[j+1+shift]
                p = gmodel.Point()
                p.x,p.y = convcoords(state,x,y)
                pp = gmodel.PathPoint()
                pp.type = 2
                pp.pts.append(p)
                path.pplist.append(pp)
            pp = gmodel.PathPoint()
            pp.type = 4
            path.pplist.append(pp)
            shift+=aPolyCounts[k]
    else:
        ppg = gmodel.PolyPolygone()
        shift = 0
        for k in range(len(aPolyCounts)): ## number of polygones
            x,y = aptl[shift]
            pgone = gmodel.Polygone()
            pgone.pl0.x,pgone.pl0.y = convcoords(state,x,y)
            for j in range(aPolyCounts[k]-1): ## number of gones for i-th polygone
                x,y = aptl[j+1+shift]
                p = gmodel.Point()
                p.x,p.y = convcoords(state,x,y)
                pgone.pl.append(p)
            shift+=aPolyCounts[k]
            ppg.polys.append(pgone)
        ShapeSetFill(ppg,state)
        ShapeSetStroke(ppg,state,page.zoom)
        ppg.pagetrafo = page.trafo
        page.objs.append(ppg)

def Polybezier(mf,num,page,state):
    x,y = mf.records[num].aptl[0]
    xr,yr = convcoords(state,x,y)
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        pp = gmodel.PathPoint()
        pp.type = 1
        p = gmodel.Point()
        p.x,p.y = xr,yr
        pp.pts.append(p)
        path.pplist.append(pp)
        for j in range(len(mf.records[num].aptl)/3):
            pp = gmodel.PathPoint()
            pp.type = 3
            p = gmodel.Point()
            x,y = mf.records[num].aptl[j*3+1]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            p = gmodel.Point()         
            x,y = mf.records[num].aptl[j*3+2]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            p = gmodel.Point()                     
            x,y = mf.records[num].aptl[j*3+3]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            path.pplist.append(pp)        
    else:
        curve = gmodel.Polybezier()
        curve.p0.x, curve.p0.y= xr,yr
        for j in range(len(mf.records[num].aptl)/3):
            trpl = gmodel.Triple()
            x1,y1 = mf.records[num].aptl[j*3+1]
            trpl.x1,trpl.y1 = convcoords(state,x1,y1)
            x2,y2 = mf.records[num].aptl[j*3+2]
            trpl.x2,trpl.y2 = convcoords(state,x2,y2)
            x3,y3 = mf.records[num].aptl[j*3+3]
            trpl.x3,trpl.y3 = convcoords(state,x3,y3)
            curve.trpl.append(trpl)
        ShapeSetStroke(curve,state,page.zoom)
        curve.pagetrafo = page.trafo
        page.objs.append(curve)
    
def PolybezierTo(mf,num,page,state):
    if state.DCs[state.curdc].pathmode:
        path = page.objs[state.DCs[state.curdc].pathobj]
        for j in range(len(mf.records[num].aptl)/3):
            pp = gmodel.PathPoint()
            pp.type = 3
            p = gmodel.Point()
            x,y = mf.records[num].aptl[j*3]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            p = gmodel.Point()         
            x,y = mf.records[num].aptl[j*3+1]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            p = gmodel.Point()                     
            x,y = mf.records[num].aptl[j*3+2]
            xr,yr = convcoords(state,x,y)
            p.x,p.y = xr,yr
            pp.pts.append(p)
            path.pplist.append(pp)        
    else:
        curve = gmodel.Polybezier()
        curve.p0.x, curve.p0.y= state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y
        for j in range(len(mf.records[num].aptl)/3):
            trpl = gmodel.Triple()
            x1,y1 = mf.records[num].aptl[j*3]
            trpl.x1,trpl.y1 = convcoords(state,x1,y1)
            x2,y2 = mf.records[num].aptl[j*3+1]
            trpl.x2,trpl.y2 = convcoords(state,x2,y2)
            x3,y3 = mf.records[num].aptl[j*3+2]
            trpl.x3,trpl.y3 = convcoords(state,x3,y3)
            curve.trpl.append(trpl)
        state.DCs[state.curdc].p0x = trpl.x3
        state.DCs[state.curdc].p0y = trpl.y3
        ShapeSetStroke(curve,state,page.zoom)
        curve.pagetrafo = page.trafo
        page.objs.append(curve)

def SetWorldTransform(mf,num,page,state):
    em11,em12,em21,em22,dx,dy,mode = mf.records[num].values
    matrix = cairo.Matrix(em11,em12,em21,em22,dx,dy)
    state.DCs[state.curdc].trafo = matrix
    state.DCs[state.curdc].trafomode = 1
    
def ModifyWorldTransform(mf,num,page,state):
    em11,em12,em21,em22,dx,dy,mode = mf.records[num].values
    matrix = cairo.Matrix(em11,em12,em21,em22,dx,dy)
    state.DCs[state.curdc].trafo = matrix
    state.DCs[state.curdc].trafomode = mode
    
def IntersectClipRect(mf,num,page,state):
##    l,t,r,b = mf.records[num].values
    parser.IntersectClipRect(mf,num,page,state)
    
def BeginPath(mf,num,page,state):
    state.DCs[state.curdc].pathmode = 1
    state.DCs[state.curdc].pathobj = len(page.objs)
    path = gmodel.Path()
    path.pagetrafo = page.trafo
    page.objs.append(path)
    
def EndPath(mf,num,page,state):
    state.DCs[state.curdc].pathmode = 0
    
def CloseFigure(mf,num,page,state):
    pp = gmodel.PathPoint()
    pp.type = 4
    page.objs[state.DCs[state.curdc].pathobj].pplist.append(pp)

def FillPath(mf,num,page,state):
    ShapeSetFill(page.objs[state.DCs[state.curdc].pathobj],state)
    page.objs[state.DCs[state.curdc].pathobj].noline = 1
    
def StrokePath(mf,num,page,state):
    ShapeSetStroke(page.objs[state.DCs[state.curdc].pathobj],state,page.zoom)
    page.objs[state.DCs[state.curdc].pathobj].nofill = 1
    
def StrokeAndFillPath(mf,num,page,state):
    ShapeSetFill(page.objs[state.DCs[state.curdc].pathobj],state)
    ShapeSetStroke(page.objs[state.DCs[state.curdc].pathobj],state,page.zoom)

def SelectClipPath(mf,num,page,state):
    state.clipflag = 1
    state.DCs[state.curdc].clipset=1
    
symbol = {
  0x00:'\x00\x00', 0x01:'\x01\x00', 0x02:'\x02\x00', 0x03:'\x03\x00',
  0x04:'\x04\x00', 0x05:'\x05\x00', 0x06:'\x06\x00', 0x07:'\x07\x00',
  0x08:'\x08\x00', 0x09:'\x09\x00', 0x0a:'\x0a\x00', 0x0b:'\x0b\x00',
  0x0c:'\x0c\x00', 0x0d:'\x0d\x00', 0x0e:'\x0e\x00', 0x0f:'\x0f\x00',
  0x10:'\x10\x00', 0x11:'\x11\x00', 0x12:'\x12\x00', 0x13:'\x13\x00',
  0x14:'\x14\x00', 0x15:'\x15\x00', 0x16:'\x16\x00', 0x17:'\x17\x00',
  0x18:'\x18\x00', 0x19:'\x19\x00', 0x1a:'\x1a\x00', 0x1b:'\x1b\x00',
  0x1c:'\x1c\x00', 0x1d:'\x1d\x00', 0x1e:'\x1e\x00', 0x1f:'\x1f\x00',
  0x20:'\x20\x00', 0x21:'\x21\x00', 0x22:'\x00\x22', 0x23:'\x23\x00',
  0x24:'\x03\x22', 0x25:'\x25\x00', 0x26:'\x26\x00', 0x27:'\x0d\x22',
  0x28:'\x28\x00', 0x29:'\x29\x00', 0x2a:'\x17\x22', 0x2b:'\x2b\x00',
  0x2c:'\x2c\x00', 0x2d:'\x12\x22', 0x2e:'\x2e\x00', 0x2f:'\x2f\x00',
  0x30:'\x30\x00', 0x31:'\x31\x00', 0x32:'\x32\x00', 0x33:'\x33\x00',
  0x34:'\x34\x00', 0x35:'\x35\x00', 0x36:'\x36\x00', 0x37:'\x37\x00',
  0x38:'\x38\x00', 0x39:'\x39\x00', 0x3a:'\x3a\x00', 0x3b:'\x3b\x00',
  0x3c:'\x3c\x00', 0x3d:'\x3d\x00', 0x3e:'\x3e\x00', 0x3f:'\x3f\x00',
  0x40:'\x45\x22', 0x41:'\x91\x03', 0x42:'\x92\x03', 0x43:'\xa7\x03',
  0x44:'\x94\x03', 0x45:'\x95\x03', 0x46:'\xa6\x03', 0x47:'\x93\x03',
  0x48:'\x97\x03', 0x49:'\x99\x03', 0x4a:'\xd1\x03', 0x4b:'\x9a\x03',
  0x4c:'\x9b\x03', 0x4d:'\x9c\x03', 0x4e:'\x9d\x03', 0x4f:'\x9f\x03',
  0x50:'\xa0\x03', 0x51:'\x98\x03', 0x52:'\xa1\x03', 0x53:'\xa3\x03',
  0x54:'\xa4\x03', 0x55:'\xa5\x03', 0x56:'\xc2\x03', 0x57:'\xa9\x03',
  0x58:'\x9e\x03', 0x59:'\xa8\x03', 0x5a:'\x96\x03', 0x5b:'\x5b\x00',
  0x5c:'\x34\x22', 0x5d:'\x5d\x00', 0x5e:'\xa5\x22', 0x5f:'\x5f\x00',
  0x60:'\xe5\xf8', 0x61:'\xb1\x03', 0x62:'\xb2\x03', 0x63:'\xc7\x03',
  0x64:'\xb4\x03', 0x65:'\xb5\x03', 0x66:'\xc6\x03', 0x67:'\xb3\x03',
  0x68:'\xb7\x03', 0x69:'\xb9\x03', 0x6a:'\xd5\x03', 0x6b:'\xba\x03',
  0x6c:'\xbb\x03', 0x6d:'\xbc\x03', 0x6e:'\xbd\x03', 0x6f:'\xbf\x03',
  0x70:'\xc0\x03', 0x71:'\xb8\x03', 0x72:'\xc1\x03', 0x73:'\xc3\x03',
  0x74:'\xc4\x03', 0x75:'\xc5\x03', 0x76:'\xd6\x03', 0x77:'\xc9\x03',
  0x78:'\xbe\x03', 0x79:'\xc8\x03', 0x7a:'\xb6\x03', 0x7b:'\x7b\x00',
  0x7c:'\x7c\x00', 0x7d:'\x7d\x00', 0x7e:'\x3c\x22', 0x7f:'\x7f\x00',
  0x80:'\x80\x00', 0x81:'\x81\x00', 0x82:'\x82\x00', 0x83:'\x83\x00',
  0x84:'\x84\x00', 0x85:'\x85\x00', 0x86:'\x86\x00', 0x87:'\x87\x00',
  0x88:'\x88\x00', 0x89:'\x89\x00', 0x8a:'\x8a\x00', 0x8b:'\x8b\x00',
  0x8c:'\x8c\x00', 0x8d:'\x8d\x00', 0x8e:'\x8e\x00', 0x8f:'\x8f\x00',
  0x90:'\x90\x00', 0x91:'\x91\x00', 0x92:'\x92\x00', 0x93:'\x93\x00',
  0x94:'\x94\x00', 0x95:'\x95\x00', 0x96:'\x96\x00', 0x97:'\x97\x00',
  0x98:'\x98\x00', 0x99:'\x99\x00', 0x9a:'\x9a\x00', 0x9b:'\x9b\x00',
  0x9c:'\x9c\x00', 0x9d:'\x9d\x00', 0x9e:'\x9e\x00', 0x9f:'\x9f\x00',
  0xa0:'\x00\x00', 0xa1:'\xd2\x03', 0xa2:'\x32\x20', 0xa3:'\x64\x22',
  0xa4:'\x44\x20', 0xa5:'\x1e\x20', 0xa6:'\x92\x01', 0xa7:'\x63\x26',
  0xa8:'\x66\x26', 0xa9:'\x65\x26', 0xaa:'\x60\x26', 0xab:'\x94\x21',
  0xac:'\x90\x21', 0xad:'\x91\x21', 0xae:'\x92\x21', 0xaf:'\x93\x21',
  0xb0:'\xb0\x00', 0xa1:'\xb1\x00', 0xb2:'\x33\x20', 0xb3:'\x65\x22',
  0xb4:'\xd7\x00', 0xb5:'\x1d\x22', 0xb6:'\x02\x22', 0xb7:'\x22\x20',
  0xb8:'\xf7\x00', 0xb9:'\x60\x22', 0xba:'\x61\x22', 0xbb:'\x48\x22',
  0xbc:'\x26\x20', 0xbd:'\xe6\xf8', 0xbe:'\xe7\xf8', 0xbf:'\xb5\x21',
  0xc0:'\x35\x21', 0xc1:'\x11\x21', 0xc2:'\x1c\x21', 0xc3:'\x18\x21',
  0xc4:'\x97\x22', 0xc5:'\x95\x22', 0xc6:'\x05\x22', 0xc7:'\x29\x22',
  0xc8:'\x2a\x22', 0xc9:'\x83\x22', 0xca:'\x87\x22', 0xcb:'\x84\x22',
  0xcc:'\x82\x22', 0xcd:'\x86\x22', 0xce:'\x08\x22', 0xcf:'\x09\x22',
  0xd0:'\x20\x22', 0xd1:'\x07\x22', 0xd2:'\xae\x00', 0xd3:'\xa9\x00',
  0xd4:'\x22\x21', 0xd5:'\x0f\x22', 0xd6:'\x1a\x22', 0xd7:'\xc5\x22',
  0xd8:'\xac\x00', 0xd9:'\x27\x22', 0xda:'\x28\x22', 0xdb:'\xd4\x21',
  0xdc:'\xd0\x21', 0xdd:'\xd1\x21', 0xde:'\xd2\x21', 0xdf:'\xd3\x21',
  0xe0:'\xc4\x22', 0xe1:'\x29\x23', 0xe2:'\xe8\xf8', 0xe3:'\xe9\xf8',
  0xe4:'\xea\xf8', 0xe5:'\x11\x22', 0xe6:'\xeb\xf8', 0xe7:'\xec\xf8',
  0xe8:'\xed\xf8', 0xe9:'\xee\xf8', 0xea:'\xef\xf8', 0xeb:'\xf0\xf8',
  0xec:'\xf1\xf8', 0xed:'\xf2\xf8', 0xee:'\xf3\xf8', 0xef:'\xf4\xf8',
  0xf0:'\xff\xf8', 0xf1:'\x2a\x23', 0xf2:'\x2b\x22', 0xf3:'\x20\x23',
  0xf4:'\xf5\xf8', 0xf5:'\x21\x23', 0xf6:'\xf6\xf8', 0xf7:'\xf7\xf8',
  0xf8:'\xf8\xf8', 0xf9:'\xf9\xf8', 0xfa:'\xfa\xf8', 0xfb:'\xfb\xf8',
  0xfc:'\xfc\xf8', 0xfd:'\xfd\xf8', 0xfe:'\xfe\xf8', 0xff:'\xc7\x02'}

charsets = {0:'iso8859-1', ##ANSI_CHARSET
1:'DEFAULT_CHARSET',
2:'SYMBOL_CHARSET',
77:'MAC_CHARSET',
128:'Shift_JIS', ##SHIFTJIS_CHARSET
129:'cp949',##HANGUL_CHARSET
##130:'x-Johab',##JOHAB_CHARSET what is it?
134:'gb2312',##GB2312_CHARSET
136:'Big5',##CHINESEBIG5_CHARSET
161:'windows-1253',##GREEK_CHARSET
162:'windows-1254',##TURKISH_CHARSET
163:'windows-1258',##VIETNAMESE_CHARSET
177:'windows-1255',##HEBREW_CHARSET
178:'windows-1256',##ARABIC_CHARSET
186:'windows-1257',##BALTIC_CHARSET
204:'windows-1251',##RUSSIAN_CHARSET
222:'cp874',##THAI_CHARSET
238:'cp1250',##EASTEUROPE_CHARSET
255:'cp437'##'OEM_CHARSET
}

def symbol_to_utf(text):
    str = ''
    for i in range(len(text)):
        str+=symbol[ord(text[i])]
    return str

txtalign = {0:0, 1:0, 6:1, 2:2,		8:0,9:0,14:1,10:2,		24:0,25:0,30:1,26:2}
cpupdate = {1:1,9:1,25:1}

########## EMF
emr_ids = {0:'Unknown', 1:'Header',2:'Polybezier',3:'Polygone',4:'Polyline',5:'PolybezierTo',\
                 6:'PolylineTo',7:'PolyPolyline',8:'PolyPolygone',9:'SetWindowExtEx',10:'SetWindowOrgEx',\
                 11:'SetViewportExtEx',12:'SetViewportOrgEx',13:'SetBrushOrgEx',14:'EOF',15:'SetPixelV',\
                 16:'SetMapperFlags',17:'SetMapMode',18:'SetBKMode',19:'SetPolyfillMode',20:'SetRop2',\
                 21:'SetStretchBltMode',22:'SetTextAlign', 23:'SetColorAdjustment',24:'SetTextColor',\
                 25:'SetBKColor',26:'OffsetClipRgn',27:'MoveToEx',28:'SetMetaRgn',29:'ExcludeClipRect',\
                 30:'IntersectClipRect',31:'ScaleViewportExtEx',32:'ScaleWindowExtEx',33:'SaveDC',\
                 34:'RestoreDC',35:'SetWorldTransform',36:'ModifyWorldTransform',37:'SelectObject',\
                 38:'CreatePen',39:'CreateBrushIndirect',40:'DeleteObject',41:'AngleArc',42:'Ellipse',\
                 43:'Rectangle',44:'RoundRect',45:'Arc',46:'Chord',47:'Pie',48:'SelectPalette',\
                 49:'CreatePalette',50:'SetPaletteEntries',51:'ResizePalette',52:'RealizePalette',\
                 53:'ExtFloodFill',54:'LineTo',55:'ArcTo',56:'Polydraw',57:'SetArcDirection',58:'SetMiterLimit',\
                 59:'BeginPath',60:'EndPath',61:'CloseFigure',62:'FillPath',63:'StrokeAndFillPath',\
                 64:'StrokePath',65:'FlattenPath',66:'WidenPath',67:'SelectClipPath',68:'AbortPath', ##69 is missed
                 70:'GDIComment',71:'FillRgn',72:'FrameRgn',73:'InvertRgn',74:'PaintRgn',75:'ExtSelectClipRgn',\
                 76:'BitBlt',77:'StretchBlt',78:'MaskBlt',79:'PlgBlt',80:'SetDIBitsToDevice',81:'StretchDIBits',\
                 82:'ExtCreateFontIndirectW',83:'ExtTextOutA',84:'ExtTextOutW',85:'Polybezier16',86:'Polygone16',\
                 87:'Polyline16',88:'PolybezierTo16',89:'PolylineTo16',90:'PolyPolyline16',91:'PolyPolygone16',\
                 92:'Polydraw16',93:'CreateMonoBrush',94:'CreateDIBPatternBrushPT',95:'ExtCreatePen',\
                 96:'PolyTextOutA',97:'PolyTextOutW',98:'SetICMMode',99:'CreateColorSpace',100:'SetColorSpace',\
                 101:'DeleteColorSpace',102:'GLSRecord',103:'GLSBoundedRecord',104:'PixelFormat',105:'DrawEscape',\
                 106:'ExtEscape',107:'StartDoc',108:'SmallTextOut',109:'ForceUFIMapping',110:'NamedEscape',\
                 111:'ColorCorrectPalette',112:'SetICMProfileA',113:'SetICMProfileW',114:'AlphaBlend',\
                 115:'SetLayout',116:'TransparentBlt',117:'Reserved_117',118:'GradientFill',119:'SetLinkedUFI',
                 120:'SetTextJustification',121:'ColorMatchToTargetW',122:'CreateColorSpaceW'}

emr_cmds = {##1:Header, ##2:Polybezier,85:Polybezier,\
            3:Polygone,86:Polygone,\
            4:Polyline,87:Polyline,\
            2:Polybezier,85:Polybezier,\
            5:PolybezierTo,88:PolybezierTo,\
            6:PolylineTo,89:PolylineTo,\
            ##7:PolyPolyline,90:PolyPolyline,\
            8:PolyPolygone,91:PolyPolygone,\
            27:MoveTo,54:LineTo,\
            55:ArcTo,
            42:Ellipse,43:Rectangle,44:RoundRect,45:Arc,46:Chord,47:Pie,\
            84:ExtTextOut,82:CreateFontIndirect,22:SetTextAlign,24:SetTextColor,\
            9:SetWindowExtEx,10:SetWindowOrgEx,11:SetViewportExtEx,12:SetViewportOrgEx,\
            33:SaveDC,34:RestoreDC,\
            35:SetWorldTransform,36:ModifyWorldTransform,\
            37:SelectObject,38:CreatePenIndirect,39:CreateBrushIndirect,40:DeleteObject,\
            95:ExtCreatePen,\
            59:BeginPath,60:EndPath,61:CloseFigure,
            62:FillPath, 63:StrokeAndFillPath,64:StrokePath,67:SelectClipPath,\
            ##21:SetStretchBltMode,81:StretchDIBits,
            19:SetPolyfillMode,\
            20:SetROP2,\
            25:SetBKColor,17:SetMapMode,18:SetBKMode,\
            ##98:SetICMMode,48:SelectPalette
            }
