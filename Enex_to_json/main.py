import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import customtkinter as ctk
import converter  # Importez le module "traitement"
import os

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

list_files_to_convert = []

def get_enex_files(input_path):
    global list_files_to_convert
    list_files_to_convert = []
    print(input_path)
    for item in input_path:
        if os.path.exists(item) and os.path.isfile(item) and item.lower().endswith(".enex"):
            list_files_to_convert.append(os.path.abspath(item))
        elif os.path.isdir(item):
            for filename in os.listdir(item):
                file_path = os.path.join(item, filename)
                if os.path.isfile(file_path) and file_path.lower().endswith(".enex"):
                    list_files_to_convert.append(os.path.abspath(file_path))
    # On affiche pour informer
    print(list_files_to_convert)
    print_files_to_gui(list_files_to_convert)


def print_files_to_gui(file_list):
    num_files = len(file_list)
    
    if num_files > 0:
        convert_button.configure(state=tk.NORMAL)
        # Affiche une tooltip avec la liste des fichiers
        info_label.configure(text=f"Number of ENEX files to convert: {len(file_list)}")
        # ToolTip(info_label, "\n".join(file_list))
    else:
        convert_button.configure(state=tk.DISABLED)
        info_label.configure(text=f"No ENEX file to convert")
        # ToolTip(info_label, "Files must be enex only.")


def browse_files():
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        get_enex_files(file_paths)


def on_drop(event):
    # Enlevez les accolades du chemin
    drop_paths = event.data[1:-1]
    file_paths = drop_paths.split("} {")
    if file_paths:
        get_enex_files(file_paths)


def convert():
    options = {
        # 'carnet': carnet_var.get(),
        # 'tags': tags_var.get()
    }
    result = converter.convert_files(list_files_to_convert, options)
    convert_button.configure(state=tk.DISABLED)
    info_label.configure(text=f"{result} enex files converted")


root = Tk()
root.geometry("479x184+720+298")
root.title("Get file path")

# Désactiver le redimensionnement automatique
root.grid_propagate(False)

FrameOptions = tk.LabelFrame(root, text="Options")
FrameOptions.grid(row=0, column=1, padx=10, pady=10, rowspan=5, sticky='nsew')

# carnet_var = ctk.BooleanVar()
# carnet_checkbox = ctk.CTkCheckBox(FrameOptions, text="Import Notebook information", variable=carnet_var)
# carnet_checkbox.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# tags_var = ctk.BooleanVar()
# tags_checkbox = ctk.CTkCheckBox(FrameOptions, text="Option to come...", variable=tags_var)
# tags_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky='w')

start_text = ctk.CTkLabel(root, text="To start, select your ENEX files or folder.\nYou can drop them here too.")
start_text.grid(row=0, column=0, padx=10, pady=10)

# Laissez une autre ligne vide
info_label = ctk.CTkLabel(root, text="")
info_label.grid(row=1, column=0, padx=10, pady=10, rowspan=2)

select_button = ctk.CTkButton(root, text="Select files or folder", command=browse_files)
select_button.grid(row=3, column=0, padx=10, pady=10)

convert_button = ctk.CTkButton(root, text="Convertir", command=convert, state=tk.DISABLED, height=24, width=107)
convert_button.grid(row=4, column=0, padx=10, pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()