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
- Export your Evernote Notes (actually, this tools doesn't support notebook export)
- Launch the gui with "main" file
- drop your enex fils to convert (or a folder with them inside) or select them with the button
- clic to Convert

A _Converted_files_  is created in the folder of your enex files, containing the converted files. Import them into Anytype.

**Warning**
It's under progress. 
Particularly, files (including image) are exported from enex but cannot be imported in Anytype actually (see [here](https://github.com/anyproto/anytype-heart/issues/456)).


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.
Some cases may not be covered yet; you can report them to me.



## Progess
**Last update : v0.7** 
- [x]Import enex with multiples notes
- [x]Import Creation date
- [x]Import table (with all what Anytype Table can support)

**Todo**
- [ ] **Files** : Import file **-> Bug in AT, issue reported**
- [ ] **Tag Management** AT testing using specific tags **-> Bug in AT, issue reported**
- [ ] **List** case with `<en-todo checked="false" />`
- [ ] **Usage** User parameter, Notebook management, zip when convert multiples notes

[See more](./docs/history.md)


