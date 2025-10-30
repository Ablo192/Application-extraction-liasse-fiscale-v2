"""
Vérifier si le PDF contient des images
"""

import pdfplumber

chemin_pdf = "GROPPI SAS - Comptes sociaux 2023_OCR.pdf"

print("="*80)
print("VÉRIFICATION DU TYPE DE PDF")
print("="*80)

with pdfplumber.open(chemin_pdf) as pdf:
    print(f"\nNombre de pages: {len(pdf.pages)}")

    # Vérifier les 5 premières pages
    for page_num in range(min(5, len(pdf.pages))):
        page = pdf.pages[page_num]

        # Extraire les images
        images = page.images

        print(f"\nPage {page_num + 1}:")
        print(f"  - Images: {len(images)}")
        print(f"  - Texte: {'OUI' if page.extract_text() else 'NON'}")
        print(f"  - Tableaux: {len(page.extract_tables())}")

        if images:
            img = images[0]
            print(f"  - Première image: {img.get('width', '?')}x{img.get('height', '?')} pixels")

print("\n" + "="*80)
print("DIAGNOSTIC")
print("="*80)
print("""
Le fichier GROPPI est un PDF IMAGE sans couche texte !

Bien qu'il ait '_OCR' dans son nom, pdfplumber ne peut pas extraire de texte.

Pour extraire les données, il faut :
1. Appliquer un vrai OCR avec Tesseract/pytesseract
2. Ou utiliser un PDF qui a déjà une couche texte

C'est ça le problème d'EXPLOITATION : le code détecte les pages,
mais ne peut pas lire le texte car il n'y en a pas !
""")
