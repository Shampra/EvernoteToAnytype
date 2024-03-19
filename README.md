# EvernoteToAnytype
Enex to JSON converter, for export Evernote note to Anytype

**Please see it as a work in progress**


### Build
For packaged version :
```
pip install PyInstaller 
pyinstaller main.py --additional-hooks-dir=.
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

**Warning**
It's under progress. 
Particularly, files (including image) are exported from enex but cannot be imported in Anytype actually (see [here](https://github.com/anyproto/anytype-heart/issues/456)).


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.
Some cases may not be covered yet; you can report them to me.



## Progess
**v0.8.3** 
- [ ] **Tag Management** : Create a "Evernote tag" relation, add all your tag, keep them in each note
- [ ] **Reliability and log** 

**Last update : v0.8.4** 
- [ ] **CLI/GUI** : lets you choose CLI or GUI and modify parameters
- [ ] **Reliability and log** 

**Todo**
- [ ] **Files** : Import file **-> Bug in AT, issue reported**
- [ ] **List** case with `<en-todo checked="false" />`
- [ ] **Evernote Tasks** Transform to text with checkbox?
- [ ] **Bug** Table with multiples merged cells (which Anytype doesn't support); it's work if only 1 roswpan / colspan
- [ ] **Bug** Color conversion... AT has limited choice and sometimes "grey" in EN become "green" in AT
- [ ] **Notebook management** Evernote doesn't export notebook name... To be reviewed if the creation of a notebook during conversion is requested...

[See more](./docs/history.md)


