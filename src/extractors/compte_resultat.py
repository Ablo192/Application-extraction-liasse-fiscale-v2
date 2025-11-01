"""
Extracteur pour le Compte de Résultat (Formulaire 2052).

Ce module gère l'extraction des données du compte de résultat depuis les PDFs
de liasses fiscales. Le compte de résultat s'étend sur 2 pages.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_COMPTE_RESULTAT, SEUIL_REUSSITE_CODES_COMPTE_RESULTAT
from src.config.mots_cles import MOTS_CLES_COMPTE_RESULTAT
from src.utils.pdf_utils import obtenir_colonne_numerique, detecter_colonnes_numeriques
from src.utils.text_processing import nettoyer_montant


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
                    codes_page1, _ = self._extraire_codes_du_tableau(table_page1, idx_montant_page1)
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
                    codes_page2, _ = self._extraire_codes_du_tableau(table_page2, idx_montant_page2)
                    codes_trouves.update(codes_page2)

        nb_trouves = len([v for v in codes_trouves.values() if v != 0.0])
        print(f"\n   ℹ️ Codes détectés : {len(codes_trouves)} | Valeurs non-nulles : {nb_trouves}")

        resultats = self._convertir_en_resultats(codes_trouves)
        return resultats, nb_trouves

    def extraire_par_libelles(self, pdf, table=None):
        """Extrait le Compte de Résultat en cherchant les LIBELLÉS (méthode de secours).

        Note: Cette méthode est complexe à implémenter sur 2 pages.
        Pour simplifier, on retourne les données extraites par codes même si partielles.

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Non utilisé

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par libellés non implémentée pour le Compte de Résultat")
        print("   → Utilisation des données partielles extraites par codes")

        # Retourner une liste vide avec tous les libellés
        return [(self.codes_dict[code], 0) for code in self.codes_dict.keys()]

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
