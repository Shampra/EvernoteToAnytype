
![v2](https://github.com/Shampra/EvernoteToAnytype/assets/16141040/1f5da137-9d4e-41a0-a916-47b920f2100e)

# EvernoteToAnytype
Enex to JSON converter, for export Evernote note to Anytype

### Mac users
Please check this post to use this tool on Mac, big thanks to solomonikvik :  
https://community.anytype.io/t/a-tool-to-import-evernote-notes-to-anytype/11483/52

### Build
_You can use the supplied release directly in a zip file [here](https://github.com/Shampra/EvernoteToAnytype/releases/latest) (for Windows).   
If you prefer to use the source code, here are the instructions._

Prerequisites : Python 3.10+ installed.  
Creating a virtual environment is recommended.

1. Clone Repository or retrieve the code
2. Install all the required Python packages
```
pip install -r requirements.txt
```

3. **CairoSVG requires the native Cairo library.**  
You must have the file libcairo-2.dll in project directory, system PATH or script directory in your python install (or .venv).   
You can install it, for example, via this runtime :   
https://github.com/tschoonj/GTK-for-Windows-runtime-environment-installer

The python tool is now ready for use.

4. For packaged version, install and run PyInstaller :
```
pip install PyInstaller 
pyinstaller run.py --additional-hooks-dir=.  --add-data "libs:libs" --add-data "image.ico:." --icon=image.ico
```

## Usage
- Export your Evernote Notes (notes or a full notebook)
- Launch run.exe (if you use the release) or run.py (with python files from Github)
    - with some parameter to execute with CLI (command line)
    - directly to open the GUI (graphic interface) 

- **With GUI**,  drop your enex file(s) to convert (or a folder with them inside) or select them with the button and click to **Convert**
    - clic to Convert

- **With CLI**, you must provide parameters at least**"--enex_sources"** with one or more folder/file

**GUI and CLI provides options.**
you can use them with options to be set on the interface or via these command-line parameters :
- **--enex_sources**, mandatory : add folders or enex files to convert
- **--debug**, optional : enables creation of a debug file
*By default*, no debug files are created
- **--nozip**, optional : deactivates the creation of a zip file with the result, so you'll have a directory with all the json files
*By default*, it create a zip
- **--pwd PASSWORD**, optional : set a global password for your encrypted notes.
It will be used to decipher encrypted notes. If it is not correct, the note will not be decrypted (if the ask_pwd option is enabled, you will be asked for another password).
- **--ask_pwd**, optional : for each encrypted notes, a password will be requested (in CLI or GUI depending on your use). 
If a global password is also defined, it will be used first.
If the password entered is incorrect, the note will not be decrypted.
*By default*, no password is requested and no note is decrypted.

Other parameters are used for development testing only.

A _Converted_files zip (or folder if zip desactivated) is created in the same folder of your enex files, containing the converted files.  
Import them into Anytype : File > Import > Any-Block > select your converted file.

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
- SVGs are not supported, this converter convert SVG to PNG
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
- [x] **Rebuild png image**  : Anytype doesn't support PNG if there are errors (CRC, ...) and it's common in Evernote, so the converter rebuilds them!
- [x] **Convert SVG to PNG** : Anytype doesn't support SVG, so the converter convert them to PNG. **Mind you**, it takes a few seconds per image and the result isn't always perfect, but it's better than losing them... 

[See more](./docs/history.md)

## Support
<a href='https://ko-fi.com/V7V716SJ8Z' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi5.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>




