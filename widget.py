#!/usr/bin/env python3

from gi.repository import Gtk, Gio, WebKit
import os

template_head='<a href="#{text}"><th>{text}: {num}</th></a>'
template_body='<a href="{file}#{line}"><td>{line}</td><td>{text}</td></tr></a>'

class TodoPanel(WebKit.WebView):
  def __init__(self, window, matches, key='TODO'):
    WebKit.WebView.__init__(self)
    self.window  = window
    self.matches = matches
    self.page    = key

  def update(self):
    head = '<table width=100%><tr>'
    body = ''
    for tag in self.matches.keys():
      count = 0
      if tag == self.page:
        body += '<table>'
        for file in self.matches[tag].keys():
          body += '<a href="?{path}"><tr><td colspan="2">{name}</td></tr></a>'
          path=file.partition('://')[2]
          body = body.format(path=path, name=os.path.basename(path))
          for line, comment in self.matches[tag][file]:
            body += template_body.format(file=file, line=line, text=comment)
            count += 1
        body += '</table>'
      else:
        for file in self.matches[tag].keys():
          count += len(self.matches[tag][file])
      head += template_head.format(text=tag, num=count)
    head += '</tr></table>'
    self.load_string('<html><body>'+head+body+'</html></body>',
                     'text/html', 'utf-8', 'file://')

  def on_navigation_request(self, page, frame, request):
    if request.get_uri().startswith('#'):
      self.page = request.get_uri().partition('#')[2]
      self.update()
      return
    elif request.get_uri().startswith('?'):
      file_uri = 'file://'+request.get_uri().partition('?')[2]
      line     = 0
    else:
      file_uri = request.get_uri().rpartition('#')[0]
      line     = int(request.get_uri().rpartition('#')[2])-1
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
