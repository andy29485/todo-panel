#!/usr/bin/env python3

from gi.repository import Gtk, Gio, Gedit
import os

class TodoPanel(Gtk.Notebook):
  def __init__(self, window, matches, keys):
    Gtk.Notebook.__init__(self)
    self.window  = window
    self.matches = matches
    self.pages = []

    for match in keys:
      page = Page(match, matches[match], self.window)
      self.pages.append(page)
      self.append_page(page, page.get_name())

  def update(self):
    self.hide()
    for page in self.pages:
      page.set_match(self.matches[page.get_match()])
      page.update()
    self.show()

class Page(Gtk.ScrolledWindow):
  def __init__(self, name="", match={}, window=None):
    Gtk.ScrolledWindow.__init__(self)
    self.window      = window
    self.file_tables = []
    self.matches     = 0
    self.match       = match
    self.name        = name
    self.label       = Gtk.Label('{}: {}'.format(self.name, self.matches))

  def update(self):
    for table in self.file_tables:
      self.remove(table)
    self.file_tables = []
    self.matches     = 0

    button = Gtk.LinkButton()
    i=0
    for file in self.match.keys():
      table = Gtk.Grid()
      path = file.partition('://')[2]
      name = os.path.basename(path)
      button = Button(self.window, name, path)
      table.attach(button, 0, i, 1, 1)
      for line, comment in self.match[file]:
        i += 1
        button = Button(self.window, comment, path, line)
        table.attach(button, 0, i, 1, 1)
        self.matches += 1
      i += 1
      self.add(table)
      self.file_tables.append(table)
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


class Button(Gtk.Label):
  def __init__(self, window, comment, file=None, line=None):
    Gtk.Label.__init__(self)
    self.window  = window
    self.comment = comment
    self.file    = file
    self.line    = line
    self.update()

  def set_file(self, file):
    self.file = file
    self.update()

  def get_file(self):
    return self.file

  def set_line(self, line):
    self.line = line
    self.update()

  def get_line(self):
    return self.line

  def set_comment(self, comment):
    self.comment = comment
    self.update()

  def get_comment(self):
    return comment

  def update(self):
    html = '<a href="{link}">{text}</a>'
    if self.file:
      if self.line:
        link = 'file://{}#{}'.format(self.file, self.line)
      else:
        link = '?{}'.format(self.file)
      self.set_markup(html.format(link=link, text=self.comment))
    else:
      self.set_text(self.comment)

  def do_activate_link(self, uri):
    if uri.startswith('?'):
      file_uri = 'file://'+uri.partition('?')[2]
      line     = 0
    else:
      file_uri = uri.rpartition('#')[0]
      line     = int(uri.rpartition('#')[2])-1
    for doc in self.window.get_documents():
      if 'file://'+doc.get_uri_for_display() == file_uri:
        tab = Gedit.Tab.get_from_document(doc)
        view = tab.get_view()
        self.window.set_active_tab(tab)
        doc.goto_line(line)
        view.scroll_to_cursor()
        return
    file_uri = Gio.file_new_for_uri(file)
    self.window.create_tab_from_location(file_uri,
                                         Gedit.encoding_get_current(),
                                         line, 0, False, True)
