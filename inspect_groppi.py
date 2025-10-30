"""
Inspection du contenu brut du fichier GROPPI
"""

import pdfplumber

chemin_pdf = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("="*80)
print("INSPECTION DU CONTENU DU FICHIER GROPPI")
print("="*80)

with pdfplumber.open(chemin_pdf) as pdf:
    print(f"\nNombre total de pages: {len(pdf.pages)}\n")

    # Afficher le contenu des 20 premières pages
    for page_num in range(min(20, len(pdf.pages))):
        page = pdf.pages[page_num]
        text = page.extract_text()

        # Chercher des mots-clés intéressants
        mots_cles = ["ACTIF", "PASSIF", "BILAN", "COMPTE", "RÉSULTAT",
                     "2050", "2051", "2052", "2053", "LIASSE"]

        mots_trouves = [mot for mot in mots_cles if mot in text]

        if mots_trouves:
            print(f"\n{'='*80}")
            print(f"PAGE {page_num + 1}")
            print(f"Mots-clés trouvés: {', '.join(mots_trouves)}")
            print(f"{'='*80}")

            # Afficher les 30 premières lignes du texte
            lignes = text.split('\n')[:30]
            for i, ligne in enumerate(lignes, 1):
                if ligne.strip():
                    print(f"{i:3d} | {ligne}")

            # Analyser les tableaux
            tables = page.extract_tables()
            print(f"\n📊 Tableaux: {len(tables)}")
            if tables:
                print(f"   - Premier tableau: {len(tables[0])} lignes x {len(tables[0][0]) if tables[0] else 0} cols")

print("\n" + "="*80)
print("FIN DE L'INSPECTION")
print("="*80)
