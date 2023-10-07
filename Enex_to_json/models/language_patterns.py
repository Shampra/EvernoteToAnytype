import re 

# Développement des patterns
language_patterns = {
    "scheme": [                     # because ini is not in AT
        r'\[\w+\]',            
        r'[\w_-]+\s*=\s*.+'
    ],
    "css": [
        r'^[^\n]*\:[^\;]*;$',        # propriété CSS
        r'[.#]?[\w-]+\s*{'  
    ],
    "bash": [
        r"echo\b",
        r"rem\b",
        r"set\b"
    ],
    "php": [
        r"<?php",                  # Déclaration PHP
        r"echo\b",                 # Instructions d'affichage
        r"function\b",             # Définition de fonctions
        r"\$[\w_]+",               # Utilisation de variables
        r"\bif\b",                 # Structures conditionnelles
        r"\belse\b",               # Suite à une structure conditionnelle
        r"\bwhile\b",              # Boucles while
        r"\bfor\b",                # Boucles for
        r"foreach\(",               # Boucles foreach
        r"\$array = array\(",      # Déclaration de tableaux
        r"->",                     # Utilisation d'objets
        r"getElementById",
        r"addEventListener"
    ],
    "python": [
        r"import\b",               # Importation de modules
        r"from\b",                 # Importation de modules (from ... import ...)
        r"def\b",                  # Définition de fonctions
        r"class\b",                # Définition de classes
        r"\bif\b",                 # Structures conditionnelles
        r"\belif\b",               # Suite à une structure conditionnelle
        r"else:",                  # Suite à une structure conditionnelle (else)
        r"\bfor\b",                # Boucles for
        r"\bwhile\b",              # Boucles while
        r"try:",                   # Bloc try
        r"except\b",               # Gestion des exceptions
        r"except:",                # Gestion des exceptions (except:)
        r"finally:",               # Bloc finally
        r"with\b",                  # Utilisation de context managers
        r"^\s*def\s+\w+\(.*?\):", 
        r"^\s*if\s(.*?):(.*?)(?:^\s*else:)?", 
        r"^\s*if\s(.*?):(.*?)(?:^\s*elif:)?", 
        r"^\s*try:(.*?)^\s*except(.*?):", 
        r"True|False", 
        r"==\s*(True|False)", 
        r"is\s+(None|True|False)", 
        r"^\s*if\s+(.*?)\s+in[^:\n]+:", 
        r"^\s*pass$", 
        r"print\((.*?)\)$", 
        r"^\s*for\s+\w+\s+in\s+(.*?):", 
        r"^\s*class\s+\w+\s*(\([.\w]+\))?:", 
        r"^\s*@(staticmethod|classmethod|property)$", 
        r"__repr__", 
        r'(.*?)"\s+%\s+(.*?)$', 
        r"'(.*?)'\s+%\s+(.*?)$", 
        r"^\s*raise\s+\w+Error(.*?)$", 
        r'"""(.*?)"""', 
        r"'''(.*?)'''", 
        r"^\s*# (.*?)$", 
        r"^\s*import re$", 
        r"re\.\w+", 
        r"^\s*import time$", 
        r"time\.\w+", 
        r"^\s*import datetime$", 
        r"datetime\.\w+", 
        r"^\s*import random$", 
        r"random\.\w+", 
        r"^\s*import math$", 
        r"math\.\w+", 
        r"^\s*import os$", 
        r"os\.\w+", 
        r"^\s*import os.path$", 
        r"os\.path\.\w+", 
        r"^\s*import sys$", 
        r"sys\.\w+", 
        r"^\s*import argparse$", 
        r"argparse\.\w+", 
        r"^\s*import subprocess$", 
        r"subprocess\.\w+", 
        r'^\s*if\s+__name__\s*=\s*"__main__"\s*:$', 
        r"^\s*if\s+__name__\s*=\s*'__main__'\s*:$", 
        r"self\.\w+(\.\w+)*\((.*?)\)"
    ],
    "sql": [
        r"\bSELECT\b",
        r"\bFROM\b",
        r"\bWHERE\b",
        r"\bJOIN\b",
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bSET\b",
        r"\bDELETE\b",
        r"\bCREATE\s+TABLE\b",
        r"\bALTER\s+TABLE\b",
        r"\bDROP\s+TABLE\b",
        r"\bGROUP\s+BY\b",
        r"\bORDER\s+BY\b",
        r"\bHAVING\b",
        r"\bCOUNT\(",
        r"\bSUM\(",
        r"\bMAX\(",
        r"\bMIN\(",
        r"\bAVG\(",
        r"\bINNER\s+JOIN\b",
        r"\bLEFT\s+JOIN\b",
        r"\bRIGHT\s+JOIN\b",
        r"\bFULL\s+OUTER\s+JOIN\b"
    ],
    "html": [
        r"<!DOCTYPE",
        r"<html>",
        r"</html>",
        r"<head>",
        r"</head>",
        r"<title>",
        r"</title>",
        r"<meta",
        r"<link",
        r"<script",
        r"</script>",
        r"<style",
        r"</style>",
        r"<body>",
        r"</body>",
        r"<div",
        r"</div>",
        r"<p>",
        r"</p>",
        r"</span>",
        r"<a",
        r"</a>",
        r"<img",
        r"<br",
        r"<ul",
        r"<ol",
        r"<li",
        r"<table",
        r"<tr",
        r"<th",
        r"<td"
    ],
    "powershell": [
        r"Read-Host\b",
        r"Get-.*",
        r"Set-.*",
        r"New-.*",
        r"Remove-.*",
        r"Invoke-.*"
    ],
    "csharp": [
        r"using\s+[\w.]+;",
        r"\bclass\s+\w+\b",
        r"\bpublic\s+\w+\b",
        r"\bprivate\s+\w+\b",
        r"\bprotected\s+\w+\b",
        r"\bstatic\s+\w+\b",
        r"\bvoid\s+\w+\(.*?\)\s*{",
        r"\bint\s+\w+\s*=\s*\d+;",
        r'\bstring\s+\w+\s*=\s*".*?";',
        r"\btrue\b|\bfalse\b"
    ],
    "javascript": [
        r'var\s+\w+(\s*,\s*\w+)*\s*=(.*?);'
    ]

}
