"""
Extracteur pour le Bilan Actif (Formulaire 2050).

Ce module gère l'extraction des données du bilan actif depuis les PDFs
de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import CODES_BILAN_ACTIF, SEUIL_REUSSITE_CODES_ACTIF
from src.config.mots_cles import MOTS_CLES_BILAN_ACTIF, LIBELLES_BILAN_ACTIF
from src.utils.pdf_utils import trouver_colonne_montant
from src.utils.text_processing import nettoyer_montant, normaliser_texte


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

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        idx_net = self._trouver_colonne_net(table)
        if idx_net is None:
            print("   ⚠️ Colonne 'Net' introuvable.")
            return [], 0

        codes_trouves, nb_trouves = self._extraire_codes_du_tableau(table, idx_net)
        resultats = self._convertir_en_resultats(codes_trouves)

        return resultats, nb_trouves

    def extraire_par_libelles(self, pdf, table):
        """Extrait le Bilan Actif en cherchant les LIBELLÉS dans le tableau.

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        idx_net = self._trouver_colonne_net(table)
        if idx_net is None:
            print("   ⚠️ Colonne 'Net' introuvable.")
            return []

        libelles_normalises = {normaliser_texte(lib): lib for lib in LIBELLES_BILAN_ACTIF.keys()}
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
                montant_brut = nettoyer_montant(row[idx_net]) if idx_net < len(row) else None
                montant = montant_brut if montant_brut is not None else 0.0
                libelles_trouves[libelle_trouve] = montant

        resultats = [(libelle, libelles_trouves.get(libelle, 0)) for libelle in LIBELLES_BILAN_ACTIF.keys()]
        return resultats

    def _trouver_colonne_net(self, table):
        """Trouve l'index de la colonne 'Net' dans le tableau de l'actif.

        Args:
            table: Tableau extrait du PDF

        Returns:
            int: Index de la colonne 'Net' ou None si non trouvée
        """
        return trouver_colonne_montant(table, "Net", offset=0, max_rows=5)
