PLUGIN_DIR = "~/.local/share/gedit/plugins"

install:
  @if [ ! -d $(PLUGIN_DIR) ]; then
    mkdir -p "$(PLUGIN_DIR)"
  fi
  @echo installing
  @rm -rf "$(PLUGIN_DIR)/todo"
  @cp -R todo "$(PLUGIN_DIR)"

uninstall:
  @echo uninstalling
  @rm -rf "$(PLUGIN_DIR)/todo"