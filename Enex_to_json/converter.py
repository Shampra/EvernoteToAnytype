import argparse
import copy
import shutil
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import json
import random
import xml.etree.ElementTree as ET
from scipy.spatial import cKDTree
import hashlib
import os
import sys
import base64
import re
from datetime import datetime
import time
from typing import List, Type
import logging
import inspect
from urllib.parse import urlparse
import urllib.request
import hmac
from Crypto.Cipher import AES
import tkinter as tk
from tkinter import simpledialog
import warnings
from PIL import Image
from nocairosvg import svg2png

from libs.language_patterns import language_patterns
import libs.table_parse, libs.pbkdf2, libs.mime, libs.json_model as Model
from libs.options import Options
from libs._version import __version__


# Ignore les avertissements de BeautifulSoup
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

## GLOBAL ##
# Déclarer options en tant que variable globale
my_options = Options()
 # Définition des balises block 
liste_balisesBlock = ['div', 'p', 'hr',  'h1', 'h2', 'h3','h4', 'h5', 'h6','en-media','table', 'img','li', 'pre', 'en-crypt']
# Liste globale des fichiers de la note
files_dict = []
#
note_title = None

# Configurer le logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log", 'w', 'utf-8')
    ]
)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)
# Desactivate spam log from PIL
logging.getLogger('PIL').setLevel(logging.WARNING)

# Color ANSI just to color console debug!
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FileInfo:
    def __init__(self, file_id: str, unique_filename: str, original_filename: str, mime_type: str, file_size: int, file_type: str, hash_md5: str):
        """Gestion des infos d'un fichier

        Args:
            file_id (str): random id pour le fichier
            filename (str): Nom du fichier (attention, fichier généré avec hash + filename)
            mime_type (str): mime
            file_size (int): taille
            file_type (str): type Anytype
            hash_md5 (str): hash_md5 si pas présent ailleurs
        """
        self.file_id = file_id
        self.original_filename = original_filename
        self.unique_filename = unique_filename
        self.mime_type = mime_type
        self.file_size = file_size
        self.file_type = file_type
        self.hash_md5 = hash_md5


def log_debug(message: str, level: int = logging.DEBUG):
    """Fonction de gestion des logs.
    Si l'option de debug est activé : 
    - on met tout les log DEBUG ou supérieur dans un fichier de log 
    - et si on exécute sous VS Code, on affiche dans la console les logging.NOSET
    Sans l'option, on affiche les logs supérieurs à DEBUG dans la console 

    Args:
        message (str): message à logger
        level (int, optional): logging level. Defaults to logging.DEBUG.
    """       
    caller_frame = inspect.stack()[1]
    caller_func = caller_frame[3].ljust(30)
    caller_lineno = str(caller_frame[2]).ljust(4)
    if my_options.is_debug:
        if level >= logging.DEBUG:
            logger.log(level, f"{caller_func} l.{caller_lineno} - {message}")
        if 'TERM_PROGRAM' in os.environ.keys() and os.environ['TERM_PROGRAM'] == 'vscode': # debug en mode dev, on affiche tout
            print(f"{caller_func} l.{caller_lineno} - {message}")
    if level > logging.DEBUG:
        try:
            print(message)
        except UnicodeEncodeError:
            # Fallback au cas où l'encodage échoue
            print(message.encode('ascii', errors='replace').decode('ascii'))
    
        
def sanitize_filename(filename):
    invalid_chars = '/\\?%*:|"<>'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = filename.strip()  # Supprimer les espaces de début et de fin
    filename = filename[:255]  # Limiter la longueur du nom de fichier à 255 caractères
    if not filename:  # Vérifier si le nom de fichier résultant est vide
        filename = "empty_filename"+generate_random_id(6)  # Si vide, attribuer un nom de fichier par défaut
    return filename


def generate_random_id(length = 48):
    """Génère un identifiant aléatoire en hexadécimal de la longueur spécifiée""" 
    
    hex_chars = '0123456789abcdef'
    id = ''.join(random.choice(hex_chars) for _ in range(length))
    return id


def extract_shifting_left(div):
    """Extrait la valeur de margin_left ou padding-left"""
    style = div.get('style')
    if style:
        style_properties = style.split(';')
        for prop in style_properties:
            if 'margin-left' in prop or 'padding-left' in prop:
                value_str = prop.split(':')[1].strip()
                try:
                    # Enlever les unités 'em' ou 'px' de la chaîne pour obtenir la valeur entière
                    if 'em' in value_str:
                        value_int = int(value_str.replace('em', '').strip()) * 16
                    elif 'px' in value_str:
                        value_int = int(value_str.replace('px', '').strip())
                    else:
                        # Si aucune unité n'est spécifiée, retourner une valeur par défaut
                        log_debug(f"Unknown shifting left value: {value_str}", logging.WARNING)
                        return 16
                    return value_int
                except ValueError:
                    # En cas d'erreur de conversion, retourner une valeur par défaut
                    log_debug(f"Invalid shifting left value: {value_str}", logging.WARNING)
                    return 16
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
    # On recréé un objet soup à partir de l'objet tag transmis
        # Supprimer toutes les balises <br/> et les remplacer par des sauts de ligne \n, sinon problème de comptage
        
    soup = BeautifulSoup(str(contenu_div), 'html.parser')
    for br_tag in soup.find_all("br"):
        br_tag.replace_with("\n")
    content = soup.find(liste_balisesBlock)
    if content:
        for elt in content.find_all(liste_balisesBlock): # Vire aussi les blocs enfant, qui ne doivent pas être traité
            elt.decompose()
    
    # Initialiser une liste pour stocker les informations des balises
    tags_info = []
    
    # Extraire le texte brut de la page sans balises HTML
    plain_text = soup.get_text()

    for tag in soup.find_all(tags_list):     
        text = tag.get_text()
        start = plain_text.find(text)
        end = start + len(text)

        log_debug(f"--- 'tag_name': {tag.name}, 'text': {text}, 'start': {start}, 'end': {end}, 'tag_object' : {tag}", logging.NOTSET)

        #Ajouter les informations de la balise à la liste
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
        style_pairs = re.findall(r'([^:]+):([^;]+);*', style_string)
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
        "lime": (183, 247, 209),
        "black": (51,51,51) # couleur mise automatiquement dans certains cas sous EN (pas de black sur AT mais ça sera ignoré)
    }
    default_color="default"

    def rgb_to_tuple(rgb):
        try:
            if "%" in rgb:
                # Gérer les valeurs en pourcentage
                values = [int(float(val[:-1]) * 255 / 100) for val in rgb.split(",")]
            else:
                # Gérer les valeurs entières ou en virgule flottante
                values = [int(float(val)) if "." in val else int(val) for val in rgb.split(",")]

            # Vérifier si le nombre de valeurs est exactement 3
            if len(values) == 3:
                return tuple(values)
            else:
                raise ValueError("Invalid RGB format")

        except (ValueError, IndexError):
            # En cas d'erreur, retourner le tuple par défaut
            return (0, 0, 0)
    
    
    
    def closest_color(rgb):
        # Vérifier s'il y a une correspondance exacte dans EN_bck_color
        exact_match = [key for key, value in EN_bck_color.items() if value == rgb]
        if exact_match:
            return exact_match[0]
        tree = cKDTree(list(colors.values()))
        _, index = tree.query(rgb)
        return list(colors.keys())[index]

    # Vérifier si le style est au format rgb()
    if style.startswith(("rgb(", "rgba(")):
        rgb_value = style.split("(")[1].split(")")[0]
        try:
            rgb_components = rgb_to_tuple(rgb_value)
            if all(component < 50 for component in rgb_components):
                return default_color
            else:
                return closest_color(rgb_components)
        except ValueError:
            return default_color
    # Vérifier si le style est au format hexadécimal
    elif style.startswith("#") and (len(style) == 7 or len(style) == 4):
        if len(style) == 4:
            style = "#" + style[1] * 2 + style[2] * 2 + style[3] * 2           
        hex_value = style.lstrip("#")
        rgb_components = tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
        if all(component < 50 for component in rgb_components):
            return default_color
        else:
            return closest_color(rgb_components)
    elif style in ('red', 'blue', 'green', 'black'):
        return style
    else:
        return default_color  # Format non reconnu, rouge mis par défaut


# Fonction pour extraire le texte de niveau supérieur sans garder le texte des sous blocs
def extract_top_level_text(element):
    """Extract top level text without text inside childen block tags

    Returns:
        str: text
    """
    result = []
    for item in element.contents:
        # log_debug(f"{bcolors.WARNING}--------  item {bcolors.ENDC} {item} {bcolors.WARNING}{bcolors.ENDC}", logging.NOTSET)
        if isinstance(item, str): # sans balise
            result.append(item)
            log=f"chaine simple, on ajoute {item}"
        elif item.name in liste_balisesBlock:
            log=f"{item.name} est une balise bloc, on passe"
            continue
        elif item.name=='br':# cas des br pour les sauts de ligne
            result.append('\n')
            log = f"ajout saut de ligne"
        else: # balise non "bloc", on boucle
            log = f"autre cas (balise inline?), on boucle"
            result.append(extract_top_level_text(item))
    #     log_debug(f"{bcolors.WARNING} ==>{bcolors.ENDC} {log}", logging.NOTSET)
    # log_debug(f"{bcolors.WARNING}--- Résultat : {bcolors.ENDC}{''.join(result)}", logging.NOTSET)
    return ''.join(result)


def get_files(xml_content: ET.Element, dest_folder):
    """Génère les fichiers en enregistrant leurs infos dans un dictionnaire

    Args:
        xml_file (str): Chemin du fichier xml à traiter
        dest_folder (str): Chemin pour l'enregistrement des fichiers

    Returns:
        dic: dictionnaire avec ('hash du fichier': ('id du fichier','nom du fichier', 'type mime du fichier', taille, 'type AT'))
    """
    files_info_dict = {} 
    log_debug(f"-- Get files...", logging.DEBUG)
    
    for resource in xml_content.findall('.//resource'):
        # Récupérer les éléments de la ressource
        data_elem = resource.find("./data")
        mime_elem = resource.find("./mime")
        attributes_elem = resource.find("./resource-attributes")

        if data_elem is not None and data_elem.text is not None and attributes_elem is not None and mime_elem is not None and mime_elem.text is not None:
            # Récupérer les valeurs des éléments
            data_base64: str  = data_elem.text.strip()
            mime: str  = mime_elem.text.strip()
            file_type: str  = ""
            file_id :str = "file" + generate_random_id()
            for type, mime_list in libs.mime.TYPE.items():
                if mime in mime_list:
                    file_type = type
                    break
                else:
                    file_type = "File"

            
            
            ## Define filename ##
            elt_file_name = attributes_elem.find("./file-name")
            if elt_file_name is not None and elt_file_name.text is not None:
                original_filename: str = attributes_elem.find("./file-name").text.strip()
            else:
                original_filename = "noname_" + data_base64[:6]
                
            ## image without extension, we add it again
            if '.' not in os.path.basename(original_filename):
                if mime == "image/jpg":
                    original_filename += ".jpg"
                elif mime == "image/png":
                    original_filename += ".png"
                elif mime == "image/svg+xml":
                    original_filename += ".svg"
            
            sanitized_filename = sanitize_filename(original_filename)
            
            try:
                data_decode = base64.b64decode(data_base64)
            except base64.binascii.Error as e:
                log_debug(f"--- Error during base64 decoding : {e}", logging.DEBUG)
                continue
            
            # Calculer le hash (MD5) du contenu
            hash_md5 = hashlib.md5(data_decode).hexdigest()

            #Avoid crushes multiples files with same name
            unique_sanitized_filename = hash_md5 + sanitized_filename
            destination_path = os.path.join(dest_folder, unique_sanitized_filename)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            with open(destination_path, 'wb') as outfile:
                outfile.write(data_decode)
            file_size = os.path.getsize(destination_path) * 8
            
            # Réparation des png, souvent avec CRC incorrect dans Evernote et Anytype ne le support pas...
            if mime == "image/png": 
                log_debug(f"{bcolors.HEADER}Récupération du fichier png {original_filename}{bcolors.ENDC}", logging.NOTSET) 
                try:
                    img = Image.open(destination_path)
                    img.save(destination_path)
                except:
                    log_debug(f"{bcolors.FAIL}Fichier {original_filename} corrompu, non récupérable {bcolors.ENDC}", logging.NOTSET)
                    log_debug(f"File {original_filename} is corrupted and cannot be repair for Anytype ", logging.WARNING)

            # Transform SVG to png because AT doesn't support them
            if mime == "image/svg+xml":
                log_debug(f"Converting svg {original_filename} to png, this can take few seconds... ", logging.INFO)
                try:
                    destination_path_converted = destination_path.replace('.svg', '.png')
                    svg2png(url=destination_path, write_to=destination_path_converted)
                    # image = pyvips.Image.new_from_file(destination_path, access='sequential')
                    # image.write_to_file(destination_path_converted)
                    os.remove(destination_path)
                    # MAJ des infos de référence
                    original_filename= original_filename.replace('.svg', '.png')
                    unique_sanitized_filename = unique_sanitized_filename.replace('.svg', '.png')
                    mime = "image/png"
                    log_debug(f"Svg {original_filename} converted ", logging.WARNING)
                except:
                    log_debug(f"{bcolors.FAIL}Error converting svg {original_filename} {bcolors.ENDC}", logging.NOTSET)
                    log_debug(f"Error converting svg {original_filename}", logging.WARNING)
            
            files_info_dict[hash_md5] = FileInfo(file_id, unique_sanitized_filename, original_filename, mime, file_size, file_type, hash_md5)    
        else:
            log_debug(f"--- Resource with empty element for one note", logging.DEBUG)

    return files_info_dict


def download_image(href, dest_folder):
    """Download image from a href link

    Args:
        href: img link
        dest_folder (_type_): _description_

    Returns:
        False, String message d'erreur
        True, FileInfo(file_id, unique_sanitized_filename, original_filename, mime_type=None, file_size=file_size, file_type="Image")
    """
    # Fonction de téléchargement de l'image
                # Elle doit 
                    # déposer le fichier dans le sous-dossier files en ajoutant une chaine aléatoire devant (généré via generate_random_id())
                    # retourner un état OK, le nom du fichier avec la chaine aléatoire (files\xxxxxxxxxmonfichier.jpg), le hash du fichier (hash_md5 = hashlib.md5(monfichier).hexdigest()), le nom du fichier d'origine avec l'extension et l'extension seule)
                # Et si une erreur est rencontrée, retourner un état NOK et un message
                    # Message = "Image non trouvée = " + lien si c'est une erreur web ou un autre message plus générique le cas échéant
                    
    try:
        # Télécharger l'image à partir du lien href
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        req = urllib.request.Request(href,headers={'User-Agent': user_agent})
        response = urllib.request.urlopen(req)
        if response.status == 200:
            # Lire le contenu de la réponse
            image_data = response.read()
            
            # Calculer le hash MD5 de l'image téléchargée
            hash_md5 = hashlib.md5(image_data).hexdigest()
            
            # Générer un nom de fichier aléatoire pour éviter les conflits
            random_id = generate_random_id()
            original_filename=os.path.basename(urlparse(href).path)
            filename = f"{hash_md5}_{original_filename}"
            
            #id du fichier json
            file_id :str = "file" + generate_random_id()
            
            # Obtenir le nom du fichier original et son extension
            file_extension = os.path.splitext(filename)[1]
            sanitized_filename = sanitize_filename(original_filename)
            unique_sanitized_filename = hash_md5 + sanitized_filename
            
            # Enregistrer l'image dans le dossier de destination
            files_path = os.path.join(dest_folder, "files")
            full_path = os.path.join(files_path, unique_sanitized_filename)
            if not os.path.exists(files_path):
                os.makedirs(files_path)
            with open(full_path, 'wb') as outfile:
                outfile.write(image_data)
            file_size = os.path.getsize(full_path) * 8

            
            files_info_dict = FileInfo(file_id, unique_sanitized_filename, original_filename, mime_type=None, file_size=file_size, file_type="Image", hash_md5=hash_md5)    
            
            
            # Retourner les informations sur l'image téléchargée
            return True, files_info_dict
        else:
            # Retourner un état d'erreur si le téléchargement a échoué
            return False, f"Failed to download image from {href}"
    except Exception as e:
        # Retourner un état d'erreur si une exception est levée lors du téléchargement
        return False, f"An error occurred while downloading image from {href}: {e}"

    

def process_details_to_json(content: ET.Element, page_model: Model.Page, working_folder: str):
    """ Retrieves note details """
    log_debug(f"- Retrieving note details", logging.DEBUG)
    title_element = content.find("title")
    title = title_element.text if title_element is not None else "Default Title"   
    log_debug(f"- Note title : {title}", logging.NOTSET)
    page_model.edit_details_key("name", title)
    
    # created date
    created_date_element = content.find("created")
    if created_date_element is not None and created_date_element.text is not None:
        created_date : str = created_date_element.text
        date_format = "%Y%m%dT%H%M%SZ"
        date_object = datetime.strptime(created_date, date_format)
        created_timestamp = int(date_object.timestamp())
        page_model.edit_details_key("createdDate", created_timestamp)
    
    # Modified date as converted date
    timestamp_converted = int(time.time())
    page_model.edit_details_key("lastModifiedDate", timestamp_converted)

    # tags
    tags_list = content.findall("tag")
    tags_id_lists=[]
    for element in tags_list:
        if element.text is not None:
            log_debug(f"Ajout de l'item tag '{element.text}'",logging.NOTSET)
            # On génère une clé, unique pour chaque tag pour éviter les doublons
            try:
                tag_key = (hashlib.md5(element.text.encode()).hexdigest())[:24]
                tag_id = "id_"+tag_key
            except Exception as e:
                log_debug(f"Error during tag processing : {e}", logging.ERROR)
                continue
            # On ne traite que si ce tag  n'est pas traité (donc fichier inexistant)
            filename = f"tagItem_{sanitize_filename(tag_key)}.json"
            filepath = os.path.join(working_folder, filename)
            if not os.path.exists(filepath):
                # On génère le modèle
                tag_option: Model.Tag_Option = Model.Tag_Option()
                # On renseigne key et uniqueKey ("opt-" + key), et l'id
                tag_option.edit_name(element.text)
                tag_option.edit_key(tag_key)
                tag_option.edit_id(tag_id)
                # On met une couleur défini suivant la clé (pour avoir des couleurs différentes mais fixe pour un même tag)
                colors = {"grey", "yellow", "orange", "red", "pink", "purple", "blue", "ice", "teal", "lime"}
                hex_value = int(tag_key, 16)
                index = hex_value % len(colors)
                selected_color = list(colors)[index]
                tag_option.edit_color(selected_color)
                # On génère le fichier à partir de Key (donc unique pour chaque chaine)
                with open(filepath, 'w', encoding='utf-8') as file:
                    json.dump(tag_option.to_json(), file, indent=2)
            else:
                log_debug(f"File '{filename} already exist'",logging.NOTSET)
            # Ajout au json de la note
            tags_id_lists.append(tag_id)
        else:
            log_debug(f"Empty text for tag", logging.WARNING)
    if tags_id_lists:
        page_model.edit_details_key("202312evernotetags",tags_id_lists)
    
    return title # on retourne le titre de la note, utilise pour la suite

def extract_text_from_codeblock(content):
    """Extrait le texte d'un codeblock : ajout de saut de ligne si besoin et nettoyage des balises

    Args:
        content (_type_): contenu html

    Returns:
        _type_: Chaine texte nettoyé
    """
    extracted_text = ""

    for div_child in content. children:
        # Traitement d'un bloc
        if div_child.name:
            # S'il a un un tag, on l'envoi en récursif pour le détailler
            extracted_text += extract_text_from_codeblock(div_child) 
            div_text=extract_top_level_text(div_child)
            # Si c'est une balise type bloc avec du texte, on ajoute un saut de ligne à la fin
            if div_text and div_child.name in liste_balisesBlock:
                    extracted_text += "\n" 
            
        # Plus de balise, juste du texte : on l'ajoute
        else:
            extracted_text += div_child.string.rstrip()
            
    return extracted_text

def process_codeblock(content, div_id, page_model: Model.Page):
    """Process code block with all content including children tags
    
    Args:
        content (_type_): _description_
        page_model (Model.Page): _description_
    """
    extracted_text = extract_text_from_codeblock(content)
            
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
    page_model.edit_block_key(div_id,"lang",text_language, master_key="fields")
    
    pass

def process_tableV2(table_content, page_model: Model.Page):
    log_debug(f"- Traitement table...", logging.DEBUG)
    # Création d'une matrice de la table
    try:
        table_matrix = libs.table_parse.parseTable(table_content)
    except Exception as ex:
        log_debug(f"- Erreur lors du traitement de la table : {ex}", logging.ERROR)
        return
    
    
    # Création bloc table
    table_id = generate_random_id()
    page_model.add_block(table_id, shifting=extract_shifting_left(table_content))
    page_model.edit_block_key(table_id, "table", {})
    
    # Création bloc liste colonnes et génération des ID des lignes
    columns_list_id = generate_random_id()
    column_ids = [generate_random_id() for _ in range(len(table_matrix[0]))]
    
    page_model.add_block(columns_list_id)
    page_model.edit_block_key(columns_list_id, "style", "TableColumns", master_key="layout")
    # Ajout de l'id du "bloc liste colonnes" aux enfants du bloc table
    page_model.add_children_id(table_id,columns_list_id)

    # Création bloc liste lignes
    rows_list_id = generate_random_id()
    row_ids = [generate_random_id() for _ in range(len(table_matrix))]
    page_model.add_block(rows_list_id)
    page_model.edit_block_key(rows_list_id, "style", "TableRows", master_key="layout")
    # Ajout de l'id du "bloc liste colonnes" aux enfants du bloc table
    page_model.add_children_id(table_id,rows_list_id)
    
    # Récup col
    col_list = table_content.find_all('col')

    # Création des colonnes (avec élément tableColumn et la largeur)
    for col_index, col_id in enumerate(column_ids):
        # TODO width; et style?
        col_width = None
        # width
        if col_list:
            current_col = col_list[col_index]
            col_style = current_col.get('style')
            styles = extract_styles(col_style) if col_style else {}
            col_width_px = styles.get("width", None)
            col_width = int(col_width_px.replace("px", "")) if col_width_px else None 
        else: # largeur sur td... si c'est en px sinon on ignore
            col_style = table_matrix[0][col_index].tag.get('style')
            styles = extract_styles(col_style) if col_style else {}
            col_width_px = styles.get("width", None)
            if 'px' in col_width_px: #Si pas px, c'est % et difficiule à appliquer sur AT 
                col_width = int(col_width_px.replace("px", "")) if col_width_px else None 
        
        page_model.add_children_id(columns_list_id,col_id)
        page_model.add_block(col_id, shifting=None, width=col_width)
        page_model.edit_block_key(col_id,"tableColumn",{})
        
    # Création des lignes (avec élément tableRow et cellules dans childrenIds)
    ## TODO ajout de isHeader:true si détecté/détectable dans le enex
    for row_index, row_id in enumerate(row_ids):
        page_model.add_children_id(rows_list_id,row_id)
        page_model.add_block(row_id, shifting=None)
        page_model.edit_block_key(row_id,"tableRow",{})
        
        # TODO : récupération du style
        
        # Création des cellules de la ligne, avec gestion du contenu (mise en forme et image)
        for col_index, element in enumerate(table_matrix[row_index]):
            cell_id = f"{row_id}-{column_ids[col_index]}"
            page_model.add_block(cell_id, shifting=None, text="")
            page_model.add_children_id(row_id,cell_id)
            
            # Style cellule
            styles = extract_styles(element.tag.get('style'))
                
            # Récup des infos
            if "vertical-align" in styles and styles["vertical-align"] == "middle":
                page_model.edit_block_key(cell_id,"verticalAlign","VerticalAlignMiddle")
            if "color" in styles:
                param = extract_color_from_style(styles["color"])
                page_model.edit_text_key(cell_id,"color",param)
            if 'background-color' in styles:
                param = extract_color_from_style(styles["background-color"])
                page_model.edit_block_key(cell_id,"backgroundColor",param)

            # Trouver les balises de type bloc et les traiter, puisque AT ne gère pas de bloc dans un tableau...
            # div,p : saut de ligne
            # hr : on vire
            # h1/2/3... : gras
            # en-media et img / li / pre : à traiter quand AT les gèrera
            # Li : à traiter ?
            # ['div', 'p', 'hr',  'h1', 'h2', 'h3','h4', 'h5', 'h6','en-media','table', 'img','li', 'pre']
            cleaned_cell = copy.copy(element.tag) # attention à copier, on ne modifie pas l'objet d'origine!
            
            elt_in_cell = cleaned_cell.find_all(['div', 'p', 'hr',  'h1', 'h2', 'h3','h4', 'h5', 'h6','en-media','img','li', 'pre', 'en-todo'])
            for tag in elt_in_cell:
                has_text =  bool(extract_top_level_text(tag).strip())
                if tag.name == "li" or tag.name == 'en-todo':
                    if len([tag for tag in elt_in_cell if tag.name in ['en-todo', 'li']]) == 1 : 
                        parent_list = tag.find_parent(['ol', 'ul'])
                        if parent_list:
                            if parent_list.name == 'ol':
                                style_liste = 'Numbered'
                            if parent_list.name == 'ul' and parent_list.has_attr('style') and '--en-todo:true' in parent_list['style']:
                                style_liste = 'Checkbox'
                                if tag.has_attr('style') and '--en-checked:true' in tag['style']:
                                    page_model.edit_text_key(cell_id,"checked",True)
                            else:
                                style_liste = 'Marked'
                            page_model.edit_text_key(cell_id,"style",style_liste)
                        elif tag.name == 'en-todo' and 'checked' in tag.attrs: 
                            page_model.edit_text_key(cell_id,"style",'Checkbox')
                            if 'true' in tag['checked']:
                                page_model.edit_text_key(cell_id,"checked",True)
                            else:
                                page_model.edit_text_key(cell_id,"checked",False)
                    else: # Plusieurs blocs, impossible dans AT, on converti en texte
                        parent_list = tag.find_parent(['ol', 'ul'])
                        if parent_list:
                            if parent_list.name == 'ol':
                                tag.insert_before('-')
                            if parent_list.name == 'ul' and parent_list.has_attr('style') and '--en-todo:true' in parent_list['style']:
                                if tag.has_attr('style') and '--en-checked:true' in tag['style']:
                                    tag.insert_before('[X]')
                                else:
                                    tag.insert_before('[ ]')
                            else:
                                tag.insert_before('-')
                        # checkbox inline, qui ne peux être converti en tant que tel
                        elif tag.name == 'en-todo' and 'checked' in tag.attrs: 
                            if 'true' in tag['checked']:
                                tag.insert_before('[X]')
                            else:
                                tag.insert_before('[ ]')    
                    if tag.name == 'li' and has_text: # pas de saut de ligne à faire sur un en-todo
                        tag.insert_after('\n')   
                elif tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:  
                    page_model.edit_text_key(cell_id,"style","Header" + tag.name[1:])
                elif tag.name in ["en-media"]:
                    process_media(tag, page_model, shifting=None, cell_id=cell_id)
                elif tag.name == 'div':
                    # On note aussi le style
                    style = extract_styles(tag.get('style'))
                    if 'text-align' in style:
                        if style['text-align'] == 'center':
                            page_model.edit_block_key(cell_id,"align","AlignCenter")
                        elif style['text-align'] == 'right':
                            page_model.edit_block_key(cell_id,"align","AlignRight")
                    if has_text:
                        tag.insert_after('\n')
                tag.unwrap() 
                
            for br in cleaned_cell.find_all('br'):
                br.replace_with('\n')
            extract_text_with_formatting(cleaned_cell, cell_id, page_model)
    

def extract_text_with_formatting(div_content, div_id, page_model: Model.Page):
    """Analyze inline tags to note text formatting in the json

    Args:
        div_content (_type_): Tag content
        div_id (_type_): block id for json
        page_model (Model.Page): Page model
    """
    # Définition des balises inline à traiter
    log_debug(f"--- extract text and format ---", logging.NOTSET)
    formatting_tags = ['span', 'b', 'u', 'i', 's', 'a','font', 'strong', 'em', 'en-todo']
    div_text = extract_top_level_text(div_content)
    
    if div_text:
        # Ajout du block text
        log_debug(f"--- Add text to json : {div_text}", logging.DEBUG)
        page_model.add_text_to_block(div_id, text=div_text)
        
        
        # On récupère les tags avec pour chaque le début et fin
        for element in extract_tag_info(div_content, formatting_tags):
            start = element['start']
            end = element['end']
            tag_object=element['tag_object']
            tag_name = tag_object.name

            formatting_type = None
            param = None

            text_style = tag_object.get('style')
            styles = extract_styles(text_style) if text_style else {}
            log_debug(f"Style extrait : {styles}")
            
            # Récup des infos
            if ("font-weight" in styles and styles["font-weight"] == "bold") or tag_name == 'b' or tag_name == 'strong':
                formatting_type = "Bold"
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} de {start} à {end}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if ("text-decoration" in styles and styles["text-decoration"] == "underline") or tag_name == 'u':
                formatting_type = "Underscored"
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} de {start} à {end}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if ("font-style" in styles and styles["font-style"] == "italic") or tag_name == 'i' or tag_name == 'em':
                formatting_type = "Italic"
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} de {start} à {end}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if ("text-decoration" in styles and styles["text-decoration"] == "line-through") or tag_name == 's':
                formatting_type = "Strikethrough"
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} de {start} à {end}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if "color" in styles or tag_object.get('color'):
                formatting_type = "TextColor"
                if "color" in styles:
                    color_value = styles["color"]
                else:
                    color_value = tag_object.get("color")
                param = extract_color_from_style(color_value)
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} = {param} de {start} à {end} -- Couleur originelle : {color_value}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if 'background-color' in styles:
                formatting_type = "BackgroundColor"
                param = extract_color_from_style(styles["background-color"])
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            if tag_name == 'a':
                formatting_type = "Link"
                param = tag_object.get('href')
                #log_debug(f"Ajout format {formatting_type if formatting_type else None} de {start} à {end}")
                page_model.add_mark_to_text(div_id, start, end, mark_param=param if param else None, mark_type=formatting_type if formatting_type else None)
            # cas de ces checkbox, en balise autofermante devant le texte!
            if tag_name == 'en-todo' and 'checked' in tag_object.attrs: 
                log_debug(f"{bcolors.FAIL}checked : {div_id} mis en checked {bcolors.ENDC}", logging.NOTSET)
                page_model.edit_text_key(div_id,"style",'Checkbox')
                if 'true' in tag_object['checked']:
                    page_model.edit_text_key(div_id,"checked",True)
                else:
                    page_model.edit_text_key(div_id,"checked",False)

def ask_password_gui(prompt:str):
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    password = simpledialog.askstring("Decryption password", prompt, show='*')
    root.destroy()  # Détruire la fenêtre principale
    return password

def decrypt_block(crypted_soup:BeautifulSoup):
    """Déchiffrement des blocs chiffrés anytype et remplacement dans l'object soup

    Args:
        crypted_str (BeautifulSoup): encrypt soup object
    """
    
    default_password = my_options.pwd
    
    is_pwd_ok = False
    current_pwd = None
    cleaned_text = None
    global note_title
    # Si mot de passe générique, on le teste
    if default_password:
        iterations = 50000
        keylength = 128
        
        encrypted_content = base64.b64decode(crypted_soup.text.strip())
        salt = encrypted_content[4:20]
        salthmac = encrypted_content[20:36]
        iv = encrypted_content[36:52]
        ciphertext = encrypted_content[52:-32]
        body = encrypted_content[0:-32]
        bodyhmac = encrypted_content[-32:]
        keyhmac = libs.pbkdf2.PBKDF2(default_password, salthmac, iterations, hashlib.sha256).read(keylength/8)
        testhmac = hmac.new(keyhmac, body, hashlib.sha256)
        is_pwd_ok = hmac.compare_digest(testhmac.digest(),bodyhmac)
        # Mot de passe par défaut ok
        if is_pwd_ok:
            current_pwd = default_password
            is_pwd_ok = True
        elif my_options.ask_pwd:
            if my_options.ask_pwd == "GUI":
                current_pwd = ask_password_gui(f"Default password is incorrect for the current encrypted block in '{note_title}' .\nType the specific password :")
            else:
                current_pwd = input(f"Note '{note_title}' : default password incorrect for the current encrypted block, type the specific password :")
            current_pwd = current_pwd if current_pwd else "x" # si pas de saisie
            log_debug(f"Default password is incorrect for this encrypted text, trying with specific password.", logging.WARNING)
        else: # mot de passe par défaut nok et pas de demande
            cleaned_text = '<div><span style="font-weight:bold; color:red;">Error decrypting a block here !</span></div>'
            log_debug(f"Error decrypting a block, bad default password?", logging.WARNING)
    elif my_options.ask_pwd:    # pas de mot de passe par défaut et demande active
        if my_options.ask_pwd == "GUI":
            current_pwd = ask_password_gui(f"Encrypted block in '{note_title}' .\nType the specific password :")
        else:
            current_pwd = input("Note '{note_title}' : type the specific password for the current encrypted block : ")
        current_pwd = current_pwd if current_pwd else "x" # si pas de saisie
    else:                       # ni mot de passe par défaut ni demande à faire, on quitte
        cleaned_text = '<div><span style="font-weight:bold; color:red;">Evernote encrypt block cannot be imported in Anytype !</span></div>'
        log_debug(f"Evernote encrypt block cannot be imported in Anytype.", logging.WARNING)

    # On tente de valider avec un nouveau mot de passe
    if current_pwd and not is_pwd_ok: 
        iterations = 50000
        keylength = 128
        
        encrypted_content = base64.b64decode(crypted_soup.text.strip())
        salt = encrypted_content[4:20]
        salthmac = encrypted_content[20:36]
        iv = encrypted_content[36:52]
        ciphertext = encrypted_content[52:-32]
        body = encrypted_content[0:-32]
        bodyhmac = encrypted_content[-32:]
        keyhmac = libs.pbkdf2.PBKDF2(current_pwd, salthmac, iterations, hashlib.sha256).read(keylength/8)
        testhmac = hmac.new(keyhmac, body, hashlib.sha256)
        is_pwd_ok = hmac.compare_digest(testhmac.digest(),bodyhmac)
        
    if current_pwd: # On a bien un mdp
        if is_pwd_ok: # C'est ok
            key = libs.pbkdf2.PBKDF2(current_pwd, salt, iterations, hashlib.sha256).read(keylength/8)
            aes = AES.new(key, AES.MODE_CBC, iv)
            plaintext = aes.decrypt(ciphertext)
            try:
                plaintext = plaintext.decode('utf-8')
            except UnicodeDecodeError:
                plaintext = plaintext.decode('utf-8', errors='ignore')
            cleaned_text = '<div><span style="font-weight:bold;"> Evernote block decrypted :</span>' + re.sub(r'[\x00-\x1F\x7F-\x9F]', '', plaintext) + '</div>'
            log_debug(f"Successful block decryption", logging.INFO)
        else: # Toujours NOK, on abandonne    
            cleaned_text = '<div><span style="font-weight:bold; color:red;">Error decrypting a block here !</span></div>'
            log_debug(f"Error decrypting a block, bad password?", logging.WARNING)
        
        
        
        
    if not cleaned_text:
        log_debug(f"Cleaned_text empty detected, this case is not valid!", logging.WARNING)
    else:  
        decrypted_soup = BeautifulSoup(cleaned_text, 'html.parser')       
        crypted_soup.replace_with(decrypted_soup)

def process_media(elt, page_model: Model.Page, shifting=None, cell_id=None):
    log_debug(f"Ajout en-media", logging.NOTSET)
    hash = elt.get('hash')
    if hash in files_dict:
        file_info :FileInfo = files_dict[hash]
        file_id = file_info.file_id
        original_filename = file_info.original_filename
        mime = file_info.mime_type
        file_size = file_info.file_size
        file_type = file_info.file_type
        # Redimensionné? Il faut retourner width="340px" divisé par style="--en-naturalWidth:1280" ; ex : style="--en-naturalWidth:1280; --en-naturalHeight:512;" width="340px" />
        text_style = elt.get('style')
        styles = extract_styles(text_style) if text_style else {}
                
        embed_width = elt.get('width') # Redimension dans Evernote
        original_width = styles.get("--en-naturalWidth") # Dimension naturelle de l'objet
        relative_width = None  # Ratio de la version embed, la seule valeur utilisée dans Anytype
        # On calcul, en mettant la valeur par défaut pour toutes les erreurs potentielles
        try:
            embed_width_value = float(embed_width.replace("px", ""))
            original_width_value = float(original_width)
            embed_width_int = int(embed_width_value)
            original_width_int = int(original_width_value)
            if embed_width_int != 0:
                relative_width = embed_width_int / original_width_int
        except Exception :
            relative_width = None
                
        # Format lien? 
        style_attr = elt.get('style')
        format = 'link' if style_attr and '--en-viewAs:attachment;' in style_attr else None
        
        if cell_id: # tableau : l'image sera le contenu possible du block-cellule
            page_model.add_file_to_block(cell_id, file_id = file_id, hash = hash, name = original_filename, file_type = file_type, mime = mime, size = file_size, format=format )
        else: # Sinon c'est l'arborescende de bloc de la page
            block_id = generate_random_id()
            page_model.add_block(block_id, shifting=shifting, width = relative_width)
            page_model.add_file_to_block(block_id, file_id = file_id, hash = hash, name = original_filename, file_type = file_type, mime = mime, size = file_size, format=format )
        
def process_content_to_json(content: str, page_model, note_id, working_folder :str):
    """Find <en-note> tag from content to create the parent element and calling a function for child elements

    Args:
        content (str): content of <content< from source file
        page_model (_type_): Page object generated for this note 
        note_id (_type_): root id racine (used to link files, blocs, ... )
        files_dict (_type_): Dictionnary of available files 
    """
    global note_title
    log_debug(f"- Converting content for note '{note_title}'", logging.DEBUG)
    # Converting to soup for specific html parsing
    cleaned_html = content.replace('\n', '').replace('\r', '') # suppression des sautes de lignes en dur
    soup = BeautifulSoup(cleaned_html, 'html.parser')  # Utilisation de l'analyseur HTML par défaut

    # Créer l'élément JSON pour la première div (shifting = -1)
    root_block = soup.find('en-note')
    if root_block:
        # Déchiffrement des éventuels blocs chiffrés
        for en_crypt in soup.find_all('en-crypt'):
            decrypt_block(en_crypt)
        
        block_id = note_id
        page_model.add_block(block_id,-1)
        
        
        # cas de texte avant les 1ères balises
        div_text = extract_top_level_text(root_block)
        if div_text:
            log_debug(f"Text out of html block tag {div_text}", logging.NOTSET)
            div_id = generate_random_id()
            page_model.add_block(div_id,shifting=0)
            extract_text_with_formatting(root_block, div_id, page_model)
            
        process_div_children(root_block, page_model, note_id, working_folder)
        
    else:
        log_debug(f"'en-note' element not find", logging.ERROR)

def process_div_children(div, page_model: Model.Page, note_id, working_folder :str):
    """Process all child tag

    Args:
        div (_type_): _description_
        page_model (Model.Page): _description_
        files_dict (_type_): _description_
        table (bool, optional): Indicate if it's a loop for a table or the default treatment. Defaults to False.
    """
    log_debug(f"- Converting childrens...", logging.DEBUG)

    children = div.find_all(liste_balisesBlock)
    for child in children:
        if 'table' in [parent.name for parent in child.parents]:
            log_debug(f"Bloc contenu dans une table, on passe!",logging.NOTSET)
            continue

        log_debug(f"{bcolors.HEADER} Traitement bloc : {bcolors.ENDC} {child}", logging.NOTSET)
        div_id = generate_random_id()
        
        # Collecter tous les parents en une seule fois
        all_parents = child.find_parents()
        
        shifting_left = 0
        # Calcul du décalage (= arborescence des blocs), selon le décalage via style ou liste
        nested_level = sum(1 for parent in all_parents if parent.name in ['ol', 'ul'])
        # Calculer le décalage basé sur le niveau d'imbrication
        shifting_left = (40 * (nested_level-1) if nested_level > 1 else 0) + extract_shifting_left(child)

        div_text = extract_top_level_text(child)

        # On commence par les blocs sans texte
        if child.name == 'hr':
            page_model.add_block(div_id, shifting=shifting_left)
            page_model.edit_block_key(div_id, "div",{})         
        # Traitement des fichiers à intégrer
        elif child.name == 'en-media':
            log_debug(f"{bcolors.OKCYAN}Ajout enfant en-media{bcolors.ENDC}", logging.NOTSET)
            hash = child.get('hash')
            if hash in files_dict:
                file_info :FileInfo = files_dict[hash]
                file_id = file_info.file_id
                original_filename = file_info.original_filename
                mime = file_info.mime_type
                file_size = file_info.file_size
                file_type = file_info.file_type
                # Redimensionné? Il faut retourner width="340px" divisé par style="--en-naturalWidth:1280" ; ex : style="--en-naturalWidth:1280; --en-naturalHeight:512;" width="340px" />
                text_style = child.get('style')
                styles = extract_styles(text_style) if text_style else {}
                
                embed_width = child.get('width') # Redimension dans Evernote
                original_width = styles.get("--en-naturalWidth") # Dimension naturelle de l'objet
                relative_width = None  # Ratio de la version embed, la seule valeur utilisée dans Anytype
                # On calcul, en mettant la valeur par défaut pour toutes les erreurs potentielles
                try:
                    embed_width_value = float(embed_width.replace("px", ""))
                    original_width_value = float(original_width)
                    embed_width_int = int(embed_width_value)
                    original_width_int = int(original_width_value)
                    if embed_width_int != 0:
                        relative_width = embed_width_int / original_width_int
                except Exception :
                    relative_width = None
                
                
                # Format lien? 
                style_attr = child.get('style')
                format = 'link' if style_attr and '--en-viewAs:attachment;' in style_attr else None
                page_model.add_block(div_id, shifting=shifting_left, width = relative_width)
                page_model.add_file_to_block(div_id, file_id = file_id, hash = hash, name = original_filename, file_type = file_type, mime = mime, size = file_size, format=format )
        
        # img avec source web
        elif child.name == 'img':
            # Exemple : <img style="--en-naturalWidth:1440; --en-naturalHeight:810;" height="476px" width="701px" src="https://www.exemple.com/truc/mon-image.jpg" />
            # Récupération du lien
            href = child.get('src')
            log_debug(f"{bcolors.OKCYAN}image à télécharger :{bcolors.ENDC} {href}", logging.NOTSET)
            download_state, download_content = download_image(href,working_folder)
            log_debug(f"{download_content}", logging.NOTSET)
            
            if download_state:
                # Enregistrement du bloc
                # Gestion redimensionnement
                text_style = child.get('style')
                styles = extract_styles(text_style) if text_style else {}
                embed_width = child.get('width') # Redimension dans Evernote
                original_width = styles.get("--en-naturalWidth") # Dimension naturelle de l'objet
                relative_width = None  # Ratio de la version embed, la seule valeur utilisée dans Anytype
                # On calcul, en mettant la valeur par défaut pour toutes les erreurs potentielles
                try:
                    embed_width_value = float(embed_width.replace("px", ""))
                    original_width_value = float(original_width)
                    embed_width_int = int(embed_width_value)
                    original_width_int = int(original_width_value)
                    if embed_width_int != 0:
                        relative_width = embed_width_int / original_width_int
                except Exception :
                    relative_width = None
                
                page_model.add_block(div_id, shifting=shifting_left, width = relative_width)
                page_model.add_file_to_block(div_id, file_id = download_content.file_id, hash = download_content.hash_md5, name = download_content.original_filename, 
                                             file_type = download_content.file_type, mime = None, size = download_content.file_size, format="Image" )
                
                # Création du json du fichier
                img_dict={} 
                img_dict[download_content.hash_md5] = download_content
                process_file_to_json(note_id,img_dict,working_folder)
                
                
            else:
                download_content:str
                page_model.add_block(div_id, shifting=shifting_left)
                page_model.add_text_to_block(div_id, text=download_content) 
                log_debug(f"{download_content}", logging.WARNING)

        # Traitement bloc code (div racine sans texte); "-en-codeblock:true" et "--en-codeblock:true" co-existent...
        elif (child.name == 'div' and 'style' in child.attrs and '-en-codeblock:true' in child['style']) or child.name=='pre':
            log_debug(f"{bcolors.OKCYAN}Ajout enfant codeblock{bcolors.ENDC}", logging.NOTSET)
            process_codeblock(child, div_id, page_model)
        #Traitement table
        elif child.name == 'table':
            log_debug(f"{bcolors.OKCYAN}Ajout enfant table{bcolors.ENDC}", logging.NOTSET)
            process_tableV2(child, page_model)
        # Traitement des blocs demandant du contenu texte
        elif div_text:
            # les div enfant des blocs codes doivent être exclues du traitement global
            log_debug(f"{bcolors.HEADER}... bloc avec texte... {bcolors.ENDC}", logging.NOTSET)
            has_codeblock_parent = False
            for parent in all_parents:
                if parent.name == 'pre' or (parent.name == 'div' and 'style' in parent.attrs and '-en-codeblock:true' in parent['style']):
                    has_codeblock_parent = True
            
            if child.name == 'div' and has_codeblock_parent:
                log_debug(f"{bcolors.HEADER} Parent codeblock ou pre -> on passe {bcolors.ENDC}", logging.NOTSET)
                pass
            # Traitements spécifiques
            else:
                # Traitement spécifique pour les listes!
                parent_list = None
                # Parcourir tous les parents pour vérifier les conditions spécifiques
                for parent in all_parents:
                    if parent.name in ['ol', 'ul']:
                        parent_list = parent
                        break 
                
                # Récupération styles du bloc
                style = extract_styles(child.get('style'))
                
                # Traitement des embed avant de récupérer le texte formatté (donc les <a>)
                if '--en-viewAs' in style and style['--en-viewAs'] != 'minimal':
                    # Récupération du lien
                    a_tag = child.find('a')
                    if a_tag:
                        href = a_tag.get("href")  
                        if href:
                            # Calcul ratio
                            ratio = None
                            if style['--en-viewAs'] == 'youtube-video-small':
                                ratio = 0.33
                            if style['--en-viewAs'] == 'youtube-video-large':
                                ratio = 0.5
                            log_debug(f"Embed size : {ratio} for original {style['--en-viewAs']}", logging.NOTSET)
                            page_model.add_block(div_id, shifting=shifting_left, width=ratio)
                            page_model.add_embed_to_block(div_id, url=href, processor="Youtube")
                            continue # On arrête le traitement pour ce bloc 
                        else:
                            log_debug("Embed block without href in a tag", logging.WARNING)
                    else:
                        log_debug("Embed block without a tag", logging.WARNING)
                    
                    continue
                    
                # Sinon on créé le bloc simple et on traite le texte inline  
                page_model.add_block(div_id, shifting=shifting_left)
                extract_text_with_formatting(child, div_id, page_model)
                
                
                if 'text-align' in style:
                    log_debug(f"Extraction style text_align : {style}",logging.NOTSET)
                    if style['text-align'] == 'center':
                        page_model.edit_block_key(div_id,"align","AlignCenter")
                    elif style['text-align'] == 'right':
                        page_model.edit_block_key(div_id,"align","AlignRight")
                        
                # Et style si c'est une liste
                if parent_list:
                    log_debug(f"C'est une liste", logging.NOTSET)
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
                parent_title = None
                for parent in all_parents:
                    if parent.name in ['h1', 'h2', 'h3']:
                        parent_title = parent
                        break  # On peut arrêter la boucle dès qu'on trouve le premier titre
                if  child.name in ['h1', 'h2', 'h3']:
                    page_model.edit_text_key(div_id,"style","Header" + child.name[1:])
                elif parent_title:
                    page_model.edit_text_key(div_id,"style","Header" + parent_title.name[1:])
                
                # Autres niveaux de titres, inexistants dans Anytype : on met en gras
                if  child.name in ['h4', 'h5', 'h6'] :
                    text_lenght = len(div_text)
                    page_model.add_mark_to_text(div_id, 0, text_lenght, mark_type="Bold")
        else:
            log_debug(f"{bcolors.WARNING}Balise non traité ou sans contenu texte, on passe{bcolors.ENDC}", logging.NOTSET)

def process_file_to_json(page_id :str, files_dict_todo :dict[str, FileInfo], working_folder :str):
    # On génère le modèle json
    for hash_md5, file_info in files_dict_todo.items():
        # On génère le modèle json pour chaque fichier
        file_json: Model.File_Object = Model.File_Object()
        file_json.edit_id(file_info.file_id)
        file_json.edit_backlinks(page_id)
        # Génération du nom : ici il faut retirer l'extension
        filename_without_extension = os.path.splitext(file_info.original_filename)[0]
        file_json.edit_name(filename_without_extension)
        file_with_path = "files/"+file_info.unique_filename
        file_json.edit_source(file_with_path)
        # Chemin complet pour enregistrer le fichier JSON
        filepath = os.path.join(working_folder, f"{file_info.file_id}.json")
        # On génère le fichier à partir de Key (donc unique pour chaque chaîne)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(file_json.to_json(), file, indent=2)
    
    

def convert_files(enex_files_list: list, options: Type[Options]):
    """Convert enex file from the list into json files

    Args:
        enex_files_list (list): list of enex file to convert

    Returns:
        string: number of notes converted
    """
    
    log_debug(f"-----CONVERTING-----", logging.DEBUG)
    if not enex_files_list:
        log_debug("No file to convert.", logging.INFO)
        return

    source_folder = os.path.dirname(enex_files_list[0])
    if options.zip_result:
        working_folder = os.path.join(source_folder, "Working_folder")
    else:
        working_folder = os.path.join(source_folder, "Converted_files")
    os.makedirs(working_folder, exist_ok=True)
    files_dest_folder = os.path.join(working_folder, "files")
    
    # Add Relation "Evernote tag"
    dirname = os.path.dirname(__file__)
    relation_file = os.path.join(dirname, "libs/Evernote_Tag_Relation.json")
    shutil.copy(relation_file,working_folder)
    
    nb_notes = 0
    for enex_file in enex_files_list:
        log_debug(f"Converting file {os.path.basename(enex_file)}...", logging.INFO)
        with open(enex_file, 'r', encoding='utf-8') as xhtml_file:
            file_content = xhtml_file.read()
            if not file_content:
                log_debug(f"No content in file", logging.ERROR)
                return
        
        try:
            root = ET.fromstring(file_content)
        except ET.ParseError as e:
            log_debug(f"XML parsing error : {e}", logging.ERROR)
            continue
        except Exception as e:
            log_debug(f"XML treatment error : {e}", logging.ERROR)
            continue
        
        # Parcours des notes dans le fichier
        for note_xml in root.iter("note"):
            log_debug(f"Treatment note {nb_notes}...", logging.INFO)
            
            # Attribution de l'ID de la page
            note_id :str = generate_random_id()
            
            # Traitement des fichiers (base64 vers fichiers) avant le reste car référencé dans le parcours des notes
            global files_dict
            files_dict = get_files(note_xml, files_dest_folder)
            log_debug("Contenu de files_dict :", logging.NOTSET)
            [log_debug(f"{hash_md5}: (file_id={file_info.file_id}, file_name={file_info.unique_filename}, original file_name={file_info.original_filename}, mime_type={file_info.mime_type}, file_size={file_info.file_size}, file_type={file_info.file_type})", logging.NOTSET) for hash_md5, file_info in files_dict.items()]

            # Génération des JSON fichiers
            process_file_to_json(note_id, files_dict, working_folder)
            
            # Utilisation de la classe Model.Page pour créer le JSON
            page_model: Model.Page = Model.Page()

            # Extraction du contenu de la balise <content> et traitement
            content_element = note_xml.find('content')
            if content_element is None or content_element.text is None:
                log_debug(f"Note {nb_notes} has no content!", logging.DEBUG)
                continue
            
            # Traitement des balises xml autre que content
            global note_title 
            note_title= process_details_to_json(note_xml, page_model, working_folder)
            
            content: str = content_element.text
            process_content_to_json(content, page_model, note_id, working_folder)
            
            

            # Nettoyer les clés "shifting" si nécessaire
            page_model.cleanup()
            
            # Filename with the create date, in case several notes have the same title
            creation_date: str = page_model.get_creation_date()
            filename = f"{sanitize_filename(note_title)}_{creation_date}.json"
            with open(os.path.join(working_folder, filename), 'w', encoding='utf-8') as file:
                json.dump(page_model.to_json(), file, indent=2)
            nb_notes += 1
    
    # On zip le résultat
    if options.zip_result:
        log_debug(f"Create zip file", logging.DEBUG)
        current_time = datetime.now()
        zip_name = current_time.strftime("ConvertedFiles_%d%m%Y_%H%M%S")
        zip_path = os.path.join(source_folder, zip_name)
        shutil.make_archive(zip_path, 'zip', working_folder)
        shutil.rmtree(working_folder)

    log_debug(f"Conversion completed: {nb_notes} notes converted", logging.INFO)
    return nb_notes
            

def main():
    enex_files =[]
    my_options.is_debug=False
    my_options.zip_result=True
    
    parser = argparse.ArgumentParser(description="Convert ENEX files.")
    parser.add_argument("--enex_sources", nargs="+", help="List of ENEX files to convert", required=True)
    parser.add_argument("--nozip", action="store_true", default=False, help="Desactivate creation of a zip file")
    parser.add_argument("--debug", action="store_true", default=False, help="Create a debug file")
    parser.add_argument("--test", action="store_true", default=False, help="test with a defaut file")
    parser.add_argument("--pwd", help="Password to decrypt encrypted Evernote notes")
    parser.add_argument("--ask_pwd", action="store_true" , help="Ask password for each encrypt text if default empty or incorrect")
    
    args = parser.parse_args()
    
    if args.enex_sources:
        for source in args.enex_sources:
            if os.path.isdir(source):
                if os.path.exists(source):
                    enex_files_from_folder = [os.path.join(source, f) for f in os.listdir(source) if f.endswith('.enex')]
                    enex_files.extend(enex_files_from_folder)
                else:
                    log_debug(f"Error: Directory {source} does not exist.", logging.WARNING)
            elif os.path.isfile(source):
                if source.endswith('.enex'):
                    if os.path.exists(source):
                        enex_files.append(source)
                    else:
                        log_debug(f"Error: File {source} does not exist.", logging.WARNING)
                else:
                    log_debug(f"Warning: {source} is not an ENEX file.", logging.WARNING)
            else:
                log_debug(f"Error: {source} is not a folder nor a file?", logging.ERROR)
    elif args.test:
        # Default value for dev ;-)
        enex_directory = 'Tests/Temp/'
        enex_files = [os.path.join(enex_directory, f) for f in os.listdir(enex_directory) if f.endswith('Bug OSI.enex')]
        
        
    # my_options.tag = "Valeur pour le tag"
    my_options.is_debug = args.debug # Faux par défaut
    my_options.zip_result = not args.nozip # Vrai par défaut
    my_options.pwd = args.pwd
    my_options.ask_pwd="CLI" if args.ask_pwd else None
        
    log_debug(f"Launched with CLI {__version__}, ZIP = {my_options.zip_result}, DEBUG = {my_options.is_debug}", logging.DEBUG)
    # Liste des fichiers enex dans le répertoire
    if enex_files:
        convert_files(enex_files, my_options)
        
    else:
        log_debug(f"No enex file to convert, check if the 'enex_sources' parameter is correct.", logging.ERROR)
    

if __name__ == "__main__":
    main()