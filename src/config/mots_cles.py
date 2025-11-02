"""
Configuration des mots-clés pour l'extraction par libellés des liasses fiscales.

Ce module contient les dictionnaires de mots-clés utilisés comme méthode de fallback
lorsque l'extraction par codes officiels échoue.
"""

# ============================================
# MOTS-CLÉS POUR LE BILAN ACTIF
# ============================================

MOTS_CLES_BILAN_ACTIF = {
    "AB": ["frais d'établissement", "frais etablissement"],
    "CX": ["frais de développement", "frais developpement"],
    "AF": ["concessions, brevets", "concessions brevets", "brevets", "licences"],
    "AH": ["fonds commercial", "fonds de commerce", "goodwill"],
    "AJ": ["autres immobilisations incorporelles", "autres immo incorporelles"],
    "AN": ["terrains"],
    "AP": ["constructions"],
    "AR": ["installations techniques", "matériel et outillage", "installations matériel outillage"],
    "AT": ["autres immobilisations corporelles", "autres immo corporelles"],
    "AV": ["immobilisations en cours", "immo en cours"],
    "BB": ["créances rattachées à des participations", "creances participations"],
    "BD": ["autres titres immobilisés", "titres immobilisés"],
    "BF": ["prêts"],
    "BH": ["autres immobilisations financières", "autres immo financières"],
    "BJ": ["total actif immobilisé", "total immo", "total immobilisations"],
    "BL": ["matières premières", "matieres premieres", "approvisionnements"],
    "BN": ["en cours de production de biens", "en-cours biens"],
    "BP": ["en cours de production de services", "en-cours services"],
    "BR": ["produits intermédiaires et finis", "produits finis"],
    "BT": ["marchandises"],
    "BX": ["clients et comptes rattachés", "creances clients", "clients"],
    "BZ": ["autres créances", "autres creances"],
    "CD": ["valeurs mobilières de placement", "vmp", "valeurs mobilieres"],
    "CF": ["disponibilités", "disponibilites", "trésorerie", "tresorerie"],
    "CH": ["charges constatées d'avance", "charges constatees avance"],
    "CJ": ["total actif circulant", "total circulant"],
    "CO": ["total général", "total general", "total bilan", "total actif"],
}

# ============================================
# MOTS-CLÉS POUR LE BILAN PASSIF
# ============================================

MOTS_CLES_BILAN_PASSIF = {
    "DA": ["capital social", "capital individuel"],
    "DB": ["primes d'émission", "primes emission", "primes de fusion"],
    "DD": ["réserve légale", "reserve legale"],
    "DE": ["réserves statutaires", "reserves statutaires"],
    "DF": ["réserves réglementées", "reserves reglementees"],
    "DG": ["autres réserves", "autres reserves"],
    "DH": ["report à nouveau", "report nouveau"],
    "DI": ["résultat de l'exercice", "resultat exercice", "bénéfice", "benefice", "perte"],
    "DJ": ["subventions d'investissement", "subventions investissement"],
    "DK": ["provisions réglementées", "provisions reglementees"],
    "DL": ["total capitaux propres", "total capitaux", "capitaux propres"],
    "DO": ["total autres fonds propres", "autres fonds propres"],
    "DP": ["provisions pour risques", "provisions risques"],
    "DQ": ["provisions pour charges", "provisions charges"],
    "DR": ["total provisions", "total provisions risques charges"],
    "DS": ["emprunts obligataires convertibles", "obligations convertibles"],
    "DT": ["autres emprunts obligataires", "emprunts obligataires"],
    "DU": ["emprunts et dettes auprès des établissements de crédit", "emprunts etablissements credit", "dettes bancaires"],
    "DV": ["emprunts et dettes financières divers", "dettes financieres divers"],
    "DW": ["avances et acomptes reçus", "avances recues", "acomptes recus"],
    "DX": ["dettes fournisseurs", "fournisseurs et comptes rattachés", "fournisseurs"],
    "DY": ["dettes fiscales et sociales", "dettes fiscales sociales"],
    "DZ": ["dettes sur immobilisations", "dettes immo"],
    "EA": ["autres dettes"],
    "EB": ["produits constatés d'avance", "produits constates avance"],
    "EC": ["total dettes"],
    "EE": ["total général", "total general", "total passif"],
}

# ============================================
# MOTS-CLÉS POUR LE COMPTE DE RÉSULTAT
# ============================================

MOTS_CLES_COMPTE_RESULTAT = {
    "FL": ["chiffre d'affaires nets", "chiffre affaires nets", "ca nets", "ca total", "chiffre d'affaires"],
    "FM": ["production stockée", "production stockee", "variation stocks production"],
    "FN": ["production immobilisée", "production immobilisee"],
    "FO": ["subventions d'exploitation", "subventions exploitation"],
    "FP": ["reprises sur amortissements et provisions", "reprises amortissements provisions"],
    "FQ": ["autres produits"],
    "FR": ["total des produits d'exploitation", "total produits exploitation"],
    "FS": ["achats de marchandises", "achats marchandises"],
    "FT": ["variation de stocks marchandises", "variation stocks marchandises"],
    "FU": ["achats de matières premières", "achats matieres premieres", "achats approvisionnements"],
    "FV": ["variation de stocks matières", "variation stocks matieres"],
    "FW": ["autres achats et charges externes", "autres achats charges externes", "charges externes"],
    "FX": ["impôts, taxes", "impots taxes"],
    "FY": ["salaires et traitements", "salaires"],
    "FZ": ["charges sociales"],
    "GA": ["dotations aux amortissements sur immobilisations", "dotations amortissements immo"],
    "GB": ["dotations aux provisions sur immobilisations", "dotations provisions immo"],
    "GC": ["dotations aux provisions sur actif circulant", "dotations provisions actif circulant"],
    "GD": ["dotations aux provisions pour risques et charges", "dotations provisions risques"],
    "GE": ["autres charges"],
    "GF": ["total des charges d'exploitation", "total charges exploitation"],
    "GG": ["résultat d'exploitation", "resultat exploitation"],
    "GH": ["bénéfice attribué", "benefice attribue"],
    "GI": ["perte supportée", "perte supportee"],
    "GM": ["reprises sur provisions financières", "reprises provisions financieres"],
    "GQ": ["dotations financières", "dotations financieres"],
    "GU": ["total des charges financières", "total charges financieres", "charges financières"],
    "HA": ["produits exceptionnels sur opérations de gestion", "produits exceptionnels gestion"],
    "HB": ["produits exceptionnels sur opérations en capital", "produits exceptionnels capital"],
    "HC": ["reprises sur provisions exceptionnelles", "reprises provisions exceptionnelles"],
    "HF": ["charges exceptionnelles sur opérations en capital", "charges exceptionnelles capital"],
    "HG": ["dotations exceptionnelles", "dotations exceptionnelles provisions"],
    "HI": ["résultat exceptionnel", "resultat exceptionnel"],
    "HJ": ["participation des salariés", "participation salaries"],
    "HK": ["impôts sur les bénéfices", "impots benefices", "is"],
    "HN": ["bénéfice ou perte", "resultat net", "benefice", "perte"],
    "A1": ["transfert de charges", "transferts charges"],
}

# ============================================
# MOTS-CLÉS POUR L'ÉTAT DES ÉCHÉANCES
# ============================================

MOTS_CLES_ETAT_ECHEANCES = {
    "VA": ["clients douteux", "creances douteuses", "clients litigieux"],
    "VC": ["groupe et associés", "groupe associes", "comptes courants actif"],
    "VH": ["annuité à venir", "annuite venir", "annuites"],
    "VI": ["groupe et associés", "groupe associes", "comptes courants passif"],
}

# ============================================
# MOTS-CLÉS POUR L'AFFECTATION DU RÉSULTAT
# ============================================

MOTS_CLES_AFFECTATION = {
    "ZE": ["dividendes"],
    "YQ": ["engagements de crédit-bail mobilier", "credit-bail mobilier", "credit bail mobilier"],
    "YR": ["engagements de crédit-bail immobilier", "credit-bail immobilier", "credit bail immobilier"],
    "YT": ["sous-traitance"],
    "YU": ["personnel extérieur", "personnel exterieur", "intérim", "interim"],
}

# ============================================
# LIBELLÉS DE RÉFÉRENCE (pour fuzzy matching)
# ============================================

LIBELLES_BILAN_ACTIF = {
    "Frais d'établissement": "Frais d'établissement",
    "Frais de développement": "Frais de développement",
    "Concessions, brevets et droits similaires": "Concessions, brevets et droits similaires",
    "Fonds commercial": "Fonds commercial",
    "Autres immobilisations incorporelles": "Autres immobilisations incorporelles",
    "Avances et acomptes sur immobilisations incorporelles": "Avances et acomptes sur immobilisations incorporelles",
    "Terrains": "Terrains",
    "Constructions": "Constructions",
    "Installations techniques, matériel et outillage industriels": "Installations techniques, matériel et outillage industriels",
    "Autres immobilisations corporelles": "Autres immobilisations corporelles",
    "Immobilisations en cours": "Immobilisations en cours",
    "Avances et acomptes": "Avances et acomptes",
    "Participations évaluées selon la méthode de mise en équivalence": "Participations évaluées selon la méthode de mise en équivalence",
    "Autres participations": "Autres participations",
    "Créances rattachées à des participations": "Créances rattachées à des participations",
    "Autres titres immobilisés": "Autres titres immobilisés",
    "Prêts": "Prêts",
    "Autres immobilisations financières": "Autres immobilisations financières",
    "TOTAL ACTIF IMMOBILISÉ": "TOTAL ACTIF IMMOBILISÉ",
    "Matières premières, approvisionnements": "Matières premières, approvisionnements",
    "En cours de production de biens": "En cours de production de biens",
    "En cours de production de services": "En cours de production de services",
    "Produits intermédiaires et finis": "Produits intermédiaires et finis",
    "Marchandises": "Marchandises",
    "Avances et acomptes versés sur commandes": "Avances et acomptes versés sur commandes",
    "Clients et comptes rattachés": "Clients et comptes rattachés",
    "Autres créances": "Autres créances",
    "Capital souscrit et appelé, non versé": "Capital souscrit et appelé, non versé",
    "Valeurs mobilières de placement": "Valeurs mobilières de placement",
    "Disponibilités": "Disponibilités",
    "Charges constatées d'avance": "Charges constatées d'avance",
    "TOTAL ACTIF CIRCULANT": "TOTAL ACTIF CIRCULANT",
    "Frais d'émission d'emprunt à étaler": "Frais d'émission d'emprunt à étaler",
    "TOTAL GÉNÉRAL": "TOTAL GÉNÉRAL",
    "Écarts de conversion actif": "Écarts de conversion actif"
}

LIBELLES_BILAN_PASSIF = {
    "Capital social ou individuel": "Capital social ou individuel",
    "Primes d'émission, de fusion, d'apport…": "Primes d'émission, de fusion, d'apport…",
    "Écarts de réévaluation": "Écarts de réévaluation",
    "Réserve légale": "Réserve légale",
    "Réserves statutaires ou contractuelles": "Réserves statutaires ou contractuelles",
    "Réserves réglementées": "Réserves réglementées",
    "Autres réserves": "Autres réserves",
    "Report à nouveau": "Report à nouveau",
    "RÉSULTAT DE L'EXERCICE (bénéfice ou perte)": "RÉSULTAT DE L'EXERCICE (bénéfice ou perte)",
    "Subventions d'investissement": "Subventions d'investissement",
    "Provisions réglementées": "Provisions réglementées",
    "Produit des émissions de titres participatifs": "Produit des émissions de titres participatifs",
    "Avances conditionnées": "Avances conditionnées",
    "Provisions pour risques": "Provisions pour risques",
    "Provisions pour charges": "Provisions pour charges",
    "Emprunts obligataires convertibles": "Emprunts obligatoires convertibles",
    "Autres emprunts obligatoires": "Autres emprunts obligataires",
    "Emprunts et dettes auprès des établissements de crédit": "Emprunts et dettes auprès des établissements de crédit",
    "Emprunts et dettes financières divers": "Emprunts et dettes financières divers",
    "Avances et acomptes reçus sur commandes en cours": "Avances et acomptes reçus sur commandes en cours",
    "Dettes fournisseurs et comptes rattachés": "Dettes fournisseurs et comptes rattachés",
    "Dettes fiscales et sociales": "Dettes fiscales et sociales",
    "Dettes sur immobilisations et comptes rattachés": "Dettes sur immobilisations et comptes rattachés",
    "Autres dettes": "Autres dettes",
    "Produits constatés d'avance": "Produits constatés d'avance",
    "TOTAL (I) - Capitaux propres": "TOTAL (I) - Capitaux propres",
    "TOTAL GENERAL (I à V)": "TOTAL GENERAL (I à V)"
}

LIBELLES_COMPTE_RESULTAT = {
    "Ventes de marchandises (France)": "Ventes de marchandises (France)",
    "Ventes de marchandises (Exportations)": "Ventes de marchandises (Exportations)",
    "Ventes de marchandises (TOTAL)": "Ventes de marchandises (TOTAL)",
    "Production vendue - Biens (France)": "Production vendue - Biens (France)",
    "Production vendue - Biens (Exportations)": "Production vendue - Biens (Exportations)",
    "Production vendue - Biens (TOTAL)": "Production vendue - Biens (TOTAL)",
    "Production vendue - Services (France)": "Production vendue - Services (France)",
    "Production vendue - Services (Exportations)": "Production vendue - Services (Exportations)",
    "Production vendue - Services (TOTAL)": "Production vendue - Services (TOTAL)",
    "Chiffres d'affaires nets (France)": "Chiffres d'affaires nets (France)",
    "Chiffres d'affaires nets (Exportations)": "Chiffres d'affaires nets (Exportations)",
    "Chiffres d'affaires nets (TOTAL)": "Chiffres d'affaires nets (TOTAL)",
    "Production stockée": "Production stockée",
    "Production immobilisée": "Production immobilisée",
    "Subventions d'exploitation": "Subventions d'exploitation",
    "Reprises sur amortissements et provisions, transferts de charges": "Reprises sur amortissements et provisions, transferts de charges",
    "Autres produits": "Autres produits",
    "TOTAL DES PRODUITS D'EXPLOITATION (I)": "TOTAL DES PRODUITS D'EXPLOITATION (I)",
    "Achats de marchandises (y compris droits de douane)": "Achats de marchandises (y compris droits de douane)",
    "Variation de stocks (marchandises)": "Variation de stocks (marchandises)",
    "Achats de matières premières et autres approvisionnements": "Achats de matières premières et autres approvisionnements",
    "Variation de stocks (matières premières et approvisionnements)": "Variation de stocks (matières premières et approvisionnements)",
    "Autres achats et charges externes": "Autres achats et charges externes",
    "Impôts, taxes et versements assimilés": "Impôts, taxes et versements assimilés",
    "Salaires et traitements": "Salaires et traitements",
    "Charges sociales": "Charges sociales",
    "Dotations aux amortissements (sur immobilisations)": "Dotations aux amortissements (sur immobilisations)",
    "Dotations aux provisions (sur immobilisations)": "Dotations aux provisions (sur immobilisations)",
    "Dotations aux amortissements (sur actif circulant)": "Dotations aux amortissements (sur actif circulant)",
    "Dotations aux provisions (sur actif circulant)": "Dotations aux provisions (sur actif circulant)",
    "Autres charges": "Autres charges",
    "TOTAL DES CHARGES D'EXPLOITATION (II)": "TOTAL DES CHARGES D'EXPLOITATION (II)",
    "RÉSULTAT D'EXPLOITATION (I - II)": "RÉSULTAT D'EXPLOITATION (I - II)",
    "Bénéfice attribué ou perte transférée (III)": "Bénéfice attribué ou perte transférée (III)",
    "Perte supportée ou bénéfice transféré (IV)": "Perte supportée ou bénéfice transféré (IV)",
    "Produits financiers de participations": "Produits financiers de participations",
    "Produits des autres valeurs mobilières et créances de l'actif immobilisé": "Produits des autres valeurs mobilières et créances de l'actif immobilisé",
    "Autres intérêts et produits assimilés": "Autres intérêts et produits assimilés",
    "Reprises sur provisions et transferts de charges": "Reprises sur provisions et transferts de charges",
    "Différences positives de change": "Différences positives de change",
    "Produits nets sur cessions de valeurs mobilières de placement": "Produits nets sur cessions de valeurs mobilières de placement",
    "TOTAL DES PRODUITS FINANCIERS (V)": "TOTAL DES PRODUITS FINANCIERS (V)",
    "Dotations financières aux amortissements et provisions": "Dotations financières aux amortissements et provisions",
    "Intérêts et charges assimilées": "Intérêts et charges assimilées",
    "Différences négatives de change": "Différences négatives de change",
    "Charges nettes sur cessions de valeurs mobilières de placement": "Charges nettes sur cessions de valeurs mobilières de placement",
    "TOTAL DES CHARGES FINANCIÈRES (VI)": "TOTAL DES CHARGES FINANCIÈRES (VI)",
    "RÉSULTAT FINANCIER (V - VI)": "RÉSULTAT FINANCIER (V - VI)",
    "RÉSULTAT COURANT AVANT IMPÔTS (I - II + III - IV + V - VI)": "RÉSULTAT COURANT AVANT IMPÔTS (I - II + III - IV + V - VI)",
    "Produits exceptionnels sur opérations de gestion": "Produits exceptionnels sur opérations de gestion",
    "Produits exceptionnels sur opérations en capital": "Produits exceptionnels sur opérations en capital",
    "Total des produits exceptionnels (VII)": "Total des produits exceptionnels (VII)",
    "Charges exceptionnelles sur opérations de gestion": "Charges exceptionnelles sur opérations de gestion",
    "Charges exceptionnelles sur opérations en capital": "Charges exceptionnelles sur opérations en capital",
    "Dotations exceptionnelles aux amortissements et provisions": "Dotations exceptionnelles aux amortissements et provisions",
    "Total des charges exceptionnelles (VIII)": "Total des charges exceptionnelles (VIII)",
    "RÉSULTAT EXCEPTIONNEL (VII - VIII)": "RÉSULTAT EXCEPTIONNEL (VII - VIII)",
    "Participation des salariés aux résultats de l'entreprise (IX)": "Participation des salariés aux résultats de l'entreprise (IX)",
    "Impôts sur les bénéfices (X)": "Impôts sur les bénéfices (X)",
    "TOTAL DES PRODUITS (I + III + V + VII)": "TOTAL DES PRODUITS (I + III + V + VII)",
    "TOTAL DES CHARGES (II + IV + VI + VIII + IX + X)": "TOTAL DES CHARGES (II + IV + VI + VIII + IX + X)",
    "BÉNÉFICE OU PERTE (Total des produits - Total des charges)": "BÉNÉFICE OU PERTE (Total des produits - Total des charges)",
    "Crédit-bail mobilier": "Crédit-bail mobilier",
    "Crédit-bail immobilier": "Crédit-bail immobilier",
    "Transfert de charges": "Transfert de charges"
}

LIBELLES_ETAT_ECHEANCES = {
    "Clients douteux ou litigieux": "Clients douteux ou litigieux",
    "Groupe et associés (créances)": "Groupe et associés (créances)",
    "Annuité à venir": "Annuité à venir",
    "Groupe et associés (dettes)": "Groupe et associés (dettes)"
}

LIBELLES_AFFECTATION = {
    "Dividendes": "Dividendes",
    "Engagements de crédit-bail mobilier": "Engagements de crédit-bail mobilier",
    "Engagements de crédit-bail immobilier": "Engagements de crédit-bail immobilier",
    "Sous-traitance": "Sous-traitance",
    "Personnel extérieur à l'entreprise": "Personnel extérieur à l'entreprise"
}
