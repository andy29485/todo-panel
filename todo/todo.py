#!/usr/bin/env python3

from gi.repository import GObject, Gedit, Gtk
import os, re
from widget import TodoPanel

import os

#next two functions shamlessly taken from(and modified):
#https://thomassileo.name/blog/2013/12/12/tracking-changes-in-directories-with-python
#also see:
#https://github.com/tsileo/dirtools

def compute_dir_index(path, ext=[]):
  """ Return a tuple containing:
  - list of files (relative to path)
  - lisf of subdirs (relative to path)
  - a dict: filepath => last.
  """
  files   = []
  subdirs = []
  items   = 0

  for root, dirs, filenames in os.walk(path):
    if items < 300:
      for subdir in dirs:
        if subdir not in ['.git']:
          subdirs.append(os.path.relpath(os.path.join(root, subdir), path))

      for f in filenames:
        if not ext or f.rpartition(os.path.sep)[2] in ext:
          files.append(os.path.relpath(os.path.join(root, f), path))
          items += 1
    else:
      break

  index = {}
  for f in files:
    index[f] = os.path.getmtime(os.path.join(path, files[0]))

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
  allowed_extensions  = 'java php py c h cpp hpp c++ html'
  allowed_types       = 'TODO FIXME NOTE IMPROVE OPTIMIZE REFACTOR'
  matches             = {}
  settings            = {'font':'Ubuntu Mono', 'size':11, 'spacing':2}

  def __init__(self):
    GObject.Object.__init__(self)
    self.allowed_extensions = re.split('[\\s\\.;\\|:]', self.allowed_extensions)
    self.allowed_types      = re.split('[\\s\\.;\\|:]', self.allowed_types)
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

  def update_dirs(self):
    l1 = [doc.get_uri_for_display().rpartition('/')[0]
          for doc in self.window.get_documents()]
    l1 = list(set(l1))
    print(l1)
    l2 = [path for path in l1 if os.path.exists(path)]

    minus = 0

    for i in range(len(l1)):
      for j in range(len(l2)):
        if l2[j].startswith(l1[i]) and l1[i] != l1[j]:
          l2.remove(l2[j-minus])
          minus += 1
    self.dirs = l2

  def update_files(self):
    removed    = []
    self.files = []
    for d in self.dirs:
      tmp = compute_dir_index(d, self.allowed_extensions)
      if d in self.dir_hash.keys():
        diff = compute_diff(self.dir_hash[d], tmp)
      else:
        diff = compute_diff({'files':[], 'subdirs':[], 'index':[]}, tmp)
      self.dir_hash[d] = tmp
      removed    += diff['remove']
      self.files += [i for i in diff['check']
                     if i.rpartition(os.path.sep)[2] in self.allowed_extensions]
      for tag in self.matches.keys():
        self.matches[tag] = {key: value for key, value
                             in self.matches[tag].items()
                             if value not in removed}

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
