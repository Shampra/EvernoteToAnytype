from pygments.lexers import guess_lexer
from whats_that_code.election import guess_language_all_methods

code = """
SELECT Soft.name, Soft.ID, Version.name, Version.ID FROM glpi_softwareversions as Version
LEFT JOIN glpi_softwares as Soft ON Soft.id=Version.softwares_id WHERE Version.id NOT IN(SELECT softwareversions_id FROM glpi_items_softwareversions);
"""

lexer = guess_lexer(code)
lang_name = lexer.name
print(f"Langage détecté  par pgyments : {lang_name}")

result = guess_language_all_methods(code)
print(f"Langage détecté  par whats_that_code : {result}")