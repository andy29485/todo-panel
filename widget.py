#!/usr/bin/env python3

from gi.repository import Gtk
import os, re

class TodoPlugin(Gtk.Window):
  def __init__(self, window, matches):
    Gtk.Window.__init__(self)
    self.window  = window
    self.matches = matches
    self.buttons = []

    self.box = Gtk.Box()
    self.add(self.box)

    for i in matches.keys():
      button = Gtk.Button(label='{} {}'.format(i, len(matches[i])))
      button.connect("clicked", self.on_button_clicked)
      self.buttons.append(button)
      self.box.pack_start(self.button, True, True, 0)

  def update(self):
    for button in self.buttons:
      key = re.sub('\\s+\\d+$', '', button.get_label())
      button.set_label('{} {}'.format(key, len(self.matches[key])))

  def on_button_clicked(self, button):
    #this is the match key to use
    key = re.sub('\\s+\\d+$', '', button.get_label())
