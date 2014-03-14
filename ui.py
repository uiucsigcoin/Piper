import pygtk
pygtk.require('2.0')
import gtk
import pango
from time import sleep

from threading import Thread
import gobject

global_ui = None

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
        self.display_message("Welcome to Coinverter!\n\nEnter a coin to get started.")
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

    def update_widget(self):
        while gtk.events_pending():
            gtk.main_iteration_do(True)
        return True

    def someFunc(self):

        # Wait for window
        counter = 0
        for i in range(1,10):
            counter += 1
            message = "counter: " + str(counter)

            print counter

            # Redraw
            self.main_text.set_text(message)
            self.main_text.queue_draw()
                
            sleep(0.5)

if __name__ == '__main__':

    gobject.threads_init()
    ui = CoinUI()

    thread = Thread(target = ui.someFunc, args = ())
    thread.start()
    sleep(0.2)

    ui.main()

    # Show market price (pass thru func)
    # Money put in (USD + BTC)
    # Instructions for each step
        
