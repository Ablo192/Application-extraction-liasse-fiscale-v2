"""
EXTRACTION POUR FORMULAIRES VIERGES
====================================

Adapté pour extraire la STRUCTURE d'un PDF vierge :
- Détecte les lignes avec codes (AA, AB, etc.)
- Retourne 0 pour toutes les cellules de montants vides
- Extrait les libellés présents dans le formulaire
"""

import pdfplumber
from typing import Dict, List, Optional, Tuple


# ============================================================================
# UTILITAIRES DE BASE
# ============================================================================

def nettoyer_texte(texte) -> str:
    """Nettoie un texte en supprimant les sauts de ligne et espaces multiples"""
    if not texte:
        return ""
    return str(texte).replace('\n', ' ').replace('  ', ' ').strip()


def nettoyer_montant_vierge(texte) -> float:
    """
    Convertit un texte en montant numérique.
    POUR FORMULAIRE VIERGE : retourne 0 si la cellule est vide ou invalide.

    Gère les formats : (1 000), -1 000, 1 000-, 1 000,00
    """
    if not texte or str(texte).strip() == '':
        return 0.0  # ← DIFFÉRENCE : retourne 0 au lieu de None

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
        return 0.0  # ← DIFFÉRENCE : retourne 0 au lieu de None


# ============================================================================
# PHASE 1 : DÉTECTION INTELLIGENTE DES PAGES (identique)
# ============================================================================

class DetecteurPages:
    """
    Détecte les pages importantes en analysant leur contenu.
    N'utilise JAMAIS de numéros de page fixes.
    """

    SIGNATURES = {
        'BILAN_ACTIF': {
            'obligatoires': ['BILAN', 'ACTIF'],
            'discriminants': [
                'Capital souscrit non appelé',
                'ACTIF IMMOBILISÉ',
                'ACTIF CIRCULANT',
                'Frais d\'établissement'
            ],
            'seuil_discriminants': 2
        },
        'BILAN_PASSIF': {
            'obligatoires': ['BILAN', 'PASSIF'],
            'discriminants': [
                'CAPITAUX PROPRES',
                'Capital social ou individuel',
                'Primes d\'émission',
                'Réserve légale'
            ],
            'seuil_discriminants': 2
        },
        'COMPTE_RESULTAT': {
            'obligatoires': ['COMPTE DE RÉSULTAT', 'EXERCICE'],
            'discriminants': [
                'Ventes de marchandises',
                'Production vendue',
                'Chiffres d\'affaires',
                'PRODUITS D\'EXPLOITATION',
                'CHARGES D\'EXPLOITATION'
            ],
            'seuil_discriminants': 2
        },
        'ETAT_ECHEANCES': {
            'obligatoires': ['ÉTAT DES', 'CRÉANCES', 'DETTES'],
            'discriminants': [
                'MONTANT BRUT',
                'À 1 AN AU PLUS',
                'À PLUS D\'UN AN',
                'Clients douteux'
            ],
            'seuil_discriminants': 2
        }
    }

    @staticmethod
    def detecter_type_page(page_text: str, table_data: List[List]) -> Optional[str]:
        """Détecte le type d'une page en analysant son contenu."""
        if not page_text:
            return None

        page_text_upper = page_text.upper()

        # Convertir le tableau en texte
        table_text = ""
        if table_data:
            table_text = " ".join([
                str(cell).upper()
                for row in table_data[:15]
                for cell in row
                if cell
            ])

        texte_complet = page_text_upper + " " + table_text

        # Tester chaque signature
        for type_page, signature in DetecteurPages.SIGNATURES.items():
            tous_obligatoires_presents = all(
                mot.upper() in texte_complet
                for mot in signature['obligatoires']
            )

            if not tous_obligatoires_presents:
                continue

            nb_discriminants = sum(
                1 for mot in signature['discriminants']
                if mot.upper() in texte_complet
            )

            if nb_discriminants >= signature['seuil_discriminants']:
                return type_page

        return None

    @staticmethod
    def trouver_pages(pdf_path: str) -> Dict[str, Tuple[int, List[List]]]:
        """Parcourt tout le PDF et identifie les pages importantes."""
        pages_trouvees = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                tables = page.extract_tables()

                # Trouver le plus grand tableau de la page
                table_principale = None
                taille_max = 0

                for table in tables:
                    if table and len(table) > taille_max:
                        taille_max = len(table)
                        table_principale = table

                if not table_principale or len(table_principale) < 10:
                    continue

                # Détecter le type
                type_page = DetecteurPages.detecter_type_page(page_text, table_principale)

                if type_page:
                    if type_page not in pages_trouvees:
                        pages_trouvees[type_page] = (page_idx, table_principale)
                        print(f"  ✓ {type_page} détecté à la page {page_idx + 1}")

        return pages_trouvees


# ============================================================================
# PHASE 2 : EXTRACTION DES DONNÉES (adaptée pour formulaires vierges)
# ============================================================================

def trouver_colonne_avec_en_tete(table_data: List[List], mots_cles: List[str]) -> Optional[int]:
    """Trouve l'index de la colonne contenant l'un des mots-clés dans les en-têtes"""
    if not table_data:
        return None

    for row in table_data[:5]:
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


def trouver_colonne_code(table_data: List[List], ligne_debut=5) -> Optional[int]:
    """Trouve la colonne contenant les codes (2 lettres majuscules)"""
    if not table_data or len(table_data) < ligne_debut:
        return None

    codes_par_colonne = {}

    for row_idx in range(ligne_debut, min(ligne_debut + 10, len(table_data))):
        if row_idx >= len(table_data):
            break

        row = table_data[row_idx]

        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_clean = str(cell).strip().upper()

            # Code = 2 lettres majuscules
            if len(cell_clean) == 2 and cell_clean.isalpha():
                codes_par_colonne[col_idx] = codes_par_colonne.get(col_idx, 0) + 1

    if codes_par_colonne:
        return max(codes_par_colonne.items(), key=lambda x: x[1])[0]

    return None


def trouver_colonne_montant_ou_derniere(table_data: List[List]) -> int:
    """
    Trouve la colonne de montant, ou la dernière colonne du tableau.
    POUR FORMULAIRE VIERGE : on a besoin d'une colonne même si elle est vide.
    """
    if not table_data or not table_data[0]:
        return 0

    # Chercher une colonne avec des montants (même approche que avant)
    for col_idx in range(len(table_data[0]) - 1, -1, -1):
        nb_montants = 0

        for row_idx in range(5, min(15, len(table_data))):
            if row_idx < len(table_data) and col_idx < len(table_data[row_idx]):
                cell = table_data[row_idx][col_idx]
                if cell and nettoyer_montant_vierge(cell) != 0:
                    nb_montants += 1

        if nb_montants >= 3:
            return col_idx

    # Si aucune colonne de montant trouvée, retourner la dernière colonne
    # C'est là où les montants DEVRAIENT être dans un formulaire vierge
    return len(table_data[0]) - 1


def extraire_donnees_formulaire_vierge(
    table_data: List[List],
    codes_recherches: Dict[str, str],
    col_codes: Optional[int],
    col_montant: int,
    ligne_debut: int = 5
) -> Dict[str, float]:
    """
    Extrait les montants d'un FORMULAIRE VIERGE.
    DIFFÉRENCE MAJEURE : retourne 0 pour les cellules vides.
    """
    resultats = {}
    codes_majuscules = {code.upper(): libelle for code, libelle in codes_recherches.items()}

    for row_idx in range(ligne_debut, len(table_data)):
        row = table_data[row_idx]

        if not row:
            continue

        # Chercher le code dans la ligne
        code_trouve = None

        if col_codes is not None and col_codes < len(row):
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

        # Si code trouvé, extraire le montant (ou 0 si vide)
        if code_trouve:
            montant = 0.0  # Valeur par défaut

            if col_montant < len(row):
                montant_brut = row[col_montant]
                montant = nettoyer_montant_vierge(montant_brut)  # Retourne 0 si vide

            libelle = codes_majuscules[code_trouve]
            resultats[libelle] = montant

    return resultats


# ============================================================================
# ORCHESTRATEUR PRINCIPAL
# ============================================================================

def extraire_formulaire_vierge(
    pdf_path: str,
    codes_actif: Dict[str, str],
    codes_passif: Dict[str, str],
    codes_cr: Dict[str, str]
) -> Dict:
    """
    Extrait la STRUCTURE d'un PDF de liasse fiscale VIERGE.
    Retourne 0 pour toutes les cellules de montants vides.

    Returns:
        Dict avec clés 'actif', 'passif', 'cr'
    """
    print("\n" + "="*80)
    print("EXTRACTION FORMULAIRE VIERGE - MODE 0 POUR CELLULES VIDES")
    print("="*80)

    # PHASE 1 : Détecter les pages
    print("\n📍 PHASE 1 : Détection des pages importantes...")
    pages = DetecteurPages.trouver_pages(pdf_path)

    if not pages:
        print("\n❌ Aucune page identifiée")
        return {'actif': {}, 'passif': {}, 'cr': {}}

    print(f"\n✓ {len(pages)} page(s) identifiée(s)\n")

    # PHASE 2 : Extraire les données
    print("📍 PHASE 2 : Extraction de la structure (montants vides = 0)...")
    resultats = {}

    # --- BILAN ACTIF ---
    if 'BILAN_ACTIF' in pages:
        print("\n→ Extraction BILAN ACTIF...")
        page_idx, table = pages['BILAN_ACTIF']

        col_montant = trouver_colonne_avec_en_tete(table, ['net', 'brut'])
        if col_montant is None:
            col_montant = trouver_colonne_montant_ou_derniere(table)

        col_codes = trouver_colonne_code(table)

        print(f"  ✓ Colonne montant : index {col_montant}")
        if col_codes:
            print(f"  ✓ Colonne codes : index {col_codes}")

        donnees = extraire_donnees_formulaire_vierge(table, codes_actif, col_codes, col_montant)
        resultats['actif'] = donnees
        print(f"  ✓ {len(donnees)}/{len(codes_actif)} codes trouvés (montants vides = 0)")
    else:
        print("\n⚠️  BILAN ACTIF non trouvé")
        resultats['actif'] = {}

    # --- BILAN PASSIF ---
    if 'BILAN_PASSIF' in pages:
        print("\n→ Extraction BILAN PASSIF...")
        page_idx, table = pages['BILAN_PASSIF']

        col_montant = trouver_colonne_montant_ou_derniere(table)
        col_codes = trouver_colonne_code(table)

        print(f"  ✓ Colonne montant : index {col_montant}")
        if col_codes:
            print(f"  ✓ Colonne codes : index {col_codes}")

        donnees = extraire_donnees_formulaire_vierge(table, codes_passif, col_codes, col_montant)
        resultats['passif'] = donnees
        print(f"  ✓ {len(donnees)}/{len(codes_passif)} codes trouvés (montants vides = 0)")
    else:
        print("\n⚠️  BILAN PASSIF non trouvé")
        resultats['passif'] = {}

    # --- COMPTE DE RÉSULTAT ---
    pages_cr = [(k, v) for k, v in pages.items() if k == 'COMPTE_RESULTAT']

    if pages_cr:
        print("\n→ Extraction COMPTE DE RÉSULTAT...")
        donnees_cr = {}

        for type_page, (page_idx, table) in pages_cr:
            col_montant = trouver_colonne_avec_en_tete(table, ['total', 'exercice'])
            if col_montant is None:
                col_montant = trouver_colonne_montant_ou_derniere(table)

            col_codes = trouver_colonne_code(table)

            print(f"  ✓ Page {page_idx + 1} - Colonne montant : index {col_montant}")
            donnees = extraire_donnees_formulaire_vierge(table, codes_cr, col_codes, col_montant)
            donnees_cr.update(donnees)

        resultats['cr'] = donnees_cr
        print(f"  ✓ {len(donnees_cr)}/{len(codes_cr)} codes trouvés (montants vides = 0)")
    else:
        print("\n⚠️  COMPTE DE RÉSULTAT non trouvé")
        resultats['cr'] = {}

    print("\n" + "="*80)
    print("✓ EXTRACTION TERMINÉE")
    print("="*80)
    print(f"\nRésumé :")
    print(f"  - ACTIF : {len(resultats.get('actif', {}))} lignes")
    print(f"  - PASSIF : {len(resultats.get('passif', {}))} lignes")
    print(f"  - COMPTE DE RÉSULTAT : {len(resultats.get('cr', {}))} lignes")
    print(f"\n💡 Les cellules vides ont été remplies avec 0")
    print()

    return resultats


if __name__ == "__main__":
    print("Module d'extraction pour formulaires vierges chargé.")
    print("Retourne 0 pour toutes les cellules de montants vides.")
