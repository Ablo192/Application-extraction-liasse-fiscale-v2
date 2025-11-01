"""
Stratégies alternatives d'extraction pour gérer les PDFs mal structurés.

Ce module fournit des méthodes de secours quand pdfplumber.extract_table()
fusionne les cellules au lieu de les séparer correctement.
"""

import re


def detecter_extraction_fusionnee(table):
    """Détecte si l'extraction du tableau a fusionné les cellules.

    Cherche des indicateurs de fusion:
    - Cellules contenant plusieurs codes séparés par \n
    - Cellules anormalement longues

    Args:
        table: Tableau extrait par pdfplumber

    Returns:
        bool: True si l'extraction semble fusionnée, False sinon
    """
    if not table or len(table) == 0:
        return False

    # Compter les cellules contenant des \n multiples
    cellules_avec_newlines = 0

    for row in table[:20]:  # Analyser les 20 premières lignes
        for cell in row:
            if cell and '\n' in str(cell):
                # Compter le nombre de \n
                nb_newlines = str(cell).count('\n')
                if nb_newlines >= 3:  # Si 3+ retours à la ligne dans une cellule
                    cellules_avec_newlines += 1

    # Si plusieurs cellules ont beaucoup de \n, c'est probablement fusionné
    return cellules_avec_newlines >= 2


def extraire_avec_table_settings_alternatifs(page):
    """Essaie différentes configurations de pdfplumber pour extraire le tableau.

    Args:
        page: Page pdfplumber

    Returns:
        list: Meilleur tableau extrait, ou None
    """
    strategies = [
        # Stratégie 1: Par défaut
        {},

        # Stratégie 2: Intersection explicite
        {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_tolerance": 3
        },

        # Stratégie 3: Détection de texte
        {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
        },

        # Stratégie 4: Stratégie mixte
        {
            "vertical_strategy": "lines",
            "horizontal_strategy": "text",
            "intersection_tolerance": 5
        },

        # Stratégie 5: Seuils ajustés
        {
            "vertical_strategy": "lines_strict",
            "horizontal_strategy": "lines_strict",
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
        }
    ]

    meilleur_table = None
    meilleur_score = -1

    for settings in strategies:
        try:
            table = page.extract_table(table_settings=settings)

            if not table:
                continue

            # Évaluer la qualité de l'extraction
            score = evaluer_qualite_extraction(table)

            if score > meilleur_score:
                meilleur_score = score
                meilleur_table = table

        except Exception:
            continue

    return meilleur_table


def evaluer_qualite_extraction(table):
    """Évalue la qualité d'une extraction de tableau.

    Un bon tableau a:
    - Beaucoup de lignes
    - Peu de cellules fusionnées (avec \n)
    - Des cellules courtes et distinctes

    Args:
        table: Tableau extrait

    Returns:
        int: Score de qualité (plus élevé = meilleur)
    """
    if not table:
        return 0

    score = 0

    # +1 point par ligne (mais plafonné à 50)
    score += min(len(table), 50)

    # -5 points par cellule avec beaucoup de \n
    for row in table[:20]:
        for cell in row:
            if cell and str(cell).count('\n') >= 3:
                score -= 5

    # +2 points si on trouve des codes isolés (2 lettres majuscules)
    pattern_code = r'^[A-Z]{2}$'
    for row in table[:20]:
        for cell in row:
            if cell and re.match(pattern_code, str(cell).strip()):
                score += 2

    return score


def extraire_codes_depuis_texte_fusionne(table, codes_attendus):
    """Extrait les codes depuis un tableau avec cellules fusionnées.

    Quand pdfplumber fusionne les cellules (ex: 'DA\\nDL\\nDM\\n...'),
    cette fonction split les cellules et cherche les codes.

    Args:
        table: Tableau avec cellules potentiellement fusionnées
        codes_attendus: Dictionnaire des codes à chercher

    Returns:
        dict: {code: (row_idx, col_idx, valeurs_splitees)} pour chaque code trouvé
    """
    codes_trouves = {}

    for row_idx, row in enumerate(table):
        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_text = str(cell)

            # Si la cellule contient des \n, la splitter
            if '\n' in cell_text:
                lignes_splittees = cell_text.split('\n')

                # Chercher les codes dans les lignes splittées
                for ligne_idx, ligne in enumerate(lignes_splittees):
                    ligne_clean = ligne.strip().upper()

                    if ligne_clean in codes_attendus:
                        codes_trouves[ligne_clean] = {
                            'row_idx': row_idx,
                            'col_idx': col_idx,
                            'ligne_dans_cellule': ligne_idx,
                            'toutes_lignes': lignes_splittees,
                            'row_complete': row
                        }

    return codes_trouves


def extraire_montants_depuis_texte_fusionne(codes_info, index_colonne_montant):
    """Extrait les montants correspondant aux codes depuis un texte fusionné.

    Args:
        codes_info: Dict retourné par extraire_codes_depuis_texte_fusionne()
        index_colonne_montant: Index de la colonne contenant les montants

    Returns:
        dict: {code: montant_text} pour chaque code
    """
    montants = {}

    for code, info in codes_info.items():
        row = info['row_complete']
        ligne_idx = info['ligne_dans_cellule']

        # Vérifier si la colonne des montants existe
        if index_colonne_montant >= len(row):
            montants[code] = None
            continue

        # Récupérer la cellule des montants
        cellule_montants = row[index_colonne_montant]

        if not cellule_montants:
            montants[code] = None
            continue

        # Si la cellule des montants est aussi fusionnée
        if '\n' in str(cellule_montants):
            lignes_montants = str(cellule_montants).split('\n')

            # Essayer de récupérer le montant à la même position que le code
            if ligne_idx < len(lignes_montants):
                montants[code] = lignes_montants[ligne_idx]
            else:
                montants[code] = None
        else:
            # Si pas fusionné, utiliser directement
            montants[code] = cellule_montants

    return montants


def extraire_tableau_avec_fallback(page, codes_attendus):
    """Stratégie complète d'extraction avec fallbacks multiples.

    1. Essaie extract_table() par défaut
    2. Si fusionné, essaie différents table_settings
    3. Si toujours fusionné, parse le texte fusionné

    Args:
        page: Page pdfplumber
        codes_attendus: Dictionnaire des codes fiscaux attendus

    Returns:
        tuple: (table, est_fusionne, methode_utilisee)
    """
    # Tentative 1: Extraction standard
    table = page.extract_table()

    if table and not detecter_extraction_fusionnee(table):
        return table, False, "standard"

    print("   ⚠️  Extraction fusionnée détectée. Essai de stratégies alternatives...")

    # Tentative 2: Essayer différents table_settings
    table_alt = extraire_avec_table_settings_alternatifs(page)

    if table_alt and not detecter_extraction_fusionnee(table_alt):
        print("   ✅ Extraction réussie avec stratégie alternative!")
        return table_alt, False, "alternative_settings"

    # Tentative 3: Parser le tableau fusionné
    print("   ℹ️  Utilisation du parser de texte fusionné...")

    # Utiliser le meilleur tableau disponible (même fusionné)
    table_a_parser = table_alt if table_alt else table

    return table_a_parser, True, "texte_fusionne"
