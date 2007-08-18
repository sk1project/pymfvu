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

symbol2 = {
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

symbol = {
  0x00:'\x00\x00', 0x01:'\x00\x01', 0x02:'\x00\x02', 0x03:'\x00\x03',
  0x04:'\x00\x04', 0x05:'\x00\x05', 0x06:'\x00\x06', 0x07:'\x00\x07',
  0x08:'\x00\x08', 0x09:'\x00\x09', 0x0a:'\x00\x0a', 0x0b:'\x00\x0b',
  0x0c:'\x00\x0c', 0x0d:'\x00\x0d', 0x0e:'\x00\x0e', 0x0f:'\x00\x0f',
  0x10:'\x00\x10', 0x11:'\x00\x11', 0x12:'\x00\x12', 0x13:'\x00\x13',
  0x14:'\x00\x14', 0x15:'\x00\x15', 0x16:'\x00\x16', 0x17:'\x00\x17',
  0x18:'\x00\x18', 0x19:'\x00\x19', 0x1a:'\x00\x1a', 0x1b:'\x00\x1b',
  0x1c:'\x00\x1c', 0x1d:'\x00\x1d', 0x1e:'\x00\x1e', 0x1f:'\x00\x1f',
  0x20:'\x00\x20', 0x21:'\x00\x21', 0x22:'\x22\x00', 0x23:'\x00\x23',
  0x24:'\x22\x03', 0x25:'\x00\x25', 0x26:'\x00\x26', 0x27:'\x22\x0d',
  0x28:'\x00\x28', 0x29:'\x00\x29', 0x2a:'\x22\x17', 0x2b:'\x00\x2b',
  0x2c:'\x00\x2c', 0x2d:'\x22\x12', 0x2e:'\x00\x2e', 0x2f:'\x00\x2f',
  0x30:'\x00\x30', 0x31:'\x00\x31', 0x32:'\x00\x32', 0x33:'\x00\x33',
  0x34:'\x00\x34', 0x35:'\x00\x35', 0x36:'\x00\x36', 0x37:'\x00\x37',
  0x38:'\x00\x38', 0x39:'\x00\x39', 0x3a:'\x00\x3a', 0x3b:'\x00\x3b',
  0x3c:'\x00\x3c', 0x3d:'\x00\x3d', 0x3e:'\x00\x3e', 0x3f:'\x00\x3f',
  0x40:'\x22\x45', 0x41:'\x03\x91', 0x42:'\x03\x92', 0x43:'\x03\xa7',
  0x44:'\x03\x94', 0x45:'\x03\x95', 0x46:'\x03\xa6', 0x47:'\x03\x93',
  0x48:'\x03\x97', 0x49:'\x03\x99', 0x4a:'\x03\xd1', 0x4b:'\x03\x9a',
  0x4c:'\x03\x9b', 0x4d:'\x03\x9c', 0x4e:'\x03\x9d', 0x4f:'\x03\x9f',
  0x50:'\x03\xa0', 0x51:'\x03\x98', 0x52:'\x03\xa1', 0x53:'\x03\xa3',
  0x54:'\x03\xa4', 0x55:'\x03\xa5', 0x56:'\x03\xc2', 0x57:'\x03\xa9',
  0x58:'\x03\x9e', 0x59:'\x03\xa8', 0x5a:'\x03\x96', 0x5b:'\x00\x5b',
  0x5c:'\x22\x34', 0x5d:'\x00\x5d', 0x5e:'\x22\xa5', 0x5f:'\x00\x5f',
  0x60:'\xf8\xe5', 0x61:'\x03\xb1', 0x62:'\x03\xb2', 0x63:'\x03\xc7',
  0x64:'\x03\xb4', 0x65:'\x03\xb5', 0x66:'\x03\xc6', 0x67:'\x03\xb3',
  0x68:'\x03\xb7', 0x69:'\x03\xb9', 0x6a:'\x03\xd5', 0x6b:'\x03\xba',
  0x6c:'\x03\xbb', 0x6d:'\x03\xbc', 0x6e:'\x03\xbd', 0x6f:'\x03\xbf',
  0x70:'\x03\xc0', 0x71:'\x03\xb8', 0x72:'\x03\xc1', 0x73:'\x03\xc3',
  0x74:'\x03\xc4', 0x75:'\x03\xc5', 0x76:'\x03\xd6', 0x77:'\x03\xc9',
  0x78:'\x03\xbe', 0x79:'\x03\xc8', 0x7a:'\x03\xb6', 0x7b:'\x00\x7b',
  0x7c:'\x00\x7c', 0x7d:'\x00\x7d', 0x7e:'\x22\x3c', 0x7f:'\x00\x7f',
  0x80:'\x00\x80', 0x81:'\x00\x81', 0x82:'\x00\x82', 0x83:'\x00\x83',
  0x84:'\x00\x84', 0x85:'\x00\x85', 0x86:'\x00\x86', 0x87:'\x00\x87',
  0x88:'\x00\x88', 0x89:'\x00\x89', 0x8a:'\x00\x8a', 0x8b:'\x00\x8b',
  0x8c:'\x00\x8c', 0x8d:'\x00\x8d', 0x8e:'\x00\x8e', 0x8f:'\x00\x8f',
  0x90:'\x00\x90', 0x91:'\x00\x91', 0x92:'\x00\x92', 0x93:'\x00\x93',
  0x94:'\x00\x94', 0x95:'\x00\x95', 0x96:'\x00\x96', 0x97:'\x00\x97',
  0x98:'\x00\x98', 0x99:'\x00\x99', 0x9a:'\x00\x9a', 0x9b:'\x00\x9b',
  0x9c:'\x00\x9c', 0x9d:'\x00\x9d', 0x9e:'\x00\x9e', 0x9f:'\x00\x9f',
  0xa0:'\x00\x00', 0xa1:'\x03\xd2', 0xa2:'\x20\x32', 0xa3:'\x22\x64',
  0xa4:'\x20\x44', 0xa5:'\x22\x1e', 0xa6:'\x01\x92', 0xa7:'\x26\x63',
  0xa8:'\x26\x66', 0xa9:'\x26\x65', 0xaa:'\x26\x60', 0xab:'\x21\x94',
  0xac:'\x21\x90', 0xad:'\x21\x91', 0xae:'\x21\x92', 0xaf:'\x21\x93',
  0xb0:'\x00\xb0', 0xa1:'\x00\xb1', 0xb2:'\x20\x33', 0xb3:'\x22\x65',
  0xb4:'\x00\xd7', 0xb5:'\x22\x1d', 0xb6:'\x22\x02', 0xb7:'\x20\x22',
  0xb8:'\x00\xf7', 0xb9:'\x22\x60', 0xba:'\x22\x61', 0xbb:'\x22\x48',
  0xbc:'\x20\x26', 0xbd:'\xf8\xe6', 0xbe:'\xf8\xe7', 0xbf:'\x21\xb5',
  0xc0:'\x21\x35', 0xc1:'\x21\x11', 0xc2:'\x21\x1c', 0xc3:'\x21\x18',
  0xc4:'\x22\x97', 0xc5:'\x22\x95', 0xc6:'\x22\x05', 0xc7:'\x22\x29',
  0xc8:'\x22\x2a', 0xc9:'\x22\x83', 0xca:'\x22\x87', 0xcb:'\x22\x84',
  0xcc:'\x22\x82', 0xcd:'\x22\x86', 0xce:'\x22\x08', 0xcf:'\x22\x09',
  0xd0:'\x22\x20', 0xd1:'\x22\x07', 0xd2:'\x00\xae', 0xd3:'\x00\xa9',
  0xd4:'\x21\x22', 0xd5:'\x22\x0f', 0xd6:'\x22\x1a', 0xd7:'\x22\xc5',
  0xd8:'\x00\xac', 0xd9:'\x22\x27', 0xda:'\x22\x28', 0xdb:'\x21\xd4',
  0xdc:'\x21\xd0', 0xdd:'\x21\xd1', 0xde:'\x21\xd2', 0xdf:'\x21\xd3',
  0xe0:'\x22\xc4', 0xe1:'\x23\x29', 0xe2:'\xf8\xe8', 0xe3:'\xf8\xe9',
  0xe4:'\xf8\xea', 0xe5:'\x22\x11', 0xe6:'\xf8\xeb', 0xe7:'\xf8\xec',
  0xe8:'\xf8\xed', 0xe9:'\xf8\xee', 0xea:'\xf8\xef', 0xeb:'\xf8\xf0',
  0xec:'\xf8\xf1', 0xed:'\xf8\xf2', 0xee:'\xf8\xf3', 0xef:'\xf8\xf4',
  0xf0:'\xf8\xff', 0xf1:'\x23\x2a', 0xf2:'\x22\x2b', 0xf3:'\x23\x20',
  0xf4:'\xf8\xf5', 0xf5:'\x23\x21', 0xf6:'\xf8\xf6', 0xf7:'\xf8\xf7',
  0xf8:'\xf8\xf8', 0xf9:'\xf8\xf9', 0xfa:'\xf8\xfa', 0xfb:'\xf8\xfb',
  0xfc:'\xf8\xfc', 0xfd:'\xf8\xfd', 0xfe:'\xf8\xfe', 0xff:'\x02\xc7'}

def symbol_to_utf(text):
    str = ''
    for i in range(len(text)):
        str+=symbol2[ord(text[i])]
    return str

def TextOut(ctx,page,i):
    ExtTextOut(ctx,page,i)

txtalign = {0:0, 1:0, 6:1, 2:2,		8:0,9:0,14:1,10:2,		24:0,25:0,30:1,26:2}
cpupdate = {1:1,9:1,25:1}
    
def ExtTextOut(ctx,page,i):
    x,y,text,dx = page.cmds[i].args
    lentext = len(text)
    if cpupdate.has_key(page.txtalign):
        x,y = ctx.get_current_point()
    else:
        x = wmfdraw.convx(page,x)
        y = wmfdraw.convy(page,y)
        
    alignh = txtalign[page.txtalign]
    eonum = page.curfnt
    eo = page.wmfobjs[eonum]
    size = eo.size
    bld = ''
    itl = ''
    if eo.weight > 400:
        bld = 'Bold '
    if eo.italic !=0:
        itl = 'Italic '
    FONT = eo.font+' '+bld+itl+str(size/1.5)
    fdesc = pango.FontDescription(FONT)

    layout = ctx.create_layout()
    layout.set_font_description(fdesc)
    cw = 0
    if eo.font == 'Symbol':
        print 'Symbol! ------ SOME GLYPHS CAN BE MISSED! --------------------------------------------------'
    
    layout.set_text(text)
    xsize,ysize = layout.get_size()
    print 'Xsize,Ysize:',xsize,ysize
    dxsum = 0
    xsize/=1000.
    if len(dx)>3: ## there is shifts
        dxsum=0
        dxoffs = 0
        dxlist = []
        if lentext/2. != lentext/2:
            dxoffs = 1
        for i in range(lentext-1):
            [d] = struct.unpack('h',dx[i*2+dxoffs:i*2+2+dxoffs])
            dxlist.append(d)
            dxsum+=d
        dxlist.append(0) ## to simplify my life later
        t = text[lentext-1]
        layout.set_text(t)
        x0,y0 = layout.get_size()
        xsize=x0/1000.+dxsum
        
    if alignh == 0:
        xs = x
    if alignh == 1:
        xs = x-xsize/2.
    if alignh == 2:
        xs = x-xsize
    if page.txtalign<8: ##top
        ys = y + ysize/1000.
    if page.txtalign>7 and page.txtalign<24: ##bottom
        ys = y 
    if page.txtalign>23: ##baseline
        ys = y - ysize/1250.
 
    ctx.save()
    ctx.translate(xs,ys)
    if eo.escape !=0:
        ctx.rotate(-eo.escape*math.pi/1800) ## rotation angle is set in 10th of degree
    ctx.translate(-xs,-ys)
    if page.bkmode == 2:
        r = page.bkcolor.r
        g = page.bkcolor.g
        b = page.bkcolor.b
        ctx.save()
        ctx.set_source_rgba(r/255.,g/255.,b/255.,1)
        ctx.move_to(xs,ys)
        ctx.line_to(xs+xsize,ys)
        ctx.line_to(xs+xsize,ys+ysize/1000.)
        ctx.line_to(xs,ys+ysize/1000.)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    ctx.set_source_rgba(page.txtclr.r/255.,page.txtclr.g/255.,page.txtclr.b/255.,1)
    if eo.under == 1:
        ctx.move_to(xs,ys+ysize/1050.)
        ctx.line_to(xs+xsize,ys+ysize/1050.)
        ctx.set_line_width(size*0.06)
        ctx.stroke()
    if eo.strike == 1:
        ctx.move_to(xs,ys+ysize/2000.)
        ctx.line_to(xs+xsize,ys+ysize/2000.)
        ctx.set_line_width(size*0.06)
        ctx.stroke()
    ctx.move_to(xs,ys)
    if dxsum>0 or eo.orient!=0:
        ctx.save()
        for i in range(lentext):
            t = text[i]
            layout.set_text(t)
            x0,y0 = layout.get_size()
            ctx.save()
            if eo.orient!=0:
                ctx.translate(xs+x0/2000.,ys+y0/2000.)
                ctx.rotate(-eo.orient*math.pi/1800) ## rotation angle is set in 10th of degree
                ctx.translate(-xs-x0/2000.,-ys-y0/2000.)
                xup = x0*math.sin(eo.orient*math.pi/1800)/1000+y0*math.cos(eo.orient*math.pi/1800)/1000
            ctx.show_layout(layout)
            if dxsum >0:
                xs=xs+dxlist[i]*1.
            else:
                xs = xs+xup
            ctx.restore()
            ctx.move_to(xs,ys)                
        ctx.restore()
    else:
        layout.set_text(text)
        ctx.show_layout(layout)
    ctx.restore()
##    print i,'ExtTextOut. x: %u y: %u Text: %s'%(x,y,text),'Align:',xsize/1000,'Font: ',FONT,eo.weight,'dX: ',len(dx)
