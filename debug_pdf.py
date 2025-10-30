"""
Script de diagnostic pour analyser le PDF
"""
import pdfplumber

pdf_path = "liasses/Liasse fiscale vierge.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"\n=== ANALYSE DU PDF: {len(pdf.pages)} pages ===\n")

    for page_idx, page in enumerate(pdf.pages[:15]):  # Analyser les 15 premières pages
        print(f"\n{'='*80}")
        print(f"PAGE {page_idx + 1}")
        print('='*80)

        # Extraire le texte
        text = page.extract_text() or ""
        lines = text.split('\n')[:20]  # Premières 20 lignes

        print("\n--- TEXTE (premières lignes) ---")
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}. {line[:100]}")

        # Extraire les tableaux
        tables = page.extract_tables()
        print(f"\n--- TABLEAUX: {len(tables)} trouvé(s) ---")

        for table_idx, table in enumerate(tables):
            if not table:
                continue

            print(f"\n  TABLEAU #{table_idx + 1}:")
            print(f"    Dimensions: {len(table)} lignes × {len(table[0]) if table else 0} colonnes")

            # Afficher les 5 premières lignes du tableau
            print("    Premières lignes:")
            for row_idx, row in enumerate(table[:5]):
                if not row:
                    continue
                # Afficher seulement les cellules non vides
                cells_non_vides = [f"[{i}]:'{cell[:30]}'" for i, cell in enumerate(row) if cell and str(cell).strip()]
                if cells_non_vides:
                    print(f"      Ligne {row_idx}: {', '.join(cells_non_vides[:5])}")
