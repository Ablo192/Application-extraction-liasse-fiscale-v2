"""
Test de l'extraction sur un FORMULAIRE VIERGE
Les cellules vides doivent retourner 0
"""

from pathlib import Path
from extraction_formulaire_vierge import extraire_formulaire_vierge
from main import CODES_BILAN_ACTIF, CODES_BILAN_PASSIF, CODES_COMPTE_RESULTAT


def test():
    pdf_path = Path("liasses/Liasse fiscale vierge.pdf")

    if not pdf_path.exists():
        print("❌ PDF non trouvé")
        return

    print(f"📄 Test du fichier : {pdf_path.name}\n")

    # Extraire avec mode formulaire vierge
    resultats = extraire_formulaire_vierge(
        str(pdf_path),
        CODES_BILAN_ACTIF,
        CODES_BILAN_PASSIF,
        CODES_COMPTE_RESULTAT
    )

    # Afficher des exemples de résultats
    print("\n" + "="*80)
    print("EXEMPLES DE RÉSULTATS EXTRAITS")
    print("="*80)

    if resultats.get('actif'):
        print("\n📊 BILAN ACTIF (quelques exemples) :")
        for i, (libelle, montant) in enumerate(resultats['actif'].items()):
            if i < 10:  # Afficher les 10 premiers
                print(f"  {libelle:50s} : {montant:>12.2f} €")

    if resultats.get('passif'):
        print("\n📊 BILAN PASSIF (quelques exemples) :")
        for i, (libelle, montant) in enumerate(resultats['passif'].items()):
            if i < 10:
                print(f"  {libelle:50s} : {montant:>12.2f} €")

    if resultats.get('cr'):
        print("\n📊 COMPTE DE RÉSULTAT (quelques exemples) :")
        for i, (libelle, montant) in enumerate(resultats['cr'].items()):
            if i < 10:
                print(f"  {libelle:50s} : {montant:>12.2f} €")

    print("\n" + "="*80)
    print("STATISTIQUES")
    print("="*80)
    print(f"\n✓ Total de lignes extraites :")
    print(f"  - ACTIF : {len(resultats.get('actif', {}))} lignes")
    print(f"  - PASSIF : {len(resultats.get('passif', {}))} lignes")
    print(f"  - COMPTE DE RÉSULTAT : {len(resultats.get('cr', {}))} lignes")
    print(f"\n💡 Toutes les cellules vides contiennent maintenant 0.00")


if __name__ == "__main__":
    test()
