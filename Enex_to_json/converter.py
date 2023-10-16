from bs4 import BeautifulSoup
import json
import random
import xml.etree.ElementTree as ET
from scipy.spatial import cKDTree
import hashlib
import os
import base64
import json
import re
from datetime import datetime
import time

from models.language_patterns import language_patterns
import models.mime
import models.json_model as Model
from models.options import Options


def sanitize_filename(filename):
    invalid_chars = '/\\?%*:|"<>'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def generate_random_id():
    """Génère un identifiant aléatoire en hexadécimal de la longueur spécifiée""" 
    
    hex_chars = '0123456789abcdef'
    id = ''.join(random.choice(hex_chars) for _ in range(24))
    return id


def extract_shifting_left(div):
    """Extrait la valeur de margin_left ou padding-left"""
    style = div.get('style')
    if style:
        style_properties = style.split(';')
        for prop in style_properties:
            if 'margin-left' in prop or 'padding-left' in prop :
                return int(prop.split(':')[1].replace('px', '').strip())
    return 0


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
        text = tag.get_text()

        # On compte le nombre de caractères du texte de contenu_div jusqu'à la position de la balise
        content_to_count = contenu_str[0:tag.sourcepos]
        soup_to_count = BeautifulSoup(content_to_count, 'html.parser')
        start = len(soup_to_count.get_text())
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


def extract_styles(style_string):
    """Génère un dictionnaire des styles à partir de l'attribut style

    Args:
        style_string (string): contenu de l'attribut string

    Returns:
        dic: contient les couples style CSS->valeur
    """
    style_dict = {}
    if style_string:
        # Cas particuliers à gérer :
        ## href:https://example.com
        ## et les background:(...) url(&quot;data:image/svg+xml;base64,PHN2ZyB3(...)
        style_pairs = re.findall(r'([^:]+):([^;]+);', style_string)
        for key, value in style_pairs:
                style_dict[key.strip()] = value.strip()
            
    return style_dict


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


def get_files(xml_content: ET.Element, dest_folder):
    """_summary_

    Args:
        xml_file (str): Chemin du fichier xml à traiter
        dest_folder (str): Chemin pour l'enregistrement des fichiers

    Returns:
        dic: dictionnaire avec 'hash du fichier': ('chemin du fichier', 'type mime du fichier') 
    """
    files_info_dict = {} 

    for resource in xml_content.findall('.//resource'):
        # Récupérer les éléments de la ressource
        data_elem = resource.find("./data")
        mime_elem = resource.find("./mime")
        attributes_elem = resource.find("./resource-attributes")

        if data_elem is not None and attributes_elem is not None:
            # Récupérer les valeurs des éléments
            data_base64 = data_elem.text.strip()
            mime = mime_elem.text.strip()
            file_type = ""
            for type, mime_list in models.mime.TYPE.items():
                if mime in mime_list:
                    file_type = type
                    break
                else:
                    file_type = "File"

            file_name = attributes_elem.find("./file-name").text.strip()
            sanitized_filename = sanitize_filename(file_name)
            data_decode = base64.b64decode(data_base64)
            # Calculer le hash (MD5) du contenu
            hash_md5 = hashlib.md5(data_decode).hexdigest()

            destination_path = os.path.join(dest_folder, sanitized_filename)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            with open(destination_path, 'wb') as outfile:
                outfile.write(data_decode)
            file_size = os.path.getsize(destination_path) * 8

            files_info_dict[hash_md5] = (sanitized_filename, mime, file_size, file_type)

    return files_info_dict


def process_details_to_json(content: ET.Element, page_model: Model.Page):
    """ Récupére le détail de la note """
    title_element = content.find("title")
    title = title_element.text if title_element is not None else "Default Title"   
    page_model.edit_details_key("name", title)
    
    # created date
    created_date_element = content.find("created")
    if created_date_element is not None:
        created_date = created_date_element.text
        date_format = "%Y%m%dT%H%M%SZ"
        date_object = datetime.strptime(created_date, date_format)
        created_timestamp = int(date_object.timestamp())
        page_model.edit_details_key("createdDate", created_timestamp)
    
    # Modified date as converted date
    timestamp_converted = int(time.time())
    page_model.edit_details_key("lastModifiedDate", timestamp_converted)

    pass


def process_codeblock(content, div_id, page_model: Model.Page):
    """Process code block with all content including children div
    
    Args:
        content (_type_): _description_
        page_model (Model.Page): _description_
    """
    extracted_text = ""
    for div_child in content.find_all(['div', 'br']):
        if div_child.name == 'br':  # Vérifie si le contenu de la div enfant est vide.
            extracted_text += "\n"  # Remplacez le contenu par "\
        elif not div_child.text.strip():
            pass
        else:
            extracted_text += div_child.get_text()
            # Sometimes EN add /n at the end of div/line, sometimes not...
            if not extracted_text.endswith("\n"):
                extracted_text += "\n"
            
    # Estimation du type de langage
    text_language = None
    max_occurrences = 0
    for lang, patterns in language_patterns.items():
        occurrences = 0
        for pattern in patterns:
            occurrences += len(re.findall(pattern, extracted_text))
        
        # Mise à jour de text_language si le nombre d'occurrences est plus élevé
        if occurrences > max_occurrences:
            max_occurrences = occurrences
            text_language = lang
  
    shifting_left = extract_shifting_left(content)
    page_model.add_block(div_id, shifting=shifting_left, text = extracted_text)
    page_model.edit_text_key(div_id, "style", "Code")
    page_model.edit_block_key(div_id,"fields",text_language)
    
    pass


def extract_text_with_formatting(div_content, div_id, page_model: Model.Page):
    """
    Analyze the tags to transform the text formatting into AT JSON format. 
    """
    # Définition des balises inline à traiter
    formatting_tags = ['span', 'b', 'u', 'i', 's', 'a','font']
    div_text = extract_top_level_text(div_content)
    
    if div_text:
        # Ajout du block text
        #print(div_text)
        page_model.add_text_to_block(div_id, text=div_text)
        pass
        
        for element in extract_tag_info(div_content, formatting_tags):
            start = element['start']
            end = element['end']
            tag_object=element['tag_object']
            tag_name = tag_object.name
            #print(f"'tag_name': {tag_name}, 'text': {div_text}, 'start': {start}, 'end': {end}")

            formatting_type = None
            param = None

            text_style = tag_object.get('style')
            styles = extract_styles(text_style) if text_style else {}
            
            # Récup des infos
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
                param = tag_object.get('href')
                
            if param or formatting_type:
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            

def process_content_to_json(content: str, page_model, files_dict):
    """
    Processing <content> to create the parent element and calling a function for child elements
    """
    # Converting to soup for specific html parsing
    soup = BeautifulSoup(content, 'html.parser')  # Utilisation de l'analyseur HTML par défaut

    # Créer l'élément JSON pour la première div (shifting = -1)
    root_block = soup.find('en-note')
    block_id = generate_random_id()
    page_model.add_block(block_id,-1)
    first_text = root_block.find_all(string=True, recursive=False)
    if first_text:
        page_model.add_text_to_block(id,first_text[0].strip())

    process_div_children(root_block, page_model, files_dict)


def process_div_children(div, page_model: Model.Page, files_dict):
    # Définition des balises block à traiter
    balisesBlock = ['div', 'hr', 'br', 'h1', 'h2', 'h3','en-media']
    children = div.find_all(balisesBlock)
    for child in children:
        div_id = generate_random_id()
        shifting_left = extract_shifting_left(child)
        div_text = extract_top_level_text(child)
        div_tag = child.get('id')

        # On commence par les blocs sans texte
        if child.name == 'hr':
            page_model.add_block(div_id, shifting=shifting_left)
            page_model.edit_block_key(div_id, "div",{})
        elif child.name == 'br':
            page_model.add_block(div_id, shifting=shifting_left, text = "")
        # Traitement des fichiers à intégrer
        elif child.name == 'en-media':
            hash = child.get('hash')
            if hash in files_dict:
                sanitized_filename, mime, file_size, file_type = files_dict[hash]
                # Redimensionné? Il faut retourner width="340px" divisé par style="--en-naturalWidth:1280"  style="--en-naturalWidth:1280; --en-naturalHeight:512;" width="340px" />
                text_style = child.get('style')
                styles = extract_styles(text_style) if text_style else {}
                
                embed_width = child.get('width')
                original_width = int(styles.get("--en-naturalWidth", "0"))
                
                relative_width = None  
                if embed_width is not None and original_width is not None and original_width != 0:
                    relative_width = float(embed_width.replace("px", "")) / original_width
                # Format lien? 
                style_attr = child.get('style')
                format = 'link' if style_attr and '--en-viewAs:attachment;' in style_attr else None
                page_model.add_block(div_id, shifting=shifting_left)
                page_model.add_file_to_block(div_id, hash = hash, name = sanitized_filename, file_type = file_type, mime = mime, size = file_size, embed_size = relative_width, format=format )
            
                # TODO : quand AnyType permettra l'import des fichiers            
        # Traitement bloc code (div racine sans texte)
        elif child.name == 'div' and 'style' in child.attrs and '--en-codeblock:true' in child['style']:
                process_codeblock(child, div_id, page_model)
        # Traitement des blocs demandant du contenu texte
        elif div_text:
            # les div enfant des blocs codes doivent être exclues du traitement global
            parent_div = child.find_parent('div')
            if child.name == 'div' and parent_div and 'style' in parent_div.attrs and '--en-codeblock:true' in parent_div['style']:
                pass
            # Traitements spécifiques
            elif child.name in ['div', 'h1', 'h2', 'h3']:
                # Traitement spécifique pour les listes!
                parent_list = child.find_parent(['ol', 'ul'])
                if parent_list:
                    #Est-ce dans une liste imbriquée? 1ère étape pouvoir pouvoir placer le childrenIds!
                    #TODO
                    # TODO : ajout imbrication à l'imbrication existante? Si padding = 40 et imbrication 40 : traiter comme 80?
                    #        A tester quels cas EN peut générer...
                    nested_level = len(parent_list.find_parents(['ol', 'ul']))
                    if nested_level > 0:
                        # On va traiter comme les blocs décalés...
                        shifting_left = 40 * (nested_level)
                
                # Puis on créé le bloc
                page_model.add_block(div_id, shifting=shifting_left)
                
                # Traitement texte
                extract_text_with_formatting(child, div_id, page_model)
                
                # Traitements styles du bloc
                style = extract_styles(child.get('style'))
                if 'padding-left' in style:
                    # Le traitement est déjà fait, on ne fait rien
                    pass
                elif '--en-codeblock' in style:
                    # Traitement à définir plus tard de tous les sous-blocs
                    pass
                elif 'text-align' in style:
                    if style['text-align'] == 'center':
                        page_model.edit_block_key(div_id,"align","AlignCenter")
                    elif style['text-align'] == 'right':
                        page_model.edit_block_key(div_id,"align","AlignRight")

                # Et style si c'est une liste
                if parent_list:
                    checked = False 
                    if parent_list.name == 'ol':
                        style_liste = 'Numbered'
                    elif parent_list.name == 'ul' and parent_list.has_attr('style') and '--en-todo:true' in parent_list['style']:
                        style_liste = 'Checkbox'
                        li_parent = child.find_parent('li')
                        if li_parent and li_parent.has_attr('style') and '--en-checked:true' in li_parent['style']:
                            page_model.edit_text_key(div_id,"checked",True)
                    else:
                        style_liste = 'Marked'
                    page_model.edit_text_key(div_id,"style",style_liste)
                
                # et style des titres
                if  child.name in ['h1', 'h2', 'h3']:
                    page_model.edit_text_key(div_id,"style","Header" + child.name[1:])
            
                


def convert_files(enex_files_list: list):
    """Conert enex file from the list into json files

    Args:
        enex_files_list (list): list of enex file to convert

    Returns:
        string: number of notes converted
    """
    if not enex_files_list:
        print("Aucun fichier à convertir.")
        return
    
    source_folder = os.path.dirname(enex_files_list[0])
    result_folder = os.path.join(source_folder, "Converted_files")
    os.makedirs(result_folder, exist_ok=True)
    files_dest_folder = os.path.join(result_folder, "files")
    
    nb_notes = 0
    for enex_file in enex_files_list:
        print(f"Conversion de {os.path.basename(enex_file)}...")
        with open(enex_file, 'r', encoding='utf-8') as xhtml_file:
            file_content = xhtml_file.read()
            #file_id = hashlib.md5(xhtml_content).hexdigest()
        
        soup = BeautifulSoup(file_content, 'xml')
        root = ET.fromstring(file_content)
        
        # is unique or multiple note?
        for note_xml in root.iter("note"):
            # Traitement des fichiers (base64 vers fichiers)
            files_dict = get_files(note_xml, files_dest_folder)
            
            # Utilisation de la classe Model.Page pour créer le JSON
            page_model: Model.Page = Model.Page()

            # Extraction du contenu de la balise <content> et traitement
            content_element = note_xml.find('content')
            content = content_element.text if content_element is not None else None
            process_content_to_json(content, page_model, files_dict)
            
            # Processing xml tags (other than <content>)
            process_details_to_json(note_xml,page_model)

            # Nettoyer les clés "shifting" si nécessaire
            page_model.cleanup()

            # Générer le nom du fichier JSON en supprimant l'extension .enex
            # json_file_name = os.path.splitext(os.path.basename(enex_file))[0] + '.json'
            
            
            # Name for file : TODO, case of multiples notes with same name in Evernote... add an ID?
            note_title = page_model.page_json["snapshot"]["data"]["details"]["name"]
            filename = f"{sanitize_filename(note_title)}.json"
            with open(os.path.join(result_folder, filename), 'w', encoding='utf-8') as file:
                json.dump(page_model.to_json(), file, indent=2)
            nb_notes += 1
        
    
    return nb_notes
            

def main():
    # Répertoire contenant les fichiers enex de test
    enex_directory = 'Tests/'
    
    # Liste des fichiers enex dans le répertoire
    enex_files = [os.path.join(enex_directory, f) for f in os.listdir(enex_directory) if f.endswith('code.enex')]
    convert_files(enex_files)

    


if __name__ == "__main__":
    main()