#!/usr/bin/env python3

from gi.repository import GObject, Gedit, Gtk
import os, re
from xml.etree import ElementTree, cElementTree
from widget import TodoPanel

class TodoPlugin(GObject.Object, Gedit.WindowActivatable):
  __gtype_name__      = 'TodoPanel'
  window              = GObject.property(type=Gedit.Window)
  dirs                = []
  matches             = {}
  settings            = {}

  def __init__(self):
    GObject.Object.__init__(self)
    self.load_settings()
    self.allowed_extensions = re.split('[\\s\\.;\\|:]',
                                self.settings['extensions'])
    self.allowed_types      = re.split('[\\s\\.;\\|:]', self.settings['types'])
    for i in self.allowed_types:
      self.matches[i] = {}
    self.widget = None

  def do_activate(self):
    icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
    self.widget = TodoPanel(self.window, self.matches,
                            self.allowed_types, self.settings)
    self.widget.show_all()

    bottom = self.window.get_bottom_panel()
    bottom.add_item(self.widget, "TodoBottomPanel", _("TODO List"), icon)
    bottom.activate_item(self.widget)

  def do_deactivate(self):
    bottom = self.window.get_bottom_panel()
    bottom.remove_item(self.widget)

  def do_update_state(self):
    self.update_dirs()
    for i in self.allowed_types:
      self.matches[i] = {}
    self.walk()
    if self.widget:
      self.widget.update()

  def save_settings(self):
    config = os.path.join(os.path.dirname(__file__), 'config.xml')
    root = cElementTree.Element("settings")

    with open(config, 'rt') as f:
      tree = ElementTree.parse(f)

    for node in tree.iter():
      name = node.attrib.get('name')
      default = node.attrib.get('default')
      cElementTree.SubElement(root, "setting", name=name,
                              value=self.settings[name], default=default)
    tree = cElementTree.ElementTree(root)
    tree.write(config)

  def load_settings(self):
    self.settings = {}
    config = os.path.join(os.path.dirname(__file__), 'config.xml')
    with open(config, 'rt') as f:
      tree = ElementTree.parse(f)
    for node in tree.iter():
      name    = str(node.attrib.get('name'))
      value   = str(node.attrib.get('value'))
      default = str(node.attrib.get('default'))
      if re.search('\\d+', value):
        value = int(value)
      if re.search('\\d+', default):
        default = int(default)
      self.settings[name] = value if value else default

  def update_dirs(self):
    l1 = [doc.get_uri_for_display().rpartition('/')[0]
          for doc in self.window.get_documents()]
    l1 = list(set(l1))
    l2 = l1[:]

    minus = 0

    for i in range(len(l1)):
      for j in range(len(l2)):
        if l2[j].startswith(l1[i]) and l1[i] != l1[j]:
          l2.remove(l2[j-minus])
          minus += 1
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
