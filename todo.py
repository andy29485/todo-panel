#!/usr/bin/env python3

from gi.repository import GObject, Gedit

class TodoPanel(GObject.Object, Gedit.WindowActivatable):
  __gtype_name__ = "TodoPanel"
  window = GObject.property(type=Gedit.Window)

  def __init__(self):
    GObject.Object.__init__(self)

  def do_activate(self):
    #TODO

  def do_deactivate(self):
    #TODO

  def do_update_state(self):
    #TODO
