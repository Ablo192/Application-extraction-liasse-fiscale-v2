"""
Script de test pour la nouvelle extraction simple
"""

from pathlib import Path
from extraction_simple import extraire_pdf_complet
from main import CODES_BILAN_ACTIF, CODES_BILAN_PASSIF, CODES_COMPTE_RESULTAT

def test_extraction():
    """Test de l'extraction simple"""

    # Chercher le PDF
    pdf_path = Path("liasses/Liasse fiscale vierge.pdf")

    if not pdf_path.exists():
        print("❌ PDF non trouvé")
        return

    print(f"📄 Test du fichier : {pdf_path.name}\n")

    # Extraire
    resultats = extraire_pdf_complet(
        str(pdf_path),
        CODES_BILAN_ACTIF,
        CODES_BILAN_PASSIF,
        CODES_COMPTE_RESULTAT
    )

    # Afficher quelques valeurs pour vérification
    print("\n" + "="*80)
    print("ÉCHANTILLON DES VALEURS EXTRAITES")
    print("="*80)

    print("\n--- ACTIF (premiers 10) ---")
    for i, (libelle, montant) in enumerate(list(resultats['actif'].items())[:10]):
        print(f"  {libelle}: {montant:,.2f}")

    print("\n--- PASSIF (premiers 10) ---")
    for i, (libelle, montant) in enumerate(list(resultats['passif'].items())[:10]):
        print(f"  {libelle}: {montant:,.2f}")

    print("\n--- COMPTE DE RÉSULTAT (premiers 10) ---")
    for i, (libelle, montant) in enumerate(list(resultats['cr'].items())[:10]):
        print(f"  {libelle}: {montant:,.2f}")


if __name__ == "__main__":
    test_extraction()
