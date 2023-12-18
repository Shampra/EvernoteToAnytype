
class Page:
    """JSON model for a "Page" object in Anytype
    """

    def __init__(self):
        self.page_json = {
            "sbType": "Page",
            "snapshot": {
                "data": {
                    "blocks": [],
                    "details": {
                        "featuredRelations": [
                            "202312evernotetags"
                        ],
                        "layout": 0,
                        "name": "Default name",
                        "type": "ot-page"
                    },
                    "objectTypes": ["ot-page"],
                    "relationLinks": [
                        {
                        "key": "202312evernotetags",
                        "format": "tag"
                        }
                    ]
                }
            }
        }

    def find_block_by_id(self, block_id):
        """
        Recherche un bloc par son ID.

        Args:
            block_id (str): ID du bloc à rechercher.

        Returns:
            dict or None: Le bloc trouvé ou None s'il n'est pas trouvé.
        """
        return next((b for b in self.page_json["snapshot"]["data"]["blocks"] if b["id"] == block_id), None)

    def find_parent_id(self, shifting_left):
        """
        Trouve le bloc précédent avec une valeur de style margin-left inférieure.

        Args:
            shifting_left (int): La valeur de shifting de l'élément actuel.

        Returns:
            dict or None: Le bloc précédent s'il existe, sinon None.
        """
        for block in self.page_json["snapshot"]["data"]["blocks"][::-1]:
            prev_shifting = block.get("shifting")
            if prev_shifting is not None and shifting_left is not None and shifting_left > prev_shifting:
                return block["id"]
        return None

    def get_creation_date(self):
        creation_date = self.page_json["snapshot"]["data"]["details"]["createdDate"]
        if creation_date is not None:
            return creation_date
        else:
            return "0"
        pass

    def add_children_id(self, parent_id, div_id):
        """
        Ajoute l'id de la div dans la liste "childrenIds" du parent.

        Args:
            parent_id (str): L'ID du block parent.
            div_id (str): L'ID du block enfant
        """
        parent_block = self.find_block_by_id(parent_id)
        if parent_block:
            children_ids = parent_block.setdefault("childrenIds", [])
            if div_id not in children_ids:
                children_ids.append(div_id)
        else:
            print(
                f"Erreur, block {parent_id} inexistant lors de l'ajout d'enfant {div_id}")

    def add_block(self, block_id, shifting=None, width=None, align=None, text=None):
        """Création d'un blocs avec gestion parent/enfant ou 1er bloc

        Args:
            block_id (_type_): id du block
            shifting (_type_, optional): Value of shifting used to link parents/childrens. None if no parent/children needed (Default value).
            width (_type_, optional): _description_. Defaults to None.
            align (_type_, optional): _description_. Defaults to None.
            text (_type_, optional): _description_. Defaults to None.
        """

        block = {
            "id": block_id,
        }

        # C'est le premier bloc, on l'init de façon spécifique
        if not self.page_json["snapshot"]["data"]["blocks"]:
            block["fields"] = {
                "width": 1
            }
            block["shifting"] = -1
        # pour les autres blocs, il faut trouver le parent et y ajouter l'enfant (sauf si shifting=None, bloc géré différemment)
        elif shifting is not None:
            parent_id = self.find_parent_id(shifting)
            if parent_id:
                self.add_children_id(parent_id, block_id)
            else:
                print("erreur pas de parent")

        if shifting is not None:
            block["shifting"] = shifting
        if width is not None:
            block["fields"] = {"width": width}
        if align is not None:
            block["align"] = align
        if text is not None:
            block["text"] = {"text": text, "marks": {}}
        self.page_json["snapshot"]["data"]["blocks"].append(block)

    def edit_details_key(self, key, value):
        """Ajoute une clé ou modifie sa valeur dans les détails"""
        self.page_json["snapshot"]["data"]["details"][key] = value
        pass

    def edit_block_key(self, block_id, key, value, master_key=None):
        """Ajoute une clé ou modifie sa valeur dans le bloc ciblé

        Args:
            block_id (_type_): id du bloc à modifier
            key (_type_): clé
            value (_type_): valeur
            master_key(string) : optionnal, used if key is under another key like fields
        """
        block = self.find_block_by_id(block_id)
        if block:
            if master_key is not None:
                block[master_key] = {key: value}
            else:
                block[key] = value
                # Modification du shifting, on traite
                # TODO : attention, si c'est modification il faudrait aussi retirer l'id de l'ancien parent!
                if "shifting" in key:
                    # Trouve l'id précédent

                    # Puis trouver le nouveau parent
                    parent_id = self.find_parent_id(value)
                    if parent_id:
                        self.add_children_id(parent_id, block_id)
                    else:
                        print("erreur pas de parent")
            return

    def edit_text_key(self, block_id, key, value):
        """Ajoute une clé ou modifie sa valeur dans la clé "text" du bloc ciblé

        Args:
            block_id (_type_): id du bloc à modifier
            key (_type_): clé
            value (_type_): valeur
        """
        block = self.find_block_by_id(block_id)
        if block:
            if "text" in block:
                block["text"][key] = value
                return
            else:
                print("Clé text manquante, elle doit être créé avant de la modifier!")
        else:
            print(
                f"Erreur, block {block_id} inexistant lors de l'ajout de texte")

    def add_text_to_block(self, block_id, text=None, block_style=None, div=None):
        """Ajout d'une clé text au bon format

        Args:
            block_id (_type_): _description_
            text (string, optional): _description_
            block_style (string, optional): Style for text block : Checkbox, Marked, ...
                For inline style, use add_mark_to_text! 
        """
        block = self.find_block_by_id(block_id)
        if block:
            # Si div en param, on ajouté (pour le cas hr)
            if div is not None:
                block["div"] = {}
            else:
                if "text" not in block:
                    block["text"] = {}
                if text is not None:
                    block["text"]["text"] = text
                if "marks" not in block["text"]:
                    block["text"]["marks"] = {}
                if text is not None:
                    block["text"]["text"] = text
                if block_style is not None:
                    block["text"]["marks"]["type"] = block_style
        else:
            print(
                f"Erreur, block {block_id} inexistant lors de l'ajout de texte")

    def add_mark_to_text(self, block_id, start, end, mark_type=None, mark_param=None):
        block = self.find_block_by_id(block_id)
        if block and "text" in block:
            if "marks" not in block["text"]["marks"]:
                block["text"]["marks"] = {"marks": []}
            mark = {"range": {"from": start, "to": end}}
            if mark_type is not None:
                mark["type"] = mark_type
            if mark_param is not None:
                mark["param"] = mark_param
            block["text"]["marks"]["marks"].append(mark)
        else:
            print(
                f"Erreur, block {block_id} inexistant lors de l'ajout de mark")

    def add_file_to_block(self, block_id, hash, name, file_type, mime, size, embed_size=None, format=None):
        block = self.find_block_by_id(block_id)
        if block:
            block["file"] = {}
            block["file"]["hash"] = hash
            block["file"]["name"] = name
            block["file"]["type"] = file_type
            block["file"]["mime"] = mime
            # block["file"]["size"] = size
            if embed_size is not None:
                # TODO
                pass
            if format == "link":
                block["file"]["style"] = "Link"
            # Les images ont toujours un style défini
            elif file_type == "Image":
                block["file"]["style"] = "Embed"
            block["file"]["state"] = "Done"
            pass
        else:
            print(
                f"Erreur, block {block_id} inexistant lors de l'ajout de fichier")

    def cleanup(self):
        # Supprimer toutes les clés "shifting" de chaque bloc à la fin
        for block in self.page_json["snapshot"]["data"]["blocks"]:
            if "shifting" in block:
                del block["shifting"]

    def to_json(self):
        return self.page_json


class Tag_Option:
    """JSON model for a "tag option" object in Anytype"""

    def __init__(self):
        self.page_json = {
            "sbType": "STRelationOption",
            "snapshot": {
                "data": {
                    "details": {
                        "layout": 13,
                        "name": "DEFAULT",
                        "relationKey": "202312evernotetags",
                        "relationOptionColor": "grey",
                        "uniqueKey": ""
                    },
                    "objectTypes": [
                        "ot-relationOption"
                    ],
                    "key": ""
                }
            }
        }

    def edit_name(self, value):
        """Ajoute une clé ou modifie sa valeur dans les détails"""
        self.page_json["snapshot"]["data"]["details"]["name"] = value
        pass
    
    def edit_id(self, value):
        """Ajoute ou modifie l'id"""
        self.page_json["snapshot"]["data"]["details"]["id"] = value
        pass
    
    def edit_key(self, value):
        """Ajoute ou modifie la valeur pour key et uniqueKey"""
        self.page_json["snapshot"]["data"]["key"] = value
        self.page_json["snapshot"]["data"]["details"]["uniqueKey"] = "opt-" + value
        pass
    
    def edit_color(self, value):
        """Ajoute ou modifie la valeur de la couleur"""
        self.page_json["snapshot"]["data"]["details"]["relationOptionColor"] = value
        pass
    
    def to_json(self):
        return self.page_json