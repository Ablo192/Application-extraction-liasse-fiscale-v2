"""
Extracteur pour le Bilan Passif (Formulaire 2051).

Ce module gère l'extraction des données du bilan passif depuis les PDFs
de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_BILAN_PASSIF, SEUIL_REUSSITE_CODES_PASSIF
from src.config.mots_cles import MOTS_CLES_BILAN_PASSIF, LIBELLES_BILAN_PASSIF
from src.utils.pdf_utils import trouver_colonne_montant
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

        Les montants sont décalés de +1 par rapport à l'en-tête 'Exercice N'.

        Args:
            table: Tableau extrait du PDF

        Returns:
            int: Index de la colonne des montants ou None si non trouvée
        """
        print("🔍 Recherche de la colonne 'Exercice N' pour le Passif...")
        idx_montant = trouver_colonne_montant(table, "Exercice N", offset=1, max_rows=10)

        if idx_montant:
            print(f"   ✓ Colonne des montants trouvée à l'index : {idx_montant}\n")
        else:
            print("❌ En-tête 'Exercice N' non trouvé.")

        return idx_montant
