#!/usr/bin/env python3
"""
Application d'extraction de liasses fiscales françaises depuis des PDFs avec Camelot.

Ce script utilise Camelot (au lieu de pdfplumber) pour une extraction plus robuste
des tableaux. Camelot offre deux modes:
- 'lattice': pour les tableaux avec des lignes visibles (par défaut)
- 'stream': pour les tableaux sans lignes (fallback)

Usage:
    python main_camelot.py

Le script traite tous les PDFs du dossier 'liasses/' et génère un fichier Excel
dans le dossier 'resultats/'.
"""

import camelot
import pdfplumber
from pathlib import Path
import pandas as pd

# Importation des modules refactorisés (MÊMES QUE main.py)
from src.extractors.bilan_actif import BilanActifExtractor
from src.extractors.bilan_passif import BilanPassifExtractor
from src.extractors.compte_resultat import CompteResultatExtractor
from src.extractors.etat_echeances import EtatEcheancesExtractor
from src.extractors.affectation import AffectationExtractor
from src.export.excel_generator import creer_fichier_excel as creer_fichier_excel_intelligent
from src.utils.pdf_utils import extraire_annee_fiscale, trouver_page_contenant as trouver_page_pdfplumber


# ============================================================
# UTILITAIRES CAMELOT
# ============================================================

def dataframe_vers_table(df):
    """
    Convertit un DataFrame pandas (Camelot) en liste de listes (compatible avec extracteurs).

    Args:
        df: DataFrame pandas retourné par Camelot

    Returns:
        list: Liste de listes représentant le tableau
    """
    # Convertir le DataFrame en liste de listes
    # Inclure les en-têtes si nécessaire
    table = df.values.tolist()
    return table


def trouver_page_contenant(chemin_pdf, mots_cles):
    """Trouve le numéro de page contenant les mots-clés (wrapper pour pdfplumber)."""
    with pdfplumber.open(chemin_pdf) as pdf:
        return trouver_page_pdfplumber(pdf, mots_cles)


def extraire_tables_camelot(chemin_pdf, page_num, mode='lattice'):
    """
    Extrait les tables d'une page avec Camelot.

    Args:
        chemin_pdf: Path du PDF
        page_num: Numéro de page (1-indexed pour Camelot)
        mode: 'lattice' (défaut) ou 'stream'

    Returns:
        list de DataFrames pandas
    """
    try:
        print(f"   📊 Mode Camelot: {mode}")
        tables = camelot.read_pdf(
            str(chemin_pdf),
            pages=str(page_num),
            flavor=mode,
            suppress_stdout=True
        )

        if tables:
            print(f"   ✓ {len(tables)} tableau(x) extrait(s)")
            # Afficher quelques infos sur la qualité
            for i, table in enumerate(tables):
                if hasattr(table, 'parsing_report'):
                    accuracy = table.parsing_report.get('accuracy', 0)
                    print(f"      Table {i+1}: précision = {accuracy:.1f}%")

            return [table.df for table in tables]
        else:
            print(f"   ❌ Aucun tableau trouvé")
            return []

    except Exception as e:
        print(f"   ❌ Erreur Camelot ({mode}): {e}")
        return []


# ============================================================
# FONCTION PRINCIPALE D'EXTRACTION (avec extracteurs intelligents)
# ============================================================

def extraire_un_pdf(chemin_pdf):
    """Extrait les données d'un seul PDF avec Camelot + extracteurs intelligents."""
    print(f"\n{'='*80}")
    print(f"📄 Traitement : {chemin_pdf.name}")
    print(f"{'='*80}\n")

    try:
        # Ouvrir le PDF avec pdfplumber (nécessaire pour certains extracteurs)
        with pdfplumber.open(chemin_pdf) as pdf:

            # Extraire l'année fiscale
            annee = extraire_annee_fiscale(pdf)
            if annee:
                print(f"📅 Année fiscale détectée : {annee}\n")

            # ============================================================
            # BILAN ACTIF (Formulaire 2050)
            # ============================================================
            print("\n" + "="*80)
            print("📋 BILAN ACTIF (Formulaire 2050)")
            print("="*80)

            print("🔍 Recherche de la page du Bilan Actif...")
            actif_page_index = trouver_page_contenant(chemin_pdf, ["Brut", "Net", "ACTIF"])

            if actif_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_actif = []
            else:
                print(f"   ✓ Page identifiée : {actif_page_index + 1}")

                print("📊 Extraction du tableau avec Camelot...")
                # Extraire avec Camelot (page_num est 1-indexed)
                tables_df = extraire_tables_camelot(chemin_pdf, actif_page_index + 1, mode='lattice')
                if not tables_df:
                    # Fallback sur stream
                    tables_df = extraire_tables_camelot(chemin_pdf, actif_page_index + 1, mode='stream')

                if not tables_df:
                    print("❌ Aucun tableau trouvé.")
                    donnees_actif = []
                else:
                    # Convertir DataFrame → liste de listes
                    table_actif = dataframe_vers_table(tables_df[0])
                    print("   ✓ Tableau converti au format liste")

                    print("🚀 Traitement avec extracteur intelligent...")
                    actif_extractor = BilanActifExtractor()
                    donnees_actif = actif_extractor.extraire(pdf, table_actif)
                    print(f"✅ Actif terminé: {len(donnees_actif)} lignes extraites")

            # ============================================================
            # BILAN PASSIF (Formulaire 2051)
            # ============================================================
            print("\n" + "="*80)
            print("📋 BILAN PASSIF (Formulaire 2051)")
            print("="*80)

            print("🔍 Recherche de la page du Bilan Passif...")
            passif_page_index = trouver_page_contenant(chemin_pdf, ["Capital social ou individuel", "PASSIF"])

            if passif_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_passif = []
            else:
                print(f"   ✓ Page identifiée : {passif_page_index + 1}")

                print("📊 Extraction du tableau avec Camelot...")
                tables_df = extraire_tables_camelot(chemin_pdf, passif_page_index + 1, mode='lattice')
                if not tables_df:
                    tables_df = extraire_tables_camelot(chemin_pdf, passif_page_index + 1, mode='stream')

                if not tables_df:
                    print("❌ Aucun tableau trouvé.")
                    donnees_passif = []
                else:
                    table_passif = dataframe_vers_table(tables_df[0])
                    print("   ✓ Tableau converti au format liste")

                    print("🚀 Traitement avec extracteur intelligent...")
                    passif_extractor = BilanPassifExtractor()
                    donnees_passif = passif_extractor.extraire(pdf, table_passif)
                    print(f"✅ Passif terminé: {len(donnees_passif)} lignes extraites")

            # ============================================================
            # COMPTE DE RÉSULTAT (Formulaires 2052-2053)
            # ============================================================
            print("\n" + "="*80)
            print("📋 COMPTE DE RÉSULTAT (Formulaires 2052-2053)")
            print("="*80)

            print("🚀 Traitement avec extracteur intelligent (2 pages)...")
            cr_extractor = CompteResultatExtractor()
            # L'extracteur CR gère lui-même l'extraction avec pdfplumber ou peut être adapté
            # Pour l'instant, on le laisse utiliser pdfplumber en interne
            donnees_cr = cr_extractor.extraire(pdf, None)
            print(f"✅ Compte de Résultat terminé: {len(donnees_cr)} lignes extraites")

            # ============================================================
            # ÉTAT DES ÉCHÉANCES (Formulaire 2057)
            # ============================================================
            print("\n" + "="*80)
            print("📋 ÉTAT DES ÉCHÉANCES (Formulaire 2057)")
            print("="*80)

            print("🔍 Recherche de la page de l'État des Échéances...")
            echeances_page_index = trouver_page_contenant(chemin_pdf, ["ÉTAT DES ÉCHÉANCES", "ETAT DES ECHEANCES"])

            if echeances_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_echeances = []
            else:
                print(f"   ✓ Page identifiée : {echeances_page_index + 1}")

                print("📊 Extraction du tableau avec Camelot...")
                tables_df = extraire_tables_camelot(chemin_pdf, echeances_page_index + 1, mode='lattice')
                if not tables_df:
                    tables_df = extraire_tables_camelot(chemin_pdf, echeances_page_index + 1, mode='stream')

                if not tables_df:
                    print("❌ Aucun tableau trouvé.")
                    donnees_echeances = []
                else:
                    table_echeances = dataframe_vers_table(tables_df[0])
                    print("   ✓ Tableau converti au format liste")

                    print("🚀 Traitement avec extracteur intelligent...")
                    echeances_extractor = EtatEcheancesExtractor()
                    donnees_echeances = echeances_extractor.extraire(pdf, table_echeances)
                    print(f"✅ Échéances terminé: {len(donnees_echeances)} lignes extraites")

            # ============================================================
            # AFFECTATION DU RÉSULTAT (Formulaire 2058-C)
            # ============================================================
            print("\n" + "="*80)
            print("📋 AFFECTATION DU RÉSULTAT (Formulaire 2058-C)")
            print("="*80)

            print("🔍 Recherche de la page de l'Affectation...")
            affectation_page_index = trouver_page_contenant(chemin_pdf, ["AFFECTATION DU RÉSULTAT", "RENSEIGNEMENTS DIVERS"])

            if affectation_page_index == -1:
                print("❌ Page non trouvée. Passage au formulaire suivant.")
                donnees_affectation = []
            else:
                print(f"   ✓ Page identifiée : {affectation_page_index + 1}")

                print("📊 Extraction du tableau avec Camelot...")
                tables_df = extraire_tables_camelot(chemin_pdf, affectation_page_index + 1, mode='lattice')
                if not tables_df:
                    tables_df = extraire_tables_camelot(chemin_pdf, affectation_page_index + 1, mode='stream')

                if not tables_df:
                    print("❌ Aucun tableau trouvé.")
                    donnees_affectation = []
                else:
                    table_affectation = dataframe_vers_table(tables_df[0])
                    print("   ✓ Tableau converti au format liste")

                    print("🚀 Traitement avec extracteur intelligent...")
                    affectation_extractor = AffectationExtractor()
                    donnees_affectation = affectation_extractor.extraire(pdf, table_affectation)
                    print(f"✅ Affectation terminé: {len(donnees_affectation)} lignes extraites")

            return {
                'annee': annee,
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
    print("🚀 EXTRACTION LIASSE FISCALE - VERSION CAMELOT")
    print("="*80)
    print("\n🔧 Utilisation de Camelot pour une extraction robuste des tableaux")
    print("   Modes: Lattice (tableaux avec lignes) + Stream (fallback)\n")

    dossier_liasses = Path("liasses")
    dossier_resultats = Path("resultats")
    dossier_resultats.mkdir(exist_ok=True)

    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("\n❌ Aucun PDF dans 'liasses/'\n")
        return

    print(f"📁 {len(fichiers_pdf)} fichier(s) PDF trouvé(s)")
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
            # Récupérer l'année extraite
            annee = resultats.get('annee')

            # Si l'année n'est pas détectée, utiliser une attribution automatique
            if not annee:
                annee = str(2023 + idx)
                print(f"\n⚠️ Année non détectée, utilisation de l'année par défaut : {annee}")

            donnees_par_annee[annee] = resultats
            print(f"\n✅ Extraction réussie pour {chemin_pdf.name} (année {annee})")
        else:
            print(f"\n❌ Échec de l'extraction pour {chemin_pdf.name}")

    # Générer le fichier Excel avec le générateur intelligent
    if donnees_par_annee:
        print(f"\n{'='*80}")
        print("📊 GÉNÉRATION DU FICHIER EXCEL (avec analyse financière)")
        print(f"{'='*80}\n")

        nom_excel = dossier_resultats / "extraction_multi_annees_camelot.xlsx"
        creer_fichier_excel_intelligent(donnees_par_annee, nom_excel)

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
