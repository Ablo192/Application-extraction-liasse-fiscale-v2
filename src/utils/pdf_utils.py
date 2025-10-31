"""
Fonctions utilitaires pour la manipulation et l'analyse des PDFs.

Ce module fournit des fonctions pour extraire des métadonnées et détecter
des structures dans les PDFs de liasses fiscales.
"""

import re


def extraire_annee_fiscale(pdf):
    """Extrait l'année fiscale depuis le PDF.

    Cherche dans les 3 premières pages les patterns suivants :
    - "Exercice N : 2024"
    - "Exercice clos le 31/12/2024"
    - "Période du ... au 31/12/2024"
    - "ANNÉE 2024"

    Args:
        pdf: Objet PDF ouvert avec pdfplumber

    Returns:
        str: Année fiscale (ex: "2024") ou None si non trouvée

    Examples:
        >>> with pdfplumber.open("liasse_2024.pdf") as pdf:
        ...     annee = extraire_annee_fiscale(pdf)
        ...     print(annee)
        '2024'
    """
    for page in pdf.pages[:3]:
        text = page.extract_text()
        if not text:
            continue

        # Patterns à chercher (par ordre de priorité)
        patterns = [
            r'Exercice\s+N\s*:?\s*(\d{4})',  # Exercice N : 2024
            r'Exercice clos le\s+\d{2}/\d{2}/(\d{4})',  # Exercice clos le 31/12/2024
            r'au\s+\d{2}/\d{2}/(\d{4})',  # au 31/12/2024
            r'ANNÉE\s+(\d{4})',  # ANNÉE 2024
            r'Année\s+(\d{4})',  # Année 2024
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

    return None


def trouver_colonne_montant(table, marqueur_colonne, offset=1, max_rows=10):
    """Trouve dynamiquement l'index de la colonne contenant les montants.

    Cherche un marqueur dans l'en-tête du tableau (ex: "Exercice N", "TOTAL", "Net")
    et retourne l'index de la colonne des montants (généralement marqueur + offset).

    Args:
        table: Tableau extrait du PDF (liste de listes)
        marqueur_colonne: Texte à chercher dans l'en-tête ("Exercice N", "TOTAL", "Net", etc.)
        offset: Décalage par rapport au marqueur (défaut: +1)
        max_rows: Nombre maximum de lignes à examiner pour trouver l'en-tête (défaut: 10)

    Returns:
        int: Index de la colonne des montants, ou None si non trouvée

    Examples:
        >>> table = [["Libellé", "Exercice N", "Montant"], ["Capital", "", "500000"]]
        >>> trouver_colonne_montant(table, "Exercice N", offset=1)
        2
    """
    for row in table[:max_rows]:
        for idx, cell in enumerate(row):
            if cell and marqueur_colonne in str(cell):
                return idx + offset
    return None


def trouver_page_contenant(pdf, marqueurs):
    """Trouve la première page contenant au moins un des marqueurs spécifiés.

    Args:
        pdf: Objet PDF ouvert avec pdfplumber
        marqueurs: Liste de chaînes de caractères à chercher (sensible à la casse)

    Returns:
        int: Index de la page (0-based) ou -1 si non trouvée

    Examples:
        >>> with pdfplumber.open("liasse.pdf") as pdf:
        ...     idx = trouver_page_contenant(pdf, ["BILAN ACTIF", "Brut"])
        ...     print(f"Page trouvée : {idx + 1}")
        Page trouvée : 1
    """
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue

        for marqueur in marqueurs:
            if marqueur in text:
                return i

    return -1


def detecter_section_dettes(row):
    """Détecte si une ligne marque le début de la section DETTES dans l'état des échéances.

    Args:
        row: Ligne du tableau (liste de cellules)

    Returns:
        bool: True si la ligne marque le début de la section DETTES

    Examples:
        >>> row = ["ÉTAT DES DETTES", "", ""]
        >>> detecter_section_dettes(row)
        True
    """
    row_text = " ".join(str(cell) for cell in row if cell).upper()

    # Variantes possibles du titre DETTES
    marqueurs_dettes = [
        "ÉTAT DES DETTES",
        "ETAT DES DETTES",
        "DETTES (4)",
        "B – PLUS-VALUES",
        "DETTES ET PRODUITS CONSTATÉS"
    ]

    return any(marqueur in row_text for marqueur in marqueurs_dettes)


def extraire_duree_exercice(pdf):
    """Extrait la durée de l'exercice fiscal en mois depuis le PDF.

    Cherche les patterns :
    - "Période du 01/01/2024 au 31/12/2024" → calcule la durée
    - "Durée : 12 mois"

    Args:
        pdf: Objet PDF ouvert avec pdfplumber

    Returns:
        int: Durée en mois (par défaut 12 si non trouvée)

    Examples:
        >>> with pdfplumber.open("liasse.pdf") as pdf:
        ...     duree = extraire_duree_exercice(pdf)
        12
    """
    for page in pdf.pages[:3]:
        text = page.extract_text()
        if not text:
            continue

        # Pattern 1 : Durée explicite
        match_duree = re.search(r'Durée\s*:?\s*(\d+)\s*mois', text, re.IGNORECASE)
        if match_duree:
            return int(match_duree.group(1))

        # Pattern 2 : Période avec dates
        match_periode = re.search(
            r'(?:Période|Exercice)\s+du\s+(\d{2})/(\d{2})/(\d{4})\s+au\s+(\d{2})/(\d{2})/(\d{4})',
            text,
            re.IGNORECASE
        )
        if match_periode:
            jour_debut, mois_debut, annee_debut = map(int, match_periode.groups()[:3])
            jour_fin, mois_fin, annee_fin = map(int, match_periode.groups()[3:])

            # Calcul approximatif en mois
            duree_mois = (annee_fin - annee_debut) * 12 + (mois_fin - mois_debut)
            if duree_mois > 0:
                return duree_mois

    # Par défaut, exercice de 12 mois
    return 12
