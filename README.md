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

### Done
- [x] **Block alignement** : Centered and Right
- [x] **Titles** : H1 , H2, H3, Hx (if...)
- [x] Horizontal Separator and empty line
- [x] **Inline Text Formatting** : Handling duplicates; Italic, Bold, Underline, Strike
- [x] **List** (with ul/ol) : Bullet, Numbered, Checklist (Checked and Unchecked)
- [x] **Indented Text** via margin-left and in subList
- [x] **Colors** EN to AT color mapping; color style and background-color style

- [x] **Détails** Title intégration

- [x] **Files** : Decoding files from EN, association with content, define mime/type/..., define embed or linked

- [X] **use** Treat enex folder

### TODO
- [ ] **Files** : Import file **-> Bug in AT, issue reported**
- [ ] **Tag Management** AT testing using specific tags **-> Bug in AT, issue reported**

- [ ] **List** case with `<en-todo checked="false" />`
- [ ] **Détails** Creation date (format and integration)

- [ ] **BUG? Link doesn't work anymore!**


**Code Block**
- [ ] Testing AT format 
- [ ] Language selection...
- [ ] Handling line breaks
- [ ] Handling spaces

**Tables**
Coming soon, need to check how it's work

- [ ] **use** User parameter, Notebook management


### Other
- Task integration?
- Embed integration of link -> Non-existent in AT currently
- Adding more properties for file ? (OCR text?)
