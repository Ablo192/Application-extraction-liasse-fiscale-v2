"""
Script pour vérifier si le PDF contient des montants ou est vierge
"""
import pdfplumber
from extraction_simple import nettoyer_montant

pdf_path = "liasses/Liasse fiscale vierge.pdf"

print("\n" + "="*80)
print("VÉRIFICATION DU CONTENU DU PDF")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"\nPDF : {pdf_path}")
    print(f"Nombre de pages : {len(pdf.pages)}\n")

    # Analyser la page 1 (ACTIF)
    print("="*80)
    print("PAGE 1 : BILAN ACTIF")
    print("="*80)

    page = pdf.pages[0]
    tables = page.extract_tables()

    table = None
    for t in tables:
        if t and len(t) >= 20:
            table = t
            break

    if table:
        print(f"\nTableau : {len(table)} lignes × {len(table[0])} colonnes")

        # Chercher des montants dans TOUTES les colonnes
        montants_trouves = []
        codes_trouves = []

        for row_idx in range(5, len(table)):
            row = table[row_idx]

            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                cell_str = str(cell).strip()

                # Vérifier si c'est un code (2 lettres)
                if len(cell_str) == 2 and cell_str.upper().isalpha():
                    codes_trouves.append((row_idx, col_idx, cell_str.upper()))

                # Vérifier si c'est un montant (nombre)
                montant = nettoyer_montant(cell)
                if montant is not None and montant != 0:
                    montants_trouves.append((row_idx, col_idx, montant))

        print(f"\n📊 STATISTIQUES :")
        print(f"   - Codes trouvés : {len(codes_trouves)}")
        print(f"   - Montants trouvés : {len(montants_trouves)}")

        if codes_trouves:
            print(f"\n📌 Échantillon de codes trouvés (premiers 10) :")
            for row, col, code in codes_trouves[:10]:
                print(f"     Ligne {row}, Colonne {col} : {code}")

        if montants_trouves:
            print(f"\n💰 Échantillon de montants trouvés (premiers 10) :")
            for row, col, montant in montants_trouves[:10]:
                print(f"     Ligne {row}, Colonne {col} : {montant:,.2f}")
        else:
            print(f"\n❌ AUCUN MONTANT TROUVÉ DANS CE PDF")
            print(f"   → Ce PDF est VIERGE (formulaire sans données)")
            print(f"   → Il contient seulement les codes de référence")

        # Vérifier les autres pages
        print("\n" + "="*80)
        print("VÉRIFICATION RAPIDE DES AUTRES PAGES")
        print("="*80)

        for page_num in [1, 2, 3]:
            if page_num >= len(pdf.pages):
                continue

            page = pdf.pages[page_num]
            tables = page.extract_tables()

            nb_montants_page = 0
            for table in tables:
                if not table:
                    continue

                for row in table:
                    if not row:
                        continue

                    for cell in row:
                        montant = nettoyer_montant(cell)
                        if montant is not None and montant != 0:
                            nb_montants_page += 1

            print(f"   Page {page_num + 1} : {nb_montants_page} montants trouvés")

print("\n" + "="*80)
