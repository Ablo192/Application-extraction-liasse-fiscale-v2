import pdfplumber
from pathlib import Path


def diagnostiquer_pdf():
    """
    Affiche la structure complète du PDF pour comprendre comment l'extraire.
    """
    print("\n" + "=" * 80)
    print("🔍 DIAGNOSTIC DU PDF - STRUCTURE DÉTAILLÉE")
    print("=" * 80 + "\n")

    # Chercher le PDF
    dossier_liasses = Path("liasses")
    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("❌ Aucun PDF trouvé dans le dossier 'liasses/'")
        return

    chemin_pdf = fichiers_pdf[0]
    print(f"📄 Fichier analysé : {chemin_pdf.name}\n")

    with pdfplumber.open(chemin_pdf) as pdf:
        print(f"📊 Nombre total de pages : {len(pdf.pages)}\n")

        # Analyser la première page (Bilan Actif)
        page = pdf.pages[0]

        print("=" * 80)
        print("PAGE 1 - BILAN ACTIF")
        print("=" * 80 + "\n")

        # Extraire les tableaux
        tables = page.extract_tables()

        print(f"Nombre de tableaux détectés : {len(tables)}\n")

        if not tables:
            print("❌ Aucun tableau détecté !")
            print("\nEssai avec extract_text() :")
            print(page.extract_text()[:500])
            return

        # Analyser chaque tableau
        for table_idx, table in enumerate(tables):
            print(f"\n{'─' * 80}")
            print(f"TABLEAU {table_idx + 1}")
            print(f"{'─' * 80}\n")

            if not table:
                print("   (tableau vide)")
                continue

            nb_lignes = len(table)
            nb_colonnes = len(table[0]) if table else 0

            print(f"Nombre de lignes : {nb_lignes}")
            print(f"Nombre de colonnes : {nb_colonnes}\n")

            # Afficher les 15 premières lignes avec détail
            print("PREMIÈRES LIGNES (détail complet) :\n")

            for i, row in enumerate(table[:15]):
                print(f"Ligne {i + 1} ({len(row)} cellules) :")

                for j, cell in enumerate(row):
                    # Afficher la cellule avec son index
                    cell_display = repr(cell) if cell else "None"
                    print(f"   Col {j} : {cell_display}")

                print()  # Ligne vide entre chaque ligne du tableau

            print("\n" + "─" * 80)

            # Chercher spécifiquement les lignes avec certains codes
            print("\nRECHERCHE DE CODES SPÉCIFIQUES :\n")

            codes_test = ["CN", "BK", "CK", "AC", "AG"]

            for code in codes_test:
                print(f"Recherche du code '{code}' :")
                trouve = False

                for i, row in enumerate(table):
                    for j, cell in enumerate(row):
                        if cell and code in str(cell):
                            print(f"   ✓ Trouvé à la ligne {i + 1}, colonne {j}")
                            print(f"   Contenu complet de la ligne :")
                            for k, c in enumerate(row):
                                print(f"      Col {k}: {repr(c)}")
                            trouve = True
                            break
                    if trouve:
                        break

                if not trouve:
                    print(f"   ✗ Code '{code}' non trouvé dans ce tableau")

                print()


if __name__ == "__main__":
    diagnostiquer_pdf()