"""
Configuration des codes fiscaux officiels pour l'extraction des liasses fiscales.

Ce module contient tous les dictionnaires de codes officiels utilisés dans les formulaires
fiscaux français (2050, 2051, 2052, 2057, 2058).
"""

# ============================================
# BILAN ACTIF (Formulaire 2050)
# ============================================

CODES_BILAN_ACTIF = {
    "AB": "Frais d'établissement",
    "CX": "Frais de développement",
    "AF": "Concessions, brevets et droits similaires",
    "AH": "Fonds commercial",
    "AJ": "Autres immobilisations incorporelles",
    "AL": "Avances et acomptes sur immobilisations incorporelles",
    "AN": "Terrains",
    "AP": "Constructions",
    "AR": "Installations techniques, matériel et outillage industriels",
    "AT": "Autres immobilisations corporelles",
    "AV": "Immobilisations en cours",
    "AX": "Avances et acomptes",
    "CS": "Participations évaluées selon la méthode de mise en équivalence",
    "CU": "Autres participations",
    "BB": "Créances rattachées à des participations",
    "BD": "Autres titres immobilisés",
    "BF": "Prêts",
    "BH": "Autres immobilisations financières",
    "BJ": "TOTAL ACTIF IMMOBILISÉ",
    "BL": "Matières premières, approvisionnements",
    "BN": "En cours de production de biens",
    "BP": "En cours de production de services",
    "BR": "Produits intermédiaires et finis",
    "BT": "Marchandises",
    "BV": "Avances et acomptes versés sur commandes",
    "BX": "Clients et comptes rattachés",
    "BZ": "Autres créances",
    "CB": "Capital souscrit et appelé, non versé",
    "CD": "Valeurs mobilières de placement",
    "CF": "Disponibilités",
    "CH": "Charges constatées d'avance",
    "CJ": "TOTAL ACTIF CIRCULANT",
    "CM": "Frais d'émission d'emprunt à étaler",
    "CO": "TOTAL GÉNÉRAL",
    "CW": "Écarts de conversion actif"
}

# ============================================
# BILAN PASSIF (Formulaire 2051)
# ============================================

CODES_BILAN_PASSIF = {
    "DA": "Capital social ou individuel",
    "DB": "Primes d'émission, de fusion, d'apport…",
    "DC": "Écarts de réévaluation",
    "DD": "Réserve légale",
    "DE": "Réserves statutaires ou contractuelles",
    "DF": "Réserves réglementées",
    "DG": "Autres réserves",
    "DH": "Report à nouveau",
    "DI": "RÉSULTAT DE L'EXERCICE (bénéfice ou perte)",
    "DJ": "Subventions d'investissement",
    "DK": "Provisions réglementées",
    "DL": "TOTAL (I)",
    "DM": "Produit des émissions de titres participatifs",
    "DN": "Avances conditionnées",
    "DO": "TOTAL (II)",
    "DP": "Provisions pour risques",
    "DQ": "Provisions pour charges",
    "DR": "TOTAL (III)",
    "DS": "Emprunts obligatoires convertibles",
    "DT": "Autres emprunts obligataires",
    "DU": "Emprunts et dettes auprès des établissements de crédit",
    "DV": "Emprunts et dettes financières divers",
    "DW": "Avances et acomptes reçus sur commandes en cours",
    "DX": "Dettes fournisseurs et comptes rattachés",
    "DY": "Dettes fiscales et sociales",
    "DZ": "Dettes sur immobilisations et comptes rattachés",
    "EA": "Autres dettes",
    "EB": "Produits constatés d'avance",
    "EC": "TOTAL (IV)",
    "ED": "Écart de conversion passif",
    "EE": "TOTAL GENERAL (I à V)"
}

# ============================================
# COMPTE DE RÉSULTAT (Formulaire 2052)
# ============================================

CODES_COMPTE_RESULTAT = {
    # PRODUITS D'EXPLOITATION
    "FA": "Ventes de marchandises (France)",
    "FB": "Ventes de marchandises (Exportations)",
    "FC": "Ventes de marchandises (TOTAL)",
    "FD": "Production vendue - Biens (France)",
    "FE": "Production vendue - Biens (Exportations)",
    "FF": "Production vendue - Biens (TOTAL)",
    "FG": "Production vendue - Services (France)",
    "FH": "Production vendue - Services (Exportations)",
    "FI": "Production vendue - Services (TOTAL)",
    "FJ": "Chiffres d'affaires nets (France)",
    "FK": "Chiffres d'affaires nets (Exportations)",
    "FL": "Chiffres d'affaires nets (TOTAL)",
    "FM": "Production stockée",
    "FN": "Production immobilisée",
    "FO": "Subventions d'exploitation",
    "FP": "Reprises sur amortissements et provisions, transferts de charges",
    "FQ": "Autres produits",
    "FR": "TOTAL DES PRODUITS D'EXPLOITATION (I)",

    # CHARGES D'EXPLOITATION
    "FS": "Achats de marchandises (y compris droits de douane)",
    "FT": "Variation de stocks (marchandises)",
    "FU": "Achats de matières premières et autres approvisionnements",
    "FV": "Variation de stocks (matières premières et approvisionnements)",
    "FW": "Autres achats et charges externes",
    "FX": "Impôts, taxes et versements assimilés",
    "FY": "Salaires et traitements",
    "FZ": "Charges sociales",
    "GA": "Dotations aux amortissements (sur immobilisations)",
    "GB": "Dotations aux provisions (sur immobilisations)",
    "GC": "Dotations aux amortissements (sur actif circulant)",
    "GD": "Dotations aux provisions (sur actif circulant)",
    "GE": "Autres charges",
    "GF": "TOTAL DES CHARGES D'EXPLOITATION (II)",

    # RÉSULTAT D'EXPLOITATION
    "GG": "RÉSULTAT D'EXPLOITATION (I - II)",

    # OPÉRATIONS EN COMMUN
    "GH": "Bénéfice attribué ou perte transférée (III)",
    "GI": "Perte supportée ou bénéfice transféré (IV)",

    # PRODUITS FINANCIERS
    "GJ": "Produits financiers de participations",
    "GK": "Produits des autres valeurs mobilières et créances de l'actif immobilisé",
    "GL": "Autres intérêts et produits assimilés",
    "GM": "Reprises sur provisions et transferts de charges",
    "GN": "Différences positives de change",
    "GO": "Produits nets sur cessions de valeurs mobilières de placement",
    "GP": "TOTAL DES PRODUITS FINANCIERS (V)",

    # CHARGES FINANCIÈRES
    "GQ": "Dotations financières aux amortissements et provisions",
    "GR": "Intérêts et charges assimilées",
    "GS": "Différences négatives de change",
    "GT": "Charges nettes sur cessions de valeurs mobilières de placement",
    "GU": "TOTAL DES CHARGES FINANCIÈRES (VI)",

    # RÉSULTAT FINANCIER
    "GV": "RÉSULTAT FINANCIER (V - VI)",

    # RÉSULTAT COURANT
    "GW": "RÉSULTAT COURANT AVANT IMPÔTS (I - II + III - IV + V - VI)",

    # PRODUITS EXCEPTIONNELS
    "HA": "Produits exceptionnels sur opérations de gestion",
    "HB": "Produits exceptionnels sur opérations en capital",
    "HC": "Reprises sur provisions et transferts de charges",
    "HD": "Total des produits exceptionnels (VII)",

    # CHARGES EXCEPTIONNELLES
    "HE": "Charges exceptionnelles sur opérations de gestion",
    "HF": "Charges exceptionnelles sur opérations en capital",
    "HG": "Dotations exceptionnelles aux amortissements et provisions",
    "HH": "Total des charges exceptionnelles (VIII)",

    # RÉSULTAT EXCEPTIONNEL
    "HI": "RÉSULTAT EXCEPTIONNEL (VII - VIII)",

    # PARTICIPATION ET IMPÔTS
    "HJ": "Participation des salariés aux résultats de l'entreprise (IX)",
    "HK": "Impôts sur les bénéfices (X)",

    # TOTAUX
    "HL": "TOTAL DES PRODUITS (I + III + V + VII)",
    "HM": "TOTAL DES CHARGES (II + IV + VI + VIII + IX + X)",

    # RÉSULTAT NET
    "HN": "BÉNÉFICE OU PERTE (Total des produits - Total des charges)",

    # RENVOIS DEMANDÉS
    "HP": "Crédit-bail mobilier",
    "HQ": "Crédit-bail immobilier",
    "A1": "Transfert de charges"
}

# ============================================
# ÉTAT DES ÉCHÉANCES (Formulaire 2057-SD)
# ============================================

CODES_ETAT_ECHEANCES_CREANCES = {
    "VA": "Clients douteux ou litigieux",
    "VC": "Groupe et associés (créances)"
}

CODES_ETAT_ECHEANCES_DETTES = {
    "VH": "Annuité à venir",
    "VI": "Groupe et associés (dettes)"
}

# ============================================
# AFFECTATION DU RÉSULTAT (Formulaire 2058-C-SD)
# ============================================

CODES_AFFECTATION_RESULTAT = {
    "ZE": "Dividendes"
}

# ============================================
# RENSEIGNEMENTS DIVERS (Formulaire 2058-C-SD)
# ============================================

CODES_RENSEIGNEMENTS_DIVERS = {
    "YQ": "Engagements de crédit-bail mobilier",
    "YR": "Engagements de crédit-bail immobilier",
    "YT": "Sous-traitance",
    "YU": "Personnel extérieur à l'entreprise"
}

# ============================================
# SEUILS DE RÉUSSITE POUR L'EXTRACTION
# ============================================

SEUIL_REUSSITE_CODES_ACTIF = 5
SEUIL_REUSSITE_CODES_PASSIF = 5
SEUIL_REUSSITE_CODES_COMPTE_RESULTAT = 10
SEUIL_REUSSITE_CODES_ETAT_ECHEANCES = 3
SEUIL_REUSSITE_CODES_AFFECTATION_RESULTAT = 4
