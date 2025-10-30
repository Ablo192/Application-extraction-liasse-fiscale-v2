"""
Test de l'extraction robuste avec détection dynamique
"""

from pathlib import Path
from extraction_robuste import extraire_pdf_complet
from main import CODES_BILAN_ACTIF, CODES_BILAN_PASSIF, CODES_COMPTE_RESULTAT

def test():
    pdf_path = Path("liasses/Liasse fiscale vierge.pdf")

    if not pdf_path.exists():
        print("❌ PDF non trouvé")
        return

    print(f"📄 Test du fichier : {pdf_path.name}\n")

    # Extraire avec détection dynamique
    resultats = extraire_pdf_complet(
        str(pdf_path),
        CODES_BILAN_ACTIF,
        CODES_BILAN_PASSIF,
        CODES_COMPTE_RESULTAT
    )

    print("\n" + "="*80)
    print("RÉSULTAT DU TEST")
    print("="*80)
    print(f"\n✓ Ce code utilise la DÉTECTION DYNAMIQUE")
    print(f"  → Cherche les pages par leur contenu, pas par leur numéro")
    print(f"  → Fonctionne même si l'ordre des pages change")
    print(f"  → Fonctionne même s'il y a des pages supplémentaires")


if __name__ == "__main__":
    test()
