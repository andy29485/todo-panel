# TODO panel
Gedit3 plugin that lists all TODO comments and their messages in the side or
bottom panel
Idea for plugin was taken from [this] (https://github.com/iromli/gedit-todo)
obsolete plugin.

## Authors/Contributors
- Andriy Zasypkin

## Notes
This *should* work, but either I or the GEdit API have some errors. The widget
window gets added to the bottom panel, and activated. The tab for this widget
appears in the bottom panel, however no content is shown.
  - It should be mentioned that a Gtk.Label does appear, if set as the widget.
  - A Gtk.Notebook(as demonstrated [here]
  (http://python-gtk-3-tutorial.readthedocs.org/en/latest/layout.html#notebook))
  does not appear when set(and activated) as the widget

## TODO
###### Allow for configuration
- switch between the bottom and side panels
- add(and choose) colour for tabs
- add custom tabs
- add extensions to whitelist
