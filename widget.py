#!/usr/bin/env python3

from gi.repository import Gtk, Gio
import os

template_head='<a href="#{text}"><th>{text}: {num}</th></a>'
template_body='<a href="{file}#{line}"><td>{line}</td><td>{text}</td></tr></a>'

class TodoPanel(Gtk.Label):
  def __init__(self, window, matches):
    Gtk.Label.__init__(self)
    self.window  = window
    self.matches = matches
    self.page    = list(matches.keys())[0]

  def update(self):
    head = '<table width=100%><tr>'
    body = ''
    for tag in self.matches.keys():
      count = 0
      if tag = self.page:
        body += '<table>'
        for file in matches[tag].keys():
          body += '<a href="?{path}"><tr><td colspan="2">{name}</td></tr></a>'
          path=file.partition('://')[2]
          body = body.format(path=path, name=os.path.basename(path))
          for line, comment in matches[tag][file]:
            body += template_body.format(file=file, line=line, text=comment)
            count += 1
        body += '</table>'
      else:
        for file in matches[tag].keys():
          count += len(matches[tag][file])
      head += template_head.format(text=tag, num=count)
    head += '</tr></table>'
    self.set_markup(head+body)

  def on_activate_link(page, uri, data):
    if uri.startswith('#'):
      self.page = uri.partition('#')[2]
      self.update()
      return
    elif uri.startswith('?'):
      file_uri = 'file://'+uri.partition('?')[2]
      line     = 1
    else:
      file_uri = uri.rpartition('#')[0]
      line     = int(uri.rpartition('#')[2])
    for doc in self.window.get_documents():
      doc_uri = 'file://%s' % doc.get_uri_for_display()
      if 'file://"'+doc.get_uri_for_display() == file_uri:
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
