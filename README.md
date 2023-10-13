# EvernoteToAnytype - IN DEVELOPMENT!
Enex to JSON converter, for export Evernote note to Anytype



### Environment
```
pip install beautifulsoup4
pip install lxml
pip install scipy
```

For packaged version :
```
pip install PyInstaller 
pyinstaller main.py --additional-hooks-dir=.
```


## Usage
- Launch the gui with "main" file
- drop your enex fils to convert (or a folder with them inside) or select them with the button
- clic to Convert
A _Converted_files_  is created in the folder of your enex files, containing the converted files.

**Warning**
It's under progress. 
Particularly, files (including image) are exported from enex but cannot be imported in Anytype actually (see [here](https://github.com/anyproto/anytype-heart/issues/456)).


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.



## Progess
- [ ] **Files** : Import file **-> Bug in AT, issue reported**
- [ ] **Tag Management** AT testing using specific tags **-> Bug in AT, issue reported**
- [ ] **List** case with `<en-todo checked="false" />`
- [ ] **Détails** Creation date (format and integration)
- [ ] **Usage** User parameter, Notebook management
- [ ] **Tables** Coming soon, need to check how it's work



