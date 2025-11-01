"""
Extracteur pour l'Affectation du Résultat et Renseignements Divers (Formulaire 2058-C-SD).

Ce module gère l'extraction des données d'affectation du résultat et des renseignements
divers depuis les PDFs de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import (
    CODES_AFFECTATION_RESULTAT,
    CODES_RENSEIGNEMENTS_DIVERS,
    SEUIL_REUSSITE_CODES_AFFECTATION_RESULTAT
)
from src.config.mots_cles import MOTS_CLES_AFFECTATION
from src.utils.pdf_utils import obtenir_colonne_numerique, detecter_colonnes_numeriques
from src.utils.text_processing import nettoyer_montant


class AffectationExtractor(BaseExtractor):
    """Extracteur pour l'Affectation du Résultat et Renseignements Divers."""

    def __init__(self):
        # Combiner les dictionnaires affectation + renseignements
        codes_combines = {**CODES_AFFECTATION_RESULTAT, **CODES_RENSEIGNEMENTS_DIVERS}

        super().__init__(
            codes_dict=codes_combines,
            mots_cles_dict=MOTS_CLES_AFFECTATION,
            seuil_reussite=SEUIL_REUSSITE_CODES_AFFECTATION_RESULTAT
        )

    def extraire_par_codes(self, pdf, table):
        """Extrait l'Affectation du résultat et Renseignements divers par codes.

        Logique intelligente : Utilise la 1ère colonne numérique pour tous les montants.

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        print("📊 Extraction par CODES de l'Affectation du résultat et Renseignements divers...")

        # Détecter la 1ère colonne numérique
        colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)
        print(f"   🔍 Colonnes numériques détectées pour Affectation : {colonnes_num}")

        idx_montant = obtenir_colonne_numerique(table, position=1, start_row=1, max_rows=20)

        if idx_montant is None:
            print("   ⚠️ Impossible de trouver la 1ère colonne numérique")
            return [], 0

        print(f"   ✓ Colonne des montants (1ère colonne numérique) : index {idx_montant}")

        donnees = []
        nb_trouves = 0

        # Parcourir toutes les lignes pour trouver les codes
        for row_idx, row in enumerate(table):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                code = str(cell).strip().upper()

                # AFFECTATION DU RÉSULTAT - Code ZE (Dividendes)
                if code == "ZE" and code in CODES_AFFECTATION_RESULTAT:
                    libelle = CODES_AFFECTATION_RESULTAT[code]
                    montant_cell = row[idx_montant] if idx_montant < len(row) else None
                    montant = nettoyer_montant(montant_cell)

                    if montant is not None:
                        donnees.append((libelle, montant))
                        nb_trouves += 1
                        print(f"   ✓ {code} ({libelle}) → {montant} [index {idx_montant}]")
                    else:
                        donnees.append((libelle, 0))
                        print(f"   ⚠️  {code} ({libelle}) → montant non trouvé [index {idx_montant}]")

                # RENSEIGNEMENTS DIVERS - Codes YQ, YR, YT, YU
                elif code in CODES_RENSEIGNEMENTS_DIVERS:
                    libelle = CODES_RENSEIGNEMENTS_DIVERS[code]
                    montant_cell = row[idx_montant] if idx_montant < len(row) else None
                    montant = nettoyer_montant(montant_cell)

                    if montant is not None:
                        donnees.append((libelle, montant))
                        nb_trouves += 1
                        print(f"   ✓ {code} ({libelle}) → {montant} [index {idx_montant}]")
                    else:
                        donnees.append((libelle, 0))
                        print(f"   ⚠️  {code} ({libelle}) → montant non trouvé [index {idx_montant}]")

        total_codes = len(CODES_AFFECTATION_RESULTAT) + len(CODES_RENSEIGNEMENTS_DIVERS)
        print(f"   📊 Total : {nb_trouves} valeur(s) trouvée(s) sur {total_codes}")

        return donnees, nb_trouves

    def extraire_par_libelles(self, pdf, table):
        """Extrait l'Affectation en cherchant les LIBELLÉS (méthode de secours).

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par libellés non implémentée pour l'Affectation")
        return [(self.codes_dict[code], 0) for code in self.codes_dict.keys()]
