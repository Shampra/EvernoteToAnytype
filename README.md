# EvernoteToAnytype
Enex to JSON converter, for export Evernote note to Anytype

**Please see it as a work in progress**


### Build
For packaged version :
```
pip install -r requirements.txt
pip install PyInstaller 
pyinstaller run.py --additional-hooks-dir=.  --add-data "models:models" --add-data "image.ico:."
```


## Usage
- Export your Evernote Notes (notes or a full notebook)
- Launch run.exe (if you use the release) or run.py (with python files from Github)
    - with some parameter to execute with CLI (command line)
    - directly to open the GUI (graphic interface) 

- **With GUI**
    - drop your enex file(s) to convert (or a folder with them inside) or select them with the button
    - clic to Convert

- **With CLI**, you must provide parameters
    - "--enex_sources", mandatory : one or more folder/file
    - "--debug", optional : enables creation of a debug file
    - "--nozip", optional : deactivates the creation of a zip file with the result, so you'll have a directory with all the json files

A _Converted_files zip is created in the folder of your enex files, containing the converted files. Import them into Anytype.

## Limitations
This tool is usable!
But beware of its limitations...

**Not (yet) managed by the converter:** 
- note decryption: you can decrypt notes before export. This should be integrated later
- complete web pages retrieved via the webclipper: this is functional, but there will always be some cases that won't work as well. In any case, Anytype remains limited: it's impossible to faithfully reproduce all web pages.
- tasks, for now

**Anytype limitations :** 
- Tables
    - No merged cells: the converter "unmerges" them and copies the content into each cell.
    - no block elements (checkbox, image, title, etc.):
        - when there's a single image or checkbox, the tool lets you import them (but you won't be able to edit them in Anytype unless you delete it)
        - when there are several checkboxes or lists, they are transformed into text ("[ ]", "[X]", "-")
        - when there are several images, only the first is kept
- Colors: colors are converted to the limited anytype list, trying to take the closest color...
- Some images are currently buggy
- SVGs are not supported (integration of a converter planned for the tool)
- no embedding for txt files, Google drive, etc.

**Evernote limitations :** 
- notebook names are not exported

**Other limitations:**
- Beware of exporting large enex files: they must be loaded into memory to be processed, so you may be limited to batch exporting.
- internal Evernote links are not transposable, so cannot be converted


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.
Some cases may not be covered yet; you can report them to me.



## Progess
**v0.8.5** 
- [ ] **CLI/GUI** : lets you choose CLI or GUI and modify parameters
- [ ] **Reliability and log** 

**v0.8.7** 
- [ ] **Image** : for image as embed weblink, the converter download them (AT doesn't support embeb image from an url)


**Last update : v0.8.8** 
- [ ] **Table converter V2** : Better converter with improved handling of twisted cell merges, and improved cell content conversion (non-Anytype compatible content).
- [ ] **More html case** 

[See more](./docs/history.md)


