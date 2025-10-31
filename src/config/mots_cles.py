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
