# EvernoteToAnytype - IN DEVELOPMENT!
Enex to JSON converter, for export Evernote note to Anytype

### Environment
```
pip install beautifulsoup4
pip install lxml
pip install scipy
```

### General Definition
- [x] Creation of the basic JSON model -> Update : as a class
- [x] Generation of ID for blocks
- [x]  Insertion of elements from divs, as a type page, with full width


**Points d'attention :**
Evernote exports are not clean (especially between Legacy and version 10): variations in the method for the same style, unnecessary divs, etc.

### Specific Evernote Blocks and Block Formatting

**List**
- [ ] **Bullet List**
- [ ] **Numbered List**
- [ ] Checklist : Checked and Unchecked


**Alignment**
- [x] Centered and Right


**Titles**
- [x] H1 , H2, H3, Hx (if...)


- [x] Horizontal Separator

**Code Block**
- [ ] Testing AT format 
- [ ] Language selection...
- [ ] Handling line breaks
- [ ] Handling spaces

### Inline Text Formatting
- [x] Handling duplicates
- [x] Italic
- [x] Bold
- [x] Underligne
- [x] Strike


**Indented Text**
**_(creation of child blocks)_**
- [x] via margin-left


**Colors**
- [x] EN to AT color mapping
- [x] color style
- [x] background-color style


### Note Details
**Title**
- [ ] Intégration

**Tag Management**
- [ ] AT testing using specific tags **-> Bug in AT, issue reported**
- [ ] Adding retrieved tags to relation
- [ ] Adding tags to the note

**Creation Date**
- [ ] Format
- [ ] Integration

### Files
- [x] Decoding files from EN
- [X] Association with content
- [x] Define mime, type,...
- [X] Define embed or linked
- [X] Import file **-> Bug in AT, issue reported**


### Table
Coming soon, need to check how it's work

### Generla
- [X] Treat enex folder
- [X] User parameter
- [X] Notebook management

### Autres
- Task integration?
- Embed integration of link -> Non-existent in AT currently
- Adding more properties for file ? (OCR text?)
