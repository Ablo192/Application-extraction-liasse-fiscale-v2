"""
Extracteur pour le Compte de Résultat (Formulaire 2052).

Ce module gère l'extraction des données du compte de résultat depuis les PDFs
de liasses fiscales. Le compte de résultat s'étend sur 2 pages.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_COMPTE_RESULTAT, SEUIL_REUSSITE_CODES_COMPTE_RESULTAT
from src.config.mots_cles import MOTS_CLES_COMPTE_RESULTAT
from src.utils.pdf_utils import trouver_colonne_montant
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

        Logique GPS pour PAGE 1 :
        1. Cherche "TOTAL" dans l'en-tête
        2. Les montants sont à index TOTAL + 1
        """
        # Chercher "TOTAL" dans les premières lignes
        idx_total = None
        for row in table[:5]:
            for idx, cell in enumerate(row):
                if cell and "TOTAL" in str(cell).strip().upper():
                    idx_total = idx
                    print(f"   ℹ️ [PAGE 1] 'TOTAL' trouvé à l'index {idx}")
                    break
            if idx_total is not None:
                break

        # Déduire l'index des montants
        if idx_total is not None:
            idx_montants = idx_total + 1
            print(f"   ✓ [PAGE 1] Colonne des montants déduite : index {idx_montants}")
            return idx_montants
        else:
            print("   ⚠️ [PAGE 1] Impossible de trouver 'TOTAL'")
            return None

    def _trouver_colonne_page2(self, table):
        """Trouve l'index de la colonne avec les montants dans la PAGE 2.

        Logique GPS pour PAGE 2 :
        1. Cherche "Exercice N"
        2. Les montants sont à index Exercice N + 1
        """
        idx_exercice_n = trouver_colonne_montant(table, "Exercice N", offset=1, max_rows=10)

        if idx_exercice_n:
            print(f"   ✓ [PAGE 2] Colonne des montants déduite : index {idx_exercice_n}")
            return idx_exercice_n
        else:
            print("   ⚠️ [PAGE 2] Impossible de trouver 'Exercice N'")
            return None
