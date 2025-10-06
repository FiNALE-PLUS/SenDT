# SenDT
SenDT is a toolkit for Maimai FiNALE including a CLI and GUI for various functions to simplify adding content to the game. 
SenDT is comprised of two components:
- A CLI for converting simai files to SDT [where compatible](#whats-a-compatible-simai-file)
- A GUI that incorporates wider functionality useful to modders

SenDT CLI (AKA [senDT.py](senDT.py))
---
SenDT's CLI has one purpose, which is to convert a simai file to valid SDT that can be used by Maimai FiNALE. 
SenDT *does not* provide conversion to earlier versions of the format (AKA `SRT`, `SCT` and `SZT`).

SenDT's default behaviour when finding features that aren't compatible with classic charts 
is to omit them from the output and warn you of the omission in the console. 
This is most notable for Festival slides, which *will not* be output 
and require a user to explicitly chart the segments in a compatible manner to be converted.
There are also valid features that omit warnings such as 0 length holds 
to ensure the creator is aware of their existence in case its inclusion was accidental.

SenDT can handle Simai files with multiple BPM markers, and will ask the user to select the correct BPM of the ones found. 
SenDT will automatically use that BPM to time all other notes, adjusting as necessary.

For more usage information, consult the help text within the CLI.

### What's a 'compatible' simai file?
SenDT is primarily aimed at using [sentakki](https://github.com/LumpBloom7/sentakki)'s simai output as its source for conversion. 
As such, conversion has been majorly tested against its output. If you have created a simai file that 
does not output a valid SDT file ***and does not use any non-classic chart feature***, 
please open an issue and I'll try to fix it as soon as possible.

---

### CLI TODO list

- [ ] Clean up the spaghetti code

---

## SenDT GUI (AKA [senDToolkitUI.py](senDToolkitUI.py))
---
SenDT's GUI is intended to serve as a toolkit for users to allow them to easily add extra content to the game as they wish.
This includes providing a UI to add to the tables required to add content, abstracting requirements of the asset file formats 
and automating addition of the files to a target destination. By default, the GUI will back up all relevant files to its own subdirectory before exporting.
If existing tables are to be used as a base for the DB to then add to, [build_db.py](tableUI/build_db.py) is available to extract the relavent data.

---

### GUI TODO list

- [x] Table parsing/export
  - [x] DB representation for internal editing
- [x] Cover art (jacket) conversion to DDS (thanks [Pillow](https://github.com/python-pillow/Pillow))
  - [x] Generate all necessary versions in correct formats to be read correctly
- [x] Convert input background videos to WMV for use in-game (thanks [FFmpeg](https://github.com/FFmpeg/FFmpeg))
  - [ ] Add to UI with cover art selection
- [ ] Look further into XACT
- [ ] Add settings for simple configuration
- [ ] `SoundBGM.txt`
- [ ] Refactor to reduce coupling between CLI and GUI

---