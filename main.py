import pdfplumber
import openpyxl
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

# Codes à extraire du Bilan Actif (colonne NET uniquement)
CODES_BILAN_ACTIF = {
    # ACTIF IMMOBILISÉ
    "AC": "Frais d'établissement",
    "CQ": "Frais de développement",
    "AG": "Concessions, brevets et droits similaires",
    "AI": "Fonds commercial",
    "AK": "Autres immobilisations incorporelles",
    "AM": "Avances et acomptes sur immobilisations incorporelles",
    "AO": "Terrains",
    "AQ": "Constructions",
    "AS": "Installations techniques, matériel et outillage industriels",
    "AU": "Autres immobilisations corporelles",
    "AW": "Immobilisations en cours",
    "AY": "Avances et acomptes",
    "CT": "Participations évaluées selon la méthode de mise en équivalence",
    "CV": "Autres participations",
    "BC": "Créances rattachées à des participations",
    "BE": "Autres titres immobilisés",
    "BG": "Prêts",
    "BI": "Autres immobilisations financières",
    "BK": "TOTAL ACTIF IMMOBILISÉ",

    # ACTIF CIRCULANT
    "BM": "Matières premières, approvisionnements",
    "BO": "En cours de production de biens",
    "BQ": "En cours de production de services",
    "BS": "Produits intermédiaires et finis",
    "BU": "Marchandises",
    "BW": "Avances et acomptes versés sur commandes",
    "BY": "Clients et comptes rattachés",
    "CA": "Autres créances",
    "CC": "Capital souscrit et appelé, non versé",
    "CE": "Valeurs mobilières de placement",
    "CG": "Disponibilités",
    "CI": "Charges constatées d'avance",
    "CK": "TOTAL ACTIF CIRCULANT",

    # TOTAUX
    "CM": "Frais d'émission d'emprunt à étaler",
    "CO": "Primes de remboursement des obligations",
    "CW": "Écarts de conversion actif",
    "CN": "TOTAL GÉNÉRAL"
}


# ============================================
# FONCTION D'EXTRACTION
# ============================================

def extraire_bilan_actif(chemin_pdf):
    """
    Extrait les données du Bilan Actif d'une liasse fiscale.

    Args:
        chemin_pdf: Chemin vers le fichier PDF de la liasse fiscale

    Returns:
        Liste de tuples (libellé, montant)
    """
    resultats = []

    print(f"📄 Ouverture du fichier : {chemin_pdf}")

    with pdfplumber.open(chemin_pdf) as pdf:
        # Le Bilan Actif est sur la première page
        page = pdf.pages[0]

        # Extraire tout le texte de la page
        texte = page.extract_text()

        if not texte:
            print("❌ Erreur : Impossible d'extraire le texte du PDF")
            return resultats

        # Diviser le texte en lignes
        lignes = texte.split('\n')

        print(f"📊 Nombre de lignes trouvées : {len(lignes)}")
        print()

        # Parcourir chaque code dans l'ordre défini
        for code, libelle in CODES_BILAN_ACTIF.items():
            montant = 0  # Valeur par défaut si aucun montant trouvé
            code_trouve = False

            # Chercher le code dans toutes les lignes
            for ligne in lignes:
                if code in ligne:
                    code_trouve = True

                    # Essayer d'extraire le montant (dernière valeur numérique de la ligne)
                    mots = ligne.split()

                    # Chercher le dernier nombre dans la ligne
                    for mot in reversed(mots):
                        # Nettoyer le mot (enlever espaces, virgules)
                        mot_nettoye = mot.replace(' ', '').replace(',', '.')
                        try:
                            montant = float(mot_nettoye)
                            break
                        except ValueError:
                            continue

                    break  # Code trouvé, on passe au suivant

            # Ajouter le résultat (même si montant = 0)
            if code_trouve:
                resultats.append((libelle, montant))
                if montant == 0:
                    print(f"  ⚪ {code} - {libelle}: 0 (vide)")
                else:
                    print(f"  ✓ {code} - {libelle}: {montant}")
            else:
                # Code pas trouvé dans le PDF
                resultats.append((libelle, 0))
                print(f"  ⚠️  {code} - {libelle}: non trouvé dans le PDF")

    print(f"\n✅ Extraction terminée : {len(resultats)} lignes extraites")
    return resultats


# ============================================
# FONCTION D'EXPORT EXCEL
# ============================================

def creer_fichier_excel(donnees, nom_fichier):
    """
    Crée un fichier Excel avec les données extraites.

    Args:
        donnees: Liste de tuples (libellé, montant)
        nom_fichier: Nom du fichier Excel à créer
    """
    print(f"\n📊 Création du fichier Excel : {nom_fichier}")

    # Créer un nouveau classeur
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bilan Actif"

    # En-têtes
    ws['A1'] = "Libellé"
    ws['B1'] = "Montant Net"

    # Mettre en gras les en-têtes
    ws['A1'].font = openpyxl.styles.Font(bold=True)
    ws['B1'].font = openpyxl.styles.Font(bold=True)

    # Ajouter les données
    for i, (libelle, montant) in enumerate(donnees, start=2):
        ws[f'A{i}'] = libelle
        ws[f'B{i}'] = montant

        # Formater le montant avec 2 décimales
        ws[f'B{i}'].number_format = '#,##0.00'

        # Mettre en gras les lignes de totaux
        if "TOTAL" in libelle.upper():
            ws[f'A{i}'].font = openpyxl.styles.Font(bold=True)
            ws[f'B{i}'].font = openpyxl.styles.Font(bold=True)

    # Ajuster la largeur des colonnes
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 20

    # Sauvegarder
    wb.save(nom_fichier)
    print(f"✅ Fichier créé avec succès : {nom_fichier}")


# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    """
    Fonction principale du programme.
    """
    print("=" * 60)
    print("🚀 EXTRACTION LIASSE FISCALE - BILAN ACTIF")
    print("=" * 60)
    print()

    # Définir les chemins
    dossier_liasses = Path("liasses")
    dossier_resultats = Path("resultats")

    # Créer le dossier resultats s'il n'existe pas
    dossier_resultats.mkdir(exist_ok=True)

    # Chercher le premier fichier PDF dans le dossier liasses
    fichiers_pdf = list(dossier_liasses.glob("*.pdf"))

    if not fichiers_pdf:
        print("❌ ERREUR : Aucun fichier PDF trouvé dans le dossier 'liasses/'")
        print("   Veuillez placer au moins une liasse fiscale PDF dans ce dossier.")
        return

    # Prendre le premier PDF trouvé
    chemin_pdf = fichiers_pdf[0]
    print(f"📁 Fichier trouvé : {chemin_pdf.name}\n")

    # Extraire les données
    donnees = extraire_bilan_actif(chemin_pdf)

    if not donnees:
        print("❌ Aucune donnée extraite. Vérifiez le format du PDF.")
        return

    # Créer le fichier Excel
    nom_excel = dossier_resultats / f"extraction_{chemin_pdf.stem}.xlsx"
    creer_fichier_excel(donnees, nom_excel)

    print("\n" + "=" * 60)
    print("✅ TRAITEMENT TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()