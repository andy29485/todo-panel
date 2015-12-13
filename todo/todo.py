#!/usr/bin/env python3

from gi.repository import GObject, Gedit, Gtk
import os, re
from xml.etree import ElementTree, cElementTree
from widget import TodoPanel

#next two functions shamlessly taken from(and modified):
#https://thomassileo.name/blog/2013/12/12/tracking-changes-in-directories-with-python
#also see:
#https://github.com/tsileo/dirtools

def compute_dir_index(path, files=[], ext=[]):
  """ Return a tuple containing:
  - list of files (relative to path)
  - lisf of subdirs (relative to path)
  - a dict: filepath => last.
  """
  subdirs = []
  items   = 0

  for root, dirs, filenames in os.walk(path):
    if items < 500:
      for subdir in dirs:
        if subdir not in ['.git'] and not subdir.startswith('.'):
          subdirs.append(os.path.relpath(os.path.join(root, subdir), path))
        items += 1

      for f in filenames:
        if not ext or f.rpartition('.')[2] in ext:
          files.append(os.path.realpath(os.path.join(root, f)))
        items += 1
    else:
      break

  index = {}
  for f in files:
    index[f] = os.path.getmtime(f)

  return dict(files=files, subdirs=subdirs, index=index)

def compute_diff(dir_base, dir_cmp):
  data = {}
  data['remove'] = list(set(dir_cmp['files']) - set(dir_base['files']))
  data['check'] = list(set(dir_base['files']) - set(dir_cmp['files']))

  for f in set(dir_cmp['files']).intersection(set(dir_base['files'])):
    if dir_base['index'][f] != dir_cmp['index'][f]:
      data['check'].append(f)

  return data

class TodoPlugin(GObject.Object, Gedit.WindowActivatable):
  __gtype_name__      = 'TodoPanel'
  window              = GObject.property(type=Gedit.Window)
  dir_hash            = {}
  dirs                = []
  files               = []
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
    if self.widget:
      #get dirs that need to be checked
      self.update_dirs()
      #get files that need to be checked
      self.update_files()
      #scan files
      self.walk()
      #update panel
      self.widget.update()
    bottom = self.window.get_bottom_panel()
    bottom.activate_item(self.widget)

  def on_tab_removed(self, window, tab, data=None):
    self.do_update_state()

  def do_create_configure_widget(self):
    widget = ConfigurationWidget(self.settings)
    return widget

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
    self.files = [doc.get_uri_for_display()
                  for doc in self.window.get_documents()]
    self.dirs = [f.rpartition('/')[0] for f in self.files]
    self.dirs = list(set([i for i in self.dirs if i]))

    def matches(dirs, name):
      for d in dirs:
        if name.startswith(d):
          return True
      return False

    remove = []
    for tag in self.matches.keys():
      for f in self.matches[tag]:
        name = f.partition('file://')[2]
        if not matches(self.dirs, name):
          remove.append(f)
      self.matches[tag] = {key: value for key, value
                             in self.matches[tag].items()
                             if key not in remove}

  def update_files(self):
    check = []
    for d in self.dirs:
      tmp = compute_dir_index(d, self.files, self.allowed_extensions)
      if d in self.dir_hash.keys():
        diff = compute_diff(tmp, self.dir_hash[d])
      else:
        diff = compute_diff(tmp, {'files':[], 'subdirs':[], 'index':[]})
      self.dir_hash[d] = tmp
      check += [i for i in diff['check']
                     if i.rpartition('.')[2] in self.allowed_extensions]
      for tag in self.matches.keys():
        self.matches[tag] = {key: value for key, value in
                             self.matches[tag].items() if
                             key.partition('file://')[2] not in diff['remove']}
    self.files = list(set(check))

  def walk(self):
    match_re = '^(.*?)({})(:|[ \t]*-)?[ \t]*([^\n]*?)(\n|$)'.format(
                          '|'.join(self.allowed_types))
    for fi in self.files:
      with open(fi, 'r') as f:
        fi = 'file://'+fi
        line = 0
        for i in re.findall(match_re, f.read(), re.DOTALL|re.MULTILINE):
          line += len(i[0].split('\n'))
          if fi in self.matches[i[1]].keys():
            self.matches[i[1]][fi].append((line, i[3]))
          else:
            self.matches[i[1]][fi] = [(line, i[3])]
