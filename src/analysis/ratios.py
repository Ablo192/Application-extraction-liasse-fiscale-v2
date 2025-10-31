"""
Module de calcul des ratios financiers.

Ce module calcule l'ensemble des indicateurs financiers à partir des données
extraites des liasses fiscales.
"""

from src.config.codes_fiscaux import (
    CODES_BILAN_ACTIF,
    CODES_BILAN_PASSIF,
    CODES_COMPTE_RESULTAT
)


def calculer_ratios_financiers(donnees_par_annee):
    """Calcule les ratios financiers à partir des données extraites.

    Args:
        donnees_par_annee: Dict avec structure {
            'annee1': {'actif': [...], 'passif': [...], 'cr': [...], 'echeances': [...], 'affectation': [...]},
            'annee2': {...}
        }

    Returns:
        dict: {annee: {ratio: valeur}}
    """
    ratios_par_annee = {}

    for annee, donnees in donnees_par_annee.items():
        ratios = _calculer_ratios_annee(donnees)
        ratios_par_annee[annee] = ratios

    return ratios_par_annee


def _calculer_ratios_annee(donnees):
    """Calcule les ratios pour une seule année.

    Args:
        donnees: Dict avec keys 'actif', 'passif', 'cr', 'echeances', 'affectation'

    Returns:
        dict: {ratio_key: valeur}
    """
    ratios = {}

    # Fonction helper pour récupérer une valeur par code
    def get_valeur(section, code):
        """Récupère la valeur d'un code dans une section."""
        if section not in donnees:
            return 0

        for libelle, montant in donnees[section]:
            # Chercher dans les dictionnaires de codes
            if section == 'actif' and code in CODES_BILAN_ACTIF:
                if libelle == CODES_BILAN_ACTIF[code]:
                    return montant or 0
            elif section == 'passif' and code in CODES_BILAN_PASSIF:
                if libelle == CODES_BILAN_PASSIF[code]:
                    return montant or 0
            elif section == 'cr' and code in CODES_COMPTE_RESULTAT:
                if libelle == CODES_COMPTE_RESULTAT[code]:
                    return montant or 0
            elif section == 'echeances':
                if code == 'VA' and libelle == "Clients douteux ou litigieux":
                    return montant or 0
                elif code == 'VC' and libelle == "Groupe et associés (créances)":
                    return montant or 0
                elif code == 'VH' and libelle == "Annuité à venir":
                    return montant or 0
                elif code == 'VI' and libelle == "Groupe et associés (dettes)":
                    return montant or 0
            elif section == 'affectation':
                if code == 'ZE' and libelle == "Dividendes":
                    return montant or 0
                elif code == 'YQ' and libelle == "Engagements de crédit-bail mobilier":
                    return montant or 0
                elif code == 'YR' and libelle == "Engagements de crédit-bail immobilier":
                    return montant or 0
                elif code == 'YT' and libelle == "Sous-traitance":
                    return montant or 0
                elif code == 'YU' and libelle == "Personnel extérieur à l'entreprise":
                    return montant or 0
        return 0

    # ========================================
    # SECTION 1: ACTIVITÉ & RENTABILITÉ
    # ========================================

    ratios['duree_mois'] = 12  # TODO: Extraire du PDF

    # CA et production
    ca = get_valeur('cr', 'FL')
    ratios['ca'] = ca

    prod_stockee = get_valeur('cr', 'FM')
    prod_immobilisee = get_valeur('cr', 'FN')
    prod_stockee_immo = prod_stockee + prod_immobilisee
    ratios['prod_stockee_immo'] = prod_stockee_immo

    prod_globale = ca + prod_stockee_immo
    ratios['prod_globale'] = prod_globale

    # AACE et sous-traitance
    aace = get_valeur('cr', 'FW')
    ratios['aace'] = aace

    sous_traitance = get_valeur('affectation', 'YT')
    ratios['sous_traitance'] = sous_traitance
    ratios['pct_sous_traitance'] = (sous_traitance / prod_globale * 100) if prod_globale else 0

    prod_interne = prod_globale - sous_traitance
    ratios['prod_interne'] = prod_interne

    # Consommation de matières
    achats_matieres = get_valeur('cr', 'FU')
    var_stocks_matieres = get_valeur('cr', 'FV')
    conso_matieres = achats_matieres + var_stocks_matieres
    ratios['conso_matieres'] = conso_matieres
    ratios['pct_conso_matieres'] = (conso_matieres / prod_interne * 100) if prod_interne else 0

    # Charges de personnel
    salaires = get_valeur('cr', 'FY')
    charges_sociales = get_valeur('cr', 'FZ')
    charge_personnel = salaires + charges_sociales
    ratios['charge_personnel'] = charge_personnel

    interim = get_valeur('affectation', 'YU')
    ratios['interim'] = interim
    ratios['pct_charge_personnel'] = ((charge_personnel + interim) / prod_interne * 100) if prod_interne else 0

    # EBE
    resultat_exploitation = get_valeur('cr', 'GG')
    benefice_attribue = get_valeur('cr', 'GH')
    perte_supportee = get_valeur('cr', 'GI')
    dot_amort = get_valeur('cr', 'GA')
    dot_prov_immo = get_valeur('cr', 'GB')
    dot_prov_actif_circ = get_valeur('cr', 'GC')
    dot_prov_risques = get_valeur('cr', 'GD')
    dotations_exploitation = dot_amort + dot_prov_immo + dot_prov_actif_circ + dot_prov_risques
    reprises = get_valeur('cr', 'FP')
    transferts_charges = get_valeur('cr', 'A1')

    ebe = resultat_exploitation + benefice_attribue - perte_supportee + dotations_exploitation - reprises - transferts_charges
    ratios['ebe'] = ebe
    ratios['pct_ebe'] = (ebe / prod_interne * 100) if prod_interne else 0

    # Résultat d'exploitation
    ratios['resultat_exploitation'] = resultat_exploitation
    ratios['pct_resultat_exploitation'] = (resultat_exploitation / prod_interne * 100) if prod_interne else 0

    # Charges financières
    charges_financieres = get_valeur('cr', 'GU')
    ratios['charges_financieres'] = charges_financieres
    ratios['pct_charges_financieres'] = (charges_financieres / ebe * 100) if ebe else 0

    # Résultats
    resultat_exceptionnel = get_valeur('cr', 'HI')
    ratios['resultat_exceptionnel'] = resultat_exceptionnel

    resultat_net = get_valeur('cr', 'HN')
    ratios['resultat_net'] = resultat_net
    ratios['pct_resultat_net'] = (resultat_net / prod_interne * 100) if prod_interne else 0

    # CAF
    dot_financieres = get_valeur('cr', 'GQ')
    reprises_financieres = get_valeur('cr', 'GM')
    dot_exceptionnelles = get_valeur('cr', 'HG')
    reprises_exceptionnelles = get_valeur('cr', 'HC')
    charges_except_capital = get_valeur('cr', 'HF')
    produits_except_capital = get_valeur('cr', 'HB')
    cb_mobilier = get_valeur('affectation', 'YQ')
    cb_immobilier = get_valeur('affectation', 'YR')

    caf = (resultat_net + dotations_exploitation - reprises + transferts_charges +
           dot_financieres - reprises_financieres + dot_exceptionnelles - reprises_exceptionnelles +
           charges_except_capital - produits_except_capital + (0.8 * cb_mobilier) + (0.6 * cb_immobilier))
    ratios['caf'] = caf

    # ========================================
    # SECTION 2: BILAN
    # ========================================

    non_valeurs = get_valeur('actif', 'BJ')
    ratios['non_valeurs'] = non_valeurs

    total_bilan = get_valeur('actif', 'CO')
    ratios['total_bilan'] = total_bilan

    capitaux_propres = get_valeur('passif', 'DL')
    ratios['capitaux_propres'] = capitaux_propres

    ratios['solvabilite'] = (capitaux_propres / total_bilan * 100) if total_bilan else 0
    ratios['couverture_activite'] = (capitaux_propres / ca * 100) if ca else 0

    # Dette
    emprunts_obl_convert = get_valeur('passif', 'DS')
    autres_emprunts_obl = get_valeur('passif', 'DT')
    dette_mlt = get_valeur('passif', 'DU')
    concours_bancaires = get_valeur('passif', 'DU')

    dette_brute = emprunts_obl_convert + autres_emprunts_obl + dette_mlt + cb_mobilier + cb_immobilier + concours_bancaires
    ratios['dette_brute'] = dette_brute
    ratios['gearing_brut'] = (dette_brute / capitaux_propres) if capitaux_propres else 0
    ratios['leverage_brut'] = (dette_brute / ebe) if ebe else 0
    ratios['dont_mlt'] = dette_mlt
    ratios['dont_cb'] = cb_mobilier + cb_immobilier
    ratios['capacite_remboursement'] = (dette_brute / caf) if caf else 0

    # Annuités
    annuites = get_valeur('echeances', 'VH')
    ratios['annuites'] = annuites
    ratios['couverture_annuites'] = (caf / annuites) if annuites else 0

    # Dette nette
    disponibilites = get_valeur('actif', 'CF')
    vmp = get_valeur('actif', 'CD')
    dette_nette = dette_brute - disponibilites - vmp
    ratios['dette_nette'] = dette_nette
    ratios['gearing_net'] = (dette_nette / capitaux_propres) if capitaux_propres else 0
    ratios['leverage_net'] = (dette_nette / ebe) if ebe else 0

    # Comptes courants
    cc_actif = get_valeur('echeances', 'VC')
    ratios['cc_actif'] = cc_actif
    cc_passif = get_valeur('echeances', 'VI')
    ratios['cc_passif'] = cc_passif

    # Dividendes
    dividendes = get_valeur('affectation', 'ZE')
    ratios['dividendes'] = dividendes

    # ========================================
    # SECTION 3: CYCLE D'EXPLOITATION
    # ========================================

    actif_immo_net = get_valeur('actif', 'BJ')
    autres_fonds_propres = get_valeur('passif', 'DO')
    provisions = get_valeur('passif', 'DR')

    # FRNG
    frng = (capitaux_propres + autres_fonds_propres + provisions +
            emprunts_obl_convert + autres_emprunts_obl + dette_mlt - actif_immo_net)
    ratios['frng'] = frng

    # Stocks
    stocks_mp = get_valeur('actif', 'BL')
    stocks_prod_biens = get_valeur('actif', 'BN')
    stocks_prod_services = get_valeur('actif', 'BP')
    stocks_produits_finis = get_valeur('actif', 'BR')
    stocks_marchandises = get_valeur('actif', 'BT')
    stocks = stocks_mp + stocks_prod_biens + stocks_prod_services + stocks_produits_finis + stocks_marchandises
    ratios['stocks'] = stocks

    # Créances
    creances_clients = get_valeur('actif', 'BX')
    autres_creances = get_valeur('actif', 'BZ')
    creances = creances_clients + autres_creances
    ratios['creances'] = creances

    # Dettes
    charges_constatees_avance = get_valeur('actif', 'CH')
    dettes_fin_divers = get_valeur('passif', 'DV')
    avances_recues = get_valeur('passif', 'DW')
    dettes_fournisseurs = get_valeur('passif', 'DX')
    dettes_fiscales_sociales = get_valeur('passif', 'DY')
    dettes_immo = get_valeur('passif', 'DZ')
    autres_dettes = get_valeur('passif', 'EA')
    produits_constates_avance = get_valeur('passif', 'EB')

    # BFR
    bfr = (stocks + creances - cc_actif + charges_constatees_avance -
           dettes_fin_divers - avances_recues - dettes_fournisseurs -
           dettes_fiscales_sociales - dettes_immo - autres_dettes -
           cc_passif - produits_constates_avance)
    ratios['bfr'] = bfr

    # BFRE
    bfre = bfr - (cc_actif - cc_passif)
    ratios['bfre'] = bfre
    ratios['nb_jours_bfre'] = ((bfre / (1.2 * ca)) * 360) if ca else 0
    ratios['nb_jours_stocks'] = ((stocks / (1.2 * ca)) * 360) if ca else 0

    # Créances clients
    ratios['creances_clients'] = creances_clients
    en_cours_prod = stocks_prod_biens + stocks_prod_services
    ratios['nb_jours_creances'] = ((en_cours_prod + creances_clients - avances_recues - produits_constates_avance) /
                                   ((ca + prod_stockee) * 1.2) * 360) if (ca + prod_stockee) else 0

    # Créances douteuses
    creances_douteuses = get_valeur('echeances', 'VA')
    ratios['creances_douteuses'] = creances_douteuses
    ratios['pct_creances_douteuses'] = (creances_douteuses / creances_clients * 100) if creances_clients else 0
    ratios['pct_creances_douteuses_prov'] = 0  # À compléter si provision disponible

    # Dettes fournisseurs
    ratios['dettes_fournisseurs'] = dettes_fournisseurs
    if sous_traitance > 0:
        ratios['nb_jours_fournisseurs'] = ((dettes_fournisseurs / ((conso_matieres + sous_traitance) * 1.2)) * 360) if (conso_matieres + sous_traitance) else 0
    else:
        ratios['nb_jours_fournisseurs'] = ((dettes_fournisseurs / ((conso_matieres + aace) * 1.2)) * 360) if (conso_matieres + aace) else 0

    # Trésorerie nette
    tresorerie_nette = frng - bfr
    ratios['tresorerie_nette'] = tresorerie_nette

    return ratios
