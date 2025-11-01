"""
Script de diagnostic AUTOMATIQUE pour analyser l'extraction des tableaux PDF.

Ce script détecte automatiquement tous les PDFs dans le dossier 'liasse/'
et les analyse un par un. PLUS BESOIN DE PASSER D'ARGUMENTS!

Usage simple:
    1. Mettez vos PDFs dans le dossier 'liasse/'
    2. Lancez ce script: python diagnostic_auto.py
    3. Ou dans PyCharm: clic droit → Run 'diagnostic_auto'
"""

import pdfplumber
from pathlib import Path
from src.utils.pdf_utils import (
    trouver_page_contenant,
    detecter_colonnes_numeriques,
    obtenir_colonne_numerique
)
from src.config.codes_fiscaux import (
    CODES_BILAN_ACTIF,
    CODES_BILAN_PASSIF,
    CODES_COMPTE_RESULTAT,
    CODES_ETAT_ECHEANCES_CREANCES,
    CODES_ETAT_ECHEANCES_DETTES,
    CODES_AFFECTATION_RESULTAT,
    CODES_RENSEIGNEMENTS_DIVERS
)


def afficher_separateur(titre):
    """Affiche un séparateur visuel avec un titre."""
    print("\n" + "=" * 80)
    print(f"  {titre}")
    print("=" * 80)


def analyser_tableau(nom_formulaire, table, codes_attendus):
    """Analyse un tableau extrait et affiche des informations de diagnostic.

    Args:
        nom_formulaire: Nom du formulaire (ex: "BILAN ACTIF")
        table: Tableau extrait par pdfplumber
        codes_attendus: Dictionnaire des codes fiscaux attendus
    """
    afficher_separateur(f"DIAGNOSTIC: {nom_formulaire}")

    if not table or len(table) == 0:
        print("❌ ERREUR: Tableau vide ou non extrait!")
        return

    # 1. INFORMATIONS GÉNÉRALES
    print(f"\n📊 Informations générales:")
    print(f"   - Nombre de lignes: {len(table)}")
    print(f"   - Nombre de colonnes (max): {max(len(row) for row in table if row)}")

    # 2. AFFICHER LES 10 PREMIÈRES LIGNES BRUTES
    print(f"\n📋 Les 10 premières lignes du tableau brut:")
    for idx, row in enumerate(table[:10]):
        print(f"   Ligne {idx}: {row}")

    # 3. DÉTECTION DES COLONNES NUMÉRIQUES
    print(f"\n🔢 Détection des colonnes numériques:")
    colonnes_num = detecter_colonnes_numeriques(table, start_row=1, max_rows=20)
    print(f"   - Colonnes numériques détectées: {colonnes_num}")

    if colonnes_num:
        for i in range(1, len(colonnes_num) + 1):
            idx = obtenir_colonne_numerique(table, position=i, start_row=1, max_rows=20)
            print(f"   - {i}ère colonne numérique: index {idx}")
    else:
        print("   ⚠️ Aucune colonne numérique détectée!")

    # 4. RECHERCHE DES CODES FISCAUX
    print(f"\n🔍 Recherche des codes fiscaux attendus:")
    print(f"   - Codes attendus: {len(codes_attendus)} codes")
    print(f"   - Liste: {', '.join(list(codes_attendus.keys())[:10])}...")

    codes_trouves = {}
    codes_positions = {}

    for row_idx, row in enumerate(table):
        for col_idx, cell in enumerate(row):
            if cell:
                cell_text = str(cell).strip().upper()
                if cell_text in codes_attendus:
                    codes_trouves[cell_text] = row
                    codes_positions[cell_text] = (row_idx, col_idx)

    print(f"\n   ✅ Codes trouvés: {len(codes_trouves)}/{len(codes_attendus)}")

    if codes_trouves:
        print(f"\n   📍 Détails des codes trouvés:")
        for code, (row_idx, col_idx) in list(codes_positions.items())[:10]:
            libelle = codes_attendus[code]
            print(f"      - {code} ({libelle})")
            print(f"        Position: ligne {row_idx}, colonne {col_idx}")
            print(f"        Ligne complète: {codes_trouves[code]}")
    else:
        print(f"\n   ❌ AUCUN CODE TROUVÉ!")
        print(f"\n   🔍 Analyse des cellules (20 premières lignes):")

        # Afficher toutes les cellules pour débugger
        cellules_uniques = set()
        for row_idx, row in enumerate(table[:20]):
            for col_idx, cell in enumerate(row):
                if cell:
                    cell_text = str(cell).strip().upper()
                    if len(cell_text) <= 4:  # Les codes font 2 lettres généralement
                        cellules_uniques.add(cell_text)

        print(f"      Cellules courtes trouvées (≤4 caractères): {sorted(cellules_uniques)}")

    # 5. ANALYSE COLONNE PAR COLONNE (en-tête)
    print(f"\n📑 Contenu des colonnes (ligne 0 - en-tête):")
    if table and len(table) > 0:
        for col_idx, cell in enumerate(table[0]):
            print(f"   - Colonne {col_idx}: '{cell}'")

    print("\n" + "-" * 80)


def diagnostic_complet(pdf_path):
    """Effectue un diagnostic complet de l'extraction des tableaux.

    Args:
        pdf_path: Chemin vers le fichier PDF de la liasse fiscale
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"❌ ERREUR: Le fichier {pdf_path} n'existe pas!")
        return

    print("=" * 80)
    print(f"  DIAGNOSTIC D'EXTRACTION - {pdf_path.name}")
    print("=" * 80)
    print(f"\nFichier: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Nombre de pages: {len(pdf.pages)}")

        # 1. BILAN ACTIF (Formulaire 2050)
        page_actif = trouver_page_contenant(pdf, ["BILAN - ACTIF", "ACTIF IMMOBILISÉ"])
        if page_actif != -1:
            print(f"\n✅ BILAN ACTIF trouvé à la page {page_actif + 1}")
            table_actif = pdf.pages[page_actif].extract_table()
            analyser_tableau("BILAN ACTIF (2050)", table_actif, CODES_BILAN_ACTIF)
        else:
            print("\n❌ BILAN ACTIF non trouvé")

        # 2. BILAN PASSIF (Formulaire 2051)
        page_passif = trouver_page_contenant(pdf, ["BILAN - PASSIF", "CAPITAUX PROPRES"])
        if page_passif != -1:
            print(f"\n✅ BILAN PASSIF trouvé à la page {page_passif + 1}")
            table_passif = pdf.pages[page_passif].extract_table()
            analyser_tableau("BILAN PASSIF (2051)", table_passif, CODES_BILAN_PASSIF)
        else:
            print("\n❌ BILAN PASSIF non trouvé")

        # 3. COMPTE DE RÉSULTAT - Page 1 (Formulaire 2052)
        page_cr1 = trouver_page_contenant(pdf, ["COMPTE DE RÉSULTAT", "Ventes de marchandises"])
        if page_cr1 != -1:
            print(f"\n✅ COMPTE DE RÉSULTAT (Page 1) trouvé à la page {page_cr1 + 1}")
            table_cr1 = pdf.pages[page_cr1].extract_table()
            analyser_tableau("COMPTE DE RÉSULTAT - PAGE 1 (2052)", table_cr1, CODES_COMPTE_RESULTAT)
        else:
            print("\n❌ COMPTE DE RÉSULTAT (Page 1) non trouvé")

        # 4. COMPTE DE RÉSULTAT - Page 2 (Formulaire 2053)
        page_cr2 = trouver_page_contenant(pdf, ["COMPTE DE RÉSULTAT (SUITE)", "Charges exceptionnelles"])
        if page_cr2 != -1:
            print(f"\n✅ COMPTE DE RÉSULTAT (Page 2) trouvé à la page {page_cr2 + 1}")
            table_cr2 = pdf.pages[page_cr2].extract_table()
            analyser_tableau("COMPTE DE RÉSULTAT - PAGE 2 (2053)", table_cr2, CODES_COMPTE_RESULTAT)
        else:
            print("\n❌ COMPTE DE RÉSULTAT (Page 2) non trouvé")

        # 5. ÉTAT DES ÉCHÉANCES (Formulaire 2057)
        page_echeances = trouver_page_contenant(pdf, ["ÉTAT DES ÉCHÉANCES", "Clients douteux"])
        if page_echeances != -1:
            print(f"\n✅ ÉTAT DES ÉCHÉANCES trouvé à la page {page_echeances + 1}")
            table_echeances = pdf.pages[page_echeances].extract_table()
            codes_echeances = {**CODES_ETAT_ECHEANCES_CREANCES, **CODES_ETAT_ECHEANCES_DETTES}
            analyser_tableau("ÉTAT DES ÉCHÉANCES (2057)", table_echeances, codes_echeances)
        else:
            print("\n❌ ÉTAT DES ÉCHÉANCES non trouvé")

        # 6. AFFECTATION DU RÉSULTAT (Formulaire 2058-C)
        page_affectation = trouver_page_contenant(pdf, ["AFFECTATION DU RÉSULTAT", "RENSEIGNEMENTS DIVERS"])
        if page_affectation != -1:
            print(f"\n✅ AFFECTATION trouvée à la page {page_affectation + 1}")
            table_affectation = pdf.pages[page_affectation].extract_table()
            codes_affectation = {**CODES_AFFECTATION_RESULTAT, **CODES_RENSEIGNEMENTS_DIVERS}
            analyser_tableau("AFFECTATION DU RÉSULTAT (2058-C)", table_affectation, codes_affectation)
        else:
            print("\n❌ AFFECTATION non trouvée")

    # RÉSUMÉ FINAL
    afficher_separateur("RÉSUMÉ DU DIAGNOSTIC")
    print("\n✅ Diagnostic terminé!")
    print("\n💡 Conseils:")
    print("   - Si aucun code n'est trouvé, vérifiez le format des codes dans le PDF")
    print("   - Si les colonnes numériques ne sont pas détectées, vérifiez le format des montants")
    print("   - Comparez les 'Cellules courtes trouvées' avec les codes attendus")
    print("   - Vérifiez si les codes sont dans des colonnes fusionnées ou mal extraites")
    print("\n" + "=" * 80)


def detecter_pdfs_dans_liasse():
    """Détecte automatiquement tous les PDFs dans le dossier 'liasse/'."""
    dossier_liasse = Path("liasse")

    # Créer le dossier s'il n'existe pas
    if not dossier_liasse.exists():
        print(f"📁 Création du dossier 'liasse/'...")
        dossier_liasse.mkdir()
        print(f"✅ Dossier créé! Mettez vos PDFs dedans et relancez le script.")
        return []

    # Chercher tous les fichiers PDF
    pdfs = list(dossier_liasse.glob("*.pdf"))

    return pdfs


if __name__ == "__main__":
    print("=" * 80)
    print("  🔍 DIAGNOSTIC AUTOMATIQUE - EXTRACTION DE LIASSES FISCALES")
    print("=" * 80)

    # Détecter les PDFs dans le dossier liasse/
    print("\n📂 Recherche de PDFs dans le dossier 'liasse/'...")
    pdfs = detecter_pdfs_dans_liasse()

    if not pdfs:
        print("\n❌ Aucun fichier PDF trouvé dans le dossier 'liasse/'!")
        print("\n💡 Instructions:")
        print("   1. Placez vos fichiers PDF dans le dossier 'liasse/'")
        print("   2. Relancez ce script")
        print("\nExemple:")
        print("   liasse/")
        print("   ├── ma_liasse_2024.pdf")
        print("   └── liasse_vierge.pdf")
    else:
        print(f"\n✅ {len(pdfs)} fichier(s) PDF trouvé(s):")
        for pdf in pdfs:
            print(f"   - {pdf.name}")

        # Demander à l'utilisateur quel PDF analyser
        if len(pdfs) == 1:
            print(f"\n🚀 Analyse automatique de {pdfs[0].name}...\n")
            diagnostic_complet(pdfs[0])
        else:
            print("\n📋 Sélectionnez un fichier à analyser:")
            for idx, pdf in enumerate(pdfs, 1):
                print(f"   {idx}. {pdf.name}")
            print(f"   0. Analyser TOUS les fichiers")

            try:
                choix = input("\nVotre choix (0-{}): ".format(len(pdfs)))
                choix = int(choix)

                if choix == 0:
                    # Analyser tous les PDFs
                    for pdf in pdfs:
                        diagnostic_complet(pdf)
                        print("\n" + "🔄" * 40 + "\n")
                elif 1 <= choix <= len(pdfs):
                    # Analyser le PDF sélectionné
                    diagnostic_complet(pdfs[choix - 1])
                else:
                    print("❌ Choix invalide!")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Annulé ou choix invalide!")

    print("\n✅ Fin du diagnostic automatique.")
