"""
Script de debug détaillé pour comprendre la structure
"""
import pdfplumber

pdf_path = "liasses/Liasse fiscale vierge.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # PAGE 1 : BILAN ACTIF
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

        # Afficher les 10 premières lignes avec tous les index
        print("\nPremières lignes du tableau :")
        for row_idx, row in enumerate(table[:10]):
            print(f"\nLigne {row_idx}:")
            for col_idx, cell in enumerate(row):
                if cell and str(cell).strip():
                    cell_display = str(cell).replace('\n', '\\n')[:50]
                    print(f"  [{col_idx}]: '{cell_display}'")

        # Afficher les lignes 5 à 15 (là où sont les codes normalement)
        print("\n" + "="*80)
        print("LIGNES DE DONNÉES (5-15)")
        print("="*80)
        for row_idx in range(5, min(15, len(table))):
            row = table[row_idx]
            print(f"\nLigne {row_idx}:")

            # Chercher les codes (2 lettres majuscules)
            codes_trouves = []
            for col_idx, cell in enumerate(row):
                if cell:
                    cell_upper = str(cell).strip().upper()
                    if len(cell_upper) == 2 and cell_upper.isalpha():
                        codes_trouves.append((col_idx, cell_upper))

            if codes_trouves:
                print(f"  CODES TROUVÉS : {codes_trouves}")

            # Afficher toutes les cellules non vides
            for col_idx, cell in enumerate(row):
                if cell and str(cell).strip():
                    cell_display = str(cell).replace('\n', '\\n')[:40]
                    print(f"    [{col_idx}]: '{cell_display}'")
