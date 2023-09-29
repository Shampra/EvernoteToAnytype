from bs4 import BeautifulSoup
import json
import random
import string



def generate_random_id():
    """
    Génère un identifiant aléatoire en hexadécimal de la longueur spécifiée (par défaut 20 caractères)
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
    # TODO : il faut aussi intégrer les cas de type #ffef9e
        ## Puis définir des plages (couleurs rgb vers 10 couleurs sur AT)


    #rgb_value = style.split("(")[1].split(")")[0]
    #rgb_components = [int(component) for component in rgb_value.split(",")]

    # Définition de certaines couleurs courantes
    colors = {
        (255, 0, 0): "red",
        (0, 255, 0): "vert",
        (0, 0, 255): "bleu",
        (255, 255, 0): "yellow",
        (0, 255, 255): "purple",
        (255, 0, 255): "pink",
        (128, 0, 0): "maroon",
        (240, 168, 65): "lime",
        (0, 0, 128): "orange",
        (128, 128, 0): "olive",
        (128, 0, 128): "violet",
        (0, 128, 128): "grey",
        (192, 192, 192): "argent",
        (128, 128, 128): "gris foncé",
        (0, 0, 0): "noir",
        (255, 255, 255): "blanc"
    }

    # Cherche une correspondance de couleur basée sur la valeur RGB
    # if tuple(rgb_components) in colors:
    #     return colors[tuple(rgb_components)]
    # else:
    #     return "red"
    return "red"

def extract_styles(style_string):
    # Divisez la chaîne de style en une liste de styles et de valeurs
    styles = [style.strip() for style in style_string.split(';') if style.strip()]

    # Créez un dictionnaire pour stocker les styles et leurs valeurs
    style_dict = {}
    for style in styles:
        style_name, style_value = style.split(':')
        style_dict[style_name.strip()] = style_value.strip()

    return style_dict


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
    formatting_tags = ['span', 'b', 'u', 'i', 's', 'a']
    text = extract_top_level_text(tag)

    if text:
        formatting_info = []

        for tag_name in formatting_tags:
            formatting_elements = tag.find_all(tag_name)
            for element in formatting_elements:
                element_text = element.get_text()
                start = text.find(element_text)
                end = start + len(element_text)

                formatting_type = None
                param = None

                text_style = element.get('style')
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
    balisesBlock = ['div'] # ['div', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'blockquote', 'table', 'form']

# TODO DEMAIN : améliorer/optimiser! Un case? Inverser logique? Un find_all() puis if in balisesblock?
    for tag_name in balisesBlock:
            children = div.find_all(tag_name)

            for child in children:
                # Utilisation de la fonction pour générer un ID aléatoire
                div_id = generate_random_id()
                shifting_left = extract_shifting_left(child)
                div_tag = child.get('id')

                # Récupérer le texte uniquement dans cette div (et pas dans les divs enfants)
                div_text = child.get_text()
                element = {
                    "id": div_id,
                    #"tag": div_tag if div_tag else "",
                    "shifting": shifting_left,
                }

                # Si pas de texte, on continue (div vide TODO : à changer avec le cas HR)
                if not div_text:
                    break

                if tag_name == 'h1':
                    element["style"] = "Header1"
                elif tag_name == 'h2':
                    element["style"] = "Header2"
                elif tag_name == 'h3':
                    element["style"] = "Header3"


                # Trouver la div précédente avec une valeur de style margin-left inférieure
                for prev_element in elements_json[::-1]:
                    prev_style = prev_element["shifting"]
                    if shifting_left > prev_style:
                        if "childrenIds" not in prev_element:
                            prev_element["childrenIds"] = []
                            # Ajouter le layout seulement si c'est le premier enfant
                            # Apparemment supprimé dans les dernières versions d'AT
                            # if prev_element["id"] != div_id and prev_element["shifting"] != -1:
                            #     prev_element["layout"] = {"style": "Div"}
                        prev_element["childrenIds"].append(element["id"])
                        break

                elements_json.append(element)






    # children = div.find_all('div')
    # for child in children:
    #     # Utilisation de la fonction pour générer un ID aléatoire
    #     div_id = generate_random_id()
    #     shifting_left = extract_shifting_left(child)
    #     div_tag = child.get('id')

    #     # Récupérer le texte uniquement dans cette div (et pas dans les divs enfants)
    #     div_text = child.get_text()
    #     element = {
    #         "id": div_id,
    #         #"tag": div_tag if div_tag else "",
    #         "style": shifting_left,
    #         "text": extract_text_with_formatting(child) if div_text else ""
    #     }
    #     # Trouver la div précédente avec une valeur de style margin-left inférieure
    #     for prev_element in elements_json[::-1]:
    #         prev_style = prev_element["style"]
    #         if shifting_left > prev_style:
    #             if "childrenIds" not in prev_element:
    #                 prev_element["childrenIds"] = []
    #                 # Ajouter le layout seulement si c'est le premier enfant
    #                 # Apparemment supprimé dans les dernières versions d'AT
    #                 # if prev_element["id"] != div_id and prev_element["style"] != -1:
    #                 #     prev_element["layout"] = {"style": "Div"}
    #             prev_element["childrenIds"].append(element["id"])
    #             break

        # elements_json.append(element)

    # Retirer la clé "style" à la fin
    for element in elements_json:
        if "shifting" in element:
            del element["shifting"]

def main():
    # On charge un modèle json : les données elements_json et details_json seront complétés via les traitements
    elements_json = []
    details_json = {}

    # On traite le contenu d'un fichier xhtml (nommé test.xml)
    xhtml_file = open('test.xml', 'r', encoding='utf-8')
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
    with open('resultat.json', 'w', encoding='utf-8') as file:
        json.dump(page_json, file, indent=2)

if __name__ == "__main__":
    main()