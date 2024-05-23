# EvernoteToAnytype
Enex to JSON converter, for export Evernote note to Anytype

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
But beware of the limitations of each tool...

**Converter limitations:** 
- Evernote tasks (and no Anytype equivalent, so nothing planned)
- Beware of exporting large enex files: they must be loaded into memory to be processed, so you may be limited to batch exporting.
- internal Evernote links are not transposable, so cannot be converted

**Anytype limitations :** 
- Tables
    - No merged cells: the converter "unmerges" them and copies the content into each cell.
    - no block elements (checkbox, image, title, etc.):
        - when there's a single image or checkbox, the tool lets you import them (but you won't be able to edit them in Anytype unless you delete it)
        - when there are several checkboxes or lists, they are transformed into text ("[ ]", "[X]", "-")
        - when there are several images, **only the first is kept**
- Colors: colors are converted to the limited anytype list, trying to take the closest color...
- Some images are currently buggy
- SVGs are not supported (integration of a converter planned for the tool)
- no embedding for txt files, Google drive, etc.

**Evernote limitations :** 
- notebook names are not exported
- no notebook stack export, so you have to export them one by one and recreate the tree structure once imported into Anytype ([an how-to here](https://community.anytype.io/t/recreate-your-evernote-environment-in-anytype/21206))


**Points to consider :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.
Some cases may not be covered yet; you can report them to me.


## Progess
**Last update : v.1.0** 
- [x] **Bloc tree** : Better management of offsets (lists, nested blocks)
- [x] **More strange case**  : Some corrections (incorrect Evernote xhtml processing)
- [x] **Encrypted notes**  : Decryption with various options




[See more](./docs/history.md)


