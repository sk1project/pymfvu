#!/usr/bin/env python
# This program was made as part of the sk1project activity to improve UniConvertor
# See http://www.sk1project.org
#
# Copyright (C) 2007,	Valek Filippov (frob@df.ru)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 or later of the GNU Lesser General Public
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
# pywmf was made on the base of Rob McMullen (robm@users.sourceforge.net) pyemf module
# http://pyemf.sourceforge.net
# and I hope one day we will merge those modules.

import os,sys,re
import struct
from cStringIO import StringIO
import copy

__version__ = "0.0.1"
__author__ = "Valek Filippov (on the base of Rob McMullen pyemf code)"
__url__ = "http://www.sk1project.org"
__description__ = "Python Windows Metafile Library"
__keywords__ = "graphics, scalable, vector, image, clipart, emf"
__license__ = "LGPL v3"

# Brush styles
BS_SOLID	    = 0
BS_NULL		    = 1
BS_HOLLOW	    = 1
BS_HATCHED	    = 2
BS_PATTERN	    = 3
BS_INDEXED	    = 4
BS_DIBPATTERN	    = 5
BS_DIBPATTERNPT	    = 6
BS_PATTERN8X8	    = 7
BS_DIBPATTERN8X8    = 8
BS_MONOPATTERN      = 9

# Hatch styles
HS_HORIZONTAL       = 0
HS_VERTICAL         = 1
HS_FDIAGONAL        = 2
HS_BDIAGONAL        = 3
HS_CROSS            = 4
HS_DIAGCROSS        = 5

# mapping modes
MM_TEXT = 1
MM_LOMETRIC = 2
MM_HIMETRIC = 3
MM_LOENGLISH = 4
MM_HIENGLISH = 5
MM_TWIPS = 6
MM_ISOTROPIC = 7
MM_ANISOTROPIC = 8
MM_MAX = MM_ANISOTROPIC

# background modes
TRANSPARENT = 1
OPAQUE = 2
BKMODE_LAST = 2

# polyfill modes
ALTERNATE = 1
WINDING = 2
POLYFILL_LAST = 2

# line styles and options
PS_SOLID         = 0x00000000
PS_DASH          = 0x00000001
PS_DOT           = 0x00000002
PS_DASHDOT       = 0x00000003
PS_DASHDOTDOT    = 0x00000004
PS_NULL          = 0x00000005
PS_INSIDEFRAME   = 0x00000006
PS_USERSTYLE     = 0x00000007
PS_ALTERNATE     = 0x00000008
PS_STYLE_MASK    = 0x0000000f

PS_ENDCAP_ROUND  = 0x00000000
PS_ENDCAP_SQUARE = 0x00000100
PS_ENDCAP_FLAT   = 0x00000200
PS_ENDCAP_MASK   = 0x00000f00

PS_JOIN_ROUND    = 0x00000000
PS_JOIN_BEVEL    = 0x00001000
PS_JOIN_MITER    = 0x00002000
PS_JOIN_MASK     = 0x0000f000

PS_COSMETIC      = 0x00000000
PS_GEOMETRIC     = 0x00010000
PS_TYPE_MASK     = 0x000f0000
 
# Stock GDI objects for GetStockObject()
WHITE_BRUSH         = 0
LTGRAY_BRUSH        = 1
GRAY_BRUSH          = 2
DKGRAY_BRUSH        = 3
BLACK_BRUSH         = 4
NULL_BRUSH          = 5
HOLLOW_BRUSH        = 5
WHITE_PEN           = 6
BLACK_PEN           = 7
NULL_PEN            = 8
OEM_FIXED_FONT      = 10
ANSI_FIXED_FONT     = 11
ANSI_VAR_FONT       = 12
SYSTEM_FONT         = 13
DEVICE_DEFAULT_FONT = 14
DEFAULT_PALETTE     = 15
SYSTEM_FIXED_FONT   = 16
DEFAULT_GUI_FONT    = 17

STOCK_LAST          = 17

# Text alignment
TA_NOUPDATECP       = 0x00
TA_UPDATECP         = 0x01
TA_LEFT             = 0x00
TA_RIGHT            = 0x02
TA_CENTER           = 0x06
TA_TOP              = 0x00
TA_BOTTOM           = 0x08
TA_BASELINE         = 0x18
TA_RTLREADING       = 0x100
TA_MASK             = TA_BASELINE+TA_CENTER+TA_UPDATECP+TA_RTLREADING

# lfWeight values
FW_DONTCARE         = 0
FW_THIN             = 100
FW_EXTRALIGHT       = 200
FW_ULTRALIGHT       = 200
FW_LIGHT            = 300
FW_NORMAL           = 400
FW_REGULAR          = 400
FW_MEDIUM           = 500
FW_SEMIBOLD         = 600
FW_DEMIBOLD         = 600
FW_BOLD             = 700
FW_EXTRABOLD        = 800
FW_ULTRABOLD        = 800
FW_HEAVY            = 900
FW_BLACK            = 900

# lfCharSet values
ANSI_CHARSET          = 0   # CP1252, ansi-0, iso8859-{1,15}
DEFAULT_CHARSET       = 1
SYMBOL_CHARSET        = 2
SHIFTJIS_CHARSET      = 128 # CP932
HANGEUL_CHARSET       = 129 # CP949, ksc5601.1987-0
HANGUL_CHARSET        = HANGEUL_CHARSET
GB2312_CHARSET        = 134 # CP936, gb2312.1980-0
CHINESEBIG5_CHARSET   = 136 # CP950, big5.et-0
GREEK_CHARSET         = 161 # CP1253
TURKISH_CHARSET       = 162 # CP1254, -iso8859-9
HEBREW_CHARSET        = 177 # CP1255, -iso8859-8
ARABIC_CHARSET        = 178 # CP1256, -iso8859-6
BALTIC_CHARSET        = 186 # CP1257, -iso8859-13
RUSSIAN_CHARSET       = 204 # CP1251, -iso8859-5
EE_CHARSET            = 238 # CP1250, -iso8859-2
EASTEUROPE_CHARSET    = EE_CHARSET
THAI_CHARSET          = 222 # CP874, iso8859-11, tis620
JOHAB_CHARSET         = 130 # korean (johab) CP1361
MAC_CHARSET           = 77
OEM_CHARSET           = 255

VISCII_CHARSET        = 240 # viscii1.1-1
TCVN_CHARSET          = 241 # tcvn-0
KOI8_CHARSET          = 242 # koi8-{r,u,ru}
ISO3_CHARSET          = 243 # iso8859-3
ISO4_CHARSET          = 244 # iso8859-4
ISO10_CHARSET         = 245 # iso8859-10
CELTIC_CHARSET        = 246 # iso8859-14

FS_LATIN1              = 0x00000001L
FS_LATIN2              = 0x00000002L
FS_CYRILLIC            = 0x00000004L
FS_GREEK               = 0x00000008L
FS_TURKISH             = 0x00000010L
FS_HEBREW              = 0x00000020L
FS_ARABIC              = 0x00000040L
FS_BALTIC              = 0x00000080L
FS_VIETNAMESE          = 0x00000100L
FS_THAI                = 0x00010000L
FS_JISJAPAN            = 0x00020000L
FS_CHINESESIMP         = 0x00040000L
FS_WANSUNG             = 0x00080000L
FS_CHINESETRAD         = 0x00100000L
FS_JOHAB               = 0x00200000L
FS_SYMBOL              = 0x80000000L

# lfOutPrecision values
OUT_DEFAULT_PRECIS      = 0
OUT_STRING_PRECIS       = 1
OUT_CHARACTER_PRECIS    = 2
OUT_STROKE_PRECIS       = 3
OUT_TT_PRECIS           = 4
OUT_DEVICE_PRECIS       = 5
OUT_RASTER_PRECIS       = 6
OUT_TT_ONLY_PRECIS      = 7
OUT_OUTLINE_PRECIS      = 8

# lfClipPrecision values
CLIP_DEFAULT_PRECIS     = 0x00
CLIP_CHARACTER_PRECIS   = 0x01
CLIP_STROKE_PRECIS      = 0x02
CLIP_MASK               = 0x0F
CLIP_LH_ANGLES          = 0x10
CLIP_TT_ALWAYS          = 0x20
CLIP_EMBEDDED           = 0x80

# lfQuality values
DEFAULT_QUALITY        = 0
DRAFT_QUALITY          = 1
PROOF_QUALITY          = 2
NONANTIALIASED_QUALITY = 3
ANTIALIASED_QUALITY    = 4

# lfPitchAndFamily pitch values
DEFAULT_PITCH       = 0x00
FIXED_PITCH         = 0x01
VARIABLE_PITCH      = 0x02
MONO_FONT           = 0x08

FF_DONTCARE         = 0x00
FF_ROMAN            = 0x10
FF_SWISS            = 0x20
FF_MODERN           = 0x30
FF_SCRIPT           = 0x40
FF_DECORATIVE       = 0x50

# Graphics Modes
GM_COMPATIBLE     = 1
GM_ADVANCED       = 2
GM_LAST           = 2

# Arc direction modes
AD_COUNTERCLOCKWISE = 1
AD_CLOCKWISE        = 2

# Clipping paths
RGN_ERROR         = 0
RGN_AND           = 1
RGN_OR            = 2
RGN_XOR           = 3
RGN_DIFF          = 4
RGN_COPY          = 5
RGN_MIN           = RGN_AND
RGN_MAX           = RGN_COPY

# Color management
ICM_OFF   = 1
ICM_ON    = 2
ICM_QUERY = 3
ICM_MIN   = 1
ICM_MAX   = 3

# World coordinate system transformation
MWT_IDENTITY      = 1
MWT_LEFTMULTIPLY  = 2
MWT_RIGHTMULTIPLY = 3

#Used for ExtTextOut
ETO_OPAQUE = 2
ETO_CLIPPED = 4
ETO_GLYPH_INDEX = 16
ETO_RTLREADING = 128


class _MR_FORMAT:
    def __init__(self,mr_id,typedef):
        self.typedef=typedef
        self.id=mr_id
        self.fmtlist=[] # list of typecodes
        self.defaults=[] # list of default values
        self.fmt="<" # string for pack/unpack.  little endian
        self.structsize=0

        self.names=[]
        self.namepos={}
        
        self.debug=0

        self.setFormat(typedef)

    def setFormat(self,typedef,default=None):
        if self.debug: print "typedef=%s" % str(typedef)
        if isinstance(typedef,list) or isinstance(typedef,tuple):
            for item in typedef:
                if len(item)==3:
                    typecode,name,default=item
                else:
                    typecode,name=item
                self.appendFormat(typecode,name,default)
        elif typedef:
            raise AttributeError("format must be a list")
        self.structsize=struct.calcsize(self.fmt)
        if self.debug: print "current struct=%s size=%d\n  names=%s" % (self.fmt,self.structsize,self.names)

    def appendFormat(self,typecode,name,default):
        self.fmt+=typecode
        self.fmtlist.append(typecode)
        self.defaults.append(default)
        self.namepos[name]=len(self.names)
        self.names.append(name)



class _MR_UNKNOWN(object):
    """baseclass for WMF objects"""
    
    mr_id=0
    mr_typedef=()
    format=None
    twobytepadding='\0'*2
    
    def __init__(self):
        self.rdFunction = self.__class__.mr_id
        self.nSize=0

        self.verbose=0
        
        self.datasize=0
        self.data=None
        self.unhandleddata=None

        # number of padding zeros we had to add because the format was
        # expecting more data
        self.zerofill=0

        # if we've never seen this class before, create a new format.
        # Note that subclasses of classes that we have already seen
        # pick up any undefined class attributes from their
        # superclasses, so we have to check if this is a subclass with
        # a different typedef
        if self.__class__.format==None or self.__class__.mr_typedef != self.format.typedef:
            if self.verbose: print "creating format for %d" % self.__class__.mr_id
            self.__class__.format=_MR_FORMAT(self.__class__.mr_id,self.__class__.mr_typedef)

        # list of values parsed from the input stream
        self.values=copy.copy(self.__class__.format.defaults)

        # error code.  Currently just used as a boolean
        self.error=0


    def __getattr__(self,name):
        """Return EMR attribute if the name exists in the typedef list
        of the object.  This is only called when the standard
        attribute lookup fails on this object, so we don't have to
        handle the case where name is an actual attribute of self."""
        f=_MR_UNKNOWN.__getattribute__(self,'format')
        try:
            if name in f.names:
                v=_MR_UNKNOWN.__getattribute__(self,'values')
                index=f.namepos[name]
                return v[index]
        except IndexError:
            raise IndexError("name=%s index=%d values=%s" % (name,index,str(v)))
        raise AttributeError("%s not defined in MR object" % name)

    def __setattr__(self,name,value):
        """Set a value in the object, propagating through to
        self.values[] if the name is in the typedef list."""
        f=_MR_UNKNOWN.__getattribute__(self,'format')
        try:
            if f and name in f.names:
                v=_MR_UNKNOWN.__getattribute__(self,'values')
                index=f.namepos[name]
                v[index]=value
            else:
                # it's not an automatically serializable item, so store it.
                self.__dict__[name]=value
        except IndexError:
            raise IndexError("name=%s index=%d values=%s" % (name,index,str(v)))

    def hasHandle(self):
        """Return true if this object has a handle that needs to be
        saved in the object array for later recall by SelectObject."""
        return False

    def setBounds(self,bounds):
        """Set bounds of object.  Depends on naming convention always
        defining the bounding rectangle as
        rclBounds_[left|top|right|bottom]."""
        self.rclBounds_left=bounds[0]
        self.rclBounds_top=bounds[1]
        self.rclBounds_right=bounds[2]
        self.rclBounds_bottom=bounds[3]

    def getBounds(self):
        """Return bounds of object, or None if not applicable."""
        return None

    def unserialize(self,fh,rdFunction=-1,nSize=-1):
        """Read data from the file object and, using the format
        structure defined by the subclass, parse the data and store it
        in self.values[] list."""
        if rdFunction >0:
            self.rdFunction=rdFunction
            self.nSize=nSize
        else:
            print 'frob: something wrong?',rdFunction
            fh.seek(0,2)
        if self.nSize>6:
            self.datasize=self.nSize-6
            self.data=fh.read(self.datasize)
            if self.format.structsize>0:
                if self.format.structsize>len(self.data):
                    # we have a problem.  More stuff to unparse than
                    # we have data.  Hmmm.  Fill with binary zeros
                    # till I think of a better idea.
                    self.zerofill=self.format.structsize-len(self.data)
                    self.data+="\0"*self.zerofill
                self.values=list(struct.unpack(self.format.fmt,self.data[0:self.format.structsize]))
            if self.datasize>self.format.structsize:
                self.unserializeExtra(self.data[self.format.structsize:])

    def unserializeOffset(self,offset):
        """Adjust offset to point to correct location in extra data.
        Offsets in the MR record are from the start of the record, so
        we must subtract 6 bytes for rdFunction and nSize, and also
        subtract the size of the format structure."""
        return offset-6-self.format.structsize-self.zerofill

    def unserializeExtra(self,data):
        """Hook for subclasses to handle extra data in the record that
        isn't specified by the format statement."""
        self.unhandleddata=data
        pass

    def unserializeList(self,fmt,count,data,start):
        fmt="<%d%s" % (count,fmt)
        size=struct.calcsize(fmt)
        vals=list(struct.unpack(fmt,data[start:start+size]))
        #print "vals fmt=%s size=%d: %s" % (fmt,len(vals),str(vals))
        start+=size
        return (start,vals)

    def unserializePoints(self,fmt,count,data,start):
        fmt="<%d%s" % ((2*count),fmt)
        size=struct.calcsize(fmt)
        vals=struct.unpack(fmt,data[start:start+size])
        pairs=[(vals[i],vals[i+1]) for i in range(0,len(vals),2)]
        #print "points size=%d: %s" % (len(pairs),pairs)
        start+=size
        return (start,pairs)
            
    def serialize(self,fh):
        fh.write(struct.pack("<ih",self.nSize,self.rdFunction))
        try:
            fh.write(struct.pack(self.format.fmt,*self.values))
        except struct.error:
            print "!!!!!Struct error:",
            print self
            raise
        self.serializeExtra(fh)

    def serializeOffset(self):
        """Return the initial offset for any extra data that must be
        written to the record.  See L{unserializeOffset}."""
        return 6+self.format.structsize

    def serializeExtra(self,fh):
        """This is for special cases, like writing text or lists.  If
        this is not overridden by a subclass method, it will write out
        anything in the self.unhandleddata string."""
        if self.unhandleddata:
            fh.write(self.unhandleddata)
            

    def serializeList(self,fh,fmt,vals):
        fmt="<%s" % fmt
        for val in vals:
            fh.write(struct.pack(fmt,val))

    def serializePoints(self,fh,fmt,pairs):
        fmt="<2%s" % fmt
        for pair in pairs:
            fh.write(struct.pack(fmt,pair[0],pair[1]))

    def serializeString(self,fh,txt):
        if isinstance(txt,unicode):
            txt=txt.encode('utf-16le')
        fh.write(txt)
        extra=_round4(len(txt))-len(txt)
        if extra>0:
            fh.write('\0'*extra)

    def resize(self):
        before=self.nSize
        self.nSize=6+self.format.structsize+self.sizeExtra()
        if self.verbose and before!=self.nSize:
            print "resize: before=%d after=%d" % (before,self.nSize),
            print self
        if self.nSize%4 != 0:
            print "size error.  Must be divisible by 4"
            print self
            raise TypeError

    def sizeExtra(self):
        """Hook for subclasses before anything is serialized.  This is
        used to return the size of any extra components not in the
        format string, and also provide the opportunity to recalculate
        any changes in size that should be reflected in self.nSize
        before the record is written out."""
        if self.unhandleddata:
            return len(self.unhandleddata)
        return 0

    def str_extra(self):
        """Hook to print out extra data that isn't in the format"""
        return ""

    def str_color(self,val):
        return "red=0x%02x green=0x%02x blue=0x%02x" % ((val&0xff),((val&0xff00)>>8),((val&0xff0000)>>16))

    def str_decode(self,typecode,name):
        val=_MR_UNKNOWN.__getattr__(self,name)
        if name.endswith("olor"):
            val=self.str_color(val)
        elif typecode.endswith("s"):
            val=val.decode('utf-16le')
        return val
    
    def str_details(self):
        txt=StringIO()

        # _MR_UNKNOWN objects don't have a typedef, so only process
        # those that do
        if self.format.typedef:
            #print "typedef=%s" % str(self.format.typedef)
            for item in self.format.typedef:
                typecode=item[0]
                name=item[1]
                val=self.str_decode(typecode,name)
                try:
                    txt.write("\t%-20s: %s\n" % (name,val))
                except UnicodeEncodeError:
                    txt.write("\t%-20s: <<<BAD UNICODE STRING>>>\n" % name)
        txt.write(self.str_extra())
        return txt.getvalue()

    def __str__(self):
        ret=""
        details=self.str_details()
        if details:
            ret=os.linesep
        return "**%s: rdFunction=%s nSize=%s  struct='%s' size=%d\n%s%s" % (self.__class__.__name__.lstrip('_'),self.rdFunction,self.nSize,self.format.fmt,self.format.structsize,details,ret)
        return 


# Collection of classes
class _MR:
    class _AP_HEADER(_MR_UNKNOWN): #header for aldus placeable metafile
        mr_id = 1 # False ID !!!
        mr_typedef=[('i','Key', 0x9AC6CDD7), # signature
                            ('h','Handle',0),               # always 0
                            ('h','rclLeft'),
                            ('h','rclTop'),
                            ('h','rclRight'),
                            ('h','rclBotttom'),
                            ('h','Inch'),                       #num of metafile units per inch
                            ('i','Reserved'),                #always 0
                            ('h','Checksum')]
                            
    class _CLIP_HEADER16(_MR_UNKNOWN): # header for 16bits CLP file
        mr_id = 2 # False ID !!!
        mr_typedef=[('h','MappingMode'),
                            ('h','Width'),
                            ('h','Height'),
                            ('h','Handle')]

    class _CLIP_HEADER32(_MR_UNKNOWN): # header for 32bits CLP file  MappingMode = [1:8], if MM>8 => it's 16bits header (not quite good detection method)
        mr_id = 3 # False ID !!!
        mr_typedef=[('i','MappingMode'),
                            ('i','Width'),
                            ('i','Height'),
                            ('i','Handle')]
                            
    class _HEADER(_MR_UNKNOWN):
        mr_id = 4 # False ID !!!
        mr_typedef=[('h','mtType'),
        ('h','mtHeaderSize'),
        ('h','mtVersion'),
        ('i','mtSize'),
        ('h','mtNoObjects'),
        ('i','mtMaxRecord'),
        ('h','mtNoParameters')]
        def __init__(self,description=''):
            _MR_UNKNOWN.__init__(self)


    class _SAVEDC(_MR_UNKNOWN):
        mr_id = 0x001E
        pass

    class _REALIZEPALETTE(_MR_UNKNOWN):
        mr_id = 0x0035
        pass

    class _SETPALENTRIES(_MR_UNKNOWN):
        mr_id = 0x0037
        pass

    class _STARTPAGE(_MR_UNKNOWN):
        mr_id = 0x004F
        pass

    class _ENDPAGE(_MR_UNKNOWN):
        mr_id = 0x0050
        pass

    class _ABORTDOC(_MR_UNKNOWN):
        mr_id = 0x0052
        pass

    class _ENDDOC(_MR_UNKNOWN):
        mr_id = 0x005E
        pass

    class _CREATEPALETTE(_MR_UNKNOWN):
        mr_id = 0x00F7
        mr_typedef=[('h','Version',3),
                            ('h','lpltNumofclr')]
        def __init__(self):
            _MR_UNKNOWN.__init__(self)
            
    class _CREATEBRUSH(_MR_UNKNOWN):
        mr_id = 0x00F8
        mr_typedef=[
                ('h','lbStyle'),
                ('i','lbColor'),
                ('h','lbHatch')]
        def __init__(self,style=BS_SOLID,hatch=HS_HORIZONTAL,color=0):
            _MR_UNKNOWN.__init__(self)
            self.lbStyle = style
            self.lbColor = color
            self.lbHatch = hatch

    class _SETMAPMODE(_MR_UNKNOWN):
        mr_id = 0x0103
        mr_typedef=[('h','iMode',MM_ANISOTROPIC)]
        def __init__(self,mode=MM_ANISOTROPIC,first=0,last=MM_MAX):
            _MR_UNKNOWN.__init__(self)
            if mode<first or mode>last:
                self.error=1
            else:
                self.iMode=mode

    class _SETBKMODE(_SETMAPMODE):
        mr_id = 0x0102
        def __init__(self,mode=OPAQUE):
            _MR._SETMAPMODE.__init__(self,mode,last=BKMODE_LAST)

    class _SETROP2(_SETMAPMODE):
        mr_id = 0x0104
        pass

    class _SETRELABS(_MR_UNKNOWN):
        mr_id = 0x0105
        pass

    class _SETPOLYFILLMODE(_SETMAPMODE):
        mr_id = 0x0106
        def __init__(self,mode=ALTERNATE):
            _MR._SETMAPMODE.__init__(self,mode,last=POLYFILL_LAST)

    class _SETSTRETCHBLTMODE(_SETMAPMODE):
        mr_id = 0x0107
        def __init__(self,mode=ALTERNATE):
            _MR._SETMAPMODE.__init__(self,mode,last=1)
        pass

    class _SETTEXTCHAREXTRA(_MR_UNKNOWN):
        mr_id = 0x0108
        mr_typedef=[('h','extra')]
        pass

    class _RESTOREDC(_MR_UNKNOWN):
        mr_id = 0x0127
        mr_typedef=[('h','level')]
        def __init__(self,level=-1):
            _MR_UNKNOWN.__init__(self)
            self.level=level

    class _INVERTREGION(_MR_UNKNOWN):
        mr_id = 0x012A
        pass
        
    class _PAINTREGION(_MR_UNKNOWN):
        mr_id = 0x012B
        pass

    class _SELECTCLIPREGION(_MR_UNKNOWN):
        mr_id = 0x012C
        mr_typedef=[('h','rclBox_bottom'),('h','rclBox_right'),
                            ('h','rclBox_top'),('h','rclBox_left')
                            ]

        pass

    class _SELECTOBJECT(_MR_UNKNOWN):
        mr_id = 0x012D
        mr_typedef=[('I','handle')]
        def __init__(self,dc=None,handle=0):
            _MR_UNKNOWN.__init__(self)
            self.handle=handle

    class _SETTEXTALIGN(_SETMAPMODE):
        mr_id = 0x012E
        def __init__(self,mode=TA_BASELINE):
            _MR._SETMAPMODE.__init__(self,mode,last=TA_MASK)
        
    class _RESIZEPALETTE(_MR_UNKNOWN):
        mr_id = 0x0139
        pass
        
    class _DIBCREATEPATTERNBRUSH(_MR_UNKNOWN):
        mr_id = 0x0142
        mr_typedef=[
                    ('i','Version'),            ## Is it version?
                    ## looks like a DIB values in StretchDIBits class
                    ('i','biSize'),             ## bitmapinfoheader size
                    ('i','biWidth'),           ## pixel W
                    ('i','biHeight'),         ## pixel H
                    ('h','biPlanes'),            ## num of planes, always 1
                    ('h','biDepth'),              ## num of bits per pixel
                    ('i','biCompression'),   ## compression scheme
                    ('i','biImageSize'),    ## size of pix array
                    ('i','biXres'),             ## horizontal resolution
                    ('i','biYres'),             ## vertical resolution
                    ('i','buClrUsed'),        ## num of used colors
                    ('i','biClrImportant')]## num of important colors
                    ## color table starts here, 4 bytes per color (never used for 16-, 24- and 32- bpp depth images)
                    ## raster data starts after color table
        pass

    class _RESETDC(_MR_UNKNOWN):
        mr_id = 0x014C
        pass

    class _STARTDOC(_MR_UNKNOWN):
        mr_id = 0x014D
        pass

    class _DELETEOBJECT(_SELECTOBJECT):
        mr_id = 0x01F0
        pass

    class _CREATEPATTERNBRUSH(_MR_UNKNOWN):
        mr_id = 0x01F9
        pass
        
    class _SETTEXTCOLOR(_MR_UNKNOWN):
        mr_id = 0x0209
        mr_typedef=[('i','crColor',0)]
        def __init__(self,color=0):
            _MR_UNKNOWN.__init__(self)
            self.crColor=color
        pass

    class _SETBKCOLOR(_SETTEXTCOLOR):
        mr_id = 0x0201
        mr_typedef=[('i','bkColor',0)]
        def __init__(self,color=0):
            _MR_UNKNOWN.__init__(self)
            self.bkColor=color

        pass

    class _SETTEXTJUSTIFICATION(_MR_UNKNOWN):
        mr_id = 0x020A
        pass

    class _SETWINDOWORGEX(_MR_UNKNOWN):
        mr_id = 0x020B
        mr_typedef=[('h','ptlOrigin_y'),
                     ('h','ptlOrigin_x')]
        def __init__(self,x=0,y=0):
            _MR_UNKNOWN.__init__(self)
            self.ptlOrigin_x=x
            self.ptlOrigin_y=y
        pass

    class _SETWINDOWEXTEX(_MR_UNKNOWN):
        mr_id = 0x020C
        mr_typedef=[('h','szlExtent_cy'),
                     ('h','szlExtent_cx')]
        def __init__(self,cx=0,cy=0):
            _MR_UNKNOWN.__init__(self)
            self.szlExtent_cx=cx
            self.szlExtent_cy=cy
        pass

    class _SETVIEWPORTORG(_SETWINDOWORGEX):
        mr_id = 0x020D
        pass

    class _SETVIEWPORTEXT(_SETWINDOWEXTEX):
        mr_id = 0x020E
        pass

    class _OFFSETWINDOWORG(_MR_UNKNOWN):
        mr_id = 0x020F
        pass

    class _OFFSETVIEWPORTORG(_MR_UNKNOWN):
        mr_id = 0x0211
        pass

    class _MOVETOEX(_MR_UNKNOWN):
        mr_id = 0x0214
        mr_typedef=[
                ('h','ptl_y'),
                ('h','ptl_x')]
        def __init__(self,x=0,y=0):
            _MR_UNKNOWN.__init__(self)
            self.ptl_x=x
            self.ptl_y=y

        def getBounds(self):
            return (self.ptl_x,self.ptl_y,self.ptl_x,self.ptl_y)
        pass

    class _LINETO(_MOVETOEX):
        mr_id = 0x0213
        pass


    class _OFFSETCLIPRGN(_MR_UNKNOWN):
        mr_id = 0x0220
        mr_typedef=[('h','offY'),('h','offX')]
        pass

    class _FILLREGION(_MR_UNKNOWN):
        mr_id = 0x0228
        pass

    class _SETMAPPERFLAGS(_MR_UNKNOWN):
        mr_id = 0x0231
        mr_format=[('i','dwFlags',0)]
        def __init__(self):
            _MR_UNKNOWN.__init__(self)
        pass

    class _SELECTPALETTE(_MR_UNKNOWN):
        mr_id = 0x0234
        mr_typedef=[('i','handle')]
        def __init__(self):
            _MR_UNKNOWN.__init__(self)
        pass

    class _CREATEPENINDIRECT(_MR_UNKNOWN):
        mr_id = 0x02FA
        mr_typedef=[('h','lopnStyle'),
                ('h','lopnWidth'),## x size of pen
                ('h','lopnHeight'), ## y size of pen -- ignore it
                ('i','lopnColor'),
                ('h','lopnFlag') ## what is it?
                ]
        def __init__(self,style=PS_SOLID,width=1,color=0):
            _MR_UNKNOWN.__init__(self)
            self.lopn_style=style
            self.lopn_width=width
            self.lopn_color=color
        pass

    class _CREATEFONTINDIRECT(_MR_UNKNOWN):
        mr_id = 0x02FB
        mr_typedef=[('h','lfHeight'),
                ('h','lfWidth'),
                ('h','lfEscapement'), ## rotation of text string counterclockwise in 0.1 degree units
                ('h','lfOrientation'), ## rotation of every char in the string counterclockwise in 0.1 degree units
                ('h','lfWeight'),
                ('B','lfItalic'),
                ('B','lfUnderline'),
                ('B','lfStrikeOut'),
                ('B','lfCharset'),
                ('B','lfOutPrecision'),
                ('B','lfClipPrecision'),
                ('B','lfQuality'),
                ('B','lfPitchAndFamily')
                ]
                ## followed by 0-terminated font name and 1 more unidentified byte (==100)
        pass

    class _CREATEBRUSHINDIRECT(_MR_UNKNOWN):
        mr_id = 0x02FC
        mr_typedef=[
                ('h','lbStyle'),
                ('i','lbColor'),
                ('h','lbHatch')]
        def __init__(self,style=BS_SOLID,hatch=HS_HORIZONTAL,color=0):
            _MR_UNKNOWN.__init__(self)
            self.lbStyle = style
            self.lbColor = color
            self.lbHatch = hatch

        def hasHandle(self):
            return True

        pass

    class _CREATEBITMAPINDIRECT(_MR_UNKNOWN):
        mr_id = 0x02FD
        pass

    class _POLYGON(_MR_UNKNOWN):
        mr_id = 0x0324
        mr_typedef=[('h','cptl')]
        mr_point_type='h'
        
        def __init__(self,points=[],bounds=(0,0,0,0)):
            _MR_UNKNOWN.__init__(self)
            self.setBounds(bounds)
            self.cptl=len(points)
            self.aptl=points

        def unserializeExtra(self,data):
            # print "found %d extra bytes." % len(data)
            start=0
            start,self.aptl=self.unserializePoints(self.mr_point_type,self.cptl,data,start)
            # print "apts size=%d: %s" % (len(self.apts),self.apts)

        def sizeExtra(self):
            return struct.calcsize(self.mr_point_type)*2*self.cptl

        def serializeExtra(self,fh):
            self.serializePoints(fh,self.mr_point_type,self.aptl)

        def str_extra(self):
            txt=StringIO()
            start=0
            txt.write("\tpoints: %s\n" % str(self.aptl))
            return txt.getvalue()
        pass
        
    class _POLYLINE(_POLYGON):
        mr_id = 0x0325
        pass
        
    class _SCALEWINDOWEXTEX(_MR_UNKNOWN):
        mr_id = 0x0410
        mr_typedef=[
                ('i','xNum',1),
                ('i','xDenom',1),
                ('i','yNum',1),
                ('i','yDenom',1)]
        def __init__(self,xn=1,xd=1,yn=1,yd=1):
            _MR_UNKNOWN.__init__(self)
            self.xNum=xn
            self.xDenom=xd
            self.yNum=yn
            self.yDenom=yd
        pass

    class _SCALEVIEWPORTEXTEX(_SCALEWINDOWEXTEX):
        mr_id = 0x0412
        pass

    class _EXCLUDECLIPRECT(_MR_UNKNOWN):
        mr_id = 0x0415
        mr_typedef=[('h','rclBox_bottom'),('h','rclBox_right'),
                            ('h','rclBox_top'),('h','rclBox_left')
                            ]
        pass

    class _INTERSECTCLIPRECT(_MR_UNKNOWN):
        mr_id = 0x0416
        mr_typedef=[('h','rclBox_bottom'),('h','rclBox_right'),
                            ('h','rclBox_top'),('h','rclBox_left')
                            ]
        pass

    class _ELLIPSE(_MR_UNKNOWN):
        mr_id = 0x0418
        mr_typedef=[('h','rclBox_bottom'),('h','rclBox_right'),
                            ('h','rclBox_top'),('h','rclBox_left')
                            ]
        def __init__(self,box=(0,0,0,0)):
            _MR_UNKNOWN.__init__(self)
            self.rclBox_left=box[0]
            self.rclBox_top=box[1]
            self.rclBox_right=box[2]
            self.rclBox_bottom=box[3]
        pass

    class _FLOODFILL(_MR_UNKNOWN):
        mr_id = 0x0419
        pass

    class _RECTANGLE(_ELLIPSE):
        mr_id = 0x041B
        pass

    class _SETPIXELV(_MR_UNKNOWN):
        mr_id = 0x041F
        mr_typedef=[
                ('i','ptlPixel_x'),
                ('i','ptlPixel_y'),
                ('i','crColor')]
        def __init__(self,x=0,y=0,color=0):
            _MR_UNKNOWN.__init__(self)
            self.ptlPixel_x=x
            self.ptlPixel_y=y
            self.crColor=color
        pass

    class _FRAMEREGION(_MR_UNKNOWN):
        mr_id = 0x0429
        pass

    class _ANIMATEPALETTE(_MR_UNKNOWN):
        mr_id = 0x0436
        pass

    class _TEXTOUT(_MR_UNKNOWN):  ##was _TEXTOUT in WMF!!!
        mr_id = 0x0521
        mr_typedef=[
                ('h','count')]
                ## after that  -- 'count' chars
                ## after chars -- y and x
        pass

    class _UNKNOWN_MAGIC(_MR_UNKNOWN):
        mr_id = 0x0529 ##MAGIC?
        pass

    class _POLYPOLYGON(_MR_UNKNOWN):
        mr_id = 0x0538
        mr_typedef=[('h','nPolys')]
        mr_point_type='h'
        pass

    class _EXTFLOODFILL(_MR_UNKNOWN):
        mr_id = 0x0548
        pass

    class _ROUNDRECT(_MR_UNKNOWN):
        mr_id = 0x061C
        mr_typedef=[('h','szlCorner_cx'),
                ('h','szlCorner_cy'),
                ('h','rclBox_bottom'),
                ('h','rclBox_right'),
                ('h','rclBox_top'),
                ('h','rclBox_left')
                ]
        def __init__(self,box=(0,0,0,0),cx=0,cy=0):
            _MR_UNKNOWN.__init__(self)
            self.rclBox_left=box[0]
            self.rclBox_top=box[1]
            self.rclBox_right=box[2]
            self.rclBox_bottom=box[3]
            self.szlCorner_cx=cx
            self.szlCorner_cy=cy
        pass

    class _PATBLT(_MR_UNKNOWN):
        mr_id = 0x061D
        pass

    class _ESCAPE(_MR_UNKNOWN):
        mr_id = 0x0626
        pass

    class _DRAWTEXT(_MR_UNKNOWN):
        mr_id = 0x062F
        pass

    class _CREATEBITMAP(_MR_UNKNOWN):
        mr_id = 0x06FE
        pass

    class _CREATEREGION(_MR_UNKNOWN):
        mr_id = 0x06FF
        pass

    class _ARC(_MR_UNKNOWN):
        mr_id = 0x0817
        mr_typedef=[
                ('h','rclBox_left'),
                ('h','rclBox_top'),
                ('h','rclBox_right'),
                ('h','rclBox_bottom'),
                ('h','ptlStart_x'),
                ('h','ptlStart_y'),
                ('h','ptlEnd_x'),
                ('h','ptlEnd_y')
                ]
        
        def __init__(self,left=0,top=0,right=0,bottom=0,xstart=0,ystart=0,xend=0,yend=0):
            _MR_UNKNOWN.__init__(self)
            self.rclBox_left=left
            self.rclBox_top=top
            self.rclBox_right=right
            self.rclBox_bottom=bottom
            self.ptlStart_x=xstart
            self.ptlStart_y=ystart
            self.ptlEnd_x=xend
            self.ptlEnd_y=yend
        pass

    class _PIE(_ARC):
        mr_id = 0x081A
        pass

    class _CHORD(_ARC):
        mr_id = 0x0830
        pass

    class _BITBLT(_MR_UNKNOWN):
        mr_id = 0x0922
        pass

    class _DIBBITBLT(_MR_UNKNOWN):
        mr_id = 0x0940
        pass

    class _EXTTEXTOUT(_MR_UNKNOWN):
        mr_id = 0x0A32
        mr_typedef=[
                ('h','y'),
                ('h','x'),
                ('h','count'),
                ('h','flag')] ## if flag&ETO_CLIPPED: <hhhh with x1,y1,x2,y2
                ## after that  -- 'count' chars
                ## after chars -- list of dx for chars
        pass

    class _STRETCHBLT(_MR_UNKNOWN):
        mr_id = 0x0B23
        pass

    class _DIBSTRETCHBLT(_MR_UNKNOWN):
        mr_id = 0x0B41
        pass

    class _SETDIBTODEV(_MR_UNKNOWN):
        mr_id = 0x0D33
        pass

    class _STRETCHDIBITS(_MR_UNKNOWN):
        mr_id = 0x0F43
        mr_typedef=[
                ('i','dwRop'),
                ('h','unknown'), ## seems to be 0
                ('h','topSrc'),
                ('h','rightSrc'),
                ('h','bottomSrc'),
                ('h','leftSrc'),
                ('h','cyDest'),
                ('h','cxDest'),
                ('h','topDest'),
                ('h','leftDest'),
                ## DIB data
                ('i','hdrSize'), ##0x28 0x00 0x00 0x00
                ('i','bmpWidth'),
                ('i','bmpHeight'),                
                ('h','numClrPlanes'), ## usualy 1
                ('h','bmpDepth'),
                ('i','CmprMethod'), ## doesn't matter
                ('i','imgSize'),
                ('i','resX'),           ##horizontal resolution, never saw it used
                ('i','resY'),           ##vertical resolution, never saw it used
                ('i','numClrUsed'),
                ('i','numClrImportant')] ## 0 when every Clr is important
        pass

### Enf_of_unimplemented part
_mrmap={}

for name in dir(_MR):
    #print name
    cls=getattr(_MR,name,None)
    if cls and callable(cls) and issubclass(cls,_MR_UNKNOWN):
        #print "subclass! id=%d %s" % (cls.emr_id,str(cls))
        _mrmap[cls.mr_id]=cls
        
class WMF:
    def __init__(self,width=6.0,height=4.0,density=300,units="in",
                 description="pyemf.sf.net",verbose=False):
        self.filename=None
##        self.dc=_DC(width,height,density,units)
        self.records=[]

        # path recordkeeping
        self.pathstart=0
        self.verbose=verbose

        # if True, scale the image using only the header, and not
        # using MapMode or SetWindow/SetViewport.
##        self.scaleheader=True

        mr=_MR._HEADER(description)
        self._append(mr)
##        if not self.scaleheader:
##            self.SetMapMode(MM_ANISOTROPIC)
##            self.SetWindowExtEx(self.dc.pixelwidth,self.dc.pixelheight)
##            self.SetViewportExtEx(
##                int(self.dc.width/100.0*self.dc.ref_pixelwidth/self.dc.ref_width),
##                int(self.dc.height/100.0*self.dc.ref_pixelheight/self.dc.ref_height))

    def loadmem(self,membuf=None):
        """
Read an existing buffer with EMF file.  If any records exist in the current
object, they will be overwritten by the records from this buffer.

@param membuf: buffer to load
@type membuf: string
@returns: True for success, False for failure.
@rtype: Boolean
        """
        fh = StringIO(membuf)
        self._load(fh)

    def load(self,filename=None):
        """
Read an existing EMF file.  If any records exist in the current
object, they will be overwritten by the records from this file.

@param filename: filename to load
@type filename: string
@returns: True for success, False for failure.
@rtype: Boolean
        """
        if filename:
            self.filename=filename

        if self.filename:
            fh=open(self.filename)
            self._load(fh)

    def _load(self,filehandler=None):
        self.records=[]
        self.placeable = 0
        nSize = 24
        rdFunction = 4 # False id for Header
        data = ord(filehandler.read(1))
        if data == 0xD7: ##Aldus placeable WMF
            filehandler.seek(28)
            mtSize = filehandler.read(4)
            filehandler.seek(0)
            rdFunction = 1
            nSize = 28  ## size of APM_header +6. because 6 will be substracted in unserialize
            e=_mrmap[rdFunction]()
            e.unserialize(filehandler,rdFunction,nSize)
            self.records.append(e)
            ## added Aldus Placable header
            nSize = 24          ## size of header +6. because 6 will be substracted in unserialize
            rdFunction = 4 # False id for Header
            e=_mrmap[rdFunction]()
            e.unserialize(filehandler,rdFunction,nSize)
            self.records.append(e)
            [self.mtSize] = struct.unpack('i',mtSize)
        else:
            filehandler.seek(6)
            mtSize = filehandler.read(4)
            [self.mtSize] = struct.unpack('i',mtSize)
            filehandler.seek(0)
            e=_mrmap[rdFunction]()
            e.unserialize(filehandler,rdFunction,nSize)
            self.records.append(e)
##        print 'Header added'
        self._unserialize(filehandler)
            

    def _unserialize(self,fh):
        print 'mtSize:',self.mtSize
        try:
            while self.mtSize*2 > fh.tell()+6:
                print 'Cur.position: ',fh.tell()
                data=fh.read(6)
                count=len(data)
                if count>0:
                    (nSize,rdFunction)=struct.unpack("<ih",data)
                    nSize*=2
                    if rdFunction in _mrmap:
                        e=_mrmap[rdFunction]()
                    else:
                        e=_MR_UNKNOWN()

                    e.unserialize(fh,rdFunction,nSize)
                    self.records.append(e)
                    
                    if self.verbose:
                        print "Unserializing: ",
                        print e
                
        except EOFError:
            pass

    def _append(self,e):
        """Append an EMR to the record list, unless the record has
        been flagged as having an error."""
        if not e.error:
            if self.verbose:
                print "Appending: ",
                print e
            self.records.append(e)
            return 1
        return 0

    def _end(self):
        """
Append an EOF record and compute header information.  The header needs
to know the number of records, number of handles, bounds, and size of
the entire metafile before it can be written out, so we have to march
through all the records and gather info.
        """
        
        end=self.records[-1]
        if not isinstance(end,_MR._EOF):
            if self.verbose: print "adding EOF record"
            e=_MR._EOF()
            self._append(e)
        header=self.records[0]
        header.setBounds(self.dc,self.scaleheader)
        header.nRecords=len(self.records)
##        header.nHandles=len(self.dc.objects)
        size=0
        for e in self.records:
            e.resize()
            size+=e.nSize
        header.nBytes=size


if __name__ == "__main__":
    try:
        from optparse import OptionParser

        parser=OptionParser(usage="usage: %prog [options] wmf-files...")
        parser.add_option("-v", action="store_true", dest="verbose", default=False)
        parser.add_option("-s", action="store_true", dest="save", default=False)
        parser.add_option("-o", action="store", dest="outputfile", default=None)
        (options, args) = parser.parse_args()
        # print options
    except:
        # hackola to work with Python 2.2, but this shouldn't be a
        # factor when imported in normal programs because __name__
        # will never equal "__main__", so this will never get called.
        class data:
            verbose=True
            save=True
            outputfile=None

        options=data()
        args=sys.argv[1:]

    if len(args)>0:
        for filename in args:
            e=EMF(verbose=options.verbose)
            e.load(filename)
            if options.save:
                if not options.outputfile:
                    options.outputfile=filename+".out.wmf"
                print "Saving %s..." % options.outputfile
                ret=e.save(options.outputfile)
                if ret:
                    print "%s saved successfully." % options.outputfile
                else:
                    print "problem saving %s!" % options.outputfile
##    else:
##        e=WMF(verbose=options.verbose)
##        e.save("new.wmf")
