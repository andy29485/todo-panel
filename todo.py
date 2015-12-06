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
      self.matches[i] = {}
    self.widget = None

  def do_activate(self):
    icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
    self.widget = TodoPanel(self.window, self.matches)
    self.scroller = Gtk.ScrolledWindow()
    self.scroller.set_property("hscrollbar-policy", Gtk.PolicyType.AUTOMATIC)
    self.scroller.set_property("vscrollbar-policy", Gtk.PolicyType.AUTOMATIC)
    self.scroller.add(self.widget)
    self.scroller.show_all()

    bottom = self.window.get_bottom_panel()
    bottom.add_item(self.scroller, "TodoBottomPanel", _("TODO List"), icon)
    bottom.activate_item(self.scroller)

  def do_deactivate(self):
    bottom = self.window.get_bottom_panel()
    bottom.remove_item(self.scroller)

  def do_create_configure_widget(self):
    pass
    #TODO figure out how this is done and maybe do it?

  def do_update_state(self):
    self.update_dirs()
    for i in self.allowed_types:
      self.matches[i] = {}
    self.walk()
    if self.widget:
      self.widget.update()

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
    matchre = '^(.*?)({})(:|[ \t]*-)?[ \t]*([^\n]*?)(\n|$)'.format(
                          '|'.join(self.allowed_types))
    for d in self.dirs:
      for root, dirs, files in os.walk(d):
        for file in files:
          for ext in self.allowed_extensions:
            if file.endswith('.'+ext):
              fi = os.path.join(root, file)
              with open(fi, 'r') as f:
                fi = 'file://'+fi
                line = 0
                for i in re.findall(matchre, f.read(), re.DOTALL|re.MULTILINE):
                  line += len(i[0].split('\n'))
                  if fi in self.matches[i[1]].keys():
                    self.matches[i[1]][fi].append((line, i[3]))
                  else:
                    self.matches[i[1]][fi] = [(line, i[3])]
