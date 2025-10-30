"""
Scanner toutes les pages pour trouver celles avec du contenu
"""

import pdfplumber

chemin_pdf = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("="*80)
print("SCAN DE TOUTES LES PAGES DU FICHIER GROPPI")
print("="*80)

with pdfplumber.open(chemin_pdf) as pdf:
    print(f"\nNombre total de pages: {len(pdf.pages)}\n")

    pages_avec_contenu = []

    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        tables = page.extract_tables()

        if text and text.strip():
            pages_avec_contenu.append((page_num, len(text), len(tables)))
            print(f"Page {page_num:3d}: {len(text):6d} caractères, {len(tables)} tableaux")

    print(f"\n{'='*80}")
    print(f"RÉSUMÉ")
    print(f"{'='*80}")
    print(f"Pages avec contenu: {len(pages_avec_contenu)} / {len(pdf.pages)}")

    if pages_avec_contenu:
        print(f"\nAffichage des 3 premières pages avec contenu:")
        for page_num, text_len, num_tables in pages_avec_contenu[:3]:
            print(f"\n{'='*80}")
            print(f"PAGE {page_num}")
            print(f"{'='*80}")
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            print(text[:1500])

print("\n" + "="*80)
print("FIN DU SCAN")
print("="*80)
