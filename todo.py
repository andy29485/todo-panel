#!/usr/bin/env python3

from gi.repository import GObject, Gedit, Gtk, PeasGtk
import os, re
from widget import TodoPanel

class TodoPlugin(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
  __gtype_name__      = 'TodoPanel'
  window              = GObject.property(type=Gedit.Window)
  config              = {''} #TODO this is not used
  dirs                = []
  allowed_extensions  = 'java php py c h cpp hpp c++ html'
  allowed_types       = 'TODO FIXME NOTE IMPROVE OPTIMIZE REFACTOR'
  matches             = {}

  def __init__(self):
    GObject.Object.__init__(self)
    self.allowed_extensions = re.split('[\\s\\.;\\|:]', self.allowed_extensions)
    self.allowed_types      = re.split('[\\s\\.;\\|:]', self.allowed_types)
    for i in self.allowed_types:
      self.matches[i] = []
    self.panel              = TodoPanel(self.window, self.matches)

  def do_activate(self):
    icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU) #TODO set
    bottom = self.window.get_bottom_panel()                           #  icon
    bottom.add_item(self.panel, "TodoBottomPanel", "TODO List", icon)
    bottom.activate_item(self.panel)

  def do_deactivate(self):
    bottom = self.window.get_bottom_panel()
    bottom.remove_item(self.panel)

  def do_create_configure_widget(self):
    pass
    #TODO figure out how this is done and maybe do it?

  def do_update_state(self):
    self.update_dirs()
    self.walk()

  def update_dirs(self):
    l1 = [doc.get_uri_for_display().rpartition('/')[0]
          for doc in self.window.get_documents()]
    l1 = list(set(l1))
    l2 = l1[:]
    for i in range(len(l1)):
      for j in range(len(l2)):
        if l2[j].startswith(l1[i]) and l1[i] != l1[j]:
          l2.remove(l2[j])
    self.dirs = l2

  def walk(self):
    matchregex = '^(.*?)({})(:|\\s*-)\\s*(.*?)(\n|$)'.format(
                   '|'.join(self.allowed_types))
    for d in self.dirs:
      for root, dirs, files in os.walk("."):
        for file in files:
          for ext in self.allowed_extensions:
            if file.endswith(ext):
              with open(file, 'w') as f:
                line = 0
                for i in re.findall(matchregex, f.read(), re.DOTALL|re.MULTILINE):
                  line += len(i[0].split('\n'))
                  matches[i[1]].append((file, line, i[3]))
                  line += 1 #TODO may need to remove

  def on_tab_added(self, window, tab, data=None):
    self.do_update_state()

  def on_tab_removed(self, window, tab, data=None):
    self.do_update_state()
