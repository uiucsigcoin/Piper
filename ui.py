import pygtk
pygtk.require('2.0')
import gtk
import pango
from time import sleep
import sys
from threading import Thread
import gobject
from serialtest import main_loop, stop_thread
import logging
import locale

global_ui = None

class CoinUI:
    def realize_cb(self, widget):
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        color = gtk.gdk.Color()
        cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
        widget.window.set_cursor(cursor)

    def __init__(self):
	self.logger = logging.getLogger('coinverter.ui')
	self.logger.info('setting up ui')

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.connect("realize", self.realize_cb)
        self.window.set_border_width(0)
        self.window.fullscreen()

        self.box = gtk.VBox()
        self.box.show()
        self.window.add(self.box)
        self.main_text = gtk.Label()
        self.display_message("Welcome to Coinverter!\n\nLoading...")
        self.box.add(self.main_text)
        fontdesc = pango.FontDescription("DejaVu Sans 30")
        attr = pango.AttrList()
        fg_color = pango.AttrForeground(65535, 65535, 65535, 0, 140)
        attr.insert(fg_color)
        self.main_text.set_attributes(attr)
        self.main_text.modify_font(fontdesc)

        self.main_text.show()

        self.exc_rate = gtk.Label()
        self.box.add(self.exc_rate)
        fontdesc = pango.FontDescription("DejaVu Sans 20")
        attr = pango.AttrList()
        fg_color = pango.AttrForeground(65535, 65535, 65535, 0, 140)
        attr.insert(fg_color)
        self.exc_rate.set_attributes(attr)
        self.exc_rate.modify_font(fontdesc)

        self.exc_rate.show()

        color = gtk.gdk.color_parse('#000000')
        self.window.modify_bg(gtk.STATE_NORMAL, color)
        self.window.show()

    def display_message(self, message):
	self.logger.debug(message)
        self.main_text.set_text(message)

    def display_exchange_rate(self, price, dollahs, btcs):
        self.exc_rate.set_text("1 BTC = {0}\nTotal processed today = {1} / {2:.6} BTC".format(price, dollahs, btcs))

    def main(self):
        gtk.main()

    def update_widget(self):
        while gtk.events_pending():
            gtk.main_iteration_do(True)
        return True

if __name__ == '__main__':

    gobject.threads_init()
    ui = CoinUI()

    thread = Thread(target = main_loop, args = (ui,))
    thread.start()
    sleep(0.2)

try:
    ui.main()
except (KeyboardInterrupt, SystemExit):
    stop_thread()
    sys.exit()

