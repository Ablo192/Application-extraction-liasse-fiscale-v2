"""
Version améliorée du main.py utilisant l'approche analytique
=============================================================

Ce fichier adapte le code existant pour utiliser le nouveau module
d'extraction analytique en 3 phases.

Auteur: Claude
Version: 2.0 - Approche analytique
"""

import pdfplumber
import openpyxl
from pathlib import Path
from extraction_analytique import (
    ExtractionAnalytique,
    DetecteurTableaux,
    AnalyseurStructure,
    ExtracteurDonnees,
    TypeTableau
)

# Importer les dictionnaires de codes du main.py original
from main import (
    CODES_BILAN_ACTIF,
    CODES_BILAN_PASSIF,
    CODES_COMPTE_RESULTAT,
    CODES_ETAT_ECHEANCES_CREANCES,
    CODES_ETAT_ECHEANCES_DETTES,
    CODES_AFFECTATION_RESULTAT,
    CODES_RENSEIGNEMENTS_DIVERS,
    creer_fichier_excel  # Réutiliser la fonction de création Excel
)


def extraire_un_pdf_analytique(chemin_pdf):
    """
    Extrait les données d'un PDF en utilisant l'approche analytique.

    Args:
        chemin_pdf: Path vers le fichier PDF

    Returns:
        dict: Données extraites ou None en cas d'erreur
    """
    print(f"\n{'='*80}")
    print(f"📄 Traitement : {chemin_pdf.name}")
    print(f"{'='*80}\n")

    try:
        # ========================================
        # PHASE 1 : DÉTECTION DES TABLEAUX
        # ========================================
        print("📍 PHASE 1 : Détection des tableaux")
        print("-" * 80)

        tableaux = DetecteurTableaux.detecter_tous_tableaux(str(chemin_pdf))

        if not tableaux:
            print("❌ Aucun tableau détecté dans le PDF")
            return None

        print(f"\n✓ {len(tableaux)} tableau(x) détecté(s)")

        # Afficher un résumé des tableaux détectés
        for idx, tableau in enumerate(tableaux):
            print(f"  {idx+1}. {tableau.type_tableau.value} (page {tableau.page_index + 1})")

        print()

        # ========================================
        # PHASE 2 : ANALYSE DES STRUCTURES
        # ========================================
        print("📍 PHASE 2 : Analyse de la structure des colonnes")
        print("-" * 80)

        for tableau in tableaux:
            print(f"\n→ Analyse du tableau '{tableau.type_tableau.value}'...")

            # Analyser les en-têtes et colonnes
            colonnes = AnalyseurStructure.analyser_en_tetes(tableau.table_data)
            tableau.colonnes = colonnes

            print(f"  Colonnes identifiées :")
            for col in colonnes:
                print(f"    - Index {col.index}: {col.type_colonne} ('{col.en_tete}') [confiance: {col.confiance:.0%}]")

        print("\n✓ Analyse terminée\n")

        # ========================================
        # PHASE 3 : EXTRACTION DES DONNÉES
        # ========================================
        print("📍 PHASE 3 : Extraction des données avec règles métier")
        print("-" * 80)

        resultats = {}

        # --- EXTRACTION DU BILAN ACTIF ---
        tableau_actif = next((t for t in tableaux if t.type_tableau == TypeTableau.ACTIF), None)
        if tableau_actif:
            print("\n→ Extraction du BILAN ACTIF...")
            donnees_actif_dict = ExtracteurDonnees.extraire_donnees_tableau(
                tableau_actif,
                CODES_BILAN_ACTIF
            )
            # Convertir en format liste de tuples (libellé, montant) pour compatibilité
            resultats['actif'] = [(lib, donnees_actif_dict.get(lib, 0)) for lib in CODES_BILAN_ACTIF.values()]
        else:
            print("\n⚠️ Tableau ACTIF non trouvé")
            resultats['actif'] = [(lib, 0) for lib in CODES_BILAN_ACTIF.values()]

        # --- EXTRACTION DU BILAN PASSIF ---
        tableau_passif = next((t for t in tableaux if t.type_tableau == TypeTableau.PASSIF), None)
        if tableau_passif:
            print("\n→ Extraction du BILAN PASSIF...")
            donnees_passif_dict = ExtracteurDonnees.extraire_donnees_tableau(
                tableau_passif,
                CODES_BILAN_PASSIF
            )
            resultats['passif'] = [(lib, donnees_passif_dict.get(lib, 0)) for lib in CODES_BILAN_PASSIF.values()]
        else:
            print("\n⚠️ Tableau PASSIF non trouvé")
            resultats['passif'] = [(lib, 0) for lib in CODES_BILAN_PASSIF.values()]

        # --- EXTRACTION DU COMPTE DE RÉSULTAT ---
        tableaux_cr = [
            t for t in tableaux
            if t.type_tableau in [TypeTableau.COMPTE_RESULTAT_1, TypeTableau.COMPTE_RESULTAT_2]
        ]
        if tableaux_cr:
            print("\n→ Extraction du COMPTE DE RÉSULTAT (pages 1 et 2)...")
            donnees_cr_dict = {}
            for tab_cr in tableaux_cr:
                print(f"  Traitement de {tab_cr.type_tableau.value}...")
                donnees_page = ExtracteurDonnees.extraire_donnees_tableau(
                    tab_cr,
                    CODES_COMPTE_RESULTAT
                )
                donnees_cr_dict.update(donnees_page)
            resultats['cr'] = [(lib, donnees_cr_dict.get(lib, 0)) for lib in CODES_COMPTE_RESULTAT.values()]
        else:
            print("\n⚠️ Tableaux COMPTE DE RÉSULTAT non trouvés")
            resultats['cr'] = [(lib, 0) for lib in CODES_COMPTE_RESULTAT.values()]

        # --- EXTRACTION ÉTAT DES ÉCHÉANCES ---
        tableau_echeances = next((t for t in tableaux if t.type_tableau == TypeTableau.ETAT_ECHEANCES), None)
        if tableau_echeances:
            print("\n→ Extraction de l'ÉTAT DES ÉCHÉANCES...")

            # Combiner tous les codes d'échéances
            codes_echeances = {**CODES_ETAT_ECHEANCES_CREANCES, **CODES_ETAT_ECHEANCES_DETTES}

            donnees_echeances_dict = ExtracteurDonnees.extraire_donnees_tableau(
                tableau_echeances,
                codes_echeances
            )
            resultats['echeances'] = [(lib, donnees_echeances_dict.get(lib, 0)) for lib in codes_echeances.values()]
        else:
            print("\n⚠️ Tableau ÉTAT DES ÉCHÉANCES non trouvé")
            codes_echeances = {**CODES_ETAT_ECHEANCES_CREANCES, **CODES_ETAT_ECHEANCES_DETTES}
            resultats['echeances'] = [(lib, 0) for lib in codes_echeances.values()]

        # --- EXTRACTION AFFECTATION DU RÉSULTAT ---
        tableau_affectation = next((t for t in tableaux if t.type_tableau == TypeTableau.AFFECTATION_RESULTAT), None)
        if tableau_affectation:
            print("\n→ Extraction de l'AFFECTATION DU RÉSULTAT ET RENSEIGNEMENTS DIVERS...")

            # Combiner affectation + renseignements divers
            codes_affectation = {**CODES_AFFECTATION_RESULTAT, **CODES_RENSEIGNEMENTS_DIVERS}

            donnees_affectation_dict = ExtracteurDonnees.extraire_donnees_tableau(
                tableau_affectation,
                codes_affectation
            )
            resultats['affectation'] = [(lib, donnees_affectation_dict.get(lib, 0)) for lib in codes_affectation.values()]
        else:
            print("\n⚠️ Tableau AFFECTATION DU RÉSULTAT non trouvé")
            codes_affectation = {**CODES_AFFECTATION_RESULTAT, **CODES_RENSEIGNEMENTS_DIVERS}
            resultats['affectation'] = [(lib, 0) for lib in codes_affectation.values()]

        print("\n" + "="*80)
        print("✓ EXTRACTION ANALYTIQUE TERMINÉE")
        print("="*80 + "\n")

        return resultats

    except Exception as e:
        print(f"❌ Erreur lors du traitement analytique : {e}")
        import traceback
        traceback.print_exc()
        return None


def main_analytique():
    """
    Version CLI améliorée utilisant l'extraction analytique.
    """
    print("\n" + "="*80)
    print("🚀 EXTRACTION LIASSE FISCALE - MODE ANALYTIQUE v2.0")
    print("="*80)

    dossier_liasses = Path("liasses")
    dossier_resultats = Path("resultats")
    dossier_resultats.mkdir(exist_ok=True)

    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("\n❌ Aucun PDF dans 'liasses/'\n")
        return

    print(f"\n📁 {len(fichiers_pdf)} fichier(s) PDF trouvé(s)")
    print("ℹ️  Mode analytique : Détection intelligente + Analyse adaptative + Règles métier")
    print()

    donnees_par_annee = {}

    # Traiter chaque PDF
    for idx, chemin_pdf in enumerate(fichiers_pdf):
        annee = str(2023 + idx)  # Attribution automatique: 2023, 2024, 2025, etc.

        print(f"\n{'='*80}")
        print(f"📄 Fichier {idx + 1}/{len(fichiers_pdf)} : {chemin_pdf.name} → Année {annee}")
        print(f"{'='*80}")

        # Extraire avec l'approche analytique
        resultats = extraire_un_pdf_analytique(chemin_pdf)

        if resultats:
            donnees_par_annee[annee] = resultats
            print(f"✅ Extraction réussie pour l'année {annee}")
        else:
            print(f"❌ Échec de l'extraction pour {chemin_pdf.name}")

    # Générer le fichier Excel si on a des données
    if donnees_par_annee:
        print("\n" + "="*80)
        print("📊 Génération du fichier Excel...")
        print("="*80)

        nom_excel = dossier_resultats / "extraction_analytique_multi_annees.xlsx"
        creer_fichier_excel(donnees_par_annee, nom_excel)

        print(f"\n✅ Fichier Excel créé : {nom_excel}")
        print(f"📈 Années traitées : {', '.join(sorted(donnees_par_annee.keys()))}")
    else:
        print("\n❌ Aucune donnée extraite.")

    print("\n" + "="*80)
    print("✓ TRAITEMENT TERMINÉ")
    print("="*80 + "\n")


if __name__ == "__main__":
    main_analytique()
