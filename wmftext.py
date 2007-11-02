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
import pango
import struct
import math
import cairo

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

def TextOut(ctx,page,i):
    ExtTextOut(ctx,page,i)
    
txtalign = {0:0, 1:0, 6:1, 2:2,		8:0,9:0,14:1,10:2,		24:0,25:0,30:1,26:2}
cpupdate = {1:1,9:1,25:1}
    
def ExtTextOut(ctx,page,i):

    x,y,text,dx = page.cmds[i].args
    print 'ExtText:',text
    lentext = len(text)
    textstr = text
    alignh = txtalign[page.txtalign]
    eonum = page.curfnt
    eo = page.mfobjs[eonum]
    size = eo.size
    bld = ''
    itl = ''
    if eo.weight > 400:
        bld = 'Bold '
    if eo.italic !=0:
        itl = 'Italic '
    FONT = eo.font+' '+bld+itl+str(size/1.5)
    fdesc = pango.FontDescription(FONT)
    if eo.font == 'Symbol':
        textstr=unicode(symbol_to_utf(text),'utf-16')
    if eo.charset > 77 and charsets.has_key(eo.charset):
        # have to reencode and have no idea about Mac encoding
        print 'Reencoding from charset %s'%charsets[eo.charset],'text: ',text
        textstr = unicode(text,charsets[eo.charset])
        textstr.encode('utf-8')

    if cpupdate.has_key(page.txtalign):
        x,y = ctx.get_current_point()
        ytr = y/1.5
    else:
        x,y = wmfdraw.convcoords(page,ctx,x,y)
        ytr = y - size*1./page.height
    print 'X,Y: ',x,y
    dxsum = 0
    if len(dx)>3: ## there is shifts
        print 'Shifts'
        dxoffs = 0
        dxlist = []
        if lentext/2. != lentext/2:
            dxoffs = 1
        for i in range(lentext-1):
            [d] = struct.unpack('h',dx[i*2+dxoffs:i*2+2+dxoffs])
            dxlist.append(d)
            dxsum=dxsum+d
        dxlist.append(0) ## to simplify my life later


    ctx.save()
    if page.width != 1 and page.height !=1:
        matrix = cairo.Matrix(1./page.width,0,0,1./page.height,0,0)##x,ytr)
        ctx.transform(matrix)
    layout = ctx.create_layout()
    layout.set_font_description(fdesc)

    layout.set_text(textstr)
    xsize,ysize = layout.get_size()
    xsize=xsize/1000./page.width
    ysize=ysize/1000./page.height
    if len(dx)>3: ## there is shifts
        t = text[lentext-1]
        layout.set_text(textstr)
        x0,y0 = layout.get_size()
        xsize=x0/1000.+dxsum
    
    if alignh == 0:
        xs = x
    if alignh == 1:
        xs = x-xsize/2.
    if alignh == 2:
        xs = x-xsize
    if page.txtalign<8: ##top
        ys = y + ysize
    if page.txtalign>7 and page.txtalign<24: ##bottom
        ys = y 
    if page.txtalign>23: ##baseline
        ys = y - ysize/1.25
    
    if cpupdate.has_key(page.txtalign):
        xe = xs+xsize
        ye = ys+ysize
    else:
        xe = xs+xsize*page.width
        ye = ys+ysize*page.height
    
    print 'Xs,Ys: ',xs,ys,'Xe,Ye: ',xe,ye

    if page.width != 1 and page.height !=1:
        ctx.translate(xs*page.width, ys*page.height)

    ctx.save()
    if eo.escape !=0:  ## change it with transform
        ctx.translate(xs,ys)
        ctx.rotate(-eo.escape*math.pi/1800) ## rotation angle is set in 10th of degree
        ctx.translate(-xs,-ys)
        
    if page.bkmode == 2:
        r = page.bkcolor.r
        g = page.bkcolor.g
        b = page.bkcolor.b
        ctx.save()
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
        ctx.move_to(xs,ys)
        ctx.line_to(xe,ys)
        ctx.line_to(xe,ye)
        ctx.line_to(xs,ye)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    ctx.set_source_rgba(page.txtclr.r/255.,page.txtclr.g/255.,page.txtclr.b/255.,1)
    if eo.under == 1:
        ctx.move_to(xs,ys+ysize*page.height/1.05)
        ctx.line_to(xe,ys+ysize*page.height/1.05)
        ctx.set_line_width(size*0.06)
        ctx.stroke()
    if eo.strike == 1:
        ctx.move_to(xs,ys+ysize*page.height/2.)
        ctx.line_to(xe,ys+ysize*page.height/2.)
        ctx.set_line_width(size*0.06)
        ctx.stroke()
    ctx.move_to(xs,ys)
    if dxsum>0 or (eo.orient!=0 and page.ai==0):
        ctx.save()
        for i in range(lentext):
            t = textstr[i]
            layout.set_text(t)
            x0,y0 = layout.get_size()
            ctx.save()
            if eo.orient!=0 and page.ai ==0:
                ctx.translate(xs+x0/2000.,ys+y0/2000.)
                ctx.rotate(-eo.orient*math.pi/1800.) ## rotation angle is set in 10th of degree
                ctx.translate(-xs-x0/2000.,-ys-y0/2000.)
                xup = x0*math.sin(eo.orient*math.pi/1800.)/1000.+y0*math.cos(eo.orient*math.pi/1800.)/1000.
            ctx.show_layout(layout)
            if dxsum >0:
                xs=xs+dxlist[i]*1.
            else:
                xs = xs+xup
            ctx.restore()
            ctx.move_to(xs,ys) 
        ctx.restore()
    else:
        layout.set_text(textstr)
        ctx.show_layout(layout)
    ctx.restore()
    
    ctx.restore()
##    print i,'ExtTextOut. x: %u y: %u'%(x,y),text,'Align:',xsize/1000,'Font: ',FONT,eo.weight,'Wx/Wy:',page.DCs[page.curdc].Wx,page.DCs[page.curdc].Wy
