# Extraction de Liasses Fiscales - Version Camelot

## Vue d'ensemble

Ce projet propose maintenant **deux approches d'extraction** des liasses fiscales:

1. **main.py** - Version originale avec pdfplumber
2. **main_camelot.py** - Nouvelle version avec Camelot ✨

## Pourquoi Camelot ?

Camelot offre plusieurs avantages par rapport à pdfplumber:

### Avantages de Camelot
- ✅ **Extraction plus robuste** des tableaux avec lignes visibles
- ✅ **Scores de précision** pour chaque table extraite (83% à 95%)
- ✅ **Deux modes d'extraction**:
  - `lattice`: Pour les tableaux avec lignes (par défaut)
  - `stream`: Fallback pour les tableaux sans lignes
- ✅ **DataFrames pandas** en sortie (plus facile à manipuler)
- ✅ **Meilleure gestion des colonnes** fusionnées et décalées

### Limites de pdfplumber
- ⚠️ Extraction moins précise des tableaux complexes
- ⚠️ Problèmes fréquents avec les colonnes numériques
- ⚠️ Pas de score de qualité d'extraction

## Résultats de comparaison

### Test sur "Liasse fiscale vierge.pdf"

**Version Camelot (main_camelot.py):**
```
✅ Bilan Actif: 93.2% précision - 8 lignes extraites
✅ Bilan Passif: 95.7% précision - 5 lignes extraites
✅ Compte de Résultat: 75-94% précision - 18 lignes extraites
✅ État des Échéances: 83.2% précision - 22 lignes extraites
✅ Affectation: 83.3% précision - 8 lignes extraites
```

**Version pdfplumber (main.py):**
```
⚠️ Bilan Actif: Colonnes numériques non trouvées - 0 valeurs
⚠️ Bilan Passif: Colonnes numériques non trouvées - 0 valeurs
⚠️ Compte de Résultat: Extraction partielle
⚠️ État des Échéances: Extraction partielle
⚠️ Affectation: 5 lignes mais 0 montants
```

## Installation

### Dépendances système
```bash
# Les dépendances système sont gérées automatiquement via pip
```

### Dépendances Python
```bash
pip install -r requirements.txt
```

Les principales dépendances Camelot:
- `camelot-py>=1.0.9` - Bibliothèque principale
- `opencv-python-headless>=4.7.0` - Traitement d'images
- `ghostscript>=0.8.0` - Rendu PDF
- `cffi>=2.0.0` - Interface C
- `pandas>=2.2.2` - Manipulation de données

## Utilisation

### Version Camelot (recommandée)
```bash
python main_camelot.py
```

### Version pdfplumber (legacy)
```bash
python main.py
```

## Structure des fichiers

```
Application-extraction-liasse-fiscale-v2/
│
├── main.py                 # Version originale (pdfplumber)
├── main_camelot.py         # Nouvelle version (Camelot) ✨
├── requirements.txt        # Dépendances mises à jour
│
├── liasses/               # Placer vos PDFs ici
│   └── *.pdf
│
├── resultats/             # Fichiers Excel générés
│   ├── extraction_multi_annees.xlsx           # Version pdfplumber
│   └── extraction_multi_annees_camelot.xlsx   # Version Camelot
│
└── src/                   # Modules partagés
    ├── extractors/        # Extractors spécifiques par formulaire
    ├── export/            # Génération Excel
    └── utils/             # Utilitaires
```

## Fonctionnalités

Les deux versions extraient les mêmes formulaires:
- 📊 **Bilan Actif** (Formulaire 2050)
- 📊 **Bilan Passif** (Formulaire 2051)
- 📊 **Compte de Résultat** (Formulaires 2052-2053)
- 📊 **État des Échéances** (Formulaire 2057)
- 📊 **Affectation du Résultat** (Formulaire 2058-C)

## Format de sortie Excel

Le fichier Excel contient:
- **Une feuille par année** fiscale
- **Sections séparées** pour chaque formulaire
- **En-têtes formatés** (bleu foncé, texte blanc)
- **Largeurs de colonnes** optimisées

## Débogage

### Version Camelot
Le script affiche des informations détaillées:
- 📊 Mode d'extraction utilisé (lattice/stream)
- ✅ Nombre de tableaux extraits
- 📈 Score de précision par table
- 📋 Dimensions du DataFrame

Exemple:
```
   📊 Mode Camelot: lattice
   ✓ 1 tableau(x) extrait(s)
      Table 1: précision = 93.2%
   📋 DataFrame shape: (44, 8)
```

### Version pdfplumber
Logs détaillés sur:
- 🔍 Colonnes détectées
- ⚠️ Problèmes d'extraction
- 📊 Libellés trouvés vs valeurs extraites

## Recommandations

🎯 **Pour de meilleurs résultats**:
1. Utilisez `main_camelot.py` pour les PDFs avec tableaux structurés
2. Vérifiez les scores de précision dans les logs
3. Si Camelot échoue sur un PDF, essayez `main.py` en fallback

## Développement futur

Améliorations possibles:
- [ ] Hybride: Camelot pour les tableaux + pdfplumber pour le texte
- [ ] Paramètres Camelot ajustables (seuils, modes)
- [ ] Post-traitement des données extraites
- [ ] Validation des montants
- [ ] Interface web avec choix de l'engine

## Licence

Ce projet est fourni tel quel, à des fins éducatives.
