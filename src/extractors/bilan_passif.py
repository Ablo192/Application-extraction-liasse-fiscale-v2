"""
Extracteur pour le Bilan Passif (Formulaire 2051).

Ce module gère l'extraction des données du bilan passif depuis les PDFs
de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_BILAN_PASSIF, SEUIL_REUSSITE_CODES_PASSIF
from src.config.mots_cles import MOTS_CLES_BILAN_PASSIF, LIBELLES_BILAN_PASSIF
from src.utils.pdf_utils import obtenir_colonne_numerique, detecter_colonnes_numeriques
from src.utils.text_processing import nettoyer_montant, normaliser_texte
from src.utils.extraction_fallback import (
    detecter_extraction_fusionnee,
    extraire_codes_depuis_texte_fusionne,
    extraire_montants_depuis_texte_fusionne
)
from src.utils.extraction_ligne_par_ligne import extraire_passif_ligne_par_ligne


class BilanPassifExtractor(BaseExtractor):
    """Extracteur pour le Bilan Passif."""

    def __init__(self):
        super().__init__(
            codes_dict=CODES_BILAN_PASSIF,
            mots_cles_dict=MOTS_CLES_BILAN_PASSIF,
            seuil_reussite=SEUIL_REUSSITE_CODES_PASSIF
        )

    def extraire_par_codes(self, pdf, table):
        """Extrait le Bilan Passif en cherchant les CODES dans le tableau.

        Utilise une stratégie de fallback si l'extraction standard échoue:
        1. Essaie l'extraction standard
        2. Si échec, détecte si cellules fusionnées
        3. Si fusionnées, parse le texte fusionné

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        idx_passif_n = self._trouver_colonne_passif_n(table)
        if idx_passif_n is None:
            print("   ⚠️ Colonne 'Exercice N' introuvable.")
            return [], 0

        # Tentative 1: Extraction standard
        codes_trouves, nb_trouves = self._extraire_codes_du_tableau(table, idx_passif_n)

        # Si échec et extraction fusionnée, utiliser fallback
        if nb_trouves == 0 and detecter_extraction_fusionnee(table):
            print("   🔄 Extraction fusionnée détectée. Utilisation du parser de fallback...")
            codes_info = extraire_codes_depuis_texte_fusionne(table, self.codes_dict)

            if codes_info:
                print(f"   ✅ {len(codes_info)} codes trouvés dans le texte fusionné")

                # Extraire les montants correspondants
                montants_texte = extraire_montants_depuis_texte_fusionne(codes_info, idx_passif_n)

                # Convertir en format attendu
                codes_trouves = {}
                for code, montant_texte in montants_texte.items():
                    montant = nettoyer_montant(montant_texte)
                    codes_trouves[code] = montant if montant is not None else 0.0

                nb_trouves = len([v for v in codes_trouves.values() if v != 0.0])
                print(f"   ℹ️ Codes avec montants non-nuls: {nb_trouves}/{len(codes_trouves)}")

        resultats = self._convertir_en_resultats(codes_trouves)

        return resultats, nb_trouves

    def extraire_par_libelles(self, pdf, table):
        """Extrait le Bilan Passif en cherchant les LIBELLÉS ligne par ligne.

        Nouvelle approche robuste:
        - Analyse chaque ligne individuellement
        - Détecte les colonnes numériques DE CETTE LIGNE
        - Prend la 1ère colonne numérique de la ligne
        - Plus robuste face aux décalages de colonnes

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par LIBELLÉS (méthode ligne par ligne)")

        # Utiliser la nouvelle logique ligne par ligne
        return extraire_passif_ligne_par_ligne(table, LIBELLES_BILAN_PASSIF, debug=True)

    def _trouver_colonne_passif_n(self, table):
        """Trouve l'index de la colonne 'Exercice N' dans le tableau du passif.

        Logique intelligente : Compte les colonnes numériques et prend la 1ère.

        Args:
            table: Tableau extrait du PDF

        Returns:
            int: Index de la colonne des montants ou None si non trouvée
        """
        # Détecter toutes les colonnes numériques (en commençant après l'en-tête)
        colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)

        print(f"   🔍 Colonnes numériques détectées pour Bilan Passif : {colonnes_num}")

        # Prendre la 1ère colonne numérique
        idx_montant = obtenir_colonne_numerique(table, position=1, start_row=1, max_rows=20)

        if idx_montant is not None:
            print(f"   ✓ Colonne 'Exercice N' (1ère colonne numérique) : index {idx_montant}")
        else:
            print(f"   ⚠️ Impossible de trouver la 1ère colonne numérique")

        return idx_montant
