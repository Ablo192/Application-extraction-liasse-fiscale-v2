# Nouvelle Approche Analytique - Extraction de Liasses Fiscales

## 🎯 Problème résolu

Tu avais raison ! L'ancienne approche était trop rigide et ne s'adaptait pas aux variations de structure des PDFs. Elle supposait que :
- La colonne "Net" serait toujours au même index
- Le décalage de +1 depuis "Exercice N" serait toujours valable
- Les codes seraient toujours trouvés aux mêmes positions

**Résultat** : Si la structure du PDF changeait légèrement, l'extraction échouait.

## ✨ Solution : Approche Analytique en 3 Phases

### 📍 **PHASE 1 : Détection Intelligente**

**Objectif** : Trouver tous les tableaux pertinents sans faire d'hypothèses sur leur position.

**Comment ça marche** :
```python
# Utilise des signatures multiples pour chaque type de tableau
SIGNATURES_TABLEAUX = {
    TypeTableau.ACTIF: [
        "ACTIF IMMOBILISÉ",
        "ACTIF CIRCULANT",
        "Brut",
        "Amortissements",
        "Net"
    ],
    TypeTableau.PASSIF: [
        "Capital social ou individuel",
        "capitaux propres",
        "Dettes fournisseurs"
    ]
}

# Nécessite au moins 2 correspondances pour valider
SEUILS_DETECTION = {
    TypeTableau.ACTIF: 2,
    TypeTableau.PASSIF: 2
}
```

**Avantages** :
- ✅ Ne suppose rien sur le numéro de page
- ✅ Détecte même si le PDF a une structure différente
- ✅ Évite les faux positifs grâce aux seuils

### 📍 **PHASE 2 : Analyse de la Structure**

**Objectif** : Comprendre comment les colonnes sont organisées dans chaque tableau.

**Fonctionnement** :
1. Analyse les 5 premières lignes pour trouver les en-têtes
2. Identifie le type de chaque colonne :
   - `code` : Colonnes avec codes (AB, DA, FL...)
   - `libelle` : Descriptions textuelles
   - `montant_net` : Colonne "Net"
   - `exercice_n` : Colonne "Exercice N"
   - `montant_brut` : Colonne "Brut"
3. Attribue un score de confiance à chaque identification

**Exemple de résultat** :
```
Colonnes identifiées :
  - Index 9: montant_brut ('Brut') [confiance: 90%]
  - Index 12: amortissement ('Amortissements') [confiance: 90%]
  - Index 15: montant_net ('Net') [confiance: 90%]
```

**Si les en-têtes ne sont pas détectés** : Analyse de secours par position et contenu typique.

### 📍 **PHASE 3 : Extraction avec Règles Métier**

**Objectif** : Extraire les bonnes données selon les règles spécifiques à chaque tableau.

**Règles implémentées** :

| Tableau | Règle | Logique |
|---------|-------|---------|
| **Actif** | 3ème colonne de montant | Cherche d'abord "Net", sinon prend la 3ème colonne |
| **Passif** | 1ère colonne de montant | Cherche "Exercice N", sinon prend la 1ère |
| **Compte Résultat** | 1ère colonne de montant | Cherche "Exercice N", sinon prend la 1ère |
| **Clients douteux** | 1ère colonne | Directement la 1ère colonne de montant |
| **Annuités** | 2ème colonne | Directement la 2ème colonne de montant |
| **Affectation** | 1ère colonne | Directement la 1ère colonne de montant |

**Stratégies d'extraction (ordre de priorité)** :
1. **Chercher par nom** : "Net" pour l'actif
2. **Chercher par numéro** : 3ème colonne de montant
3. **Fallback** : Première colonne de montant disponible

## 🚀 Utilisation

### Option 1 : Version analytique complète (recommandée)

```bash
# Place tes PDFs dans le dossier 'liasses/'
python3 main_v2_analytique.py
```

Résultat : Fichier Excel dans `resultats/extraction_analytique_multi_annees.xlsx`

### Option 2 : Tester la détection seulement

```bash
python3 test_analytique.py
```

Affiche les tableaux détectés et les colonnes identifiées.

### Option 3 : Utilisation programmatique

```python
from main_v2_analytique import extraire_un_pdf_analytique
from pathlib import Path

pdf = Path('liasses/ma_liasse.pdf')
resultats = extraire_un_pdf_analytique(pdf)

# resultats contient :
# {
#   'actif': [(libellé, montant), ...],
#   'passif': [(libellé, montant), ...],
#   'cr': [(libellé, montant), ...],
#   'echeances': [...],
#   'affectation': [...]
# }
```

## 📊 Comparaison Avant/Après

### Ancienne approche (main.py)

```python
def _trouver_colonne_passif_n(table_passif):
    for row in table_passif:
        for i, cell in enumerate(row):
            if "Exercice N" in str(cell):
                return i + 1  # ← DÉCALAGE FIXE !
    return None

# Problème : Si le décalage n'est pas +1, ça ne marche pas
```

### Nouvelle approche (extraction_analytique.py)

```python
# 1. Détecte TOUTES les colonnes de montants
colonnes_montants = AnalyseurStructure.identifier_colonnes_montants(colonnes)

# 2. Applique la règle métier
if 'exercice_n' in col.type_colonne:
    return col.index  # ← ADAPTIF !

# 3. Fallback si pas trouvé
return colonnes_montants[0].index
```

## 🔧 Fichiers créés

```
extraction_analytique.py       # Module principal (3 phases)
├── DetecteurTableaux          # Phase 1
├── AnalyseurStructure         # Phase 2
├── ExtracteurDonnees          # Phase 3
└── ExtractionAnalytique       # Orchestrateur

main_v2_analytique.py          # Adaptateur pour le code existant
test_analytique.py             # Script de test
APPROCHE_ANALYTIQUE.md         # Documentation détaillée
```

## 🎓 Concepts clés implémentés

### 1. Détection par Signatures Multiples
Au lieu d'un seul mot-clé, on utilise plusieurs mots-clés et un seuil :
```python
# Besoin d'au moins 2 de ces mots-clés pour valider "ACTIF"
["ACTIF IMMOBILISÉ", "ACTIF CIRCULANT", "Brut", "Net"]
```

### 2. Analyse Multi-Niveaux
Pour identifier une colonne, on essaie :
1. Analyse de l'en-tête
2. Analyse du contenu typique
3. Analyse par position

### 3. Règles Métier Externalisées
Au lieu de coder les règles dans chaque fonction, elles sont centralisées :
```python
REGLES_COLONNES_MONTANTS = {
    TypeTableau.ACTIF: {
        'colonne_prioritaire': 'montant_net',
        'numero_colonne_fallback': 3
    }
}
```

### 4. Dégradation Gracieuse
Si une stratégie échoue, on passe à la suivante automatiquement.

## 📈 Résultats

**Sur un PDF vierge (test de structure)** :
- ✅ Détecte 6 types de tableaux
- ✅ Identifie les colonnes (Brut, Net, Exercice N)
- ✅ Sélectionne les bonnes colonnes selon les règles métier
- ✅ 0 valeurs extraites (normal, PDF vierge)

**Sur un PDF avec données** :
- ✅ Devrait extraire tous les montants correctement
- ✅ Même si la structure varie légèrement
- ✅ Logs détaillés pour debugging

## 🔮 Évolutions possibles

1. **Prioriser le premier tableau de chaque type** : Actuellement détecte plusieurs "actif", pourrait ne garder que le premier
2. **Validation croisée** : Vérifier que Total Actif = Total Passif
3. **ML/AI** : Entraîner un modèle pour identifier les colonnes
4. **Détection d'anomalies** : Alerter si montants incohérents
5. **Multi-formats** : Export en JSON, CSV, XML

## 💡 Conseils d'utilisation

1. **Pour débugger** : Lance `test_analytique.py` pour voir la détection et l'analyse
2. **Pour production** : Utilise `main_v2_analytique.py`
3. **Pour intégrer dans l'interface** : Remplace `extraire_un_pdf` par `extraire_un_pdf_analytique` dans `interface.py`

## ⚠️ Points d'attention

- Le PDF doit être vierge OU rempli, pas corrompu
- Les signatures sont optimisées pour les liasses fiscales françaises standard
- Si un type de tableau n'est pas détecté, vérifier les signatures dans `SIGNATURES_TABLEAUX`

---

**Auteur** : Claude
**Date** : 2025-10-30
**Version** : 2.0 Analytique
