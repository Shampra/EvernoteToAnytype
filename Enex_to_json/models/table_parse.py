# Classe pour représenter un élément de tableau
from bs4 import BeautifulSoup

class TableElement(object):
    def __init__(self, row, col, tag,rowspan=1, colspan=1):
        self.row = row
        self.col = col
        self.rowspan = rowspan
        self.colspan = colspan
        self.tag = tag  

    def __repr__(self):
        return f'''TableElement(row={self.row}, col={self.col}, tag={self.tag}, rowspan={self.rowspan}, colspan={self.colspan})'''
    
    def getText(self):
        if self.tag.text:
            return self.tag.text.strip()
        else:
            return None

    def getContent(self):
        if self.tag and hasattr(self.tag, 'contents'):
            return ''.join(map(str, self.tag.contents))
        else:
            return None
        
    def hasRowspan(self):
        return self.rowspan > 1

    def hasColspan(self):
        return self.colspan > 1

# Fonction pour analyser le HTML et créer une matrice d'éléments de tableau
def parseTable(html_content:BeautifulSoup) -> [[]]:
    # Analyse le HTML avec BeautifulSoup
    soup = html_content
    # Sélectionne tous les éléments <tr>
    rows = soup.select('tr')

    table_matrix = []

    # Parcourt chaque ligne (<tr>) du tableau
    for row_index, row_tag in enumerate(rows):  
        row_elements = []
        # Sélectionne tous les éléments <th> et <td> dans la ligne
        cells = row_tag.find_all(['th', 'td'])
        # Parcourt chaque élément de la ligne
        for col_index, cell_tag in enumerate(cells):
            # Crée un objet TableElement pour représenter l'élément de tableau
            #element = TableElement(row_index, col_index, cell_tag.text.strip(),''.join(map(str, cell_tag.contents)))
            element = TableElement(row_index, col_index,cell_tag ) # cell_tag.text.strip(),''.join(map(str, cell_tag.contents))
            # Vérifie s'il y a des attributs rowspan ou colspan et les assigne à l'élément
            if cell_tag.has_attr('rowspan'):
                element.rowspan = int(cell_tag['rowspan'])
            if cell_tag.has_attr('colspan'):
                element.colspan = int(cell_tag['colspan'])
            row_elements.append(element)
        table_matrix.append(row_elements)

    # Fonction pour résoudre les éléments avec colspan
    def solveColspan(table_element):
        row, col, tag, rowspan, colspan = table_element.row, table_element.col, table_element.tag, table_element.rowspan, table_element.colspan
        table_matrix[row].insert(col + 1, TableElement(row, col, tag,rowspan, colspan - 1))
        for column in range(col + 1, len(table_matrix[row])):
            table_matrix[row][column].col += 1

    # Fonction pour résoudre les éléments avec rowspan
    def solveRowspan(table_element):
        row, col, tag, rowspan, colspan = table_element.row, table_element.col, table_element.tag, table_element.rowspan, table_element.colspan
        offset = row + 1
        table_matrix[offset].insert(col, TableElement(offset, col, tag, rowspan - 1, 1))
        for column in range(col + 1, len(table_matrix[offset])):
            table_matrix[offset][column].col += 1

    # Parcourt chaque élément de la matrice
    for row in table_matrix:
        for element in row:
            # Si l'élément a un colspan, résout-le
            if element.hasColspan():
                solveColspan(element)
            # Si l'élément a un rowspan, résout-le
            if element.hasRowspan():
                solveRowspan(element)
    return table_matrix