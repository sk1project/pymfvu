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

############################
# contain parser for files #
############################

import gmodel
import pywmf
import pyemf
import wmf
import struct
import math

def parse(page,buf):
    file = pywmf.WMF()        
    file.loadmem(buf)
    state = wmf.State()
    idx = 0
    Wx,Wy = 1,1
    for i in range(len(file.records)):
        id = file.records[i].mr_id
        if id == 523:
            idx+=1
        if id == 524:
            Wx,Wy = file.records[i].szlExtent_cx,file.records[i].szlExtent_cy
            idx+=1
        if idx == 2:
            page.width = abs(Wx) ##- self.page.DCs[0].x)
            page.height = abs(Wy) ##- self.page.DCs[0].y)
            break
    page.zoom = min(320./page.width,240./page.height)
    state.zoomx,state.zoomy = page.width,page.height
    print 'Page wxh:',page.width,page.height

    for i in range(len(file.records)):
        id = file.records[i].mr_id
        if mr_ids.has_key(id):
            if mr_cmds.has_key(id):
##                print 'COMMAND:',i,mr_ids[id]
                mr_cmds[id](file,i,page,state)
            else:
                print i,'UNSUPPORTED COMMAND!', mr_ids[id]
        else:
            print 'Unknown key: ',id
            
    print 'End of parsing'
    if min(320./page.width,240./page.height)!=page.zoom:
        page.zoom = min(320./page.width,240./page.height)
        state.zoomx,state.zoomy = page.width,page.height
        print 'Page wxh:',page.width,page.height
    if page.width == 1 and page.height == 1:
        page.zoom = 1

def convcoords(state,x,y):
    pdc = state.DCs[state.curdc]
    xr = (x-pdc.x)*pdc.VPx/pdc.Wx + pdc.VPOx
    yr = (y-pdc.y)*pdc.VPy/pdc.Wy + pdc.VPOy
    xr = xr*state.zoomx + 0.5 - (xr*state.zoomx)%1
    yr = yr*state.zoomy + 0.5 - (xr*state.zoomy)%1
    return xr,yr
            
def Aldus_Header(mf,num,page,state):
    t,b,r,l = mf.records[num].rclTop,mf.records[num].rclBottom,mf.records[num].rclRight,mf.records[num].rclLeft
    page.width = abs(r-l)
    page.height = abs(t-b)
    print 'ALD wxh',page.width,page.height
    
def Header(mf,num,page,state):
    state.maxobj = mf.records[num].mtNoObjects
    
def SetBKMode(mf,num,page,state):
    [state.bk.mode] =  mf.records[num].values
    
def SetMapMode(mf,num,page,state):
    fixme =  mf.records[num].values

def SetBKColor(mf,num,page,state):
    bkColor = mf.records[num].bkColor
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
    if state.clipflag:
        PathCopy(state,bmp)
        bmp.clipflag=state.clipflag
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
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            er = mf.records[num]
            eo = wmf.mfobj()
            eo.type = 3
            size = er.values[0]
            if size < 0:
                size = -size
            if size == 0:
                size = 12
            eo.size = size
            eo.weight = er.values[4]
            eo.escape = er.values[2]
            if eo.escape != er.values[3]:
                eo.orient = er.values[3]
            eo.italic = er.values[5]
            eo.under = er.values[6]
            eo.strike = er.values[7]
            eo.charset = er.values[8]
            font = er.data[18:]
            pos = font.find('\x00')
            font = font[0:pos]
            eo.font = font
            state.mfobjs[i]=eo
            break
    
def ExtTextOut(mf,num,page,state):
    y = mf.records[num].values[0]
    x = mf.records[num].values[1]
    count = mf.records[num].values[2]
    flag = mf.records[num].values[3]
    shift = 8
    if flag&4:
        shift = 16
    text = mf.records[num].data[shift:shift+count]
    lentext = len(text)
    dx = mf.records[num].data[shift+count:]
    textstr = text
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
    dxsum = 0
    if len(dx)>3: ## there is shifts
        dxoffs = 0
        dxlist = []
        if lentext/2. != lentext/2:
            dxoffs = 1
        for i in range(lentext-1):
            [d] = struct.unpack('h',dx[i*2+dxoffs:i*2+2+dxoffs])
            dxlist.append(d)
            dxsum=dxsum+d
        dxlist.append(0) ## to simplify my life later
        txt.dx.list = dxlist
    txt.dx.sum = dxsum
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
    if state.clipflag:
        PathCopy(state,txt)    
        txt.clipflag=state.clipflag ### INSTANCE!!!
    page.objs.append(txt)
    
def TextOut(mf,num,page,state):
    count = mf.records[num].values[0]
    textstr = mf.records[num].data[2:2+count]
    text = textstr
    lentext = len(text)
    [y] = struct.unpack('>h',mf.records[num].data[2+count:4+count])
    [x] = struct.unpack('>h',mf.records[num].data[4+count:6+count])
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
    if cpupdate.has_key(state.txt.align):
        txt.cpupdate = 1
        txt.p0.x,txt.p0.y = state.DCs[state.curdc].p0x,state.DCs[state.curdc].p0y
    else:
        txt.p0.x,txt.p0.y = x,y
    if state.clipflag:
        PathCopy(state,txt)    
        txt.clipflag=state.clipflag
    page.objs.append(txt)
    
def DeleteObject(mf,num,page,state):
    del state.mfobjs[mf.records[num].handle]
    
def CreatePalette(mf,num,page,state):
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            data = mf.records[num].data[4:]
            eo = wmf.mfobj()
            eo.type = 4
            for j in range(mf.records[num].lpltNumofclr):
                clr = wmf.Color()
                clr.r,clr.g,clr.b = ord(data[j*4]),ord(data[j*4+1]),ord(data[j*4+2])
                state.palette[j]=clr
            state.mfobjs[i] = eo
            break
            
def CreateBrushIndirect(mf,num,page,state):
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
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            mfo = wmf.mfobj()
            mfo.type = 2
            mfo.clr.r = r
            mfo.clr.g = g
            mfo.clr.b= b
            mfo.style = lbStyle
            mfo.hatch = lbHatch
            state.mfobjs[i] = mfo
            break
##    print 'Brush:',i,'Color:',r,g,b,'Style:',lbStyle,lbHatch
    
def DibCreatePatternBrush(mf,num,page,state):
    palsize = {1:8,2:16,4:64,8:1024,16:0,24:0,32:0}
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            ern = mf.records[num]
            bd = ern.biDepth
            bshift = palsize[bd]+54
            eo = wmf.mfobj()
            eo.type = 2
            eo.style = 3 ## pattern brush
            eo.data = ern.biWidth,ern.biHeight,ern.nSize+4,bshift,ern.data[4:] ## temporary assume 1 bpp image
            state.mfobjs[i] = eo
            break
            
def CreatePatternBrush(mf,num,page,state):
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            fixme = mf.records[num].data
            state.mfobjs[i] = 0
            break
            
def CreatePenIndirect(mf,num,page,state):
    lbColor = mf.records[num].lopnColor
    width = mf.records[num].lopnWidth
    style = mf.records[num].lopnStyle
    f =  (lbColor>>24)&0xFF    
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    if f ==1:
        clr = state.palette[r]  ## FIXME1 It has to be 2 bytes index made of R and G.
        r,g,b = clr.r,clr.g,clr.b 
    i = 0
    while i<state.maxobj:
        try:
            data = state.mfobjs[i]
            i+=1
        except:
            mfo = wmf.mfobj()
            mfo.type = 1
            mfo.clr.r = r
            mfo.clr.g = g
            mfo.clr.b= b
            mfo.style = style
            mfo.width = width
            state.mfobjs[i] = mfo
            break
##    print 'Pen:',i,'Color:',r,g,b,'Style:',style,width,f

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
    if state.DCs[state.curdc].clipset:
        state.clipflag=2
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
    state.DCs[state.curdc+1].cliplist = state.DCs[state.curdc].cliplist 
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
    y2,x2,y1,x1 = mf.records[num].values
    xr1,yr1 = convcoords(state,x1,y1)
    xr2,yr2 = convcoords(state,x2,y2)
    rect = gmodel.Rect()
    rect.p0.x,rect.p0.y = xr1,yr1
    rect.pe.x,rect.pe.y = xr2,yr2
    ShapeSetFill(rect,state)
    ShapeSetStroke(rect,state,page.zoom)
    if state.clipflag:
        PathCopy(state,rect)
        rect.clipflag=state.clipflag ### INSTANCE!!!
    page.objs.append(rect)
    print 'Rect3:',rect.cliplist
##    print 'Rectangle:',state.curbrush,state.curpen,'Pen w/s/b',rect.width,state.mfobjs[state.curpen].style,rect.clr.r,rect.clr.g,rect.clr.b,'Brush s/b',state.mfobjs[state.curbrush].style,rect.fclr.b

def PathCopy(state,shape):
    for j in state.DCs[state.curdc].cliplist:
        p = gmodel.Path()
        for i in j.pplist:
            pp = gmodel.PathPoint()
            pp.type = i.type
            if i.type>0 and i.type<4:
                pts = gmodel.Point()
                pts.x = i.pts[0].x
                pts.y = i.pts[0].y
                pp.pts.append(pts)
            if i.type == 3:
                pts = gmodel.Point()
                pts.x = i.pts[1].x
                pts.x = i.pts[1].y
                pp.pts.append(pts)
                pts = gmodel.Point()
                pts.x = i.pts[2].x
                pts.x = i.pts[2].y
                pp.pts.append(pts)
            p.pplist.append(pp)
        shape.cliplist.append(p)    


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
    if state.clipflag:
        PathCopy(state,rrect)
        rrect.clipflag=state.clipflag
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
    if state.clipflag:
        PathCopy(state,chord)
        chord.clipflag=state.clipflag
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
    if state.clipflag:
        PathCopy(state,pie)
        pie.clipflag=state.clipflag
    page.objs.append(pie)
    
def MoveTo(mf,num,page,state):
    y,x = mf.records[num].values
    xr1,yr1 = convcoords(state,x,y)
    state.DCs[state.curdc].p0x = xr1
    state.DCs[state.curdc].p0y = yr1

def LineTo(mf,num,page,state):
    y,x = mf.records[num].values
    xr1,yr1 = convcoords(state,x,y)
    line = gmodel.LineTo()
    line.p0.x = state.DCs[state.curdc].p0x
    line.p0.y = state.DCs[state.curdc].p0y
    line.pe.x = xr1
    line.pe.y = yr1
    state.DCs[state.curdc].p0x = xr1
    state.DCs[state.curdc].p0y = yr1
    ShapeSetStroke(line,state,page.zoom)
    if state.clipflag:
        PathCopy(state,line)
        line.clipflag=state.clipflag
    page.objs.append(line)

def Arc(mf,num,page,state):
    ye,xe,ys,xs,b,r,t,l = mf.records[num].values
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
    state.DCs[state.curdc].p0x = xc+dx*math.sin(arc.a2)
    state.DCs[state.curdc].p0y = yc+dy*math.cos(arc.a2)
    ShapeSetStroke(arc,state,page.zoom)
    if state.clipflag:
        PathCopy(state,arc)
        arc.clipflag=state.clipflag
    page.objs.append(arc)

def Ellipse(mf,num,page,state):
    y2,x2,y1,x1 = mf.records[num].values
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
    if state.clipflag:
        PathCopy(state,ellipse)
        ellipse.clipflag=state.clipflag
    page.objs.append(ellipse)
    
def Polygone(mf,num,page,state):
    pgone = gmodel.Polygone()
    x,y = mf.records[num].aptl[0]
    pgone.pl0.x,pgone.pl0.y = convcoords(state,x,y)
    for j in range(len(mf.records[num].aptl)-1):
        x,y = mf.records[num].aptl[j+1]
        p = gmodel.Point()
        p.x,p.y = convcoords(state,x,y)
        pgone.pl.append(p)
    ShapeSetFill(pgone,state)
    ShapeSetStroke(pgone,state,page.zoom)
    if state.clipflag:
        PathCopy(state,pgone)
        pgone.clipflag=state.clipflag
    page.objs.append(pgone)

def Polyline(mf,num,page,state):
    pline = gmodel.Polyline()
    x,y = mf.records[num].aptl[0]
    pline.pl0.x,pline.pl0.y = convcoords(state,x,y)
    for j in range(len(mf.records[num].aptl)-1):
        x,y = mf.records[num].aptl[j+1]
        p = gmodel.Point()
        p.x,p.y = convcoords(state,x,y)
        pline.pl.append(p)
    ShapeSetStroke(pline,state,page.zoom)
    if state.clipflag:
        PathCopy(state,pline)
        pline.clipflag=state.clipflag
    page.objs.append(pline)
    
def PolyPolygone(mf,num,page,state):
    nPolys = mf.records[num].nPolys
    erd = mf.records[num].data[2:]
    aptl = {}
    for i in range(nPolys):
        [aptl[i]] = struct.unpack('<h',erd[i*2:i*2+2])
    data = erd[nPolys*2:]
    ppg = gmodel.PolyPolygone()
    shift = 0
    for k in range(nPolys): ## number of polygones
        pgone = gmodel.Polygone()
        [x] = struct.unpack('<h',data[shift:shift+2])
        [y] = struct.unpack('<h',data[shift+2:shift+4])
        pgone.pl0.x,pgone.pl0.y = convcoords(state,x,y)
        for j in range(aptl[k]): ## number of gones for i-th polygone
            [x] = struct.unpack('<h',data[j*4+shift:j*4+shift+2])
            [y] = struct.unpack('<h',data[j*4+shift+2:j*4+shift+4])
            p = gmodel.Point()
            p.x,p.y = convcoords(state,x,y)
            pgone.pl.append(p)
        shift+=aptl[k]*4
        ppg.polys.append(pgone)
    ShapeSetFill(ppg,state)
    ShapeSetStroke(ppg,state,page.zoom)
    if state.clipflag:
        PathCopy(state,ppg)
        ppg.clipflag=state.clipflag
    page.objs.append(ppg)

def IntersectClipRect(mf,num,page,state):
    b,r,t,l = mf.records[num].values
    xr1,yr1 = convcoords(state,l,t)
    xr2,yr2 = convcoords(state,r,b)
    path = gmodel.Path()
    path.pagetrafo = page.trafo
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
    state.DCs[state.curdc].cliplist.append(path)
    state.clipflag = 1
    state.DCs[state.curdc].clipset=1

def OffsetClipRgn(mf,num,page,state):
##    return
    y,x = mf.records[num].values
    print 'Offset',x,y
    x,y = convcoords(state,x,y)
    x0,y0 = convcoords(state,0,0)
    x = x - x0
    y = y - y0
    for j in state.DCs[state.curdc].cliplist:
        for i in j.pplist:
            if i.type>0 and i.type<4:
                i.pts[0].x+=x
                i.pts[0].y+=y
            if i.type == 3:
                i.pts[1].x+=x
                i.pts[1].y+=y
                i.pts[2].x+=x
                i.pts[2].y+=y
    state.clipflag = 2
    state.DCs[state.curdc].clipset=1
        
    
mr_ids = {1:'Aldus_Header',2:'CLP_Header16',3:'CLP_Header32',4:'Header',
            30:'SaveDC', 295:'RestoreDC', 332:'ResetDc', 
            
            53:'RealizePalette', 55:'SetPalEntries', 247:'CreatePalette', 313:'ResizePalette',564:'SelectPalette', 1078:'AnimatePalette', 
            79:'StartPage', 80:'EndPage', 82:'AbortDoc', 94:'EndDoc', 333:'StartDoc', 
            
            248:'CreateBrush', 322:'DibCreatePatternBrush', 505:'CreatePatternBrush',
            762:'CreatePenIndirect',763:'CreateFontIndirect', 764:'CreateBrushIndirect', 765:'CreateBitmapIndirect', 
            496:'DeleteObject', 301:'SelectObject', 
            
            258:'SetBKMode', 259:'SetMapMode', 260:'SetROP2', 261:'SetRelabs', 262:'SetPolyfillMode', 263:'SetStretchBltMode',
            561:'SetMapperFlags', 
            264:'SetTextCharExtra', 302:'SetTextAlign', 513:'SetBKColor', 521:'SetTextColor', 522:'SetTextJustification', 
            
            298:'InvertRegion', 299:'PaintRegion', 300:'SelectClipRegion',544:'OffsetClipRgn', 552:'FillRegion', 1065:'FrameRegion', 1791:'CreateRegion',
            1045:'ExcludeClipRect', 1046:'IntersectClipRect',
            523:'SetWindowOrgEx', 524:'SetWindowExtEx',525:'SetViewportOrgEx', 526:'SetViewportExtEx', 527:'OffsetWindowOrg', 529:'OffsetViewportOrgEx',
            1040:'ScaleWindowExtEx', 1042:'ScaleViewportExtEx',
            
            1049:'FloodFill', 1321:'META_MAGIC???', 1352:'ExtFloodFill', 1574:'Escape', 
            
            531:'LineTo', 532:'MoveTo', 804:'Polygone', 805:'Polyline', 1048:'Ellipse', 1051:'Rectangle', 1055:'SetPixel', 
            1336:'PolyPolygone', 1564:'RoundRect', 2071:'Arc', 2074:'Pie', 2096:'Chord', 
            1313:'TextOut', 1583:'DrawText',2610:'ExtTextOut',
            1790:'CreateBitmap', 1565:'PatBlt', 2338:'BitBlt', 2368:'DibBitblt', 2851:'StretchBlt', 2881:'DibStretchBlt', 3379:'SetDibToDev', 3907:'StretchDIBits'
            }

mr_cmds  = {1:Aldus_Header,4:Header,
            30:SaveDC, 295:RestoreDC, ##332:ResetDc, 
            
            ##53:'RealizePalette', 55:'SetPalEntries',
            247:CreatePalette, ##313:'ResizePalette',1078:'AnimatePalette', 
##            564:SelectPalette, 
            ##79:'StartPage', 80:'EndPage', 82:'AbortDoc', 94:'EndDoc', 333:'StartDoc', 
            
            ##248:CreateBrush,
            322:DibCreatePatternBrush, 505:CreatePatternBrush,
            762:CreatePenIndirect,763:CreateFontIndirect, 764:CreateBrushIndirect, ##765:CreateBitmapIndirect, 
            496:DeleteObject, 301:SelectObject, 
            
            258:SetBKMode, 259:SetMapMode, 260:SetROP2, 262:SetPolyfillMode, 263:SetStretchBltMode,##261:SetRelabs,
            ##561:SetMapperFlags, 
            ## 264:'SetTextCharExtra',
            302:SetTextAlign, 513:SetBKColor, 521:SetTextColor, ##522:SetTextJustification, 
            
            ##298:'InvertRegion', 299:'PaintRegion', 300:'SelectClipRegion',
            544:OffsetClipRgn, ##552:'FillRegion', 1065:'FrameRegion', 1791:'CreateRegion',
            ##1045:'ExcludeClipRect',
            1046:IntersectClipRect,
            523:SetWindowOrgEx, 524:SetWindowExtEx,525:SetViewportOrgEx, 526:SetViewportExtEx, ##527:'OffsetWindowOrg', 529:'OffsetViewportOrgEx',
            ##1040:'ScaleWindowExtEx', 1042:'ScaleViewportExtEx',
            
            ##1049:'FloodFill', 1321:'META_MAGIC???', 1352:'ExtFloodFill', 1574:'Escape', 
            
            531:LineTo, 532:MoveTo, 804:Polygone, 805:Polyline, 1048:Ellipse, 1051:Rectangle, ##1055:'SetPixel', 
            1336:PolyPolygone, 1564:RoundRect, 2071:Arc, 2074:Pie, 2096:Chord, 
            1313:TextOut, ##1583:DrawText,
            2610:ExtTextOut,
            ##1790:'CreateBitmap', 1565:'PatBlt', 2338:'BitBlt', 2368:'DibBitblt', 2851:'StretchBlt', 2881:'DibStretchBlt', 3379:'SetDibToDev',
           3907:StretchDIBits
            }
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
