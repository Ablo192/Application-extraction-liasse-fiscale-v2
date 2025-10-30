"""
Script de test pour vérifier l'extraction par codes
"""

import pdfplumber

# Codes du Bilan Actif (quelques exemples)
CODES_TEST = ["AB", "AF", "AH", "AN", "AP", "BX", "CF"]

def _trouver_colonne_net(table):
    """Trouve l'index de la colonne 'Net' dans le tableau de l'actif."""
    print("\n🔍 Recherche de la colonne 'Net'...")
    for row_idx, row in enumerate(table[:10]):
        for idx, cell in enumerate(row):
            if cell and "Net" in str(cell):
                print(f"   ✓ 'Net' trouvé à la ligne {row_idx}, colonne {idx}")
                print(f"   ✓ Valeur de la cellule : {repr(cell)}")
                return idx
    print("   ❌ 'Net' non trouvé")
    return None

def test_extraction_actif():
    chemin_pdf = "/home/user/Application-extraction-liasse-fiscale-v2/liasses/Liasse fiscale vierge.pdf"

    print("="*80)
    print("TEST D'EXTRACTION DU BILAN ACTIF")
    print("="*80)

    with pdfplumber.open(chemin_pdf) as pdf:
        # Page 1 = Bilan Actif (index 0)
        tables_actif = pdf.pages[0].extract_tables()

        if not tables_actif:
            print("❌ Aucun tableau trouvé")
            return

        table_actif = tables_actif[0]
        print(f"\n✓ Tableau extrait : {len(table_actif)} lignes, {len(table_actif[0])} colonnes")

        # Trouver la colonne Net
        idx_net = _trouver_colonne_net(table_actif)

        if idx_net is None:
            print("\n❌ Impossible de continuer sans la colonne Net")
            return

        print(f"\n{'='*80}")
        print(f"RECHERCHE DES CODES")
        print(f"{'='*80}\n")

        codes_trouves = {}

        for row_idx, row in enumerate(table_actif):
            if not row:
                continue

            for cell_idx, cell in enumerate(row):
                if not cell:
                    continue

                cell_text = str(cell).strip().upper()

                # Chercher les codes de test
                if cell_text in CODES_TEST:
                    print(f"\n📍 Code '{cell_text}' trouvé :")
                    print(f"   - Ligne {row_idx}, Colonne {cell_idx}")
                    print(f"   - Contenu de la ligne : {row}")

                    # Récupérer le montant Net
                    if idx_net < len(row):
                        montant_net = row[idx_net]
                        print(f"   - Valeur dans colonne Net (index {idx_net}) : {repr(montant_net)}")
                        codes_trouves[cell_text] = montant_net
                    else:
                        print(f"   ⚠️ La ligne n'a pas assez de colonnes (seulement {len(row)})")

                    # Montrer aussi les valeurs voisines
                    if cell_idx + 1 < len(row):
                        print(f"   - Valeur à droite (index {cell_idx + 1}) : {repr(row[cell_idx + 1])}")

        print(f"\n{'='*80}")
        print(f"RÉSUMÉ")
        print(f"{'='*80}\n")
        print(f"Codes trouvés : {len(codes_trouves)}")
        for code, montant in codes_trouves.items():
            print(f"  - {code} : {repr(montant)}")

if __name__ == "__main__":
    test_extraction_actif()
