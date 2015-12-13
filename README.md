# TODO panel v1.2.2
Gedit3 plugin that lists all TODO comments and their messages in the side or
bottom panel
Idea for plugin was taken from [this] (https://github.com/iromli/gedit-todo)
obsolete plugin.

## Authors/Contributors
- Andriy Zasypkin

## Instructions
1. Enable plugin
2. Open files
3. Look at panel
4. Click on the item that you want to go to

This plugin automatically scans all the directories of the open files
for files that have allowed extensions. Then looks for defined keywords,
such as TODO and FIXME(must be all caps), and creates links to those
files/lines.

## Screen shots
![Image of panal](/screenshots/1.png?raw=true "1")

## TODO

##### Improve efficiency
- [x] save list of last scanned dirs/files
- [x] less pointless scanning
- [x] remove things that are closed
  - [ ] ~~save list of old dirs~~

##### Make it look nice
- [x] hover
- [ ] colours
  - [ ] hover colours
  - [ ] tab colours
- [x] sizes
- [x] spacing
- [ ] stay on panel after update

##### Allow for configuration
- [ ] use an xml file
- [ ] switch between the bottom and side panels
- [ ] add(and choose) colour for tabs
- [ ] add custom tabs
- [ ] add extensions to whitelist
