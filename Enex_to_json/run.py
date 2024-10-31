import sys
import converter
import gui
from libs._version import __version__

"""Version"""
version="v1.01"

"""Launch CLI if arguments provided, else GUI"""
def main():
    if len(sys.argv) > 1:
        converter.main()  # Appel de la fonction main dans converter.py pour gérer les arguments en ligne de commande
    else:
        gui.main()  # Appel de la fonction pour ouvrir l'interface utilisateur

if __name__ == "__main__":
    main()