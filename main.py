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

            # --- ÉTAPE 1 : TROUVER LA PAGE DE L'ACTIF ---
            print("🔍 Recherche de la page du Bilan Actif...")
            actif_page_index = trouver_page_contenant(pdf, ["Brut", "Net", "ACTIF"])

            if actif_page_index == -1:
                print("❌ Impossible de trouver la page du Bilan Actif.")
                return None

            print(f"   ✓ Bilan Actif identifié sur la page {actif_page_index + 1}.")

            # --- ÉTAPE 2 : TROUVER LA PAGE DU PASSIF ---
            print("🔍 Recherche de la page du Bilan Passif...")
            passif_page_index = trouver_page_contenant(pdf, ["Capital social ou individuel", "PASSIF"])

            if passif_page_index == -1:
                print("❌ Impossible de trouver la page du Bilan Passif.")
                return None

            print(f"   ✓ Bilan Passif identifié sur la page {passif_page_index + 1}.")

            # --- ÉTAPE 3 : EXTRAIRE LES TABLEAUX ---
            print("\n📊 Extraction des tableaux...")

            tables_actif = pdf.pages[actif_page_index].extract_tables()
            if not tables_actif:
                print(f"❌ Aucun tableau trouvé sur la page de l'Actif.")
                return None
            table_actif = tables_actif[0]
            print(f"   ✓ Tableau Actif extrait.")

            tables_passif = pdf.pages[passif_page_index].extract_tables()
            if not tables_passif:
                print(f"❌ Aucun tableau trouvé sur la page du Passif.")
                return None
            table_passif = tables_passif[0]
            print(f"   ✓ Tableau Passif extrait.")

            # --- ÉTAPE 4 : EXTRACTION DES DONNÉES AVEC LES EXTRACTEURS ---

            # Extraction Actif
            print("\n--- 🚀 EXTRACTION DU BILAN ACTIF ---")
            actif_extractor = BilanActifExtractor()
            donnees_actif = actif_extractor.extraire(pdf, table_actif)

            # Extraction Passif
            print("\n--- 🚀 EXTRACTION DU BILAN PASSIF ---")
            passif_extractor = BilanPassifExtractor()
            donnees_passif = passif_extractor.extraire(pdf, table_passif)

            # Extraction Compte de Résultat
            print("\n--- 🚀 EXTRACTION DU COMPTE DE RÉSULTAT ---")
            cr_extractor = CompteResultatExtractor()
            donnees_cr = cr_extractor.extraire(pdf, None)

            # Extraction État des échéances
            print("\n--- 🚀 EXTRACTION DE L'ÉTAT DES ÉCHÉANCES ---")
            echeances_page_index = trouver_page_contenant(pdf, ["ÉTAT DES ÉCHÉANCES", "ETAT DES ECHEANCES"])
            if echeances_page_index != -1:
                tables_echeances = pdf.pages[echeances_page_index].extract_tables()
                table_echeances = tables_echeances[0] if tables_echeances else []
                echeances_extractor = EtatEcheancesExtractor()
                donnees_echeances = echeances_extractor.extraire(pdf, table_echeances)
            else:
                print("⚠️ Page État des échéances non trouvée")
                donnees_echeances = []

            # Extraction Affectation du résultat
            print("\n--- 🚀 EXTRACTION DE L'AFFECTATION DU RÉSULTAT ---")
            affectation_page_index = trouver_page_contenant(pdf, ["AFFECTATION DU RÉSULTAT", "RENSEIGNEMENTS DIVERS"])
            if affectation_page_index != -1:
                tables_affectation = pdf.pages[affectation_page_index].extract_tables()
                table_affectation = tables_affectation[0] if tables_affectation else []
                affectation_extractor = AffectationExtractor()
                donnees_affectation = affectation_extractor.extraire(pdf, table_affectation)
            else:
                print("⚠️ Page Affectation du résultat non trouvée")
                donnees_affectation = []

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
