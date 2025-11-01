"""
Extracteur pour le Bilan Actif (Formulaire 2050).

Ce module gère l'extraction des données du bilan actif depuis les PDFs
de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_BILAN_ACTIF, SEUIL_REUSSITE_CODES_ACTIF
from src.config.mots_cles import MOTS_CLES_BILAN_ACTIF, LIBELLES_BILAN_ACTIF
from src.utils.pdf_utils import obtenir_colonne_numerique, detecter_colonnes_numeriques
from src.utils.text_processing import nettoyer_montant, normaliser_texte
from src.utils.extraction_fallback import (
    detecter_extraction_fusionnee,
    extraire_codes_depuis_texte_fusionne,
    extraire_montants_depuis_texte_fusionne
)
from src.utils.extraction_ligne_par_ligne import extraire_actif_ligne_par_ligne


class BilanActifExtractor(BaseExtractor):
    """Extracteur pour le Bilan Actif."""

    def __init__(self):
        super().__init__(
            codes_dict=CODES_BILAN_ACTIF,
            mots_cles_dict=MOTS_CLES_BILAN_ACTIF,
            seuil_reussite=SEUIL_REUSSITE_CODES_ACTIF
        )

    def extraire_par_codes(self, pdf, table):
        """Extrait le Bilan Actif en cherchant les CODES dans le tableau.

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
        idx_net = self._trouver_colonne_net(table)

        # Si pas de 3ème colonne, essayer la 1ère comme fallback
        if idx_net is None and detecter_extraction_fusionnee(table):
            print("   ℹ️ Pas de 3ème colonne numérique. Extraction fusionnée détectée.")
            print("   🔄 Utilisation de la 1ère colonne numérique comme fallback...")
            idx_net = obtenir_colonne_numerique(table, position=1, start_row=1, max_rows=20)

        if idx_net is None:
            print("   ⚠️ Colonne 'Net' introuvable.")
            return [], 0

        # Tentative 1: Extraction standard
        codes_trouves, nb_trouves = self._extraire_codes_du_tableau(table, idx_net)

        # Si échec et extraction fusionnée, utiliser fallback
        if nb_trouves == 0 and detecter_extraction_fusionnee(table):
            print("   🔄 Extraction fusionnée détectée. Utilisation du parser de fallback...")
            codes_info = extraire_codes_depuis_texte_fusionne(table, self.codes_dict)

            if codes_info:
                print(f"   ✅ {len(codes_info)} codes trouvés dans le texte fusionné")

                # Extraire les montants correspondants
                montants_texte = extraire_montants_depuis_texte_fusionne(codes_info, idx_net)

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
        """Extrait le Bilan Actif en cherchant les LIBELLÉS ligne par ligne.

        Nouvelle approche robuste:
        - Analyse chaque ligne individuellement
        - Détecte les colonnes numériques DE CETTE LIGNE
        - Prend la 3ème colonne numérique de la ligne
        - Plus robuste face aux décalages de colonnes

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par LIBELLÉS (méthode ligne par ligne)")

        # Utiliser la nouvelle logique ligne par ligne
        return extraire_actif_ligne_par_ligne(table, LIBELLES_BILAN_ACTIF, debug=True)

    def _trouver_colonne_net(self, table):
        """Trouve l'index de la colonne 'Net' dans le tableau de l'actif.

        Logique intelligente : Compte les colonnes numériques et prend la 3ème.
        Typiquement : Brut (1ère), Amortissement (2ème), Net (3ème)

        Args:
            table: Tableau extrait du PDF

        Returns:
            int: Index de la colonne 'Net' ou None si non trouvée
        """
        # Détecter toutes les colonnes numériques (en commençant après l'en-tête)
        colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)

        print(f"   🔍 Colonnes numériques détectées pour Bilan Actif : {colonnes_num}")

        # Prendre la 3ème colonne numérique
        idx_net = obtenir_colonne_numerique(table, position=3, start_row=1, max_rows=20)

        if idx_net is not None:
            print(f"   ✓ Colonne 'Net' (3ème colonne numérique) : index {idx_net}")
        else:
            print(f"   ⚠️ Impossible de trouver la 3ème colonne numérique")

        return idx_net
