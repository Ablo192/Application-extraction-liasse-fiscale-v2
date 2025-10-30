"""
Script de test pour l'approche analytique
==========================================

Ce script teste la nouvelle approche analytique sur un PDF.
"""

from pathlib import Path
from extraction_analytique import DetecteurTableaux, AnalyseurStructure
from main import CODES_BILAN_ACTIF, CODES_BILAN_PASSIF, CODES_COMPTE_RESULTAT


def test_detection():
    """Test de la phase 1 : Détection des tableaux"""
    print("\n" + "="*80)
    print("TEST DE LA PHASE 1 : DÉTECTION DES TABLEAUX")
    print("="*80 + "\n")

    # Chercher un PDF de test
    dossier_liasses = Path("liasses")
    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("❌ Aucun PDF trouvé dans le dossier 'liasses/'")
        return None

    pdf_test = fichiers_pdf[0]
    print(f"📄 Fichier de test : {pdf_test.name}\n")

    # Détecter les tableaux
    tableaux = DetecteurTableaux.detecter_tous_tableaux(str(pdf_test))

    print(f"\n✓ {len(tableaux)} tableau(x) détecté(s)\n")

    for idx, tableau in enumerate(tableaux):
        print(f"{idx+1}. Type: {tableau.type_tableau.value}")
        print(f"   Page: {tableau.page_index + 1}")
        print(f"   Lignes: {len(tableau.table_data)}")
        print(f"   Colonnes: {len(tableau.table_data[0]) if tableau.table_data else 0}")
        print()

    return tableaux


def test_analyse(tableaux):
    """Test de la phase 2 : Analyse de la structure"""
    if not tableaux:
        print("❌ Aucun tableau à analyser")
        return

    print("\n" + "="*80)
    print("TEST DE LA PHASE 2 : ANALYSE DE LA STRUCTURE")
    print("="*80 + "\n")

    for tableau in tableaux:
        print(f"\n→ Analyse du tableau '{tableau.type_tableau.value}'...")
        print("-" * 60)

        # Analyser la structure
        colonnes = AnalyseurStructure.analyser_en_tetes(tableau.table_data)
        tableau.colonnes = colonnes

        if colonnes:
            print(f"\nColonnes identifiées : {len(colonnes)}\n")
            for col in colonnes:
                print(f"  Index {col.index:2d} | {col.type_colonne:20s} | '{col.en_tete}' | Confiance: {col.confiance:.0%}")
        else:
            print("⚠️ Aucune colonne identifiée")

        # Identifier les colonnes de montants
        colonnes_montants = AnalyseurStructure.identifier_colonnes_montants(colonnes)
        if colonnes_montants:
            print(f"\nColonnes de montants identifiées : {len(colonnes_montants)}")
            for idx, col in enumerate(colonnes_montants, 1):
                print(f"  {idx}. Index {col.index} | '{col.en_tete}' ({col.type_colonne})")
        else:
            print("\n⚠️ Aucune colonne de montant identifiée")

        print()


def test_complet():
    """Test complet de l'approche analytique"""
    print("\n" + "="*80)
    print("🧪 TEST COMPLET DE L'APPROCHE ANALYTIQUE")
    print("="*80)

    # Phase 1
    tableaux = test_detection()

    if not tableaux:
        return

    # Phase 2
    test_analyse(tableaux)

    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DU TEST")
    print("="*80 + "\n")

    types_detectes = set(t.type_tableau.value for t in tableaux)
    print(f"Types de tableaux détectés : {', '.join(types_detectes)}")
    print(f"Nombre total de tableaux : {len(tableaux)}")

    tableaux_avec_colonnes = sum(1 for t in tableaux if hasattr(t, 'colonnes') and t.colonnes)
    print(f"Tableaux analysés : {tableaux_avec_colonnes}/{len(tableaux)}")

    print("\n" + "="*80)
    print("✓ TEST TERMINÉ")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_complet()
