from bs4 import BeautifulSoup
import json
import random
import string
from scipy.spatial import cKDTree
import models.mime as mime


def generate_random_id():
    """
    Génère un identifiant aléatoire en hexadécimal de la longueur spécifiée
    """ 
    hex_chars = '0123456789abcdef'
    return ''.join(random.choice(hex_chars) for _ in range(24))


def extract_shifting_left(div):
    """
    Extrait la valeur de margin_left ou padding-left
    """
    style = div.get('style')
    if style:
        style_properties = style.split(';')
        for prop in style_properties:
            if 'margin-left' in prop or 'padding-left' in prop :
                return int(prop.split(':')[1].replace('px', '').strip())
    return 0


# couleur AT suivant le RGB Evernote
def extract_color_from_style(style):
    """Transform RGB or Hexa color from Evernote to a AT color (limited)

    Args:
        style (string): "rgb()" or "#xxxxxx"

    Returns:
        string: color name
    """
    colors = {
        "grey": (182, 182, 182),
        "yellow": (236, 217, 27),
        "orange": (255, 181, 34),
        "red": (245, 85, 34),
        "pink": (229, 28, 160),
        "purple": (171, 80, 204),
        "blue": (62, 88, 235),
        "ice": (42, 167, 238),
        "teal": (15, 200, 186),
        "lime": (93, 212, 0),
    }
    # For background-color, map 1 to 1
    EN_bck_color ={
        "yellow": (255, 239, 158),
        "orange": (255, 209, 176),
        "red": (254, 193, 208),
        "purple": (203, 202, 255),
        "blue": (176, 236, 244),
        "lime": (183, 247, 209)
    }

    def rgb_to_tuple(rgb):
        return tuple(int(x) for x in rgb.split(","))
    
    def closest_color(rgb):
        # Vérifier s'il y a une correspondance exacte dans EN_bck_color
        exact_match = [key for key, value in EN_bck_color.items() if value == rgb]
        if exact_match:
            return exact_match[0]
        tree = cKDTree(list(colors.values()))
        _, index = tree.query(rgb)
        return list(colors.keys())[index]

    # Vérifier si le style est au format rgb()
    if style.startswith("rgb("):
        rgb_value = style.split("(")[1].split(")")[0]
        rgb_components = rgb_to_tuple(rgb_value)
        return closest_color(rgb_components)
    # Vérifier si le style est au format hexadécimal
    elif style.startswith("#") and len(style) == 7:
        hex_value = style.lstrip("#")
        rgb_components = tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
        return closest_color(rgb_components)
    else:
        return "red"  # Format non reconnu, rouge mis par défaut

def extract_styles(style_string):
    style_dict = {}
    if style_string:
        # Divisez la chaîne de style en une liste de styles et de valeurs
        styles = [style.strip() for style in style_string.split(';') if style.strip()]

        # Créez un dictionnaire pour stocker les styles et leurs valeurs
        for style in styles:
            style_name, style_value = style.split(':')
            style_dict[style_name.strip()] = style_value.strip()
    return style_dict

def extract_tag_info(contenu_div, tags_list):
    """Extract info about tag in this content

    Args:
        contenu_div (_type_): _description_
        tags_list (list): list of tag to treat

    Returns:
        list: {
            'tag_object': tag,
            'text': text into this tag,
            'start': starting position in contenu_div,
            'end': end position in contenu_div
        }
    """    
    # Analyser le contenu HTML
    
    ######### Tag avec tout
    
    # On recréé un objet soup à partir de l'objet tag transmis
    contenu_str = str(contenu_div)
    soup = BeautifulSoup(str(contenu_div), 'html.parser')
    # TODO : voir si on peut transmettre un soup plutôt que tag?
    
    # Initialiser une liste pour stocker les informations des balises
    tags_info = []

    for tag in soup.find_all(tags_list):     
        # print(tag)
        
        # Récupérer le texte à l'intérieur de la balise en utilisant extract_top_level_text
        text = tag.get_text()

        # On compte le nombre de caractères du texte de contenu_div jusqu'à la position de la balise
        content_to_count = contenu_str[0:tag.sourcepos]
        soup_to_count = BeautifulSoup(content_to_count, 'html.parser')
        start = len(soup_to_count.get_text())

        # position de fin de texte
        end = start + len(text)

        #print(f"'tag_name': {tag.name}, 'text': {text}, 'start': {start}, 'end': {end}, 'tag position' : {tag.sourcepos}")
        # Ajouter les informations de la balise à la liste
        tags_info.append({
            'tag_object': tag,
            'text': text,
            'start': start,
            'end': end
        })
    return tags_info


# Fonction pour extraire le texte de niveau supérieur sans garder le texte des div
def extract_top_level_text(element):
    """
    Return the text of a block without text in children block
    """
    result = []
    for item in element.contents:
        if isinstance(item, str):
            result.append(item)
        elif item.name == 'div':
            break
        else:
            result.append(item.text)
    return ''.join(result)


# Formatage du text récupéré selon les balises
def extract_text_with_formatting(tag):
    """
    Analyze the tags to transform the text formatting into AT JSON format. 
    """
    # Définition des balises inline à traiter
    formatting_tags = ['span', 'b', 'u', 'i', 's', 'a','font']
    text = extract_top_level_text(tag)


    if text:
        formatting_info = []
        for element in extract_tag_info(tag, formatting_tags):
            start = element['start']
            end = element['end']
            tag_object=element['tag_object']
            tag_name = tag_object.name
            
            print(f"'tag_name': {tag_name}, 'text': {text}, 'start': {start}, 'end': {end}")

            formatting_type = None
            param = None

            text_style = tag_object.get('style')
            styles = extract_styles(text_style) if text_style else {}

            if ("font-weight" in styles and styles["font-weight"] == "bold") or tag_name == 'b':
                formatting_type = "Bold"
            elif ("text-decoration" in styles and styles["text-decoration"] == "underline") or tag_name == 'u':
                formatting_type = "Underscored"
            elif ("font-style" in styles and styles["font-style"] == "italic") or tag_name == 'i':
                formatting_type = "Italic"
            elif ("text-decoration" in styles and styles["text-decoration"] == "line-through") or tag_name == 's':
                formatting_type = "Strikethrough"
            elif "color" in styles:
                formatting_type = "TextColor"
                param = extract_color_from_style(styles["color"])
            elif 'background-color' in styles:
                formatting_type = "BackgroundColor"
                param = extract_color_from_style(styles["background-color"])
            elif tag_name == 'a':
                formatting_type = "Link"
                param = element.get('href')

            if formatting_type:
                formatting_info.append({
                    "range": {
                        "from": start,
                        "to": end
                    },
                    "type": formatting_type
                })

            if param:
                formatting_info[-1]["param"] = param

        return {
            "text": text,
            "marks": {
                "marks": formatting_info
            }
        }
    else:
        return {
            "marks": {
            }
        }

    
# TODO - vide
def process_details_to_json(content):
    """
    Récupére le détail de la note
    """
    pass

def process_content_to_json(content, elements_json):
    """
    Processing <content> to create the parent element and calling a function for child elements
    """
    soup = BeautifulSoup(content, 'html.parser')  # Utilisation de l'analyseur HTML par défaut

    # Créer l'élément JSON pour la première div (shifting = -1)
    root_block = soup.find('en-note')
    first_element = {
        "id": generate_random_id(),  # Utilisation de la fonction pour générer un ID aléatoire
        "fields": {
            "width": 1
            },
        "shifting": -1,
    }
    first_text = root_block.find_all(string=True, recursive=False)
    if first_text:
        first_element["text"] = first_text[0].strip()

    elements_json.append(first_element)
    
    process_div_children(root_block, elements_json)


def process_div_children(div, elements_json):
    """
    Parcours et traitement des balises type blocs
    """
    # Définition des balises block à traiter
    balisesBlock = ['div', 'hr', 'h1', 'h2', 'h3']
    # ['div', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'blockquote', 'table', 'form']

    children = div.find_all(balisesBlock)
    for child in children:
        element = None 
        div_id = generate_random_id()
        shifting_left = extract_shifting_left(child)
        div_text = extract_top_level_text(child)
        div_tag = child.get('id')

        # On commence par hr, seul élément sans texte obligatoire
        if child.name == 'hr':
            element = {
                "id": div_id,
                #"tag": div_tag if div_tag else "",
                "shifting": shifting_left,
                "div": { }
            }
        # Si on a du texte dans le block, on le traite
        elif div_text:
            text = extract_text_with_formatting(child)
            element = {
                    "id": div_id,
                    #"tag": div_tag if div_tag else "",
                    "shifting": shifting_left,
                    "text": text
                }
            # Traitements spécifiques
            if child.name == 'div':
                style = extract_styles(child.get('style'))
                if 'padding-left' in style:
                    # Le traitement est déjà fait, on ne fait rien
                    pass
                elif '--en-codeblock' in style:
                    # Traitement à définir plus tard de tous les sous-blocs
                    pass
                elif 'text-align' in style:
                    if style['text-align'] == 'center':
                        element["align"] = "AlignCenter"
                    elif style['text-align'] == 'right':
                        element["align"] = "AlignRight"
            elif  child.name in ['h1', 'h2', 'h3']:
                text["style"] = "Header" + child.name[1:]
            elif child.name in ['ul', 'ol']:
                # Traitement spécifique du contenu (appel fonction à définir)
                pass
                
                

        if element is not None:
            # Trouver le block précédent avec une valeur de style margin-left inférieure
            for prev_element in elements_json[::-1]:
                prev_style = prev_element["shifting"]
                if shifting_left > prev_style:
                    if "childrenIds" not in prev_element:
                        prev_element["childrenIds"] = []
                    prev_element["childrenIds"].append(element["id"])
                    break
            elements_json.append(element)

    # A la fin, on retire la clé "shifting" 
    for element in elements_json:
        if "shifting" in element:
            del element["shifting"]

def main():
    # On charge un modèle json : les données elements_json et details_json seront complétés via les traitements
    elements_json = []
    details_json = {}

    # On traite le contenu d'un fichier xhtml
    xhtml_file = open('Tests/Test couleurs.enex', 'r', encoding='utf-8')
    xhtml_content = xhtml_file.read()
    xhtml_file.close()
    soup = BeautifulSoup(xhtml_content, 'html.parser')

    # Traitement des balises du fichier (sauf <content>)
    # details_json = process_details_to_json(xhtml_content, details_json)

    # Extraction du contenu de la balise <content> et traitement 
    content = soup.find('content').text
    process_content_to_json(content, elements_json)

    # On structure le modèle JSON final
    page_json = {
        "sbType": "Page",
        "snapshot": {
            "data": {
                "blocks": elements_json,
                "details": {
                    "createdDate": 1694278035,
                    "creator": "bafyreidk3ty67vxnt2nl74w6vycmm4v5vu55zatfvnq7wpefbo2po6wsxu",
                    "description": "",
                    "lastModifiedBy": "bafyreidk3ty67vxnt2nl74w6vycmm4v5vu55zatfvnq7wpefbo2po6wsxu",
                    "lastModifiedDate": 1695479472,
                    "lastOpenedDate": 1695479438,
                    "layout": 0,
                    "name": "Test d'import manuel",
                    "type": "ot-page"
                    },
                "objectTypes": ["ot-page"]
            }
        }
    }

    # Enregistrement dans un fichier resultat.json du modèle complété avec les données
    with open('Tests/resultat.json', 'w', encoding='utf-8') as file:
        json.dump(page_json, file, indent=2)

if __name__ == "__main__":
    main()