# EvernoteToAnytype - IN DEVELOPMENT!
Enex to JSON converter, for export Evernote to Anytype

### Environnement 
```
pip install beautifulsoup4
pip install lxml
```

### Définition générale
- [x] Création du modèle json de base
- [x] Génération d'ID par div
- [x] Insertion des éléments des div
- [x] Pleine page _(validé, à intégrer au modèle)_


**Points d'attention :**
Evernote exporte la même note de différentes façon si le texte (font) a été modifié, si la version est différente (legacy vs modern)...
- Imbrication de div (sans réalité dans la note)
- utilisation de style sur span ou de balise i,u,s,...

### Blocs (EN) spécifiques et mise en forme du bloc

- [ ] **Liste à puce**
- [ ] **Liste numérotée**

**Liste case à cocher**
- [ ] cochée
- [ ] décochée

**Alignement**
- [x] centré
- [x] à droite

**Titres**
- [x] H1
- [x] H2
- [x] H3

- [x] Séparateur hr

**Bloc de code**
- [ ] Test format AT
- [ ] Choix langage...
- [ ] Gestion sauts de lignes
- [ ] Gestion espaces

### Mise en forme du texte inline
- [x] Gestion doublons

**Texte en italique**
- [x] via i
- [x] via <span> style

**Texte en gras**
- [x] via b
- [x] via <span> style

**Texte souligné**
- [x] via i
- [x] via <span> style

**Texte décalé**
**_(création de blocs enfant)_**
- [x] via margin-left


**Texte en couleur**
- [x] mappage des couleurs EN > AT
- [x] style color

**Texte surligné**
- [x] mappage des couleurs EN > AT
- [x] style background-color

### Détails de la note
**Titre**
- [ ] Intégration

**Gestion tag**
- [ ] test via tag spécifique -> **NOK dans AT, bur remonté**
- [ ] Ajout des tags récupéré à la relation
- [ ] Ajout des tags à la note

**Date création**
- [ ] Format
- [ ] Intégration

### Fichiers
- [x] Décodage
- [ ] Association au contenu
- [x] Définition mime et type
- [ ] Définition taille (image seulement pour AT)
- [ ] Amélioration : ajout de propriétés? (texte OCR?)

### Tableau
A venir

### Autres
Intégration de tâches?
Intégration des embed -> Inexistant dans AT actuellement
