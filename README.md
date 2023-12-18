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
- Launch the gui with "main" file
- drop your enex file to convert (or a folder with them inside) or select them with the button
- clic to Convert

A _Converted_files zip  is created in the folder of your enex files, containing the converted files. Import them into Anytype.

**Warning**
It's under progress. 
Particularly, files (including image) are exported from enex but cannot be imported in Anytype actually (see [here](https://github.com/anyproto/anytype-heart/issues/456)).


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.
Some cases may not be covered yet; you can report them to me.



## Progess
**Last update : v0.8.3** 
- [ ] **Tag Management** : Create a "Evernote tag" relation, add all your tag, keep them in each note
- [ ] **Reliability and log** 

**Todo**
- [ ] **Files** : Import file **-> Bug in AT, issue reported**
- [ ] **List** case with `<en-todo checked="false" />`
- [ ] **Bug** Table with multiples merged cells (which Anytype doesn't support); it's work if only 1 roswpan / colspan
- [ ] **Bug** Color conversion... AT has limited choice and sometimes "grey" in EN become "green" in AT
- [ ] **Notebook management** Evernote doesn't export notebook name... To be reviewed if the creation of a notebook during conversion is requested...

[See more](./docs/history.md)


