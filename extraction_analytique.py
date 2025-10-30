"""
Module d'extraction analytique de liasses fiscales
===================================================

Approche en 3 phases pour une extraction robuste et adaptable :
1. PHASE DÉTECTION : Identifier les pages et tableaux pertinents
2. PHASE ANALYSE : Analyser la structure (colonnes de libellés, codes, montants)
3. PHASE EXTRACTION : Extraire les données selon les règles métier

Auteur: Claude
Version: 2.0 - Approche analytique
"""

import pdfplumber
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# CLASSES DE DONNÉES
# ============================================================================

class TypeTableau(Enum):
    """Types de tableaux fiscaux à extraire"""
    ACTIF = "actif"
    PASSIF = "passif"
    COMPTE_RESULTAT_1 = "compte_resultat_1"
    COMPTE_RESULTAT_2 = "compte_resultat_2"
    ETAT_ECHEANCES = "etat_echeances"
    AFFECTATION_RESULTAT = "affectation_resultat"


@dataclass
class StructureColonne:
    """Structure d'une colonne identifiée dans un tableau"""
    index: int
    type_colonne: str  # 'code', 'libelle', 'montant_brut', 'montant_net', 'exercice_n', 'exercice_n-1', etc.
    en_tete: str
    confiance: float  # Score de confiance de l'identification (0.0 à 1.0)


@dataclass
class TableauAnalyse:
    """Résultat de l'analyse d'un tableau"""
    type_tableau: TypeTableau
    page_index: int
    table_data: List[List]
    colonnes: List[StructureColonne]
    regles_extraction: Dict  # Règles métier spécifiques au tableau


# ============================================================================
# PHASE 1 : DÉTECTION DES TABLEAUX
# ============================================================================

class DetecteurTableaux:
    """Détecte et identifie les différents tableaux dans le PDF"""

    # Mots-clés pour identifier chaque type de tableau
    # Note : Les mots-clés sont ordonnés par importance (premiers = plus discriminants)
    SIGNATURES_TABLEAUX = {
        TypeTableau.ACTIF: [
            "ACTIF IMMOBILISÉ",
            "ACTIF CIRCULANT",
            "Brut",
            "Amortissements",
            "Net"
        ],
        TypeTableau.PASSIF: [
            "Capital social ou individuel",
            "capitaux propres",
            "Dettes fournisseurs",
            "PASSIF"
        ],
        TypeTableau.COMPTE_RESULTAT_1: [
            "Ventes de marchandises",
            "Production vendue",
            "PRODUITS D'EXPLOITATION",
            "CHARGES D'EXPLOITATION"
        ],
        TypeTableau.COMPTE_RESULTAT_2: [
            "Produits exceptionnels",
            "Charges exceptionnelles",
            "RÉSULTAT EXCEPTIONNEL",
            "Impôts sur les bénéfices"
        ],
        TypeTableau.ETAT_ECHEANCES: [
            "ÉTAT DES CRÉANCES",
            "ÉTAT DES DETTES",
            "MONTANT BRUT",
            "clients douteux"
        ],
        TypeTableau.AFFECTATION_RESULTAT: [
            "AFFECTATION DU RÉSULTAT",
            "dividendes",
            "Report à nouveau",
            "crédit-bail"
        ]
    }

    # Seuils minimums de correspondance pour valider un type de tableau
    SEUILS_DETECTION = {
        TypeTableau.ACTIF: 2,  # Au moins 2 mots-clés doivent correspondre
        TypeTableau.PASSIF: 2,
        TypeTableau.COMPTE_RESULTAT_1: 2,
        TypeTableau.COMPTE_RESULTAT_2: 2,
        TypeTableau.ETAT_ECHEANCES: 2,
        TypeTableau.AFFECTATION_RESULTAT: 2
    }

    @staticmethod
    def detecter_type_tableau(page_text: str, table_data: List[List]) -> Optional[TypeTableau]:
        """
        Détecte le type d'un tableau en analysant le texte de la page et le contenu du tableau.

        Args:
            page_text: Texte extrait de la page
            table_data: Données brutes du tableau

        Returns:
            TypeTableau ou None si non identifié
        """
        if not page_text or not table_data:
            return None

        page_text_lower = page_text.lower()

        # Convertir le tableau en texte pour analyse
        table_text = " ".join([
            str(cell).lower()
            for row in table_data[:10]  # Analyser les 10 premières lignes
            for cell in row
            if cell
        ])

        # Scorer chaque type de tableau en comptant les correspondances
        scores = {}
        correspondances = {}

        for type_tab, signatures in DetecteurTableaux.SIGNATURES_TABLEAUX.items():
            nb_correspondances = 0
            score = 0

            for signature in signatures:
                signature_lower = signature.lower()
                trouve = False

                if signature_lower in page_text_lower:
                    score += 2
                    trouve = True
                if signature_lower in table_text:
                    score += 3
                    trouve = True

                if trouve:
                    nb_correspondances += 1

            scores[type_tab] = score
            correspondances[type_tab] = nb_correspondances

        # Retourner le type avec le meilleur score SI il atteint le seuil minimum
        if scores:
            meilleur_type, meilleur_score = max(scores.items(), key=lambda x: x[1])
            nb_corresp = correspondances[meilleur_type]
            seuil = DetecteurTableaux.SEUILS_DETECTION.get(meilleur_type, 1)

            # Vérifier que le nombre de correspondances atteint le seuil
            if meilleur_score > 0 and nb_corresp >= seuil:
                return meilleur_type

        return None

    @staticmethod
    def detecter_tous_tableaux(pdf_path: str) -> List[TableauAnalyse]:
        """
        Parcourt tout le PDF et détecte tous les tableaux pertinents.

        Args:
            pdf_path: Chemin vers le fichier PDF

        Returns:
            Liste des tableaux détectés avec leur type
        """
        tableaux_detectes = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                tables = page.extract_tables()

                for table in tables:
                    if not table or len(table) < 3:  # Ignorer les tableaux trop petits
                        continue

                    type_tableau = DetecteurTableaux.detecter_type_tableau(page_text, table)

                    if type_tableau:
                        print(f"✓ {type_tableau.value} détecté à la page {page_idx + 1}")

                        tableau_analyse = TableauAnalyse(
                            type_tableau=type_tableau,
                            page_index=page_idx,
                            table_data=table,
                            colonnes=[],  # Sera rempli en Phase 2
                            regles_extraction={}  # Sera rempli en Phase 2
                        )
                        tableaux_detectes.append(tableau_analyse)

        return tableaux_detectes


# ============================================================================
# PHASE 2 : ANALYSE DE LA STRUCTURE DES COLONNES
# ============================================================================

class AnalyseurStructure:
    """Analyse la structure des tableaux pour identifier les colonnes"""

    # Mots-clés pour identifier les types de colonnes
    MOTS_CLES_COLONNES = {
        'code': ['code', 'réf', 'ref'],
        'libelle': ['libellé', 'libelle', 'désignation', 'designation', 'intitulé'],
        'montant_brut': ['brut'],
        'montant_net': ['net'],
        'amortissement': ['amortissement', 'amort.', 'amort'],
        'exercice_n': ['exercice n', 'n ', ' n'],
        'exercice_n_moins_1': ['exercice n-1', 'n-1'],
        'total': ['total']
    }

    @staticmethod
    def analyser_en_tetes(table_data: List[List]) -> List[StructureColonne]:
        """
        Analyse les en-têtes du tableau pour identifier les colonnes.

        Args:
            table_data: Données brutes du tableau

        Returns:
            Liste des colonnes identifiées avec leurs caractéristiques
        """
        colonnes = []

        # Analyser les 5 premières lignes pour trouver les en-têtes
        en_tetes_candidats = []
        for row_idx in range(min(5, len(table_data))):
            row = table_data[row_idx]
            if not row:
                continue

            # Vérifier si cette ligne contient des en-têtes
            est_en_tete = False
            for cell in row:
                if cell:
                    cell_lower = str(cell).lower()
                    for type_col, mots_cles in AnalyseurStructure.MOTS_CLES_COLONNES.items():
                        if any(mot in cell_lower for mot in mots_cles):
                            est_en_tete = True
                            break
                if est_en_tete:
                    break

            if est_en_tete:
                en_tetes_candidats.append((row_idx, row))

        # Prendre la ligne d'en-tête la plus complète
        if not en_tetes_candidats:
            print("⚠️ Aucun en-tête détecté, analyse des colonnes par position...")
            return AnalyseurStructure._analyser_par_position(table_data)

        # Sélectionner la meilleure ligne d'en-tête
        meilleure_ligne = max(en_tetes_candidats,
                             key=lambda x: sum(1 for cell in x[1] if cell and str(cell).strip()))
        row_idx, en_tetes = meilleure_ligne

        # Analyser chaque colonne
        for col_idx, en_tete in enumerate(en_tetes):
            if not en_tete:
                continue

            en_tete_str = str(en_tete).strip()
            en_tete_lower = en_tete_str.lower()

            # Identifier le type de colonne
            type_col = 'inconnu'
            confiance = 0.5

            for type_candidat, mots_cles in AnalyseurStructure.MOTS_CLES_COLONNES.items():
                for mot in mots_cles:
                    if mot in en_tete_lower:
                        type_col = type_candidat
                        confiance = 0.9
                        break
                if confiance > 0.5:
                    break

            colonne = StructureColonne(
                index=col_idx,
                type_colonne=type_col,
                en_tete=en_tete_str,
                confiance=confiance
            )
            colonnes.append(colonne)

        return colonnes

    @staticmethod
    def _analyser_par_position(table_data: List[List]) -> List[StructureColonne]:
        """
        Analyse de secours basée sur la position et le contenu typique des colonnes.

        Args:
            table_data: Données brutes du tableau

        Returns:
            Liste des colonnes devinées
        """
        colonnes = []

        if not table_data or len(table_data) < 5:
            return colonnes

        # Analyser les 10 premières lignes de données (ignorer la première ligne d'en-tête)
        nb_colonnes = len(table_data[0])

        for col_idx in range(nb_colonnes):
            # Extraire les valeurs de cette colonne
            valeurs = []
            for row_idx in range(1, min(10, len(table_data))):
                if col_idx < len(table_data[row_idx]):
                    val = table_data[row_idx][col_idx]
                    if val:
                        valeurs.append(str(val).strip())

            if not valeurs:
                continue

            # Détecter le type basé sur le contenu
            type_col = AnalyseurStructure._deviner_type_colonne(valeurs)

            colonne = StructureColonne(
                index=col_idx,
                type_colonne=type_col,
                en_tete=f"Colonne {col_idx}",
                confiance=0.6
            )
            colonnes.append(colonne)

        return colonnes

    @staticmethod
    def _deviner_type_colonne(valeurs: List[str]) -> str:
        """
        Devine le type d'une colonne basé sur son contenu.

        Args:
            valeurs: Liste de valeurs de la colonne

        Returns:
            Type de colonne deviné
        """
        # Compter les types de contenu
        nb_codes = 0  # Codes comme "AB", "DA", "FL"
        nb_montants = 0  # Valeurs numériques
        nb_texte_long = 0  # Texte long (libellés)

        for val in valeurs:
            val_upper = val.upper().strip()

            # Code : 2 lettres majuscules
            if len(val_upper) == 2 and val_upper.isalpha():
                nb_codes += 1

            # Montant : contient des chiffres et possiblement espaces, points, virgules
            elif any(c.isdigit() for c in val):
                nb_montants += 1

            # Texte long : plus de 10 caractères
            elif len(val) > 10:
                nb_texte_long += 1

        total = len(valeurs)
        if total == 0:
            return 'inconnu'

        # Décider du type majoritaire
        if nb_codes / total > 0.5:
            return 'code'
        elif nb_montants / total > 0.5:
            return 'montant'
        elif nb_texte_long / total > 0.5:
            return 'libelle'
        else:
            return 'mixte'

    @staticmethod
    def identifier_colonnes_montants(colonnes: List[StructureColonne]) -> List[StructureColonne]:
        """
        Identifie et classe les colonnes de montants par ordre d'apparition.

        Args:
            colonnes: Liste des colonnes déjà identifiées

        Returns:
            Liste des colonnes de type montant, triées par index
        """
        colonnes_montants = [
            col for col in colonnes
            if 'montant' in col.type_colonne or col.type_colonne in ['exercice_n', 'exercice_n_moins_1', 'total']
        ]

        return sorted(colonnes_montants, key=lambda x: x.index)


# ============================================================================
# PHASE 3 : EXTRACTION AVEC RÈGLES MÉTIER
# ============================================================================

class ExtracteurDonnees:
    """Extrait les données selon les règles métier spécifiques à chaque tableau"""

    # Règles métier : quel numéro de colonne de montant utiliser pour chaque type
    REGLES_COLONNES_MONTANTS = {
        TypeTableau.ACTIF: {
            'colonne_prioritaire': 'montant_net',  # Chercher d'abord 'Net'
            'numero_colonne_fallback': 3  # 3ème colonne de montant si pas de 'Net'
        },
        TypeTableau.PASSIF: {
            'colonne_prioritaire': 'exercice_n',
            'numero_colonne_fallback': 1  # 1ère colonne de montant
        },
        TypeTableau.COMPTE_RESULTAT_1: {
            'colonne_prioritaire': 'exercice_n',
            'numero_colonne_fallback': 1  # 1ère colonne de montant
        },
        TypeTableau.COMPTE_RESULTAT_2: {
            'colonne_prioritaire': 'exercice_n',
            'numero_colonne_fallback': 1  # 1ère colonne de montant
        },
        TypeTableau.ETAT_ECHEANCES: {
            'numero_colonne': 1  # 1ère colonne de montant
        },
        TypeTableau.AFFECTATION_RESULTAT: {
            'numero_colonne': 1  # 1ère colonne de montant
        },
        'clients_douteux': {
            'numero_colonne': 1  # 1ère colonne de montant
        },
        'groupes_associes_actif': {
            'numero_colonne': 1  # 1ère colonne de montant
        },
        'annuites': {
            'numero_colonne': 2  # 2ème colonne de montant
        },
        'groupes_associes_passif': {
            'numero_colonne': 1  # 1ère colonne de montant
        }
    }

    @staticmethod
    def determiner_colonne_extraction(
        tableau: TableauAnalyse,
        code_specifique: Optional[str] = None
    ) -> Optional[int]:
        """
        Détermine quelle colonne utiliser pour l'extraction selon les règles métier.

        Args:
            tableau: Tableau analysé
            code_specifique: Code spécifique (pour règles particulières)

        Returns:
            Index de la colonne à utiliser pour l'extraction
        """
        # Récupérer les règles métier pour ce type de tableau
        regles = ExtracteurDonnees.REGLES_COLONNES_MONTANTS.get(tableau.type_tableau)

        if not regles:
            print(f"⚠️ Pas de règles métier pour {tableau.type_tableau}")
            return None

        # Identifier toutes les colonnes de montants
        colonnes_montants = AnalyseurStructure.identifier_colonnes_montants(tableau.colonnes)

        if not colonnes_montants:
            print("⚠️ Aucune colonne de montant identifiée")
            return None

        # STRATÉGIE 1 : Chercher la colonne prioritaire par nom
        if 'colonne_prioritaire' in regles:
            type_prioritaire = regles['colonne_prioritaire']
            for col in tableau.colonnes:
                if type_prioritaire in col.type_colonne:
                    print(f"✓ Colonne '{col.en_tete}' (index {col.index}) sélectionnée (priorité: {type_prioritaire})")
                    return col.index

        # STRATÉGIE 2 : Utiliser le numéro de colonne de fallback
        if 'numero_colonne_fallback' in regles:
            numero = regles['numero_colonne_fallback']
            if numero <= len(colonnes_montants):
                col_selectionnee = colonnes_montants[numero - 1]
                print(f"✓ Colonne #{numero} de montant (index {col_selectionnee.index}) sélectionnée (fallback)")
                return col_selectionnee.index

        # STRATÉGIE 3 : Utiliser le numéro de colonne direct
        if 'numero_colonne' in regles:
            numero = regles['numero_colonne']
            if numero <= len(colonnes_montants):
                col_selectionnee = colonnes_montants[numero - 1]
                print(f"✓ Colonne #{numero} de montant (index {col_selectionnee.index}) sélectionnée")
                return col_selectionnee.index

        # Par défaut : prendre la première colonne de montant
        col_defaut = colonnes_montants[0]
        print(f"⚠️ Utilisation de la colonne par défaut (index {col_defaut.index})")
        return col_defaut.index

    @staticmethod
    def extraire_donnees_tableau(
        tableau: TableauAnalyse,
        codes_recherches: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Extrait les données d'un tableau en utilisant les codes et la colonne déterminée.

        Args:
            tableau: Tableau analysé
            codes_recherches: Dictionnaire {code: libellé}

        Returns:
            Dictionnaire {libellé: montant}
        """
        resultats = {}

        # Déterminer quelle colonne utiliser
        col_montant_idx = ExtracteurDonnees.determiner_colonne_extraction(tableau)

        if col_montant_idx is None:
            print("❌ Impossible de déterminer la colonne de montants")
            return resultats

        # Trouver la colonne des codes (si elle existe)
        col_codes = next((col for col in tableau.colonnes if col.type_colonne == 'code'), None)

        # Parcourir les lignes du tableau
        for row_idx, row in enumerate(tableau.table_data):
            if not row or row_idx < 2:  # Ignorer les en-têtes
                continue

            # Chercher un code dans cette ligne
            code_trouve = None

            # Méthode 1 : Chercher dans la colonne des codes identifiée
            if col_codes and col_codes.index < len(row):
                cell = row[col_codes.index]
                if cell:
                    cell_upper = str(cell).strip().upper()
                    if cell_upper in codes_recherches:
                        code_trouve = cell_upper

            # Méthode 2 : Chercher dans toutes les colonnes
            if not code_trouve:
                for cell in row:
                    if cell:
                        cell_upper = str(cell).strip().upper()
                        if cell_upper in codes_recherches:
                            code_trouve = cell_upper
                            break

            # Si un code est trouvé, extraire le montant
            if code_trouve:
                if col_montant_idx < len(row):
                    montant_brut = row[col_montant_idx]
                    montant = ExtracteurDonnees.nettoyer_montant(montant_brut)

                    if montant is not None:
                        libelle = codes_recherches[code_trouve]
                        resultats[libelle] = montant
                        print(f"  {code_trouve} → {libelle}: {montant:,.2f}")

        print(f"\n✓ {len(resultats)} valeurs extraites sur {len(codes_recherches)} codes recherchés")
        return resultats

    @staticmethod
    def nettoyer_montant(texte) -> Optional[float]:
        """
        Nettoie et convertit un montant textuel en nombre.

        Gère les montants négatifs sous plusieurs formats :
        - (1 000 000) → -1000000
        - -1 000 000 → -1000000
        - 1 000 000- → -1000000
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
        texte = texte.replace(',', '.').replace(' ', '').replace('\xa0', '')

        try:
            return float(texte)
        except:
            return None


# ============================================================================
# ORCHESTRATEUR PRINCIPAL
# ============================================================================

class ExtractionAnalytique:
    """Orchestrateur principal de l'extraction analytique"""

    @staticmethod
    def extraire_pdf_complet(
        pdf_path: str,
        codes_actif: Dict[str, str],
        codes_passif: Dict[str, str],
        codes_cr: Dict[str, str]
    ) -> Dict:
        """
        Extrait toutes les données d'un PDF en utilisant l'approche analytique.

        Args:
            pdf_path: Chemin vers le PDF
            codes_actif: Codes à chercher pour l'actif
            codes_passif: Codes à chercher pour le passif
            codes_cr: Codes à chercher pour le compte de résultat

        Returns:
            Dictionnaire avec toutes les données extraites
        """
        print("\n" + "="*80)
        print("EXTRACTION ANALYTIQUE - APPROCHE EN 3 PHASES")
        print("="*80 + "\n")

        # ========================================
        # PHASE 1 : DÉTECTION DES TABLEAUX
        # ========================================
        print("📍 PHASE 1 : Détection des tableaux")
        print("-" * 80)

        tableaux = DetecteurTableaux.detecter_tous_tableaux(pdf_path)

        if not tableaux:
            print("❌ Aucun tableau détecté dans le PDF")
            return {}

        print(f"\n✓ {len(tableaux)} tableau(x) détecté(s)\n")

        # ========================================
        # PHASE 2 : ANALYSE DES STRUCTURES
        # ========================================
        print("📍 PHASE 2 : Analyse de la structure des colonnes")
        print("-" * 80)

        for tableau in tableaux:
            print(f"\n→ Analyse du tableau '{tableau.type_tableau.value}'...")

            # Analyser les en-têtes et colonnes
            colonnes = AnalyseurStructure.analyser_en_tetes(tableau.table_data)
            tableau.colonnes = colonnes

            print(f"  Colonnes identifiées :")
            for col in colonnes:
                print(f"    - Index {col.index}: {col.type_colonne} ('{col.en_tete}') [confiance: {col.confiance:.0%}]")

        print("\n✓ Analyse terminée\n")

        # ========================================
        # PHASE 3 : EXTRACTION DES DONNÉES
        # ========================================
        print("📍 PHASE 3 : Extraction des données")
        print("-" * 80)

        resultats = {}

        # Extraire l'ACTIF
        tableau_actif = next((t for t in tableaux if t.type_tableau == TypeTableau.ACTIF), None)
        if tableau_actif:
            print("\n→ Extraction du BILAN ACTIF...")
            resultats['actif'] = ExtracteurDonnees.extraire_donnees_tableau(tableau_actif, codes_actif)
        else:
            print("\n⚠️ Tableau ACTIF non trouvé")
            resultats['actif'] = {}

        # Extraire le PASSIF
        tableau_passif = next((t for t in tableaux if t.type_tableau == TypeTableau.PASSIF), None)
        if tableau_passif:
            print("\n→ Extraction du BILAN PASSIF...")
            resultats['passif'] = ExtracteurDonnees.extraire_donnees_tableau(tableau_passif, codes_passif)
        else:
            print("\n⚠️ Tableau PASSIF non trouvé")
            resultats['passif'] = {}

        # Extraire le COMPTE DE RÉSULTAT (pages 1 et 2)
        tableaux_cr = [t for t in tableaux if t.type_tableau in [TypeTableau.COMPTE_RESULTAT_1, TypeTableau.COMPTE_RESULTAT_2]]
        if tableaux_cr:
            print("\n→ Extraction du COMPTE DE RÉSULTAT...")
            resultats_cr = {}
            for tab_cr in tableaux_cr:
                donnees_cr = ExtracteurDonnees.extraire_donnees_tableau(tab_cr, codes_cr)
                resultats_cr.update(donnees_cr)
            resultats['cr'] = resultats_cr
        else:
            print("\n⚠️ Tableaux COMPTE DE RÉSULTAT non trouvés")
            resultats['cr'] = {}

        print("\n" + "="*80)
        print("✓ EXTRACTION TERMINÉE")
        print("="*80 + "\n")

        return resultats


# ============================================================================
# FONCTION DE TEST
# ============================================================================

if __name__ == "__main__":
    print("Module d'extraction analytique chargé.")
    print("Utilisez ExtractionAnalytique.extraire_pdf_complet() pour extraire un PDF.")
