"""
Fonctions utilitaires pour le traitement de texte et l'extraction de données.

Ce module fournit des fonctions pour nettoyer, normaliser et comparer du texte
extrait des PDFs fiscaux.
"""

from difflib import SequenceMatcher


def nettoyer_montant(texte):
    """Nettoie et convertit un montant textuel en nombre.

    Gère les montants négatifs sous plusieurs formats :
    - (1 000 000) → -1000000
    - -1 000 000 → -1000000
    - 1 000 000- → -1000000

    Args:
        texte: Montant sous forme de chaîne de caractères

    Returns:
        float: Montant converti en nombre, ou None si conversion impossible

    Examples:
        >>> nettoyer_montant("1 000 000")
        1000000.0
        >>> nettoyer_montant("(500 000)")
        -500000.0
        >>> nettoyer_montant("1 234,56")
        1234.56
    """
    if not texte:
        return None

    texte = str(texte).strip()

    # Cas 1 : Montant entre parenthèses → négatif
    if texte.startswith('(') and texte.endswith(')'):
        texte = '-' + texte[1:-1]

    # Cas 2 : Signe - à la fin → déplacer au début
    elif texte.endswith('-'):
        texte = '-' + texte[:-1]

    # Nettoyer : enlever espaces, remplacer virgule par point
    texte = texte.replace(',', '.').replace(' ', '')

    # Ne garder que les chiffres, le point et le signe -
    texte_clean = "".join(char for char in texte if char.isdigit() or char in ['.', '-'])

    if not texte_clean or texte_clean == '-':
        return None

    try:
        return float(texte_clean)
    except ValueError:
        return None


def normaliser_texte(texte):
    """Nettoie un texte pour le rendre comparable (minuscule, sans accents, sans espaces).

    Args:
        texte: Texte à normaliser

    Returns:
        str: Texte normalisé (minuscules, sans accents, sans espaces, uniquement alphanumériques)

    Examples:
        >>> normaliser_texte("Frais d'établissement")
        'fraisdestablissement'
        >>> normaliser_texte("Capital Social")
        'capitalsocial'
    """
    if not texte:
        return ""

    texte = str(texte).lower()

    # Table de conversion des accents
    accents = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a', 'å': 'a',
        'ç': 'c',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ñ': 'n',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'ÿ': 'y'
    }

    for acc_char, char in accents.items():
        texte = texte.replace(acc_char, char)

    # Ne garder que les caractères alphanumériques
    return "".join(char for char in texte if char.isalnum())


def matcher_par_mots_cles(texte, mots_cles):
    """Vérifie si un des mots-clés est présent dans le texte.

    Args:
        texte: Le texte à analyser
        mots_cles: Liste de mots-clés à chercher

    Returns:
        bool: True si au moins un mot-clé est trouvé

    Examples:
        >>> matcher_par_mots_cles("Capital social", ["capital social", "capital individuel"])
        True
        >>> matcher_par_mots_cles("Autre chose", ["capital social"])
        False
    """
    if not texte or not mots_cles:
        return False

    texte_clean = texte.lower().strip()

    for mot_cle in mots_cles:
        if mot_cle.lower() in texte_clean:
            return True

    return False


def calculer_similarite(texte1, texte2):
    """Calcule la similarité entre deux textes (fuzzy matching).

    Utilise l'algorithme de Ratcliff/Obershelp via SequenceMatcher de Python.

    Args:
        texte1: Premier texte
        texte2: Second texte

    Returns:
        float: Score de similarité entre 0.0 et 1.0

    Examples:
        >>> calculer_similarite("Capital social", "Capital social")
        1.0
        >>> calculer_similarite("Capital social", "Kapital social")
        0.92...
    """
    if not texte1 or not texte2:
        return 0.0

    texte1_clean = texte1.lower().strip()
    texte2_clean = texte2.lower().strip()

    return SequenceMatcher(None, texte1_clean, texte2_clean).ratio()


def extraire_valeur_hybride(table, code, mots_cles, libelle_reference, index_montant, seuil_fuzzy=0.75):
    """Extrait une valeur en utilisant 3 niveaux : code exact, mots-clés, fuzzy matching.

    Stratégie d'extraction à plusieurs niveaux :
    1. Niveau 1 : Cherche le CODE exact (ex: "FL", "DA")
    2. Niveau 2 : Cherche par MOTS-CLÉS (ex: "chiffre d'affaires", "capital social")
    3. Niveau 3 : Cherche par FUZZY matching (similarité >= seuil)

    Args:
        table: Tableau extrait du PDF (liste de listes)
        code: Code officiel à chercher (ex: "FL")
        mots_cles: Liste de mots-clés alternatifs
        libelle_reference: Libellé de référence pour fuzzy matching
        index_montant: Index de la colonne contenant le montant
        seuil_fuzzy: Seuil minimum de similarité pour fuzzy (0.0 à 1.0)

    Returns:
        tuple: (montant, methode_utilisee) où methode = "code" | "mots_cles" | "fuzzy" | "non_trouve"

    Examples:
        >>> table = [["FL", "Chiffre d'affaires", "1000000"], ["DA", "Capital", "500000"]]
        >>> extraire_valeur_hybride(table, "FL", ["chiffre d'affaires"], "Chiffre d'affaires nets", 2)
        (1000000.0, 'code')
    """

    for row_idx, row in enumerate(table):
        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_text = str(cell).strip()

            # NIVEAU 1 : Chercher le CODE exact
            if cell_text.upper() == code:
                montant_cell = row[index_montant] if len(row) > index_montant else None
                montant = nettoyer_montant(montant_cell)
                if montant is not None:
                    return montant, "code"

            # NIVEAU 2 : Chercher par MOTS-CLÉS
            if matcher_par_mots_cles(cell_text, mots_cles):
                montant_cell = row[index_montant] if len(row) > index_montant else None
                montant = nettoyer_montant(montant_cell)
                if montant is not None:
                    return montant, "mots_cles"

            # NIVEAU 3 : Chercher par FUZZY matching
            similarite = calculer_similarite(cell_text, libelle_reference)
            if similarite >= seuil_fuzzy:
                montant_cell = row[index_montant] if len(row) > index_montant else None
                montant = nettoyer_montant(montant_cell)
                if montant is not None:
                    return montant, "fuzzy"

    return 0, "non_trouve"
