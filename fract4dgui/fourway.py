# Sort of a widget which controls 2 linear dimensions of the fractal
# I say sort of, because this doesn't actually inherit from gtk.Widget,
# so it's not really a widget. This is because if I attempt to do that
# pygtk crashes. Hence I delegate to a member which actually is a widget
# with some stuff drawn on it - basically an ungodly hack.

import gtk
import gobject
import pango

class T(gobject.GObject):
    __gsignals__ = {
        'value-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT)),
        'value-slightly-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))
        }

    def __init__(self,text):        
        self.button = 0
        self.radius = 0
        self.last_x = 0
        self.last_y = 0        
        self.text=text
        gobject.GObject.__init__(self)
        
        self.widget = gtk.DrawingArea()
        self.widget.set_size_request(53,53)

        self.widget.set_events(
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.BUTTON1_MOTION_MASK |
            gtk.gdk.POINTER_MOTION_HINT_MASK |
            gtk.gdk.ENTER_NOTIFY_MASK |
            gtk.gdk.LEAVE_NOTIFY_MASK |
            gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.EXPOSURE_MASK
            )

        self.notice_mouse = False
        self.widget.connect('motion_notify_event', self.onMotionNotify)
        self.widget.connect('button_release_event', self.onButtonRelease)
        self.widget.connect('button_press_event', self.onButtonPress)
        self.widget.connect('expose_event',self.onExpose)
        
    def update_from_mouse(self,x,y):
        dx = self.last_x - x
        dy = self.last_y - y
        if dx or dy:
            self.emit('value-slightly-changed',dx,dy)
            self.last_x = x
            self.last_y = y
        
    def onMotionNotify(self,widget,event):
        if not self.notice_mouse:
            return
        dummy = widget.window.get_pointer()
        self.update_from_mouse(event.x, event.y)

    def onButtonRelease(self,widget,event):
        if event.button==1:
            self.notice_mouse = False
            (xc,yc) = (widget.allocation.width//2, widget.allocation.height//2)
            dx = xc - self.last_x
            dy = yc - self.last_y
            if dx or dy:
                self.emit('value-changed',dx,dy)
        
    def onButtonPress(self,widget,event):
        if event.button == 1:
            self.notice_mouse = True
            self.last_x = widget.allocation.width/2
            self.last_y = widget.allocation.height/2
            self.update_from_mouse(event.x, event.y)

    def __del__(self):
        #This is truly weird. If I don't have this method, when you use
        # one fourway widget, it fucks up the other. Having this fixes it.
        # *even though it doesn't do anything*. Disturbing.
        pass
        
    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(widget, r)

    def redraw_rect(self,widget,r):
        style = widget.get_style()
        (w,h) = (widget.allocation.width, widget.allocation.height)
        style.paint_box(widget.window, widget.state,
                        gtk.SHADOW_IN, r, widget, "",
                        0, 0, w-1, h-1)

        xc = w//2
        yc = h//2
        radius = min(w,h)//2 -1


        th = 8
        tw = 6
        gc = style.fg_gc[widget.state]
        # Triangle pointing left        
        points = [
            (1, yc),
            (1+th, yc-tw),
            (1+th, yc+tw)]
        
        
        widget.window.draw_polygon(gc, True, points)

        # pointing right
        points = [
            (w -2, yc),
            (w -2 -th, yc-tw),
            (w -2 -th, yc+tw)]
        widget.window.draw_polygon(gc, True, points)

        # pointing up
        points = [
            (xc, 1),
            (xc - tw, th),
            (xc + tw, th)]
        widget.window.draw_polygon(gc, True, points)
        
        # pointing down
        points = [
            (xc, h - 2),
            (xc - tw, h - 2 - th),
            (xc + tw, h - 2 - th)]
        widget.window.draw_polygon(gc, True, points)

        context = widget.get_pango_context()
        layout = pango.Layout(context)

        drawtext = self.text
        while True:
            layout.set_text(drawtext)
            
            (text_width, text_height) = layout.get_pixel_size()
            # truncate text if it's too long
            if text_width < (w - th *2) or len(drawtext) < 3:
                break
            drawtext = drawtext[:-1]

        style.paint_layout(
            widget.window,
            widget.state,
            True,
            r,
            widget,
            "",
            xc - text_width//2,
            yc - text_height//2,
            layout)

        
# explain our existence to GTK's object system
gobject.type_register(T)
