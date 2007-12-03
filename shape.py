class Shape:
    def __init__(self):
        type = 0
        self.mode = Mode()
        self.clip = Clip()
        values = []
    def add(ctx):
        pass
    def draw(ctx):
        pass

class Lines(Shape):
    def __init__(self):
        Shape.__init__(self)
        type = 1
        self.outline = Outline() ## Type of stroke: color,width,dash/dots etc
        
    def line_set_props(ctx,i):
#        if (i) and line.dashed and BKMode.transparent:
#           set.dash
#           set.BKColor
#           return 1
#       else:
#           set.dash  ##'no dashes' is a kind of dashes
#           set.line_color
#           return 0
        pass
        
    def draw(ctx):
        if self.line_set_props(ctx,1):
            ctx.stroke()
            self.line_set_props(ctx,0)
        ctx.stroke()

class Figs(Lines):
    def __init__(self):
        Lines.__init__(self)
        type = 2
        self.fill = Fill() ## Type of fill: color, transparency, pattern etc
        
    def fill_set_props(ctx,i):
#        if (i) and figs.patterned and BKMode.transparent:
## check what has to be done here
#           set.pattern
#           set.BKColor
#           return 1
#       else:
#           set.fill_color
#           return 0
        pass
        
    def draw(ctx):
        if self.fill_set_props(ctx,1):
            ctx.fill_preserve()
            self.fill_set_props(ctx,0)
        ctx.fill_preserve()
        Lines.draw(ctx)

class MoveTo(Lines):
    def __init__(self):
        Lines.__init__(self)
    
    def add(ctx):
        ctx.move_to(values[0],values[1])
    
    def draw(ctx):
        pass

class LineTo(Lines):
    def __init__(self):
        Lines.__init__(self)
    
    def add(ctx):
        ctx.line_to(values[0],values[1])
        
class ArcTo(Lines):
    def __init__(self):
        Lines.__init__(self)
    
    def add(ctx):
        ctx.arc(values[0],values[1],values[2],values[3],values[4],values[5])
        
