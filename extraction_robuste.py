"""
EXTRACTION ROBUSTE : Détection dynamique + Extraction simple
=============================================================

PHASE 1 : Détection intelligente des pages
   - Cherche les pages par leur contenu, PAS par leur numéro
   - Utilise des signatures uniques et discriminantes

PHASE 2 : Extraction ciblée
   - Une fois la bonne page trouvée, extraction simple et efficace
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


# ============================================================================
# PHASE 1 : DÉTECTION INTELLIGENTE DES PAGES
# ============================================================================

class DetecteurPages:
    """
    Détecte les pages importantes en analysant leur contenu.
    N'utilise JAMAIS de numéros de page fixes.
    """

    # Signatures UNIQUES pour chaque type de tableau
    # On cherche des combinaisons de mots qui n'apparaissent QUE sur la bonne page
    SIGNATURES = {
        'BILAN_ACTIF': {
            'obligatoires': ['BILAN', 'ACTIF'],  # Doivent être présents
            'discriminants': [
                'Capital souscrit non appelé',  # Ligne spécifique au bilan actif
                'ACTIF IMMOBILISÉ',
                'ACTIF CIRCULANT',
                'Frais d\'établissement'
            ],
            'seuil_discriminants': 2  # Au moins 2 discriminants doivent être présents
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
        """
        Détecte le type d'une page en analysant son contenu.

        Args:
            page_text: Texte brut de la page
            table_data: Données du tableau principal

        Returns:
            Type de page ('BILAN_ACTIF', 'BILAN_PASSIF', etc.) ou None
        """
        if not page_text:
            return None

        page_text_upper = page_text.upper()

        # Convertir le tableau en texte
        table_text = ""
        if table_data:
            table_text = " ".join([
                str(cell).upper()
                for row in table_data[:15]  # Premières lignes
                for cell in row
                if cell
            ])

        texte_complet = page_text_upper + " " + table_text

        # Tester chaque signature
        for type_page, signature in DetecteurPages.SIGNATURES.items():
            # Vérifier les mots obligatoires
            tous_obligatoires_presents = all(
                mot.upper() in texte_complet
                for mot in signature['obligatoires']
            )

            if not tous_obligatoires_presents:
                continue

            # Compter les discriminants présents
            nb_discriminants = sum(
                1 for mot in signature['discriminants']
                if mot.upper() in texte_complet
            )

            # Si on atteint le seuil, on a trouvé le bon type
            if nb_discriminants >= signature['seuil_discriminants']:
                return type_page

        return None

    @staticmethod
    def trouver_pages(pdf_path: str) -> Dict[str, Tuple[int, List[List]]]:
        """
        Parcourt tout le PDF et identifie les pages importantes.

        Args:
            pdf_path: Chemin vers le PDF

        Returns:
            Dict {type_page: (numero_page, table_data)}
        """
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
                    # Ne garder que la première occurrence de chaque type
                    if type_page not in pages_trouvees:
                        pages_trouvees[type_page] = (page_idx, table_principale)
                        print(f"  ✓ {type_page} détecté à la page {page_idx + 1}")

        return pages_trouvees


# ============================================================================
# PHASE 2 : EXTRACTION DES DONNÉES
# ============================================================================

def trouver_colonne_avec_en_tete(table_data: List[List], mots_cles: List[str]) -> Optional[int]:
    """Trouve l'index de la colonne contenant l'un des mots-clés dans les en-têtes"""
    if not table_data:
        return None

    for row in table_data[:5]:  # Analyser les 5 premières lignes
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


def trouver_colonne_montant_derniere(table_data: List[List]) -> Optional[int]:
    """Trouve la dernière colonne contenant des montants (en partant de la droite)"""
    if not table_data or not table_data[0]:
        return None

    for col_idx in range(len(table_data[0]) - 1, -1, -1):
        nb_montants = 0

        for row_idx in range(5, min(15, len(table_data))):
            if row_idx < len(table_data) and col_idx < len(table_data[row_idx]):
                cell = table_data[row_idx][col_idx]
                if cell and nettoyer_montant(cell) is not None:
                    nb_montants += 1

        if nb_montants >= 3:
            return col_idx

    return None


def extraire_donnees_avec_codes(
    table_data: List[List],
    codes_recherches: Dict[str, str],
    col_codes: Optional[int],
    col_montant: int,
    ligne_debut: int = 5
) -> Dict[str, float]:
    """Extrait les montants d'un tableau en cherchant les codes"""
    resultats = {}
    codes_majuscules = {code.upper(): libelle for code, libelle in codes_recherches.items()}

    for row_idx in range(ligne_debut, len(table_data)):
        row = table_data[row_idx]

        if not row or len(row) <= max(col_montant, col_codes or 0):
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

        # Si code trouvé, extraire le montant
        if code_trouve and col_montant < len(row):
            montant_brut = row[col_montant]
            montant = nettoyer_montant(montant_brut)

            if montant is not None:
                libelle = codes_majuscules[code_trouve]
                resultats[libelle] = montant

    return resultats


# ============================================================================
# ORCHESTRATEUR PRINCIPAL
# ============================================================================

def extraire_pdf_complet(
    pdf_path: str,
    codes_actif: Dict[str, str],
    codes_passif: Dict[str, str],
    codes_cr: Dict[str, str]
) -> Dict:
    """
    Extrait toutes les données d'un PDF de liasse fiscale.
    Utilise la détection dynamique - pas de numéros de page fixes !

    Returns:
        Dict avec clés 'actif', 'passif', 'cr'
    """
    print("\n" + "="*80)
    print("EXTRACTION ROBUSTE - DÉTECTION DYNAMIQUE")
    print("="*80)

    # PHASE 1 : Détecter les pages
    print("\n📍 PHASE 1 : Détection des pages importantes...")
    pages = DetecteurPages.trouver_pages(pdf_path)

    if not pages:
        print("\n❌ Aucune page identifiée")
        return {'actif': {}, 'passif': {}, 'cr': {}}

    print(f"\n✓ {len(pages)} page(s) identifiée(s)\n")

    # PHASE 2 : Extraire les données
    print("📍 PHASE 2 : Extraction des données...")
    resultats = {}

    # --- BILAN ACTIF ---
    if 'BILAN_ACTIF' in pages:
        print("\n→ Extraction BILAN ACTIF...")
        page_idx, table = pages['BILAN_ACTIF']

        # Chercher colonne "Net" ou "Brut"
        col_montant = trouver_colonne_avec_en_tete(table, ['net', 'brut'])
        if col_montant is None:
            col_montant = trouver_colonne_montant_derniere(table)

        col_codes = trouver_colonne_code(table)

        if col_montant is not None:
            print(f"  ✓ Colonne montant : index {col_montant}")
            if col_codes:
                print(f"  ✓ Colonne codes : index {col_codes}")

            donnees = extraire_donnees_avec_codes(table, codes_actif, col_codes, col_montant)
            resultats['actif'] = donnees
            print(f"  ✓ {len(donnees)}/{len(codes_actif)} codes extraits")
        else:
            print("  ❌ Colonne montant non trouvée")
            resultats['actif'] = {}
    else:
        print("\n⚠️  BILAN ACTIF non trouvé")
        resultats['actif'] = {}

    # --- BILAN PASSIF ---
    if 'BILAN_PASSIF' in pages:
        print("\n→ Extraction BILAN PASSIF...")
        page_idx, table = pages['BILAN_PASSIF']

        col_montant = trouver_colonne_montant_derniere(table)
        col_codes = trouver_colonne_code(table)

        if col_montant is not None:
            print(f"  ✓ Colonne montant : index {col_montant}")
            if col_codes:
                print(f"  ✓ Colonne codes : index {col_codes}")

            donnees = extraire_donnees_avec_codes(table, codes_passif, col_codes, col_montant)
            resultats['passif'] = donnees
            print(f"  ✓ {len(donnees)}/{len(codes_passif)} codes extraits")
        else:
            print("  ❌ Colonne montant non trouvée")
            resultats['passif'] = {}
    else:
        print("\n⚠️  BILAN PASSIF non trouvé")
        resultats['passif'] = {}

    # --- COMPTE DE RÉSULTAT ---
    # Note: Il peut y avoir 2 pages de compte de résultat
    pages_cr = [(k, v) for k, v in pages.items() if k == 'COMPTE_RESULTAT']

    if pages_cr:
        print("\n→ Extraction COMPTE DE RÉSULTAT...")
        donnees_cr = {}

        for type_page, (page_idx, table) in pages_cr:
            col_montant = trouver_colonne_avec_en_tete(table, ['total', 'exercice'])
            if col_montant is None:
                col_montant = trouver_colonne_montant_derniere(table)

            col_codes = trouver_colonne_code(table)

            if col_montant is not None:
                print(f"  ✓ Page {page_idx + 1} - Colonne montant : index {col_montant}")
                donnees = extraire_donnees_avec_codes(table, codes_cr, col_codes, col_montant)
                donnees_cr.update(donnees)

        resultats['cr'] = donnees_cr
        print(f"  ✓ {len(donnees_cr)}/{len(codes_cr)} codes extraits")
    else:
        print("\n⚠️  COMPTE DE RÉSULTAT non trouvé")
        resultats['cr'] = {}

    print("\n" + "="*80)
    print("✓ EXTRACTION TERMINÉE")
    print("="*80)
    print(f"\nRésumé :")
    print(f"  - ACTIF : {len(resultats.get('actif', {}))} valeurs")
    print(f"  - PASSIF : {len(resultats.get('passif', {}))} valeurs")
    print(f"  - COMPTE DE RÉSULTAT : {len(resultats.get('cr', {}))} valeurs")
    print()

    return resultats


if __name__ == "__main__":
    print("Module d'extraction robuste chargé.")
    print("Utilise la détection dynamique - pas de numéros de page fixes !")
