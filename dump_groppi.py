"""
Dump complet du contenu du fichier GROPPI
"""

import pdfplumber

chemin_pdf = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("="*80)
print("DUMP COMPLET DU FICHIER GROPPI (10 premières pages)")
print("="*80)

with pdfplumber.open(chemin_pdf) as pdf:
    print(f"\nNombre total de pages: {len(pdf.pages)}\n")

    # Afficher le contenu des 10 premières pages
    for page_num in range(min(10, len(pdf.pages))):
        page = pdf.pages[page_num]
        text = page.extract_text()

        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}")

        if text:
            print(text[:2000])  # Premiers 2000 caractères
        else:
            print("[PAGE VIDE]")

        # Tableaux
        tables = page.extract_tables()
        print(f"\n[Tableaux détectés: {len(tables)}]")

print("\n" + "="*80)
print("FIN DU DUMP")
print("="*80)
