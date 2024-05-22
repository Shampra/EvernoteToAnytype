import sys
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import Tk, filedialog
import customtkinter as ctk
import converter  # Import du module "traitement"
import os
from models.options import Options
import base64

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

list_files_to_convert = []

class Interface:
    def __init__(self, root):
        self.root = root
        self.list_files_to_convert = []
        self.info_label = None
        self.convert_button = None
        self.zip_var = None
        self.debug_var = None
    
    def icon_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    def get_enex_files(self, input_path):
        self.list_files_to_convert = []
        for item in input_path:
            if os.path.exists(item) and os.path.isfile(item) and item.lower().endswith(".enex"):
                self.list_files_to_convert.append(os.path.abspath(item))
            elif os.path.isdir(item):
                for filename in os.listdir(item):
                    file_path = os.path.join(item, filename)
                    if os.path.isfile(file_path) and file_path.lower().endswith(".enex"):
                        self.list_files_to_convert.append(os.path.abspath(file_path))
        self.print_files_to_gui(self.list_files_to_convert)

    def print_files_to_gui(self, file_list):
        num_files = len(file_list)
        if num_files > 0:
            self.convert_button.configure(state=tk.NORMAL)
            self.info_label.configure(text=f"Number of ENEX files to convert: {len(file_list)}")
        else:
            self.convert_button.configure(state=tk.DISABLED)
            self.info_label.configure(text=f"No ENEX file to convert")

    def browse_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.get_enex_files(file_paths)

    def on_drop(self, event):
        drop_paths = event.data[1:-1]
        file_paths = drop_paths.split("} {")
        if file_paths:
            self.get_enex_files(file_paths)

    def convert(self):
        my_options = Options()
        my_options.zip_result = self.zip_var.get()
        my_options.is_debug = self.debug_var.get()
        my_options.pwd = self.pass_var.get()
        result = converter.convert_files(self.list_files_to_convert, my_options)
        self.convert_button.configure(state=tk.DISABLED)
        self.info_label.configure(text=f"{result} note(s) converted")

    def create_interface(self):
        # Options
        FrameOptions = tk.LabelFrame(self.root, text="Options")
        FrameOptions.grid(row=0, column=1, padx=10, pady=10, rowspan=5, sticky='nsew')
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.zip_var = ctk.BooleanVar(value=True)
        zip_checkbox = ctk.CTkCheckBox(FrameOptions, text="Create a zip file", variable=self.zip_var)
        zip_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.debug_var = ctk.BooleanVar()
        debug_checkbox = ctk.CTkCheckBox(FrameOptions, text="Create a debug file", variable=self.debug_var)
        debug_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        pass_checkbox = ctk.CTkLabel(FrameOptions, text="Unique password if encrypted text")
        pass_checkbox.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        self.pass_var = ctk.StringVar()
        pass_entry = ctk.CTkEntry(FrameOptions, textvariable=self.pass_var, placeholder_text="test")
        pass_entry.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        pass_entry.configure(show='*')

        # Partie principale 
        start_text = ctk.CTkLabel(self.root, text="To start, select your ENEX files or folder.\nYou can drop them here too.")
        start_text.grid(row=0, column=0, padx=5, pady=5)

        self.info_label = ctk.CTkLabel(self.root, text="")
        self.info_label.grid(row=1, column=0, padx=10, pady=10, rowspan=2)

        select_button = ctk.CTkButton(self.root, text="Select files or folder", command=self.browse_files,text_color="white")
        select_button.grid(row=3, column=0, padx=10, pady=10)

        self.convert_button = ctk.CTkButton(self.root, text="Convertir", command=self.convert, state=tk.DISABLED,  text_color="white", height=24, width=107)
        self.convert_button.grid(row=4, column=0, padx=10, pady=10)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def main(version):
    icon = resource_path("image.ico")

    root = Tk()
    root.geometry("520x184")
    root.title(f"EN to AT converter {version}")
    root.wm_iconbitmap(icon)

    root.grid_propagate(False)

    interface = Interface(root)
    interface.create_interface()

    root.mainloop()

if __name__ == "__main__":
    main("")
