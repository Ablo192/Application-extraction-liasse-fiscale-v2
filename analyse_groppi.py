"""
Script d'analyse du fichier GROPPI pour comprendre le problème d'exploitation
"""

import pdfplumber

chemin_pdf = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("="*80)
print("ANALYSE DU FICHIER GROPPI - Détection vs Exploitation")
print("="*80)

# Codes de test (exemples du Bilan)
CODES_TEST_ACTIF = ["AB", "AF", "AH", "AN", "AP", "BX", "CF"]
CODES_TEST_PASSIF = ["DA", "DB", "DL", "DM", "DN", "DP"]

with pdfplumber.open(chemin_pdf) as pdf:
    print(f"\n📄 Nombre total de pages: {len(pdf.pages)}\n")

    # Parcourir les pages
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()

        # Détection des pages avec mots-clés
        est_actif = "ACTIF" in text and "BILAN" in text
        est_passif = "PASSIF" in text and "BILAN" in text
        est_cr = "COMPTE DE RÉSULTAT" in text

        if not (est_actif or est_passif or est_cr):
            continue

        print(f"\n{'='*80}")
        print(f"PAGE {page_num} DÉTECTÉE")
        if est_actif:
            print("Type: BILAN ACTIF")
            codes_recherche = CODES_TEST_ACTIF
        elif est_passif:
            print("Type: BILAN PASSIF")
            codes_recherche = CODES_TEST_PASSIF
        elif est_cr:
            print("Type: COMPTE DE RÉSULTAT")
            codes_recherche = []
        print(f"{'='*80}")

        # Extraire les tableaux
        tables = page.extract_tables()

        print(f"\n✓ Tableaux détectés: {len(tables)}")

        # Analyser le premier tableau
        if tables:
            table = tables[0]
            print(f"✓ Dimensions du tableau: {len(table)} lignes x {len(table[0]) if table else 0} colonnes")

            # Afficher les en-têtes
            print(f"\n📋 EN-TÊTES (3 premières lignes):")
            for i in range(min(3, len(table))):
                print(f"   Ligne {i}: {table[i]}")

            # Trouver la colonne Net ou montants
            print(f"\n🔍 RECHERCHE DES COLONNES DE MONTANTS:")
            col_net = None
            col_montant = None

            for row_idx, row in enumerate(table[:10]):
                for col_idx, cell in enumerate(row):
                    if cell:
                        cell_upper = str(cell).upper()
                        if "NET" in cell_upper and "BRUT" not in cell_upper:
                            col_net = col_idx
                            print(f"   ✓ Colonne 'Net' trouvée à l'index {col_idx}: '{cell}'")
                        elif "EXERCICE N" in cell_upper or "(N)" in cell_upper:
                            col_montant = col_idx
                            print(f"   ✓ Colonne 'Exercice N' trouvée à l'index {col_idx}: '{cell}'")

            colonne_cible = col_net if col_net is not None else col_montant

            if colonne_cible is None:
                print("   ❌ Aucune colonne de montant trouvée!")
                continue

            # Rechercher les codes
            print(f"\n🔍 RECHERCHE DES CODES (exploitation):")
            codes_trouves = {}

            for row_idx, row in enumerate(table):
                for cell_idx, cell in enumerate(row):
                    if not cell:
                        continue

                    cell_text = str(cell).strip().upper()

                    if cell_text in codes_recherche:
                        print(f"\n   📍 Code '{cell_text}' trouvé:")
                        print(f"      - Position: ligne {row_idx}, colonne {cell_idx}")
                        print(f"      - Contenu ligne: {row}")

                        # Extraire le montant
                        if colonne_cible < len(row):
                            montant = row[colonne_cible]
                            print(f"      - Montant (col {colonne_cible}): '{montant}' (type: {type(montant).__name__})")
                            codes_trouves[cell_text] = montant
                        else:
                            print(f"      ⚠️ Ligne trop courte ({len(row)} colonnes)")

            # Résumé pour cette page
            print(f"\n📊 RÉSUMÉ PAGE {page_num}:")
            print(f"   - Codes trouvés: {len(codes_trouves)}")
            for code, montant in codes_trouves.items():
                print(f"   - {code} = {montant}")

print("\n" + "="*80)
print("FIN DE L'ANALYSE")
print("="*80)
