#!/usr/bin/env python3

from gi.repository import Gtk, Gio
import os, re
from operator import itemgetter

class TodoPanel(Gtk.Notebook):
  def __init__(self, window, matches):
    Gtk.Notebook.__init__(self)
    self.window  = window
    self.matches = matches
    self.pages = []

    #TODO - put pages in notebook
    for match in matches.keys():
      page = Page(match, matches[match])
      self.pages.append(page)
      self.append_page(page, page.get_name())

  def update(self):
    for page in self.pages:
      page.update()

  def set_type(self, key):
    for button in self.buttons2:
      self.buttons2.remove(button)
      self.box.remove(button)
      del button

    for comment in list(sorted(self.matches[key])):
      b = Button()
      if i[2]:
        b.set_label('{} {}: {}'.format(i[0].rpartition('/')[2], i[1], i[2]))
      else:
        b.set_label('{} {}'.format(i[0].rpartition('/')[2], i[1]))
      b.connect("clicked", self.on_button2_clicked)
      self.buttons2.append(b)
      self.box.pack_start(b, True, True, 0)

    self.key_type = key

  def on_button_clicked(self, button):
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

class Page(Gtk.ScrolledWindow):
  def __init__(self, name="", match={}):
    Gtk.ScrolledWindow.__init__(self)
    self.name    = Gtk.Label(name)
    self.match   = match
    self.html = '<a href="{0}#{1}"><tr><td>{1}</td><td>{2}</td></tr></a>'
    self.file_label = Gtk.Label()
    self.file_label.set_width_chars(-1)
    self.file_label.set_ellipsize(True)
    self.add(self.file_label)
    self.update()

  def update(self):
    label_html = ''
    for file_uri in sorted(self.match.keys()):
      label_html += '<b>{}</b><table>'.format(self.name.rpartition('/')[2])
      for line, text in sorted(elf.match[file_uri]):
        label_html += self.html.format(file_uri, line, text)
      label_html += '</table>'
    self.file_label.set_lines(len(label_html.split('<tr>')))
    self.file_label.set_markup(label_html)

  def get_name(self):
    return self.name

  def set_name(self, name):
    self.name = Gtk.Label(name)

  def set_match(self, match):
    self.match = match

  def on_activate_link(label, uri, data):
    pass
    #TODO
