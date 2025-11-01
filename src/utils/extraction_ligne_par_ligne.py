"""
Extraction ligne par ligne pour gérer les décalages de colonnes.

Cette approche analyse chaque ligne individuellement au lieu d'analyser
le tableau globalement, ce qui est plus robuste face aux décalages de colonnes
causés par une extraction PDF défaillante.
"""

from src.utils.text_processing import nettoyer_montant, normaliser_texte


def detecter_colonnes_numeriques_ligne(row):
    """Détecte les colonnes numériques d'UNE SEULE ligne.

    Args:
        row: Une ligne du tableau (liste de cellules)

    Returns:
        list: Indices des colonnes contenant des nombres dans cette ligne
    """
    colonnes_num = []

    for col_idx, cell in enumerate(row):
        if not cell:
            continue

        cell_text = str(cell).strip()
        cell_clean = cell_text.replace(' ', '').replace(',', '.').replace('(', '-').replace(')', '')

        try:
            float(cell_clean)
            colonnes_num.append(col_idx)
        except ValueError:
            pass

    return colonnes_num


def obtenir_montant_ligne(row, position):
    """Obtient le montant à la Nème position numérique d'une ligne.

    Args:
        row: Une ligne du tableau
        position: Position de la colonne numérique (1=1ère, 2=2ème, 3=3ème)

    Returns:
        float: Montant nettoyé, ou None si pas trouvé
    """
    colonnes_num = detecter_colonnes_numeriques_ligne(row)

    if not colonnes_num or position < 1 or position > len(colonnes_num):
        return None

    idx_montant = colonnes_num[position - 1]
    montant_text = row[idx_montant]

    return nettoyer_montant(montant_text)


def extraire_par_libelles_ligne_par_ligne(table, libelles_dict, position_colonne=3, debug=False):
    """Extrait les données en cherchant les libellés ligne par ligne.

    Pour chaque ligne:
    1. Cherche si un libellé connu est présent
    2. Détecte les colonnes numériques DE CETTE LIGNE
    3. Prend la Nème colonne numérique de cette ligne
    4. Extrait le montant

    Args:
        table: Tableau extrait du PDF
        libelles_dict: Dict {libellé_original: libellé_à_chercher}
        position_colonne: Position de la colonne numérique (1, 2, 3...)
        debug: Si True, affiche des infos de débogage

    Returns:
        dict: {libellé_original: montant}
    """
    # Normaliser les libellés pour la recherche
    libelles_normalises = {normaliser_texte(lib): lib for lib in libelles_dict.keys()}

    resultats = {}

    if debug:
        print(f"\n🔍 Extraction ligne par ligne (position colonne: {position_colonne})")
        print(f"   Libellés à chercher: {len(libelles_dict)}")

    for row_idx, row in enumerate(table):
        if not row:
            continue

        # Chercher un libellé dans cette ligne
        libelle_trouve = None
        for cell in row:
            if not cell:
                continue

            cell_normalise = normaliser_texte(str(cell).strip())

            # Correspondance exacte
            if cell_normalise in libelles_normalises:
                libelle_trouve = libelles_normalises[cell_normalise]
                break

            # Correspondance partielle (le libellé contient la cellule ou inverse)
            for lib_norm, lib_orig in libelles_normalises.items():
                if cell_normalise in lib_norm or lib_norm in cell_normalise:
                    if len(cell_normalise) > 5:  # Éviter les faux positifs sur des mots courts
                        libelle_trouve = lib_orig
                        break

        if libelle_trouve and libelle_trouve not in resultats:
            # Analyser les colonnes numériques DE CETTE LIGNE
            colonnes_num = detecter_colonnes_numeriques_ligne(row)
            montant = obtenir_montant_ligne(row, position_colonne)

            resultats[libelle_trouve] = montant if montant is not None else 0.0

            if debug:
                print(f"\n   Ligne {row_idx}:")
                print(f"      Libellé: {libelle_trouve}")
                print(f"      Colonnes numériques: {colonnes_num}")
                if colonnes_num and position_colonne <= len(colonnes_num):
                    idx_utilise = colonnes_num[position_colonne - 1]
                    print(f"      Colonne utilisée: index {idx_utilise} (position {position_colonne})")
                    print(f"      Montant: {montant}")
                else:
                    print(f"      ⚠️ Pas assez de colonnes numériques (besoin de {position_colonne}, trouvé {len(colonnes_num)})")

    if debug:
        print(f"\n   📊 Résumé: {len(resultats)}/{len(libelles_dict)} libellés trouvés")
        print(f"   💰 Montants non-nuls: {len([m for m in resultats.values() if m != 0])}")

    # Ajouter les libellés manquants avec montant 0
    for libelle in libelles_dict.keys():
        if libelle not in resultats:
            resultats[libelle] = 0.0

    return resultats


def extraire_actif_ligne_par_ligne(table, libelles_actif, debug=False):
    """Extrait le Bilan Actif ligne par ligne (3ème colonne = Net).

    Args:
        table: Tableau extrait du PDF
        libelles_actif: Dict des libellés de l'actif
        debug: Mode debug

    Returns:
        list: Liste de tuples (libellé, montant)
    """
    print("\n📊 Extraction ACTIF ligne par ligne (3ème colonne numérique)")

    resultats_dict = extraire_par_libelles_ligne_par_ligne(
        table,
        libelles_actif,
        position_colonne=3,
        debug=debug
    )

    # Convertir en liste de tuples dans l'ordre des libellés
    return [(libelle, resultats_dict.get(libelle, 0)) for libelle in libelles_actif.keys()]


def extraire_passif_ligne_par_ligne(table, libelles_passif, debug=False):
    """Extrait le Bilan Passif ligne par ligne (1ère colonne = Exercice N).

    Args:
        table: Tableau extrait du PDF
        libelles_passif: Dict des libellés du passif
        debug: Mode debug

    Returns:
        list: Liste de tuples (libellé, montant)
    """
    print("\n📊 Extraction PASSIF ligne par ligne (1ère colonne numérique)")

    resultats_dict = extraire_par_libelles_ligne_par_ligne(
        table,
        libelles_passif,
        position_colonne=1,
        debug=debug
    )

    # Convertir en liste de tuples dans l'ordre des libellés
    return [(libelle, resultats_dict.get(libelle, 0)) for libelle in libelles_passif.keys()]


def extraire_cr_ligne_par_ligne(table, libelles_cr, debug=False):
    """Extrait le Compte de Résultat ligne par ligne (1ère colonne).

    Args:
        table: Tableau extrait du PDF
        libelles_cr: Dict des libellés du CR
        debug: Mode debug

    Returns:
        list: Liste de tuples (libellé, montant)
    """
    print("\n📊 Extraction COMPTE DE RÉSULTAT ligne par ligne (1ère colonne numérique)")

    resultats_dict = extraire_par_libelles_ligne_par_ligne(
        table,
        libelles_cr,
        position_colonne=1,
        debug=debug
    )

    # Convertir en liste de tuples dans l'ordre des libellés
    return [(libelle, resultats_dict.get(libelle, 0)) for libelle in libelles_cr.keys()]
