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

import pyemf
import emfdoc

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

def Polybezier(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 2
##    x,y = emf.records[num].values[0],emf.records[num].values[3]
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)

def Polygone(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 3
    x,y = emf.records[num].values[0],emf.records[num].values[3]
    cmd.args = (x,y),emf.records[num].aptl
    page.cmds.append(cmd)

def Polyline(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 4
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)

def PolybezierTo(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 5
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)

def PolylineTo(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 6
    cmd.args = emf.records[num].aptl
    page.cmds.append(cmd)

def PolyPolyline(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 7
    x,y = emf.records[num].values[0],emf.records[num].values[3]
    cmd.args = emf.records[num].aPolyCounts,emf.records[num].aptl,(x,y)
    page.cmds.append(cmd)
    
def PolyPolygone(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 8
    x,y = emf.records[num].values[0],emf.records[num].values[3]
    cmd.args = emf.records[num].aPolyCounts,emf.records[num].aptl,(x,y)
    page.cmds.append(cmd)
    
def MoveTo(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 27
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def LineTo(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 54
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def ArcTo(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 55
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Ellipse(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 42
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Rectangle(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 43
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def RoundRect(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 44
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def Arc(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 45
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)
    
def Chord(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 46
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)
    
def Pie(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 47
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetWindowExtEx(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 9
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetWindowOrgEx(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 10
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetViewportExtEx(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 11
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetViewportOrgEx(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 12
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)
    
def SaveDC(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 33 #I do 'CloseFigure' here (that is not quite correct
    page.cmds.append(cmd)

def RestoreDC(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 34 #I do 'CloseFigure' here (that is not quite correct
    page.cmds.append(cmd)
    
def SetWorldTransform(emf,num,page): ##35
    cmd = emfdoc.cmd()
    cmd.type = 35
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def ModifyWorldTransform(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 36
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SelectObject(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 37
    cmd.args = emf.records[num].handle
    page.cmds.append(cmd)

def CreatePen(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 38
    handle = emf.records[num].handle
    lbColor = emf.records[num].lopn_color
    width = emf.records[num].lopn_width
    b = lbColor>>16
    g = (lbColor&0xFF00)>>8
    r = lbColor&0xFF
    cmd.args = handle,r,g,b,width
    page.cmds.append(cmd)
    
def CreateBrushIndirect(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 39
    handle = emf.records[num].handle
    lbColor = emf.records[num].lbColor
    b = lbColor>>16
    g = (lbColor&0xFF00)>>8
    r = lbColor&0xFF
    cmd.args = handle,r,g,b
    page.cmds.append(cmd)
    
def DeleteObject(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 40
    cmd.args = emf.records[num].handle
    page.cmds.append(cmd)

def ExtCreatePen(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 95
    cmd.args = emf.records[num].handle,ord(emf.records[num].data[32]),ord(emf.records[num].data[33]),ord(emf.records[num].data[34])
    page.cmds.append(cmd)

def BeginPath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 59
    page.cmds.append(cmd)

def EndPath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 60 #I do 'CloseFigure' here (that is not quite correct
    page.cmds.append(cmd)

def CloseFigure(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 61
    page.cmds.append(cmd)
    
def FillPath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 62
    page.cmds.append(cmd)

def StrokeAndFillPath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 63
    page.cmds.append(cmd)

def StrokePath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 64
    page.cmds.append(cmd)
    
def SelectClipPath(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 67
    page.cmds.append(cmd)
    
def ExtTextOutW(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 84
    text = emf.records[num].string
    x = emf.records[num].values[0]
    y = emf.records[num].values[1]
    ye = emf.records[num].values[3]
    text = unicode(text,'utf-16').encode('utf-8')
    cmd.args = x,y,ye,text
    page.cmds.append(cmd)

def ExtCreateFontIndirectW(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 82
    cmd.args = emf.records[num].values
    page.cmds.append(cmd)

def SetTextColor(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 24
    crColor = emf.records[num].crColor
    b = crColor>>16
    g = (crColor&0xFF00)>>8
    r = crColor&0xFF
    cmd.args = r,g,b
    page.cmds.append(cmd)
    
def SetTextAlign(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 22
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)

def SetStretchBltMode(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 21
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)

def StretchDIBits(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 81
    cmd.args =   emf.records[num].xDest,emf.records[num].yDest,emf.records[num].cxSrc,emf.records[num].cySrc, emf.records[num].nSize-58,\
                        emf.records[num].cbBmiSrc+14,emf.records[num].cxDest,emf.records[num].cyDest,emf.records[num].dwRop,\
                        emf.records[num].data[72:]
    page.cmds.append(cmd)

def SetPolyfillMode(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 19
    if emf.records[num].iMode == 2:
        cmd.args =  0
    else:
        cmd.args =  1
    page.cmds.append(cmd)
    
def SetRop2(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 20
    cmd.args =  emf.records[num].iMode
    page.cmds.append(cmd)

##---------------
def SetBKColor(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 25
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)

def SetMapMode(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 17
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
def SetBKMode(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 18
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
def SetICMMode(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 98
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
def SelectPalette(emf,num,page):
    cmd = emfdoc.cmd()
    cmd.type = 48
    cmd.args =  emf.records[num].values
    page.cmds.append(cmd)
    
cmds = {2:Polybezier,85:Polybezier,\
            3:Polygone,86:Polygone,\
            4:Polyline,87:Polyline,\
            5:PolybezierTo,88:PolybezierTo,\
            6:PolylineTo,89:PolylineTo,\
            7:PolyPolyline,90:PolyPolyline,\
            8:PolyPolygone,91:PolyPolygone,\
            27:MoveTo,54:LineTo,55:ArcTo,42:Ellipse,43:Rectangle,44:RoundRect,45:Arc,46:Chord,47:Pie,\
            84:ExtTextOutW,82:ExtCreateFontIndirectW,22:SetTextAlign,24:SetTextColor,\
            9:SetWindowExtEx,10:SetWindowOrgEx,11:SetViewportExtEx,12:SetViewportOrgEx,\
            33:SaveDC,34:RestoreDC,35:SetWorldTransform,36:ModifyWorldTransform,\
            37:SelectObject,38:CreatePen,39:CreateBrushIndirect,40:DeleteObject,95:ExtCreatePen,\
            59:BeginPath,60:EndPath,61:CloseFigure,62:FillPath, 63:StrokeAndFillPath,64:StrokePath,67:SelectClipPath,\
            21:SetStretchBltMode,81:StretchDIBits,19:SetPolyfillMode,20:SetRop2,\
            25:SetBKColor,17:SetMapMode,18:SetBKMode,98:SetICMMode,48:SelectPalette}

def parse(page):
    emf = page.file
    page.width = emf.records[0].values[2] ##*emf.records[0].values[6]
    page.height = emf.records[0].values[3] ##*emf.records[0].values[7]
    page.scale = emf.records[0].values[18]*1./emf.records[0].values[20]
    counter = 0
    for i in range(len(emf.records)):
        id = emf.records[i].emr_id
        if emr_ids.has_key(id):
            if cmds.has_key(id):
                cmds[id](emf,i,page)
            else:
                cmd = emfdoc.cmd()
                cmd.type = id
                page.cmds.append(cmd)
                counter+=1
                print 'UNSUPPORTED COMMAND! ', emr_ids[id]
        else:
            print 'Unknown key: ',id

    print 'Unknown commands: ',counter
    return page

        
