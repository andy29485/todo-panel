#!/usr/bin/env python3

from gi.repository import Gtk, Gio
import os, re

class TodoPanel(Gtk.Window):
  def __init__(self, window, matches):
    Gtk.Window.__init__(self)
    self.window  = window
    self.matches = matches
    self.buttons1 = []
    self.buttons2 = []

    self.box  = Gtk.Box()
    self.box1 = Gtk.Box()
    self.box.add(self.box1)
    self.add(self.box)
    #TODO - get buttons to look pretty

    for i in list(matches.keys()):
      button = Gtk.Button(label='{} {}'.format(i, len(matches[i])))
      button.connect("clicked", self.on_button1_clicked)
      self.buttons1.append(button)
      self.box.pack_start(button, True, True, 0)

    self.set_type(list(matches.keys())[0])
    #button = Gtk.LinkButton("http://www.gtk.org", "Visit GTK+ Homepage")
    #self.add(button)

  def update(self, matches):
    self.matches = matches
    for button in self.buttons1:
      key = re.sub('\\s+\\d+$', '', button.get_label())
      button.set_label('{} {}'.format(key, len(self.matches[key])))
    self.set_type(self.key_type)

  def set_type(self, key):
    for button in self.buttons2:
      self.buttons2.remove(button)
      self.box1.remove(button)
      del button

    for comment in list(sorted(self.matches[key])):
      b = Button()
      if i[2]:
        b.set_label('{} {}: {}'.format(i[0].rpartition('/')[2], i[1], i[2]))
      else:
        b.set_label('{} {}'.format(i[0].rpartition('/')[2], i[1]))
      b.connect("clicked", self.on_button2_clicked)
      self.buttons2.append(b)
      self.box1.pack_start(b, True, True, 0)

    self.key_type = key

  def on_button1_clicked(self, button):
    #this is the match key to use
    key = re.sub('\\s+\\d+$', '', button.get_label())
    self.set_type(key)

  def on_button2_clicked(self, button):
    file = 'file://' + button.get_var()
    line = int(re.search('^.*? (\\d+)(: .*?)?$', button.get_label()).group(1))
    for doc in self.window.get_documents():
      doc_uri = 'file://%s' % doc.get_uri_for_display()
      if 'file://"'+doc.get_uri_for_display() == file_uri:
        tab = Gedit.Tab.get_from_document(doc)
        view = tab.get_view()
        self.window.set_active_tab(tab)
        doc.goto_line(int(line))
        view.scroll_to_cursor()
        return
    file_uri = Gio.file_new_for_uri(file)
    self.window.create_tab_from_location(file_uri,
                                         Gedit.encoding_get_current(),
                                         int(line), 0, False, True)

class Button(Gtk.Button):
  def __init__(self, var=None):
    Gtk.Button.__init__(self)
    self.var = var

  def get_var(self):
    return self.var

  def set_var(self, var):
    self.var = var
