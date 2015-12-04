#!/usr/bin/env python3

from gi.repository import GObject, Gedit, Gtk, PeasGtk
import os

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

  def do_activate(self):
    #TODO
    icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
    self._side_widget = Gtk.Label("This is the bottom panel.")
    panel = self.window.get_bottom_panel()
    panel.add_item(self._side_widget, "TodoBottomPanel", "TODO List", icon)
    panel.activate_item(self._side_widge

  def do_deactivate(self):
    panel = self.window.get_side_panel()
    panel.remove_item(self._side_widget)

  def do_create_configure_widget(self):
    #TODO figure out how this is done and maybe do it?

  def do_update_state(self):
    self.update_dirs()
    self.walk()

  def update_dirs(self):
    l1 = [] #TODO get list of dirs - cononical paths
    l1 = list(set(l1))
    l2 = l1[:]
    for i in range(len(l1)):
      for j in range(len(l2)):
        if l2[j].startswith(l1[i]) and l1[i] != l1[j]:
          l2.remove(l2[j])
    self.dirs = l2

  def walk(self):
    self.matches
    matchregex = '^(.*?)({})(:|\\s*-)\\s*(.*?)(\n|$)'.format(
                   '|'.join(self.allowed_types))
    for d in self.dirs:
      for root, dirs, files in os.walk("."):
        for file in files:
          if re.search('({})'.format('|'.join(self.allowed_extensions), file):
            with open(file, 'w') as f:
              line = 0
              for i in re.findall(matchregex, f.read(), re.DOTALL|re.MULTILINE):
                line += len(i[0].split('\n'))
                matches[i[1]].append((line, i[3]))
                line += 1 #TODO may need to remove

  def on_tab_added(self, window, tab, data=None):
    self.do_update_state()

  def on_tab_removed(self, window, tab, data=None):
    self.do_update_state()
