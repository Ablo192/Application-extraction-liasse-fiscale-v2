#!/usr/bin/env python3
"""
Application d'extraction de liasses fiscales françaises depuis des PDFs.

Ce script extrait les données comptables des formulaires fiscaux français
(2050, 2051, 2052, 2057, 2058) et génère un fichier Excel consolidé avec analyse financière.

Usage:
    python main_refactored.py

Le script traite tous les PDFs du dossier 'liasses/' et génère un fichier Excel
dans le dossier 'resultats/'.
"""

import pdfplumber
from pathlib import Path

# Importation des modules refactorisés
from src.extractors.bilan_actif import BilanActifExtractor
from src.extractors.bilan_passif import BilanPassifExtractor
from src.extractors.compte_resultat import CompteResultatExtractor
from src.extractors.etat_echeances import EtatEcheancesExtractor
from src.extractors.affectation import AffectationExtractor
from src.export.excel_generator import creer_fichier_excel
from src.utils.pdf_utils import extraire_annee_fiscale, trouver_page_contenant


def extraire_un_pdf(chemin_pdf):
    """Extrait les données d'un seul PDF.

    Args:
        chemin_pdf: Path du fichier PDF à traiter

    Returns:
        dict: {'actif': [...], 'passif': [...], 'cr': [...], 'echeances': [...], 'affectation': [...]}
              ou None en cas d'erreur
    """
    print(f"\n{'='*80}")
    print(f"📄 Traitement : {chemin_pdf.name}")
    print(f"{'='*80}\n")

    try:
        with pdfplumber.open(chemin_pdf) as pdf:

            # Extraire l'année fiscale
            annee = extraire_annee_fiscale(pdf)
            if annee:
                print(f"📅 Année fiscale détectée : {annee}\n")

            # ============================================================
            # TRAITEMENT SÉQUENTIEL: BILAN ACTIF
            # ============================================================
            print("\n" + "="*80)
            print("📋 BILAN ACTIF (Formulaire 2050)")
            print("="*80)

            print("🔍 Recherche de la page du Bilan Actif...")
            actif_page_index = trouver_page_contenant(pdf, ["Brut", "Net", "ACTIF"])

            if actif_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_actif = []
            else:
                print(f"   ✓ Page identifiée : {actif_page_index + 1}")

                print("📊 Extraction du tableau...")
                tables_actif = pdf.pages[actif_page_index].extract_tables()
                if not tables_actif:
                    print("❌ Aucun tableau trouvé.")
                    donnees_actif = []
                else:
                    table_actif = tables_actif[0]
                    print("   ✓ Tableau extrait")

                    print("🚀 Traitement des données...")
                    actif_extractor = BilanActifExtractor()
                    donnees_actif = actif_extractor.extraire(pdf, table_actif)
                    print(f"✅ Actif terminé: {len(donnees_actif)} lignes extraites")

            # ============================================================
            # TRAITEMENT SÉQUENTIEL: BILAN PASSIF
            # ============================================================
            print("\n" + "="*80)
            print("📋 BILAN PASSIF (Formulaire 2051)")
            print("="*80)

            print("🔍 Recherche de la page du Bilan Passif...")
            passif_page_index = trouver_page_contenant(pdf, ["Capital social ou individuel", "PASSIF"])

            if passif_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_passif = []
            else:
                print(f"   ✓ Page identifiée : {passif_page_index + 1}")

                print("📊 Extraction du tableau...")
                tables_passif = pdf.pages[passif_page_index].extract_tables()
                if not tables_passif:
                    print("❌ Aucun tableau trouvé.")
                    donnees_passif = []
                else:
                    table_passif = tables_passif[0]
                    print("   ✓ Tableau extrait")

                    print("🚀 Traitement des données...")
                    passif_extractor = BilanPassifExtractor()
                    donnees_passif = passif_extractor.extraire(pdf, table_passif)
                    print(f"✅ Passif terminé: {len(donnees_passif)} lignes extraites")

            # ============================================================
            # TRAITEMENT SÉQUENTIEL: COMPTE DE RÉSULTAT
            # ============================================================
            print("\n" + "="*80)
            print("📋 COMPTE DE RÉSULTAT (Formulaires 2052-2053)")
            print("="*80)

            print("🚀 Traitement des données (2 pages)...")
            cr_extractor = CompteResultatExtractor()
            donnees_cr = cr_extractor.extraire(pdf, None)
            print(f"✅ Compte de Résultat terminé: {len(donnees_cr)} lignes extraites")

            # ============================================================
            # TRAITEMENT SÉQUENTIEL: ÉTAT DES ÉCHÉANCES
            # ============================================================
            print("\n" + "="*80)
            print("📋 ÉTAT DES ÉCHÉANCES (Formulaire 2057)")
            print("="*80)

            print("🔍 Recherche de la page de l'État des Échéances...")
            echeances_page_index = trouver_page_contenant(pdf, ["ÉTAT DES ÉCHÉANCES", "ETAT DES ECHEANCES"])

            if echeances_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_echeances = []
            else:
                print(f"   ✓ Page identifiée : {echeances_page_index + 1}")

                print("📊 Extraction du tableau...")
                tables_echeances = pdf.pages[echeances_page_index].extract_tables()
                if not tables_echeances:
                    print("❌ Aucun tableau trouvé.")
                    donnees_echeances = []
                else:
                    table_echeances = tables_echeances[0]
                    print("   ✓ Tableau extrait")

                    print("🚀 Traitement des données...")
                    echeances_extractor = EtatEcheancesExtractor()
                    donnees_echeances = echeances_extractor.extraire(pdf, table_echeances)
                    print(f"✅ Échéances terminé: {len(donnees_echeances)} lignes extraites")

            # ============================================================
            # TRAITEMENT SÉQUENTIEL: AFFECTATION DU RÉSULTAT
            # ============================================================
            print("\n" + "="*80)
            print("📋 AFFECTATION DU RÉSULTAT (Formulaire 2058-C)")
            print("="*80)

            print("🔍 Recherche de la page de l'Affectation...")
            affectation_page_index = trouver_page_contenant(pdf, ["AFFECTATION DU RÉSULTAT", "RENSEIGNEMENTS DIVERS"])

            if affectation_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_affectation = []
            else:
                print(f"   ✓ Page identifiée : {affectation_page_index + 1}")

                print("📊 Extraction du tableau...")
                tables_affectation = pdf.pages[affectation_page_index].extract_tables()
                if not tables_affectation:
                    print("❌ Aucun tableau trouvé.")
                    donnees_affectation = []
                else:
                    table_affectation = tables_affectation[0]
                    print("   ✓ Tableau extrait")

                    print("🚀 Traitement des données...")
                    affectation_extractor = AffectationExtractor()
                    donnees_affectation = affectation_extractor.extraire(pdf, table_affectation)
                    print(f"✅ Affectation terminé: {len(donnees_affectation)} lignes extraites")

            return {
                'actif': donnees_actif,
                'passif': donnees_passif,
                'cr': donnees_cr,
                'echeances': donnees_echeances,
                'affectation': donnees_affectation
            }

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Point d'entrée principal : traite tous les PDFs du dossier 'liasses/'."""
    print("\n" + "="*80)
    print("🚀 EXTRACTION LIASSE FISCALE - MODE CLI (VERSION REFACTORISÉE)")
    print("="*80)

    dossier_liasses = Path("liasses")
    dossier_resultats = Path("resultats")
    dossier_resultats.mkdir(exist_ok=True)

    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("\n❌ Aucun PDF dans 'liasses/'\n")
        return

    print(f"\n📁 {len(fichiers_pdf)} fichier(s) PDF trouvé(s)")
    print("ℹ️  Chaque PDF sera traité avec détection automatique de l'année")
    print()

    donnees_par_annee = {}

    # Traiter chaque PDF
    for idx, chemin_pdf in enumerate(fichiers_pdf):
        print(f"\n{'='*80}")
        print(f"📄 Fichier {idx + 1}/{len(fichiers_pdf)} : {chemin_pdf.name}")
        print(f"{'='*80}")

        resultats = extraire_un_pdf(chemin_pdf)

        if resultats:
            # Essayer d'extraire l'année du PDF
            with pdfplumber.open(chemin_pdf) as pdf:
                annee = extraire_annee_fiscale(pdf)

            # Si l'année n'est pas détectée, utiliser une attribution automatique
            if not annee:
                annee = str(2023 + idx)
                print(f"\n⚠️ Année non détectée, utilisation de l'année par défaut : {annee}")

            donnees_par_annee[annee] = resultats
            print(f"\n✅ Extraction réussie pour {chemin_pdf.name} (année {annee})")
        else:
            print(f"\n❌ Échec de l'extraction pour {chemin_pdf.name}")

    # Générer le fichier Excel
    if donnees_par_annee:
        print(f"\n{'='*80}")
        print("📊 GÉNÉRATION DU FICHIER EXCEL")
        print(f"{'='*80}\n")

        nom_excel = dossier_resultats / "extraction_multi_annees.xlsx"
        creer_fichier_excel(donnees_par_annee, nom_excel)

        print("="*80)
        print("✅ EXTRACTION TERMINÉE")
        print("="*80)
        print(f"\n📥 Fichier généré : {nom_excel}")
        print(f"📅 Années extraites : {', '.join(sorted(donnees_par_annee.keys()))}")
        print()
    else:
        print("\n❌ Aucune donnée n'a pu être extraite.\n")


if __name__ == "__main__":
    main()
