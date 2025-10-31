# 📊 Extraction Automatique de Liasses Fiscales

Application Python pour extraire automatiquement les données comptables des liasses fiscales françaises (formulaires 2050, 2051, 2052, 2057, 2058) et générer un fichier Excel consolidé avec analyse financière.

## ✨ Fonctionnalités

- ✅ **Extraction automatique** des bilans actif/passif
- ✅ **Compte de résultat** complet (2 pages)
- ✅ **État des échéances** (créances et dettes)
- ✅ **Affectation du résultat** et renseignements divers
- ✅ **43 ratios financiers** calculés automatiquement
- ✅ **Détection automatique de l'année fiscale** depuis le PDF
- ✅ **Interface graphique** avec Streamlit
- ✅ **Architecture modulaire** et maintenable

## 🚀 Installation

```bash
# Cloner le repository
git clone https://github.com/Ablo192/Application-extraction-liasse-fiscale-v2.git
cd Application-extraction-liasse-fiscale-v2

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Utilisation

### Option 1 : Interface Graphique (Recommandé)

Lancez l'interface Streamlit :

```bash
streamlit run interface.py
```

Puis :
1. **Téléversez** vos fichiers PDF (glisser-déposer)
2. **L'année est détectée automatiquement** (modifiable si nécessaire)
3. **Cliquez** sur "Extraire les données"
4. **Téléchargez** le fichier Excel généré

### Option 2 : Ligne de Commande

Placez vos fichiers PDF dans le dossier `liasses/` puis :

```bash
python main.py
```

Le fichier Excel sera généré dans `resultats/extraction_multi_annees.xlsx`

## 📊 Fichier Excel Généré

Le fichier Excel contient **2 onglets** :

### Onglet 1 : Données Fiscales
- Toutes les données extraites des formulaires
- Organisation par catégories (Actif, Passif, CR, etc.)
- Colonnes par année pour comparaison multi-exercices

### Onglet 2 : Analyse Financière
- **43 ratios financiers** calculés automatiquement :
  - Activité & Rentabilité (CA, EBE, Résultats, CAF, etc.)
  - Bilan (Solvabilité, Gearing, Leverage, Dette nette, etc.)
  - Cycle d'exploitation (FRNG, BFR, délais clients/fournisseurs, etc.)

## 📈 Améliorations (v2.1)

Par rapport à la version précédente :

- ✅ **Architecture modulaire** : Code organisé en modules (89% de réduction du fichier principal)
- ✅ **Détection automatique de l'année** : Plus besoin de saisir manuellement
- ✅ **Détection dynamique des colonnes** : Fini les indices hardcodés
- ✅ **Code maintenable** : Facile à modifier et étendre
- ✅ **Documentation complète** : Docstrings sur toutes les fonctions

**Version** : 2.1 (Architecture Refactorisée)
