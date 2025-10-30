"""
NOUVELLE APPROCHE : Extraction simple et ciblée
================================================

Au lieu d'une approche "analytique" complexe, on utilise une approche
DIRECTE basée sur la connaissance de la structure des liasses fiscales :

- Page 1 : BILAN ACTIF
- Page 2 : BILAN PASSIF
- Pages 3-4 : COMPTE DE RÉSULTAT
- Page 9 : ÉTAT DES ÉCHÉANCES

On extrait LE PREMIER TABLEAU de chaque page ciblée.
"""

import pdfplumber
from typing import Dict, List, Optional


def nettoyer_texte(texte) -> str:
    """Nettoie un texte en supprimant les sauts de ligne et espaces multiples"""
    if not texte:
        return ""
    return str(texte).replace('\n', ' ').replace('  ', ' ').strip()


def nettoyer_montant(texte) -> Optional[float]:
    """
    Convertit un texte en montant numérique.
    Gère les formats : (1 000), -1 000, 1 000-, 1 000,00
    """
    if not texte:
        return None

    texte = str(texte).strip()

    # Montant entre parenthèses → négatif
    if texte.startswith('(') and texte.endswith(')'):
        texte = '-' + texte[1:-1]

    # Signe - à la fin → déplacer au début
    elif texte.endswith('-'):
        texte = '-' + texte[:-1]

    # Nettoyer : enlever espaces, remplacer virgule par point
    texte = texte.replace(',', '.').replace(' ', '').replace('\xa0', '')

    try:
        return float(texte)
    except:
        return None


def trouver_colonne_avec_en_tete(table_data: List[List], mots_cles: List[str], lignes_en_tete_max=5) -> Optional[int]:
    """
    Trouve l'index de la colonne contenant l'un des mots-clés dans les premières lignes.

    Args:
        table_data: Tableau de données
        mots_cles: Liste de mots-clés à chercher (ex: ['net', 'brut'])
        lignes_en_tete_max: Nombre de lignes à analyser pour trouver l'en-tête

    Returns:
        Index de la colonne, ou None si non trouvée
    """
    if not table_data:
        return None

    # Analyser les premières lignes
    for row in table_data[:lignes_en_tete_max]:
        if not row:
            continue

        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_clean = nettoyer_texte(cell).lower()

            for mot_cle in mots_cles:
                if mot_cle.lower() in cell_clean:
                    return col_idx

    return None


def trouver_colonne_code(table_data: List[List], ligne_debut=5, lignes_max=10) -> Optional[int]:
    """
    Trouve la colonne contenant les codes (2 lettres majuscules).

    Args:
        table_data: Tableau de données
        ligne_debut: Ligne à partir de laquelle chercher
        lignes_max: Nombre de lignes à analyser

    Returns:
        Index de la colonne des codes, ou None
    """
    if not table_data or len(table_data) < ligne_debut:
        return None

    # Compter les codes trouvés par colonne
    codes_par_colonne = {}

    for row_idx in range(ligne_debut, min(ligne_debut + lignes_max, len(table_data))):
        if row_idx >= len(table_data):
            break

        row = table_data[row_idx]

        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_clean = str(cell).strip().upper()

            # Vérifier si c'est un code : 2 lettres majuscules
            if len(cell_clean) == 2 and cell_clean.isalpha():
                codes_par_colonne[col_idx] = codes_par_colonne.get(col_idx, 0) + 1

    # Retourner la colonne avec le plus de codes
    if codes_par_colonne:
        return max(codes_par_colonne.items(), key=lambda x: x[1])[0]

    return None


def extraire_donnees_avec_codes(
    table_data: List[List],
    codes_recherches: Dict[str, str],
    col_codes: Optional[int],
    col_montant: int,
    ligne_debut: int = 5
) -> Dict[str, float]:
    """
    Extrait les montants d'un tableau en cherchant les codes.

    Args:
        table_data: Tableau de données
        codes_recherches: Dict {code: libellé}
        col_codes: Index de la colonne des codes (ou None pour chercher dans toutes)
        col_montant: Index de la colonne des montants
        ligne_debut: Ligne à partir de laquelle commencer l'extraction

    Returns:
        Dict {libellé: montant}
    """
    resultats = {}
    codes_majuscules = {code.upper(): libelle for code, libelle in codes_recherches.items()}

    for row_idx in range(ligne_debut, len(table_data)):
        row = table_data[row_idx]

        if not row or len(row) <= max(col_montant, col_codes or 0):
            continue

        # Chercher le code dans la ligne
        code_trouve = None

        if col_codes is not None and col_codes < len(row):
            # Chercher dans la colonne des codes
            cell = row[col_codes]
            if cell:
                cell_upper = str(cell).strip().upper()
                if cell_upper in codes_majuscules:
                    code_trouve = cell_upper

        if not code_trouve:
            # Chercher dans toutes les colonnes
            for cell in row:
                if cell:
                    cell_upper = str(cell).strip().upper()
                    if cell_upper in codes_majuscules:
                        code_trouve = cell_upper
                        break

        # Si code trouvé, extraire le montant
        if code_trouve and col_montant < len(row):
            montant_brut = row[col_montant]
            montant = nettoyer_montant(montant_brut)

            if montant is not None:
                libelle = codes_majuscules[code_trouve]
                resultats[libelle] = montant

    return resultats


def extraire_bilan_actif(pdf_path: str, codes: Dict[str, str]) -> Dict[str, float]:
    """
    Extrait le BILAN ACTIF de la page 1.
    On cherche la colonne "Net" (3ème colonne de montant).
    """
    print("\n→ Extraction BILAN ACTIF (page 1)...")

    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) < 1:
            print("  ❌ Page 1 introuvable")
            return {}

        page = pdf.pages[0]
        tables = page.extract_tables()

        if not tables:
            print("  ❌ Aucun tableau trouvé")
            return {}

        # Prendre le premier grand tableau (au moins 20 lignes)
        table = None
        for t in tables:
            if t and len(t) >= 20:
                table = t
                break

        if not table:
            print("  ❌ Aucun tableau valide trouvé")
            return {}

        print(f"  ✓ Tableau trouvé : {len(table)} lignes × {len(table[0])} colonnes")

        # Trouver la colonne "Net" (priorité) ou "Brut"
        col_montant = trouver_colonne_avec_en_tete(table, ['net', 'brut'])

        if col_montant is None:
            print("  ❌ Colonne de montant non trouvée")
            return {}

        print(f"  ✓ Colonne montant détectée : index {col_montant}")

        # Trouver la colonne des codes
        col_codes = trouver_colonne_code(table)
        if col_codes:
            print(f"  ✓ Colonne codes détectée : index {col_codes}")
        else:
            print("  ⚠️ Colonne codes non détectée, recherche dans toutes les colonnes")

        # Extraire les données
        resultats = extraire_donnees_avec_codes(table, codes, col_codes, col_montant)

        print(f"  ✓ {len(resultats)}/{len(codes)} codes extraits")

        return resultats


def extraire_bilan_passif(pdf_path: str, codes: Dict[str, str]) -> Dict[str, float]:
    """
    Extrait le BILAN PASSIF de la page 2.
    On cherche la colonne de montant (souvent la dernière avec des montants).
    """
    print("\n→ Extraction BILAN PASSIF (page 2)...")

    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) < 2:
            print("  ❌ Page 2 introuvable")
            return {}

        page = pdf.pages[1]
        tables = page.extract_tables()

        if not tables:
            print("  ❌ Aucun tableau trouvé")
            return {}

        # Prendre le premier grand tableau
        table = None
        for t in tables:
            if t and len(t) >= 20:
                table = t
                break

        if not table:
            print("  ❌ Aucun tableau valide trouvé")
            return {}

        print(f"  ✓ Tableau trouvé : {len(table)} lignes × {len(table[0])} colonnes")

        # Trouver la colonne de montant (dernière colonne avec des chiffres)
        col_montant = None
        for col_idx in range(len(table[0]) - 1, -1, -1):
            # Vérifier si cette colonne contient des montants
            nb_montants = 0
            for row_idx in range(5, min(15, len(table))):
                if row_idx < len(table) and col_idx < len(table[row_idx]):
                    cell = table[row_idx][col_idx]
                    if cell and nettoyer_montant(cell) is not None:
                        nb_montants += 1

            if nb_montants >= 3:
                col_montant = col_idx
                break

        if col_montant is None:
            print("  ❌ Colonne de montant non trouvée")
            return {}

        print(f"  ✓ Colonne montant détectée : index {col_montant}")

        # Trouver la colonne des codes
        col_codes = trouver_colonne_code(table)
        if col_codes:
            print(f"  ✓ Colonne codes détectée : index {col_codes}")
        else:
            print("  ⚠️ Colonne codes non détectée, recherche dans toutes les colonnes")

        # Extraire les données
        resultats = extraire_donnees_avec_codes(table, codes, col_codes, col_montant)

        print(f"  ✓ {len(resultats)}/{len(codes)} codes extraits")

        return resultats


def extraire_compte_resultat(pdf_path: str, codes: Dict[str, str]) -> Dict[str, float]:
    """
    Extrait le COMPTE DE RÉSULTAT des pages 3 et 4.
    """
    print("\n→ Extraction COMPTE DE RÉSULTAT (pages 3-4)...")

    resultats = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in [2, 3]:  # Pages 3 et 4 (index 2 et 3)
            if len(pdf.pages) <= page_num:
                continue

            print(f"\n  Page {page_num + 1}:")

            page = pdf.pages[page_num]
            tables = page.extract_tables()

            if not tables:
                print(f"    ❌ Aucun tableau trouvé")
                continue

            # Prendre le premier grand tableau
            table = None
            for t in tables:
                if t and len(t) >= 20:
                    table = t
                    break

            if not table:
                print(f"    ❌ Aucun tableau valide trouvé")
                continue

            print(f"    ✓ Tableau trouvé : {len(table)} lignes × {len(table[0])} colonnes")

            # Trouver la colonne "TOTAL" ou la dernière colonne de montant
            col_montant = trouver_colonne_avec_en_tete(table, ['total', 'exercice'])

            if col_montant is None:
                # Chercher la dernière colonne avec des montants
                for col_idx in range(len(table[0]) - 1, -1, -1):
                    nb_montants = 0
                    for row_idx in range(5, min(15, len(table))):
                        if row_idx < len(table) and col_idx < len(table[row_idx]):
                            cell = table[row_idx][col_idx]
                            if cell and nettoyer_montant(cell) is not None:
                                nb_montants += 1

                    if nb_montants >= 3:
                        col_montant = col_idx
                        break

            if col_montant is None:
                print(f"    ❌ Colonne de montant non trouvée")
                continue

            print(f"    ✓ Colonne montant détectée : index {col_montant}")

            # Trouver la colonne des codes
            col_codes = trouver_colonne_code(table)
            if col_codes:
                print(f"    ✓ Colonne codes détectée : index {col_codes}")

            # Extraire les données de cette page
            resultats_page = extraire_donnees_avec_codes(table, codes, col_codes, col_montant)
            resultats.update(resultats_page)

            print(f"    ✓ {len(resultats_page)} codes extraits")

    print(f"\n  ✓ TOTAL : {len(resultats)}/{len(codes)} codes extraits")

    return resultats


def extraire_pdf_complet(
    pdf_path: str,
    codes_actif: Dict[str, str],
    codes_passif: Dict[str, str],
    codes_cr: Dict[str, str]
) -> Dict:
    """
    Extrait toutes les données d'un PDF de liasse fiscale.

    Returns:
        Dict avec clés 'actif', 'passif', 'cr' contenant les données extraites
    """
    print("\n" + "="*80)
    print("EXTRACTION LIASSE FISCALE - APPROCHE SIMPLE ET DIRECTE")
    print("="*80)

    resultats = {
        'actif': extraire_bilan_actif(pdf_path, codes_actif),
        'passif': extraire_bilan_passif(pdf_path, codes_passif),
        'cr': extraire_compte_resultat(pdf_path, codes_cr)
    }

    print("\n" + "="*80)
    print("✓ EXTRACTION TERMINÉE")
    print("="*80)
    print(f"\nRésumé :")
    print(f"  - ACTIF : {len(resultats['actif'])} valeurs")
    print(f"  - PASSIF : {len(resultats['passif'])} valeurs")
    print(f"  - COMPTE DE RÉSULTAT : {len(resultats['cr'])} valeurs")
    print()

    return resultats


if __name__ == "__main__":
    print("Module d'extraction simple chargé.")
    print("Utilisez extraire_pdf_complet() pour extraire un PDF.")
