import pygtk
pygtk.require('2.0')
import gtk
import pango


class CoinUI:
    def realize_cb(self, widget):
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        color = gtk.gdk.Color()
        cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
        widget.window.set_cursor(cursor)

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.connect("realize", self.realize_cb)
        self.window.set_border_width(0)
        self.window.fullscreen()

        self.main_text = gtk.Label()
        self.display_message("Welcome to Coinverter!")
        self.window.add(self.main_text)
        self.main_text.show()

        color = gtk.gdk.color_parse('#000000')
        self.window.modify_bg(gtk.STATE_NORMAL, color)
        self.window.show()

    def display_message(self, message):
        fontdesc = pango.FontDescription("DejaVu Sans 30")
        attr = pango.AttrList()
        fg_color = pango.AttrForeground(65535, 65535, 65535, 0, len(message))
        attr.insert(fg_color)
        self.main_text.set_attributes(attr)
        self.main_text.modify_font(fontdesc)
        self.main_text.set_text(message)
        
    def main(self):
        gtk.main()

if __name__ == '__main__':
    ui = CoinUI()
    ui.main()
        
