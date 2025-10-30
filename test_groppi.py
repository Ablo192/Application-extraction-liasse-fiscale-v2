"""Script de test pour analyser le fichier GROPPI et identifier le problème d'exploitation"""

import pdfplumber
from extraction_analytique import ExtractionAnalytique
import json

pdf_path = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("=" * 80)
print("ANALYSE DU FICHIER GROPPI")
print("=" * 80)

# Phase 1 : Extraction avec le module analytique
print("\n1. EXTRACTION AVEC MODULE ANALYTIQUE")
print("-" * 80)

extracteur = ExtractionAnalytique()
resultats = extracteur.extraire_pdf_complet(pdf_path)

print(f"\nNombre de tableaux détectés: {len(resultats)}")

for i, (type_tableau, donnees) in enumerate(resultats.items(), 1):
    print(f"\n{i}. Type: {type_tableau}")
    print(f"   Nombre de lignes extraites: {len(donnees)}")
    if donnees:
        print(f"   Premier exemple: {list(donnees.items())[0]}")
        print(f"   Dernier exemple: {list(donnees.items())[-1]}")

# Phase 2 : Analyse brute des pages détectées
print("\n\n2. ANALYSE BRUTE DES PAGES")
print("-" * 80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Nombre total de pages: {len(pdf.pages)}")

    # Recherche des pages avec tableaux
    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()

        # Détection de mots-clés de tableaux
        if "ACTIF" in text or "PASSIF" in text or "COMPTE DE RÉSULTAT" in text:
            print(f"\nPage {page_num + 1}:")
            tables = page.extract_tables()
            print(f"  - Nombre de tableaux détectés: {len(tables)}")

            if tables:
                for t_idx, table in enumerate(tables):
                    print(f"  - Tableau {t_idx + 1}: {len(table)} lignes x {len(table[0]) if table else 0} colonnes")
                    if len(table) > 2:
                        print(f"    En-tête: {table[0]}")
                        print(f"    Ligne 1: {table[1]}")

print("\n\n3. RÉSULTATS FINAUX")
print("-" * 80)
print(json.dumps(resultats, indent=2, ensure_ascii=False))
