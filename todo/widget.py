#!/usr/bin/env python3

from gi.repository import Gtk, Gio, Gedit
import os

class TodoPanel(Gtk.Notebook):
  def __init__(self, window, matches, keys, settings):
    Gtk.Notebook.__init__(self)
    self.window  = window
    self.matches = matches
    self.pages = []

    for match in keys:
      page = Page(match, matches[match], self.window, settings)
      self.pages.append(page)
      self.append_page(page, page.get_name())

  def update(self):
    self.hide()
    for page in self.pages:
      page.set_match(self.matches[page.get_match()])
      page.update()
    self.show()

class Page(Gtk.ScrolledWindow):
  def __init__(self, name, match, window, settings):
    Gtk.ScrolledWindow.__init__(self)
    self.window   = window
    self.buttons  = []
    self.matches  = 0
    self.match    = match
    self.name     = name
    self.grid     = Gtk.Grid()
    self.label    = Gtk.Label('{}: {}'.format(self.name, self.matches))
    self.settings = settings
    self.grid.set_row_spacing(self.settings['spacing'])
    self.add(self.grid)

  def update(self):#TODO
    if self.grid.get_child_at(0,0):
      self.grid.remove_column(0)
    for button in self.buttons:
      del button
    self.buttons = []
    self.matches = 0

    i=-1
    for j in range(len(list(self.match.keys()))):
      file = list(self.match.keys())[j]
      i += 1
      if j != 0:
        self.grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
                        0, i, 1, 1)
        i += 1
      path = file.partition('://')[2]
      name = os.path.basename(path)
      button = Button(self.window, self.settings, name, file)
      self.grid.attach(button, 0, i, 1, 1)
      self.buttons.append(button)
      for line, comment in self.match[file]:
        i += 1
        button = Button(self.window, self.settings, comment, file, line)
        self.grid.attach(button, 0, i, 1, 1)
        self.buttons.append(button)
        self.matches += 1
    self.label.set_text('{}: {}'.format(self.name, self.matches))
    self.show_all()

  def get_name(self):
    self.label.set_text('{}: {}'.format(self.name, self.matches))
    return self.label

  def set_name(self, name):
    self.name = name

  def set_match(self, match):
    self.match = match

  def get_match(self):
    return self.name

class Button(Gtk.EventBox):
  def __init__(self, window, settings, comment, file=None, line=None):
    Gtk.EventBox.__init__(self)
    self.window   = window
    self.file     = file
    self.line     = line
    self.label    = Gtk.Label()
    self.settings = settings
    self.label.set_justify(Gtk.Justification.LEFT)
    self.label.set_ellipsize(True)
    self.label.set_alignment(xalign=0, yalign=0.5)
    if self.line:
      if comment:
        self.label.set_text('<span font="{} {}">{:10}: {}</span>'.format(
          self.settings['font'], self.settings['size'], self.line, comment))
      else:
        self.label.set_markup('<span font="{} {}">{:10}:<u>{}</u><span>'.format(
          self.settings['font'], self.settings['size'], self.line, ' EMPTY'))
      self.line -= 1
    else:
      if comment:
        self.label.set_text(comment)
      else:
        self.label.set_markup('<u>EMPTY</u>')
      self.line = 0
    self.add(self.label)
    self.connect('button_press_event', self.click)

  def click(self, eventbox, event):
    for doc in self.window.get_documents():
      if 'file://'+doc.get_uri_for_display() == self.file:
        tab = Gedit.Tab.get_from_document(doc)
        view = tab.get_view()
        self.window.set_active_tab(tab)
        doc.goto_line(self.line)
        view.scroll_to_cursor()
        return
    file_uri = Gio.file_new_for_uri(self.file)
    self.window.create_tab_from_location(file_uri,
                                         Gedit.encoding_get_current(),
                                         self.line, 0, False, True)
