"""
Extracteur pour le Compte de Résultat (Formulaire 2052).

Ce module gère l'extraction des données du compte de résultat depuis les PDFs
de liasses fiscales. Le compte de résultat s'étend sur 2 pages.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_COMPTE_RESULTAT, SEUIL_REUSSITE_CODES_COMPTE_RESULTAT
from src.config.mots_cles import MOTS_CLES_COMPTE_RESULTAT, LIBELLES_COMPTE_RESULTAT
from src.utils.pdf_utils import obtenir_colonne_numerique, detecter_colonnes_numeriques
from src.utils.text_processing import nettoyer_montant
from src.utils.extraction_fallback import (
    detecter_extraction_fusionnee,
    extraire_codes_depuis_texte_fusionne,
    extraire_montants_depuis_texte_fusionne
)
from src.utils.extraction_ligne_par_ligne import extraire_cr_ligne_par_ligne


class CompteResultatExtractor(BaseExtractor):
    """Extracteur pour le Compte de Résultat (2 pages)."""

    def __init__(self):
        super().__init__(
            codes_dict=CODES_COMPTE_RESULTAT,
            mots_cles_dict=MOTS_CLES_COMPTE_RESULTAT,
            seuil_reussite=SEUIL_REUSSITE_CODES_COMPTE_RESULTAT
        )

    def extraire_par_codes(self, pdf, table=None):
        """Extrait le Compte de Résultat en cherchant les CODES dans les tableaux des DEUX pages.

        Le Compte de Résultat est sur 2 pages :
        - PAGE 1 (page 3 du PDF) : Codes FA à GW
        - PAGE 2 (page 4 du PDF) : Codes HA à HN + HP, HQ, A1

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Non utilisé (extraction depuis le PDF directement)

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        print("   → Tentative d'extraction par CODES (2 pages)...")

        codes_trouves = {}

        # ========================================
        # ÉTAPE 1 : TRAITER LA PAGE 1
        # ========================================
        print("\n   📄 Traitement de la PAGE 1 du Compte de Résultat...")
        cr_page1_index = self._trouver_page_compte_resultat_1(pdf)

        if cr_page1_index != -1:
            tables_page1 = pdf.pages[cr_page1_index].extract_tables()
            if tables_page1:
                table_page1 = tables_page1[0]
                idx_montant_page1 = self._trouver_colonne_page1(table_page1)

                if idx_montant_page1 is not None:
                    codes_page1, nb_page1 = self._extraire_codes_du_tableau(table_page1, idx_montant_page1)

                    # Fallback si aucun code trouvé et extraction fusionnée
                    if nb_page1 == 0 and detecter_extraction_fusionnee(table_page1):
                        print("   🔄 [PAGE 1] Extraction fusionnée détectée. Utilisation du parser de fallback...")
                        codes_info = extraire_codes_depuis_texte_fusionne(table_page1, self.codes_dict)

                        if codes_info:
                            print(f"   ✅ [PAGE 1] {len(codes_info)} codes trouvés dans le texte fusionné")
                            montants_texte = extraire_montants_depuis_texte_fusionne(codes_info, idx_montant_page1)

                            for code, montant_texte in montants_texte.items():
                                montant = nettoyer_montant(montant_texte)
                                codes_page1[code] = montant if montant is not None else 0.0

                    codes_trouves.update(codes_page1)

        # ========================================
        # ÉTAPE 2 : TRAITER LA PAGE 2
        # ========================================
        print("\n   📄 Traitement de la PAGE 2 du Compte de Résultat...")
        cr_page2_index = self._trouver_page_compte_resultat_2(pdf)

        if cr_page2_index != -1:
            tables_page2 = pdf.pages[cr_page2_index].extract_tables()
            if tables_page2:
                table_page2 = tables_page2[0]
                idx_montant_page2 = self._trouver_colonne_page2(table_page2)

                if idx_montant_page2 is not None:
                    codes_page2, nb_page2 = self._extraire_codes_du_tableau(table_page2, idx_montant_page2)

                    # Fallback si aucun code trouvé et extraction fusionnée
                    if nb_page2 == 0 and detecter_extraction_fusionnee(table_page2):
                        print("   🔄 [PAGE 2] Extraction fusionnée détectée. Utilisation du parser de fallback...")
                        codes_info = extraire_codes_depuis_texte_fusionne(table_page2, self.codes_dict)

                        if codes_info:
                            print(f"   ✅ [PAGE 2] {len(codes_info)} codes trouvés dans le texte fusionné")
                            montants_texte = extraire_montants_depuis_texte_fusionne(codes_info, idx_montant_page2)

                            for code, montant_texte in montants_texte.items():
                                montant = nettoyer_montant(montant_texte)
                                codes_page2[code] = montant if montant is not None else 0.0

                    codes_trouves.update(codes_page2)

        nb_trouves = len([v for v in codes_trouves.values() if v != 0.0])
        print(f"\n   ℹ️ Codes détectés : {len(codes_trouves)} | Valeurs non-nulles : {nb_trouves}")

        resultats = self._convertir_en_resultats(codes_trouves)
        return resultats, nb_trouves

    def extraire_par_libelles(self, pdf, table=None):
        """Extrait le Compte de Résultat en cherchant les LIBELLÉS (méthode ligne par ligne).

        Le Compte de Résultat s'étend sur 2 pages. On traite chaque page séparément
        puis on fusionne les résultats.

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Non utilisé

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par LIBELLÉS (méthode ligne par ligne sur 2 pages)")

        resultats_dict = {}

        # ========================================
        # TRAITER LA PAGE 1
        # ========================================
        print("\n   📄 Traitement PAGE 1 - Extraction par libellés ligne par ligne...")
        cr_page1_index = self._trouver_page_compte_resultat_1(pdf)

        if cr_page1_index != -1:
            tables_page1 = pdf.pages[cr_page1_index].extract_tables()
            if tables_page1:
                table_page1 = tables_page1[0]
                resultats_page1 = extraire_cr_ligne_par_ligne(table_page1, LIBELLES_COMPTE_RESULTAT, debug=True)
                resultats_dict.update(resultats_page1)

        # ========================================
        # TRAITER LA PAGE 2
        # ========================================
        print("\n   📄 Traitement PAGE 2 - Extraction par libellés ligne par ligne...")
        cr_page2_index = self._trouver_page_compte_resultat_2(pdf)

        if cr_page2_index != -1:
            tables_page2 = pdf.pages[cr_page2_index].extract_tables()
            if tables_page2:
                table_page2 = tables_page2[0]
                resultats_page2 = extraire_cr_ligne_par_ligne(table_page2, LIBELLES_COMPTE_RESULTAT, debug=True)
                resultats_dict.update(resultats_page2)

        # Convertir en liste de tuples dans l'ordre des libellés
        return [(libelle, resultats_dict.get(libelle, 0)) for libelle in LIBELLES_COMPTE_RESULTAT.keys()]

    def _trouver_page_compte_resultat_1(self, pdf):
        """Trouve la page 1 du Compte de Résultat (Produits et Charges d'exploitation)."""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and ("Ventes de marchandises" in text or "Ventes" in text):
                print(f"   ✓ Page 1 identifiée : page {i + 1} du PDF")
                return i
        return -1

    def _trouver_page_compte_resultat_2(self, pdf):
        """Trouve la page 2 du Compte de Résultat (Produits et Charges exceptionnels)."""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and ("Produits exceptionnels" in text or "PRODUITS EXCEPTIONNELS" in text):
                print(f"   ✓ Page 2 identifiée : page {i + 1} du PDF")
                return i
        return -1

    def _trouver_colonne_page1(self, table):
        """Trouve l'index de la colonne avec les montants dans la PAGE 1.

        Logique intelligente : Compte les colonnes numériques et prend la 1ère.
        """
        # Détecter toutes les colonnes numériques
        colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)
        print(f"   🔍 [PAGE 1] Colonnes numériques détectées : {colonnes_num}")

        # Prendre la 1ère colonne numérique
        idx_montants = obtenir_colonne_numerique(table, position=1, start_row=1, max_rows=20)

        if idx_montants is not None:
            print(f"   ✓ [PAGE 1] Colonne des montants (1ère colonne numérique) : index {idx_montants}")
        else:
            print("   ⚠️ [PAGE 1] Impossible de trouver la 1ère colonne numérique")

        return idx_montants

    def _trouver_colonne_page2(self, table):
        """Trouve l'index de la colonne avec les montants dans la PAGE 2.

        Logique intelligente : Compte les colonnes numériques et prend la 1ère.
        """
        # Détecter toutes les colonnes numériques
        colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)
        print(f"   🔍 [PAGE 2] Colonnes numériques détectées : {colonnes_num}")

        # Prendre la 1ère colonne numérique
        idx_montants = obtenir_colonne_numerique(table, position=1, start_row=1, max_rows=20)

        if idx_montants is not None:
            print(f"   ✓ [PAGE 2] Colonne des montants (1ère colonne numérique) : index {idx_montants}")
        else:
            print("   ⚠️ [PAGE 2] Impossible de trouver la 1ère colonne numérique")

        return idx_montants
