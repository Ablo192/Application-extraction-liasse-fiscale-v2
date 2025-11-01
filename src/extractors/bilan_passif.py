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

        codes_trouves, nb_trouves = self._extraire_codes_du_tableau(table, idx_passif_n)
        resultats = self._convertir_en_resultats(codes_trouves)

        return resultats, nb_trouves

    def extraire_par_libelles(self, pdf, table):
        """Extrait le Bilan Passif en cherchant les LIBELLÉS dans le tableau.

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        idx_passif_n = self._trouver_colonne_passif_n(table)
        if idx_passif_n is None:
            print("   ⚠️ Colonne 'Exercice N' introuvable.")
            return []

        libelles_normalises = {normaliser_texte(lib): lib for lib in LIBELLES_BILAN_PASSIF.keys()}
        libelles_trouves = {}

        for row in table:
            if not row:
                continue

            libelle_trouve = None
            for cell in row:
                if cell:
                    cell_normalise = normaliser_texte(str(cell).strip())
                    if cell_normalise in libelles_normalises:
                        libelle_trouve = libelles_normalises[cell_normalise]
                        break

            if libelle_trouve:
                montant_brut = nettoyer_montant(row[idx_passif_n]) if idx_passif_n < len(row) else None
                montant = montant_brut if montant_brut is not None else 0.0
                libelles_trouves[libelle_trouve] = montant

        resultats = [(libelle, libelles_trouves.get(libelle, 0)) for libelle in LIBELLES_BILAN_PASSIF.keys()]
        return resultats

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
