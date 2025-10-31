"""
Extracteur pour l'État des Échéances (Formulaire 2057-SD).

Ce module gère l'extraction des données de l'état des échéances (créances et dettes)
depuis les PDFs de liasses fiscales.
"""

from src.extractors.base import BaseExtractor
from src.config.codes_fiscaux import (
    CODES_ETAT_ECHEANCES_CREANCES,
    CODES_ETAT_ECHEANCES_DETTES,
    SEUIL_REUSSITE_CODES_ETAT_ECHEANCES
)
from src.config.mots_cles import MOTS_CLES_ETAT_ECHEANCES
from src.utils.pdf_utils import detecter_section_dettes
from src.utils.text_processing import nettoyer_montant


class EtatEcheancesExtractor(BaseExtractor):
    """Extracteur pour l'État des Échéances."""

    def __init__(self):
        # Combiner les dictionnaires créances + dettes
        codes_combines = {**CODES_ETAT_ECHEANCES_CREANCES, **CODES_ETAT_ECHEANCES_DETTES}

        super().__init__(
            codes_dict=codes_combines,
            mots_cles_dict=MOTS_CLES_ETAT_ECHEANCES,
            seuil_reussite=SEUIL_REUSSITE_CODES_ETAT_ECHEANCES
        )

    def extraire_par_codes(self, pdf, table):
        """Extrait l'État des échéances en utilisant les codes officiels.

        Structure:
        - CRÉANCES: codes VA, VC à l'index 13
        - DETTES: code VH à l'index 14, code VI à l'index 10

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            tuple: (liste de tuples (libellé, montant), nombre de valeurs trouvées)
        """
        print("📊 Extraction par CODES de l'État des échéances...")

        donnees = []
        nb_trouves = 0

        # Indicateur pour savoir si on est dans la section DETTES
        dans_section_dettes = False

        # Dictionnaires pour éviter les doublons
        codes_trouves_creances = set()
        codes_trouves_dettes = set()

        # Parcourir toutes les lignes pour trouver les codes
        for row_idx, row in enumerate(table):
            # Détecter le changement de section
            if detecter_section_dettes(row):
                dans_section_dettes = True
                print(f"   ℹ️  Section DETTES détectée à la ligne {row_idx + 1}")

            # Chercher les codes dans la ligne
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                code = str(cell).strip().upper()

                # SECTION CRÉANCES
                if not dans_section_dettes and code in CODES_ETAT_ECHEANCES_CREANCES:
                    if code in codes_trouves_creances:
                        continue
                    codes_trouves_creances.add(code)

                    libelle = CODES_ETAT_ECHEANCES_CREANCES[code]
                    montant_cell = row[13] if len(row) > 13 else None
                    montant = nettoyer_montant(montant_cell)

                    if montant is not None:
                        donnees.append((libelle, montant))
                        nb_trouves += 1
                        print(f"   ✓ CRÉANCES - {code} ({libelle}) → {montant} [index 13]")
                    else:
                        donnees.append((libelle, 0))
                        print(f"   ⚠️  CRÉANCES - {code} ({libelle}) → montant non trouvé [index 13]")

                # SECTION DETTES
                elif dans_section_dettes and code in CODES_ETAT_ECHEANCES_DETTES:
                    if code in codes_trouves_dettes:
                        continue
                    codes_trouves_dettes.add(code)

                    libelle = CODES_ETAT_ECHEANCES_DETTES[code]

                    # Code VH (Annuité à venir) → index 14
                    if code == "VH":
                        montant_cell = row[14] if len(row) > 14 else None
                        montant = nettoyer_montant(montant_cell)

                        if montant is not None:
                            donnees.append((libelle, montant))
                            nb_trouves += 1
                            print(f"   ✓ DETTES - {code} ({libelle}) → {montant} [index 14]")
                        else:
                            donnees.append((libelle, 0))
                            print(f"   ⚠️  DETTES - {code} ({libelle}) → montant non trouvé [index 14]")

                    # Code VI (Groupe et associés dettes) → index 10
                    elif code == "VI":
                        montant_cell = row[10] if len(row) > 10 else None
                        montant = nettoyer_montant(montant_cell)

                        if montant is not None:
                            donnees.append((libelle, montant))
                            nb_trouves += 1
                            print(f"   ✓ DETTES - {code} ({libelle}) → {montant} [index 10]")
                        else:
                            donnees.append((libelle, 0))
                            print(f"   ⚠️  DETTES - {code} ({libelle}) → montant non trouvé [index 10]")

        print(f"\n   📊 Total : {nb_trouves} valeur(s) trouvée(s)")
        return donnees, nb_trouves

    def extraire_par_libelles(self, pdf, table):
        """Extrait l'État des échéances en cherchant les LIBELLÉS (méthode de secours).

        Args:
            pdf: Objet PDF (non utilisé ici)
            table: Tableau extrait du PDF

        Returns:
            list: Liste de tuples (libellé, montant)
        """
        print("   → Extraction par libellés non implémentée pour l'État des Échéances")
        return [(self.codes_dict[code], 0) for code in self.codes_dict.keys()]
