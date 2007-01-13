from lib_christine.gtk_misc import *
from lib_christine.trans import *


class Handler(gtk_misc):
	def __init__(self,interface):
		gtk_misc.__init__(self)
		self.gconf = christine_gconf()
		active = self.gconf.gconf.key_is_writable("/apps/christine/plugins/plugin_demo")
		if active == None:
			self.gconf.set_value("plugins/plugin_demo",True)
		self.values = {
				"name": "Demo plugin",
				"active": active,
				"Author":"Marco Antonio Islas Cruz",
				"ref":self,
				}
		self.interface = interface

	def start(self):
		label = gtk.Label(translate("This is done in a plugin!!"))
		self.interface.pack(label,"list_vbox",False,False,2)
		label.show()
		pixbuf = self.gen_pixbuf("logo.png")
		image = gtk.Image()
		image.set_from_pixbuf(pixbuf)
		self.interface.pack(image,"list_vbox",False,False,2)
		image.show()
		self.interface.write("Hola mundo!!")
