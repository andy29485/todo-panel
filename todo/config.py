from gi.repository import GObject, Gedit, Gtk, PeasGtk

class ConfigurationWidget(Gtk.VBox)
  def __init__(self, setting):
    Gtk.VBox.__init__(self)
    self.setting = settings
