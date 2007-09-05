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

import pywmf
import wmfdoc
import struct

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
            
def IntersectClipRect(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1046
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Polygone(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 804
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)

def Polyline(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 805
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)
    
def PolyPolygone(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1336
    nPolys = emf.records[num].nPolys
    erd = emf.records[num].data[2:]
    aptl = {}
    for i in range(nPolys):
        [aptl[i]] = struct.unpack('<h',erd[i*2:i*2+2])
    cmd.args = nPolys,aptl,erd[nPolys*2:]
    page.cmds.append(cmd)
    
def MoveTo(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 532
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def LineTo(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 531
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Arc(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 2071
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Ellipse(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1048
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Rectangle(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1051
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def RoundRect(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1564
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Chord(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 2096
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)
    
def Pie(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 2074
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetWindowExtEx(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 524
    cmd.args = emf.records[num].szlExtent_cx,emf.records[num].szlExtent_cy
    page.cmds.append(cmd)

def SetWindowOrgEx(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 523
    cmd.args = emf.records[num].ptlOrigin_x,emf.records[num].ptlOrigin_y
    page.cmds.append(cmd)

def SetViewportExtEx(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 526
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetViewportOrgEx(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 525
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)
    
def SaveDC(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 30
    page.cmds.append(cmd)

def RestoreDC(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 295
    page.cmds.append(cmd)
    
def SelectObject(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 301
    cmd.args = emf.records[num].handle
    page.cmds.append(cmd)
    
def CreatePenIndirect(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 762
    lbColor = emf.records[num].lopnColor
    width = emf.records[num].lopnWidth
    style = emf.records[num].lopnStyle
    f =  (lbColor>>24)&0xFF    
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            cmd.args = i,r,g,b,f,width*1.,style
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break

def CreatePatternBrush(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 505
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            cmd.args = emf.records[num].data
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break
    
def DibCreatePatternBrush(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 322
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            ern = emf.records[num]
            bd = ern.biDepth
            bshift = palsize[bd]+54
            cmd.args = i,ern.biWidth,ern.biHeight,ern.nSize+4,bshift,ern.data[4:]
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break
        
def CreateBrushIndirect(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 764
    lbStyle = emf.records[num].lbStyle
    lbColor = emf.records[num].lbColor
    lbHatch = emf.records[num].lbHatch
    f =  (lbColor>>24)&0xFF
    b = (lbColor>>16)&0xFF
    g = (lbColor>>8)&0xFF
    r = lbColor&0xFF
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            cmd.args = i,r,g,b,f,lbStyle,lbHatch
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break
    
def CreatePalette(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 247
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            cmd.args = i,emf.records[num].lpltNumofclr, emf.records[num].data[4:]
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break

def DeleteObject(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 496
    cmd.args = emf.records[num].handle
    del page.wmfobjs[emf.records[num].handle]
    page.cmds.append(cmd)

def TextOut(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1313
    count = emf.records[num].values[0]
    text = emf.records[num].data[2:2+count]
    [y] = struct.unpack('>h',emf.records[num].data[2+count:4+count])
    [x] = struct.unpack('>h',emf.records[num].data[4+count:6+count])
    cmd.args = x,y,text,''
    page.cmds.append(cmd)
    
def ExtTextOut(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 2610
    y = emf.records[num].values[0]
    x = emf.records[num].values[1]
    count = emf.records[num].values[2]
    flag = emf.records[num].values[3]
    shift = 8
    if flag&4:
        shift = 16 
    text = emf.records[num].data[shift:shift+count]
    dx = emf.records[num].data[shift+count:]
    cmd.args = x,y,text,dx
    page.cmds.append(cmd)

def CreateFontIndirect(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 763
    i = 0
    while i<page.maxobj:
        try:
            data = page.wmfobjs[i]
            i+=1
        except:
            er = emf.records[num]
            cmd.args = i,er.values,er.data[18:]
            page.wmfobjs[i] = 0
            page.cmds.append(cmd)
            break

def SetTextColor(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 521
    crColor = emf.records[num].crColor
    f =  (crColor>>24)&0xFF
    b = (crColor>>16)&0xFF
    g = (crColor>>8)&0xFF
    r = crColor&0xFF
    cmd.args = r,g,b,f
    page.cmds.append(cmd)
    
def SetTextAlign(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 302
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)

def SetStretchBltMode(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 263
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)
    
palsize = {1:8,2:16,4:64,8:1024,16:0,24:0,32:0}
def StretchDIBits(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 3907
    er = emf.records[num]
    bd = er.bmpDepth
    bshift = palsize[bd]+54 
    cmd.args = er.topDest,er.leftDest,\
                     er.rightSrc-er.leftSrc,\
                     er.topSrc-er.bottomSrc,\
                     er.nSize-14,bshift,\
                     er.cxDest,\
                     er.cyDest,\
                     er.dwRop,er.data[22:]
    page.cmds.append(cmd)

def SetPolyfillMode(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 262
    if emf.records[num].iMode == 2:
        cmd.args =  0
    else:
        cmd.args =  1
    page.cmds.append(cmd)
    
def SetROP2(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 260
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)

def SetBKColor(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 513
    bkColor = emf.records[num].bkColor
    f =  (bkColor>>24)&0xFF
    b = (bkColor>>16)&0xFF
    g = (bkColor>>8)&0xFF
    r = bkColor&0xFF
    cmd.args = r,g,b,f
    page.cmds.append(cmd)

def SetMapMode(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 259
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
def SetBKMode(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 258
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
def SelectPalette(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 564
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)

def Header(emf,num,page):
    page.maxobj = emf.records[num].mtNoObjects
 
def Aldus_Header(emf,num,page):
    cmd = wmfdoc.cmd()
    cmd.type = 1
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)

mr_cmds  = {1:Aldus_Header,4:Header,
## FIXME! Commented out is 'not implemented yet'.
            30:SaveDC, 295:RestoreDC, ##332:ResetDc, 
            
            ##53:'RealizePalette', 55:'SetPalEntries',
            247:CreatePalette, ##313:'ResizePalette',1078:'AnimatePalette', 
            564:SelectPalette, 
            ##79:'StartPage', 80:'EndPage', 82:'AbortDoc', 94:'EndDoc', 333:'StartDoc', 
            
            ##248:CreateBrush,
            322:DibCreatePatternBrush, 505:CreatePatternBrush,
            762:CreatePenIndirect,763:CreateFontIndirect, 764:CreateBrushIndirect, ##765:CreateBitmapIndirect, 
            496:DeleteObject, 301:SelectObject, 
            
            258:SetBKMode, 259:SetMapMode, 260:SetROP2, 262:SetPolyfillMode, 263:SetStretchBltMode,##261:SetRelabs,
            ##561:SetMapperFlags, 
            ## 264:'SetTextCharExtra',
            302:SetTextAlign, 513:SetBKColor, 521:SetTextColor, ##522:SetTextJustification, 
            
            ##298:'InvertRegion', 299:'PaintRegion', 300:'SelectClipRegion',544:'OffsetClipRgn', 552:'FillRegion', 1065:'FrameRegion', 1791:'CreateRegion',
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
                
def parse(page):
    counter = 0
    wmf = page.file
    for i in range(len(wmf.records)):
        id = wmf.records[i].mr_id
        if mr_ids.has_key(id):
            if mr_cmds.has_key(id):
                print i,mr_ids[id]
                mr_cmds[id](wmf,i,page)
            else:
                cmd = wmfdoc.cmd()
                cmd.type = id
                page.cmds.append(cmd)
                counter+=1
                print i,'UNSUPPORTED COMMAND!', mr_ids[id]
        else:
            print 'Unknown key: ',id
    print 'Unknown commands: ',counter

        
