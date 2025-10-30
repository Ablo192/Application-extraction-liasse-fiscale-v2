"""
Script de diagnostic pour analyser la structure des tableaux extraits
"""

import pdfplumber
from pathlib import Path

def analyser_structure_tableau(table, nom_tableau="Tableau"):
    """Analyse et affiche la structure d'un tableau"""
    print(f"\n{'='*80}")
    print(f"📋 ANALYSE DE : {nom_tableau}")
    print(f"{'='*80}\n")

    if not table:
        print("❌ Tableau vide")
        return

    print(f"📊 Nombre de lignes : {len(table)}")
    print(f"📊 Nombre de colonnes : {len(table[0]) if table else 0}")

    # Afficher les 10 premières lignes
    print(f"\n🔍 Premières lignes du tableau :\n")
    for i, row in enumerate(table[:15]):
        print(f"Ligne {i:2d}: {row}")

    print(f"\n{'='*80}\n")


def main():
    chemin_pdf = "/home/user/Application-extraction-liasse-fiscale-v2/liasses/Liasse fiscale vierge.pdf"

    print("\n🔍 DIAGNOSTIC DES TABLEAUX PDF")
    print("="*80)

    with pdfplumber.open(chemin_pdf) as pdf:
        print(f"\n📄 PDF ouvert : {Path(chemin_pdf).name}")
        print(f"📄 Nombre de pages : {len(pdf.pages)}")

        # Analyser les pages clés
        pages_a_analyser = {
            0: "Page 1 - Bilan Actif",
            1: "Page 2 - Bilan Passif",
            2: "Page 3 - Compte de résultat (partie 1)",
            3: "Page 4 - Compte de résultat (partie 2)"
        }

        for page_idx, nom_page in pages_a_analyser.items():
            if page_idx < len(pdf.pages):
                print(f"\n\n{'#'*80}")
                print(f"# {nom_page} (Page {page_idx + 1})")
                print(f"{'#'*80}")

                page = pdf.pages[page_idx]
                tables = page.extract_tables()

                print(f"\n✓ Nombre de tableaux trouvés : {len(tables)}")

                for table_idx, table in enumerate(tables):
                    analyser_structure_tableau(table, f"{nom_page} - Tableau {table_idx + 1}")


if __name__ == "__main__":
    main()
