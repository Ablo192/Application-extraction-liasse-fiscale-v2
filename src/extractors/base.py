"""
Classe de base pour tous les extracteurs de données fiscales.

Ce module fournit une classe abstraite définissant l'interface commune
pour tous les extracteurs spécialisés (actif, passif, compte de résultat, etc.).
"""

from abc import ABC, abstractmethod
from src.utils.text_processing import nettoyer_montant, normaliser_texte


class BaseExtractor(ABC):
    """Classe de base abstraite pour les extracteurs de données fiscales.

    Tous les extracteurs doivent hériter de cette classe et implémenter
    les méthodes abstraites.
    """

    def __init__(self, codes_dict, mots_cles_dict=None, seuil_reussite=5):
        """Initialise l'extracteur.

        Args:
            codes_dict: Dictionnaire des codes officiels (ex: CODES_BILAN_ACTIF)
            mots_cles_dict: Dictionnaire des mots-clés (optionnel, pour fallback)
            seuil_reussite: Nombre minimum de codes trouvés pour valider l'extraction
        """
        self.codes_dict = codes_dict
        self.mots_cles_dict = mots_cles_dict
        self.seuil_reussite = seuil_reussite

    @abstractmethod
    def extraire_par_codes(self, pdf, table):
        """Extrait les données en utilisant les codes officiels.

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Tableau extrait du PDF

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        pass

    @abstractmethod
    def extraire_par_libelles(self, pdf, table):
        """Extrait les données en utilisant les libellés (méthode de secours).

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        pass

    def extraire(self, pdf, table):
        """Extrait les données en utilisant la meilleure méthode disponible.

        Stratégie :
        1. Essaie d'abord l'extraction par codes
        2. Si échec (moins de seuil_reussite valeurs), bascule sur libellés

        Args:
            pdf: Objet PDF ouvert avec pdfplumber
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print(f"   → Tentative d'extraction par CODES...")

        donnees_codes, nb_trouves = self.extraire_par_codes(pdf, table)

        if nb_trouves >= self.seuil_reussite:
            print(f"✅ Succès de l'extraction par codes ({nb_trouves} valeurs).")
            return donnees_codes
        else:
            print(f"⚠️ Échec par codes ({nb_trouves} valeurs < {self.seuil_reussite}). Basculement sur libellés.")
            return self.extraire_par_libelles(pdf, table)

    def _extraire_codes_du_tableau(self, table, index_montant):
        """Méthode helper pour extraire les codes d'un tableau.

        Args:
            table: Tableau extrait du PDF
            index_montant: Index de la colonne contenant les montants

        Returns:
            tuple: (dict des codes trouvés, nombre de valeurs non-nulles)
        """
        codes_trouves = {}

        for row in table:
            if not row:
                continue

            for idx, cell in enumerate(row):
                if cell:
                    cell_text = str(cell).strip().upper()
                    if cell_text in self.codes_dict:
                        montant_brut = nettoyer_montant(row[index_montant]) if index_montant < len(row) else None
                        montant = montant_brut if montant_brut is not None else 0.0
                        codes_trouves[cell_text] = montant

        nb_trouves = len([v for v in codes_trouves.values() if v != 0.0])
        print(f"   ℹ️ Codes détectés : {len(codes_trouves)} | Valeurs non-nulles : {nb_trouves}")

        return codes_trouves, nb_trouves

    def _convertir_en_resultats(self, codes_trouves):
        """Convertit un dictionnaire de codes en liste de résultats.

        Args:
            codes_trouves: Dict {code: montant}

        Returns:
            list: Liste de tuples (libellé, montant) dans l'ordre des codes
        """
        return [(self.codes_dict[code], codes_trouves.get(code, 0)) for code in self.codes_dict.keys()]
