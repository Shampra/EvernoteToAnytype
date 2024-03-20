import sys
import converter
import gui

"""Version"""
version="v0.8.4"

"""Launch CLI if arguments provided, else GUI"""
def main():
    if len(sys.argv) > 1:
        converter.main(version)  # Appel de la fonction main dans converter.py pour gérer les arguments en ligne de commande
    else:
        gui.main(version)  # Appel de la fonction pour ouvrir l'interface utilisateur

if __name__ == "__main__":
    main()